# /app/src/agent/agent_handler.py

# Custom modules
from src.utils.config import load_config, setup_environment_variables
from src.tools.setup import ToolSetup

# Primary Components
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.prompts import PromptTemplate

# Utilities
from typing import Dict
from pathlib import Path
import logging
import traceback

# Global variable to store the agent handler instance.
_agent_instance = None


class AgentHandler:
    """
    Class responsible for initializing and executing the conversational agent.
    Handles OpenAI setup, memory management, and prompt templates.
    """

    def __init__(self):
        self._initialize()

    def _initialize(self):
        """Initialize all components required for the agent."""
        self._setup_config_and_env()
        self._setup_openai()
        self._setup_memory()
        self._load_prompt_templates()
        self._initialize_agent_executor()

    def _setup_config_and_env(self):
        """Load configurations and setup environment variables."""
        self.CONFIG = load_config()
        setup_environment_variables(self.CONFIG)

    def _setup_openai(self):
        """Initialize the OpenAI model based on configurations."""
        try:
            self.llm = ChatOpenAI(
                model=self.CONFIG["OpenAI"]["model"], 
                temperature=self.CONFIG["OpenAI"]["llm_temp"]
            )
        except Exception as e:
            logging.error(f"Error initializing OpenAI: {e}")
            raise

    def _setup_memory(self):
        """Setup conversation buffer memory for chat history."""
        self.memory = ConversationBufferMemory(memory_key="chat_history")

    def _load_prompt_templates(self):
        """Load templates for the ZeroShotAgent's prompts."""
        try:
            template_path = Path("/app/src/template")
            self.PROMPT_TEMPLATES = {file.stem: file.read_text() for file in template_path.iterdir() if file.suffix == '.txt'}
        except Exception as e:
            logging.error(f"Error loading prompt templates: {e}")
            raise

    def _initialize_agent_executor(self):
        """Initialize the ZeroShotAgent with proper configurations."""
        self.agent_executor = self._setup_agent()

    def _setup_tools(self) -> list:
        """
        Initialize and return the tools required for the ZeroShotAgent.
        """
        return ToolSetup.setup_tools()

    def _setup_prompt_template(self) -> PromptTemplate:
        """
        Construct and return the prompt template for the agent based on loaded templates and tools.
        
        Returns:
            PromptTemplate: The constructed prompt template.
            
        Raises:
            KeyError: If a required key is missing in self.PROMPT_TEMPLATES.
        """
        tools = self._setup_tools()  # This method returns a list of tools
        
        # Extracting the templates from self.PROMPT_TEMPLATES
        try:
            prefix = self.PROMPT_TEMPLATES["prefix"]
            react_cot = self.PROMPT_TEMPLATES["react_cot"]
            suffix = self.PROMPT_TEMPLATES["suffix"]
        except KeyError as e:
            logging.error(f"Missing key in PROMPT_TEMPLATES: {e}")
            raise
        
        # Constructing the tools string and tool_names string using list comprehension
        tools_str = '\n'.join(f"{tool.name}: {tool.description}" for tool in tools)
        tool_names_str = ', '.join(tool.name for tool in tools)
        
        # Replacing the placeholder with the actual tool names in the template strings
        react_cot = react_cot.replace("{tool_names}", tool_names_str)
        
        # Constructing the final template string
        final_template_str = f"{prefix}\n{tools_str}\n{react_cot}\n{suffix}"
        
        # Creating an instance of PromptTemplate
        prompt_template = PromptTemplate(
            input_variables=["chat_history", "input", "agent_scratchpad"],
            template=final_template_str
        )
        
        return prompt_template



    def _setup_agent(self) -> AgentExecutor:
        """
        Construct and return the ZeroShotAgent with all its configurations.
        """
        prompt = self._setup_prompt_template()
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        agent = ZeroShotAgent(
            llm_chain=llm_chain, 
            tools=self._setup_tools(), 
            verbose=True
        )
        return AgentExecutor.from_agent_and_tools(
            agent=agent, 
            tools=self._setup_tools(), 
            verbose=True, 
            memory=self.memory
        )

    def chat_with_agent(self, user_input: str) -> str:
        """
        Handle user input to chat with the agent and return its response.
        """
        try:
            response = self.agent_executor.run(input=user_input)
            logging.info(f"Successful chat response for input '{user_input}': {response}")
            return response.get("output") if isinstance(response, dict) else response
        except Exception as e:
            # Capture the full stack trace for the exception and log it
            tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
            logging.error(f"Error while chatting with agent for input '{user_input}': {''.join(tb_str)}")
            return "An error occurred."

def get_agent_handler() -> AgentHandler:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgentHandler()
    return _agent_instance



