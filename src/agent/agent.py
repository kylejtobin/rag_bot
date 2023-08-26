# Import necessary modules and classes
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain import SerpAPIWrapper, LLMChain
from template.template import CustomPromptTemplate, read_template
from langchain.chat_models import ChatOpenAI
from parser.parser import CustomOutputParser
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from utils.config import load_config

# Load configuration from config.yml
config = load_config()

def setup_agent(chatbot_name):
    # Instantiate a SerpAPIWrapper object for search functionality
    search = SerpAPIWrapper()
    # Instantiate a datetime object for datetime functionality
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="The Search tool uses SerpAPI to conduct Google searches. It retrieves raw search results without any inherent interpretation. Utilize this tool to fetch real-time information, but always analyze and deduce relevant details from the results, avoiding the use of generic placeholders."
        ),
    ]

    # Set up the prompt template using the base.txt file and the tools list
    prompt = CustomPromptTemplate(
        template=read_template(str(Path(__file__).resolve().parent.parent / "template" / "base.txt")).replace("{chatbot_name}", chatbot_name),
        tools=tools,
        input_variables=["input", "intermediate_steps"]
    )

    # Instantiate a CustomOutputParser object for parsing output
    output_parser = CustomOutputParser()

    # Instantiate a ChatOpenAI object for language model interaction
    llm = ChatOpenAI(temperature=config["OpenAI"]["llm_temp"])

    # Set up the LLMChain using the ChatOpenAI object and prompt template
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Extract tool names from the tools list
    tool_names = [tool.name for tool in tools]
    # Set up the LLMSingleActionAgent with LLMChain, output parser, and allowed tools
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )

    # Create an AgentExecutor from the agent and tools with verbose output
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
    return agent_executor   

def chat_with_agent(user_input: str, chatbot_name: str):
    # Set up the agent using the setup_agent() function
    agent_executor = setup_agent(chatbot_name)
    # Execute the agent with the given user_input and get the response
    response = agent_executor.run(user_input)
    # If the response is a dictionary, return the 'output' value, otherwise, return the response itself
    if isinstance(response, dict):
        return response.get("output")
    else:
        return response
