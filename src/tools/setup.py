# /app/src/tools/setup.py

# Primary Components 
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool

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
        SerpAPI = SerpAPIWrapper()
        
        def search_web(query: str) -> str:
            """
            This function uses the SerpAPI wrapper to conduct a Google search and returns the raw search results.
            """
            return SerpAPI.run(query)
        
        def search_techdocs(query: str, collection: str="techdocs") -> str:
            """
            This tool enables the querying of a specialized vector store named ‘TechDocs,’ a repository where users archive valuable technical documentation they have encountered. It is particularly beneficial when engaging with technical subjects or when involved in coding activities. Utilize this search tool to scrutinize the vector store for pertinent context when addressing technical inquiries or tasks. If a term from the user input is unfamiliar but appears to be technical in nature, it is imperative to consult ‘TechDocs’ to ascertain whether relevant information or context is available therein. For your awareness, the information provided is sourced from ‘TechDocs,’ and we will refer to this source for any related queries.
            """
            
            search = DocumentSearch(collection, query)
            results = search.search_documents()
            
            return results
        
        return [
            Tool(
                name="search_web",
                func=search_web,
                description="This is a tool that conducts Google searches via the SerpAPI to retrieve real-time search results programmatically, allowing for efficient extraction and analysis of search data to obtain current and relevant web information for a given query."
            ),
            Tool(
                name="search_techdocs",
                func=search_techdocs,
                description="This tool enables the querying of a specialized vector store named ‘TechDocs,’ a repository where users archive valuable technical documentation they have encountered."
            )
        ]