# /app/src/api/handlers.py

# Internal Modules
from src.agent.agent_handler import AgentHandler, get_agent_handler
from src.scraper.scraper import run_web_scraper
from src.loader.document import DocumentLoader
from src.tools.doc_search import DocumentSearch
from src.api.models import ChatInput, DocumentLoaderRequest, DocumentLoaderResponse, ScrapeRequest, DocumentSearchRequest

# Primary Components
from fastapi import Depends, HTTPException

# Utilities
import logging

logger = logging.getLogger(__name__)


# ===== CHAT HANDLER =====
def handle_chat(data: ChatInput, agent: AgentHandler = Depends(get_agent_handler)):
    """Handles chat interactions with AgentHandler.

    Args:
        data (ChatInput): The user input data
        agent (AgentHandler): The AgentHandler instance  

    Returns:
        dict: Response from agent
    """
    response = agent.chat_with_agent(data.user_input)
    if isinstance(response, dict):
        # Extract just the string message from the response object
        return {"response": response["output"].response}
    else:
        # If response is already a string, return as is
        return {"response": response}


# ===== WEB SCRAPER HANDLER =====
async def handle_scrape(data: ScrapeRequest):
    """
    Initiates the web scraping process on the provided URL.

    This asynchronous function logs the triggering of the scrape endpoint
    and runs the web scraper on the URL provided in the ScrapeRequest object.

    Args:
    data (ScrapeRequest): The data containing the URL to be scraped.

    Returns:
    Any: The result of the web scraping process.
    """
    logger = logging.getLogger("Scraper")
    logger.info("Scrape endpoint triggered.")

    # Run the web scraper and return the result.
    return run_web_scraper(data.url)


# ===== DOCUMENT LOADER HANDLER =====
def handle_process_documents(data: DocumentLoaderRequest) -> DocumentLoaderResponse:
    """
    Processes documents from a specified source directory and loads them into a collection.

    This function initiates a DocumentLoader with the specified source directory and 
    collection name from the DocumentLoaderRequest object. It then loads the documents 
    from the source directory into the specified collection. If there are any errors during 
    the process, it raises an HTTPException.

    Args:
    data (DocumentLoaderRequest): The data containing the source directory and the
                                  collection name to which the documents should be loaded.

    Returns:
    DocumentLoaderResponse: A response object containing the status of the document 
                            loading process and an optional message.

    Raises:
    HTTPException: If there are any errors during the document loading process.
    """
    try:
        processor = DocumentLoader(source_dir=data.source_dir, collection=data.collection)
        processor.load_documents()  # This should block until processing is complete
        return DocumentLoaderResponse(status="success", message="Documents processed successfully")
    except Exception as e:
        logging.error(f"Error processing documents: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== DOCUMENT SEARCHER HANDLER =====
def handle_document_search(data: DocumentSearchRequest) -> str:
    """Handles document search request and returns the raw response.

    This function receives a DocumentSearchRequest containing the collection
    name and user query input. It instantiates a DocumentSearch object and 
    calls search_documents() to perform the actual search.

    The search_documents() method is returning a raw string response rather 
    than a list of results. So this handler simply returns the raw string.

    No iteration or post-processing is done on the result string. The client
    must handle the raw response appropriately.

    Args:
        data (DocumentSearchRequest): The request data containing the collection and query.

    Returns:
        str: The raw response string from the DocumentSearch.

    Raises:
        HTTPException: If any exception occurs during the search process. The
                       message will contain the underlying error details.

    Usage:

        ```
        request_data = DocumentSearchRequest(
            collection="mydocs",
            user_input="hello world"
        )

        response_string = handle_document_search(request_data)

        print(response_string)
        ```
    """
    try:
        document_search = DocumentSearch(collection=data.collection, user_input=data.user_input)

        results = document_search.search_documents()
        logging.debug(f"Raw results: {results}")

        return str(results)

    except Exception as e:
        logging.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
