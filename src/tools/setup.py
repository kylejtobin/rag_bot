# /app/src/tools/setup.py

# Primary Components 
from langchain import SerpAPIWrapper
from langchain.agents import Tool
from langchain.tools import tool

from src.tools.doc_search import DocumentSearch

class ToolSetup:
    """
    A class dedicated to the setup and initialization of tools used by the agent.
    """
    
    def __init__(self):
        # Currently, the constructor doesn't require any initializations.
        pass
        
    @staticmethod
    def setup_tools() -> list:
        """
        Static method to initialize and return a list of tools for the agent.
        
        Returns:
        - list: A list of initialized tools for agent's use. 
        """
        
        # Create an instance of the SerpAPI wrapper for Google searches.
        search = SerpAPIWrapper()
        
        @tool("search_techdocs")
        def search_techdocs(query: str, collection: str="techdocs") -> str:
            """This tool enables the querying of a specialized vector store named ‘TechDocs,’ a repository where users archive valuable technical documentation they have encountered. It is particularly beneficial when engaging with technical subjects or when involved in coding activities. Utilize this search tool to scrutinize the vector store for pertinent context when addressing technical inquiries or tasks. If a term from the user input is unfamiliar but appears to be technical in nature, it is imperative to consult ‘TechDocs’ to ascertain whether relevant information or context is available therein. For your awareness, the information provided is sourced from ‘TechDocs,’ and we will refer to this source for any related queries."""
            
            search = DocumentSearch(collection, query)
            results = search.search_documents()

            return results
            
        
        return [
            Tool(
                name="Search", 
                func=search.run,
                description="The Search tool uses SerpAPI to conduct Google searches. It retrieves raw search results without any inherent interpretation. Use this tool to fetch real-time information and analyze the results."
            ),
            search_techdocs
        ]