# /app/src/api/routes.py
import logging

from fastapi import APIRouter

from src.agent.agent_handler import get_agent_handler
from src.api.handlers import (handle_chat, handle_document_search,
                              handle_process_documents, handle_scrape)
from src.api.models import (ChatInput, ChatOutput, DocumentLoaderRequest,
                            DocumentLoaderResponse, DocumentSearchRequest,
                            ScrapeRequest, ScrapeResponse)

logger = logging.getLogger(__name__)


# Initialize the router.
router = APIRouter()


# === Chat Endpoint ===
@router.post("/chat/", response_model=ChatOutput)
def chat_endpoint(data: ChatInput):
    """
    Endpoint to interact with the chat agent.

    This function receives user input, passes it to the chat handler,
    and returns the chat agent's response.

    Args:
    data (ChatInput): The user input data encapsulated in a ChatInput object.

    Returns:
    ChatOutput: The response from the chat agent encapsulated in a ChatOutput object.
    """
    # Delegate to the chat handler and return the response.
    agent = get_agent_handler()
    return handle_chat(data, agent)


# === Web Scraper Endpoint ===
@router.post("/scrape/", response_model=ScrapeResponse)
async def scrape_endpoint(data: ScrapeRequest):
    """
    Endpoint to initiate the web scraping process.

    This asynchronous function receives a URL, passes it to the scrape handler,
    and returns the result of the scraping process.

    Args:
    data (ScrapeRequest): The data containing the URL to be scraped.

    Returns:
    ScrapeResponse: The result of the scraping process encapsulated in a ScrapeResponse object.
    """
    # Delegate to the scrape handler and return the response.
    return await handle_scrape(data)


# === Document Loader Endpoint ===
@router.post("/process-documents/", response_model=DocumentLoaderResponse)
def process_documents_endpoint(data: DocumentLoaderRequest) -> DocumentLoaderResponse:
    """
    Endpoint to initiate the document loading process.

    This function receives the source directory and the collection name,
    passes them to the document loader handler, and returns the status of the
    processed files encapsulated in a DocumentLoaderResponse object.

    Args:
    data (DocumentLoaderRequest): The data containing the source directory
                                  and the collection name to which the documents should be loaded.

    Returns:
    DocumentLoaderResponse: A response object containing the status of the document
                            loading process and an optional message.
    """
    return handle_process_documents(data)


# === Document Search Endpoint ===
@router.post("/search-documents/", response_model=str)
def search_documents_endpoint(data: DocumentSearchRequest) -> str:
    """
    Endpoint to initiate the document search process.

    Args:
    data (DocumentSearchRequest): The data containing the collection name and user input.

    Returns:
    DocumentSearchResponse: The result of the document search process.
    """
    return handle_document_search(data)
