# src/agent/agent_handler.py

# Custom module imports for config and tool setup
from src.utils.config import load_config, setup_environment_variables
from src.tools.setup import ToolSetup

# LangChain imports based on the provided code example
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents.format_scratchpad import format_log_to_str
from langchain_core.prompts import PromptTemplate

# Standard library imports
import logging
import traceback
from pathlib import Path

logger = logging.getLogger(__name__)


# Global variable to store the agent handler instance
_agent_instance = None


class AgentHandler:
    def __init__(self):
        self._initialize()

    def _initialize(self):
        self.CONFIG = load_config()
        setup_environment_variables(self.CONFIG)
        self.llm = ChatOpenAI(model=self.CONFIG["OpenAI"]["model"], temperature=self.CONFIG["OpenAI"]["llm_temp"])
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.tools = ToolSetup.setup_tools()
        self._load_prompt_templates() 
        self.agent_executor = self._initialize_agent_executor()

    def _load_prompt_templates(self):
        """Load templates for the ZeroShotAgent's prompts."""
        try:
            template_path = Path("/app/src/template")
            self.PROMPT_TEMPLATES = {file.stem: file.read_text() for file in template_path.iterdir() if file.suffix == '.txt'}
        except Exception as e:
            logging.error(f"Error loading prompt templates: {e}")
            raise

    def _setup_prompt_template(self) -> PromptTemplate:
        """
        Construct and return the prompt template for the agent based on loaded templates and tools.

        Returns:
            PromptTemplate: The constructed prompt template.

        Raises:
            KeyError: If a required key is missing in self.PROMPT_TEMPLATES.
        """
        tools = self.tools

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

    def _initialize_agent_executor(self):
        prompt = self._setup_prompt_template()

        # Bind the llm with a stop condition
        llm_with_stop = self.llm.bind(stop=["\nObservation"])

        # Correctly retrieving chat history from memory
        react_chain = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
                "chat_history": lambda x: self.memory.load_memory_variables(x).get('chat_history', '')  # Correct retrieval of chat history
            }
            | prompt
            | llm_with_stop
            | ReActSingleInputOutputParser()
        )

        return AgentExecutor(agent=react_chain, tools=self.tools, verbose=True)

    def chat_with_agent(self, user_input: str):
        try:
            response = self.agent_executor.invoke({'input': user_input})

            if 'output' in response and hasattr(response['output'], 'response'):
                chat_response = response['output'].response  # Extract the response text
            else:
                chat_response = "Unable to process your request."

            # Log the concise chat response
            logging.info(f"User input: '{user_input}' | Chatbot response: '{chat_response}'")
            return chat_response
        except Exception as e:
            tb_str = traceback.format_exception(None, e, e.__traceback__)
            logging.error(f"Chat error: {''.join(tb_str)}")
            return "An error occurred."


def get_agent_handler():
    # Singleton-like accessor for the AgentHandler instance
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgentHandler()
    return _agent_instance