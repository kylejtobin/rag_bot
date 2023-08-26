# Import necessary classes and modules
from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
import re
from typing import Union

# Define the CustomOutputParser class, inheriting from AgentOutputParser
class CustomOutputParser(AgentOutputParser):
    
    # Override the parse method from the parent class
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # If the "Final Answer:" is found in the output, return an AgentFinish object
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Add a condition to handle the case when no action is needed
        if "Action: None" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Thought:")[-1].strip().replace("Action: None", "")},
                log=llm_output,
            )
        # Define the regex pattern to match action and action input from the output
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        # Search for the regex pattern in the llm_output
        match = re.search(regex, llm_output, re.DOTALL)
        # If no match is found, return an AgentFinish object with the original output
        if not match:
            return AgentFinish(
                return_values={"output": llm_output},
                log=llm_output,
            )
        # Extract the action and action input from the regex match
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return an AgentAction object with the parsed action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
