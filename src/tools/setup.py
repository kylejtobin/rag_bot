# /app/src/tools/setup.py
import logging

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchResults

from src.tools.doc_search import DocumentSearch

logger = logging.getLogger(__name__)


class SearchWebInput(BaseModel):
    query: str = Field(description="The search query")


class SearchTechDocsInput(BaseModel):
    query: str = Field(description="The search query")
    collection: str = Field(default="techdocs", description="The document collection to search in")


class SearchWebTool(BaseTool):
    name = "search_web"
    description = "Conducts DuckDuckGo searches."
    args_schema = SearchWebInput
    return_direct = True

    def _run(self, query: str, **kwargs) -> str:
        search = DuckDuckGoSearchResults()
        return search.run(query)


class SearchTechDocsTool(BaseTool):
    name = "search_techdocs"
    description = "This tool enables the querying of a specialized vector store named ‘TechDocs,’ a repository where users archive valuable technical documentation they have encountered. It is particularly beneficial when engaging with technical subjects or when involved in coding activities. Utilize this search tool to scrutinize the vector store for pertinent context when addressing technical inquiries or tasks. If a term from the user input is unfamiliar but appears to be technical in nature, it is imperative to consult ‘TechDocs’ to ascertain whether relevant information or context is available therein. For your awareness, the information provided is sourced from ‘TechDocs,’ and we will refer to this source for any related queries."
    args_schema = SearchTechDocsInput
    return_direct = True

    def _run(self, query: str, collection: str = "techdocs", **kwargs) -> str:
        search = DocumentSearch(query, collection)
        results = search.search_documents()
        return results


class ToolSetup:
    """
    A class dedicated to the setup and initialization of tools used by the agent.
    """

    @classmethod
    def setup_tools(cls) -> list:
        """
        Initializes and returns a list of tools for the agent.
        Returns:
        - list: A list of initialized tools for agent's use.
        """
        return [SearchWebTool(), SearchTechDocsTool()]
