# /app/src/api/models.py
import logging
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


# === Chat Models ===
class ChatInput(BaseModel):
    """
    Model representing the user input for chat interactions.

    Attributes:
    user_input (str): The input string from the user to the chat.
    """
    user_input: str = "What are the basic steps to get rag_bot up and running?"


class ChatOutput(BaseModel):
    """
    Model representing the response from the chat agent.

    Attributes:
    response (str): The response string from the chat agent to the user.
    """
    response: str


# === Web Scraper Models ===
class ScrapeRequest(BaseModel):
    """
    Model representing the request to initiate web scraping.

    Attributes:
    url (str): The URL of the web page to be scraped.
    """
    url: str = 'https://github.com/kylejtobin/rag_bot'


class ScrapeResponse(BaseModel):
    """
    Model representing the response from the web scraping process.

    Attributes:
    message (str): The status message indicating the success or failure
                   of the scraping process.
    data (Optional[str]): The scraped data from the web page if the
                          scraping process is successful. None, if unsuccessful.
    """
    message: str
    data: Optional[str]


# === Document Loader Models ===
class DocumentLoaderResponse(BaseModel):
    """
    Model representing the response from the document loading process.

    Attributes:
    status (str): The status of the document loading process.
                  It will be 'success' if the documents are processed successfully.
    message (Optional[str]): Optional message field to convey any additional
                             information or details about the process.
    """
    status: str
    message: Optional[str]


class DocumentLoaderRequest(BaseModel):
    """
    Model representing the request to initiate document loading.

    Attributes:
    source_dir (str): The directory from where the documents are to be loaded.
                      Default is set to the directory where scraped data is stored.
    collection (str): The name of the collection to which the documents
                           should be loaded. Default is "techdocs".
    """
    source_dir: str = '/app/src/scraper/scraped_data'
    collection: str = "techdocs"


# === Document Search Models ===
class DocumentSearchRequest(BaseModel):
    """
    Model representing the request to initiate document search.

    Attributes:
    collection (str): The name of the collection to be queried.
    user_input (str): The user input query for searching documents.
    """
    collection: str
    user_input: str
