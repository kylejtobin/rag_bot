# /app/src/scraper/scraper_main.py

# Custom modules
from src.utils.config import load_config

# Primary Modules
from urllib.parse import urlparse
from requests.exceptions import RequestException
import requests
from bs4 import BeautifulSoup, Tag

# Utilities
import os
import hashlib
import logging
import sys
import random

logger = logging.getLogger(__name__)


# WebScraper Utilities
def setup_logging():
    """
    Set up the logging configuration for the scraper.

    This function configures the logging module to output INFO and above logs 
    to the stdout, while WARNING and above logs are redirected to stderr. 
    It uses a custom format that prefixes each log message with "RAG_BOT" 
    followed by the log timestamp, the log level, and the actual log message.

    Returns:
        bool: Always returns True to indicate successful setup.
    """

    # Basic configuration for the logging module:
    # - Direct all logs to stdout
    # - Set the lowest level of logs to be captured as INFO
    # - Define a custom format for the logs
    logging.basicConfig(
        stream=sys.stdout,  # Logs will go to stdout
        level=logging.INFO,
        format="RAG_BOT: %(asctime)s - %(levelname)s - %(message)s"
    )

    # Create a separate handler for logs of level WARNING and above. 
    # This handler will send these logs to stderr instead of stdout, 
    # which is helpful to quickly identify warnings and errors.
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(logging.Formatter("RAG_BOT: %(asctime)s - %(levelname)s - %(message)s"))

    # Add the stderr handler to the root logger
    logging.getLogger().addHandler(stderr_handler)

    return True


# WebScraper Base Class
class Scraper:
    """
    The Scraper class is designed to provide base functionality for web scraping tasks.

    Attributes:
    - logger (Logger): An instance of the logging.Logger class to facilitate event logging.
    - CONFIG (dict): Configuration data loaded from a configuration source (like a JSON file).

    Methods:
    - get_random_user_agent(): Return a random user agent from the list of user agents in the configuration.
    """

    def __init__(self):
        """
        Initialize the Scraper instance.

        This method initializes logging for the scraper and loads configuration data,
        which among other things, may contain a list of user agents to be used for scraping tasks.
        """
        # Initialize logger for the Scraper class
        self.logger = logging.getLogger("Scraper")

        # Load configuration data for the scraper
        self.CONFIG = load_config()

    def get_random_user_agent(self):
        """
        Fetch and return a random user agent string from the list specified in the configuration.

        The method chooses a user agent randomly from the list in the CONFIG attribute. Using 
        random user agents can help mimic genuine user activity, potentially avoiding blocking 
        by web servers during scraping tasks.

        Returns:
        - str: A randomly selected user agent string.
        """
        return random.choice(self.CONFIG["Scraper"]["USER_AGENTS"])


# WebScraper Content Parser
class ContentParser:
    """
    A class designed to extract meaningful content from HTML tags and 
    convert them into a markdown format.

    Supported HTML tags include paragraphs, headers (h1-h6), list items, links, 
    inline code, and code blocks.
    """

    # Dictionary that maps HTML tags to their corresponding extraction methods
    TAG_TYPES = {
        "p": "text",
        "h1": "header",
        "h2": "header",
        "h3": "header",
        "h4": "header",
        "h5": "header",
        "h6": "header",
        "li": "list_item",
        "a": "link",
        "code": "code",
        "pre": "pre"
    }

    def extract_content(self, element):
        """
        Extract content from a given HTML element and its descendants, 
        converting it into markdown format.

        Args:
        - element (Tag): A Beautiful Soup Tag object to extract content from.

        Returns:
        - str: The extracted content in markdown format.
        """
        content_list = []

        # Check if the element is a valid Beautiful Soup Tag
        if isinstance(element, Tag):

            # Get the type of tag (e.g., header, text, link)
            tag_type = self.TAG_TYPES.get(element.name)

            if tag_type:
                # Find the corresponding extraction method for the tag type
                content_method = getattr(self, f"_extract_{tag_type}_content")
   
                # Extract content from the tag
                content_list.append(content_method(element))
            else:
                # If the tag isn't directly mapped in TAG_TYPES, 
                # check its children for content extraction
                for child in element.children:
                    content_list.append(self.extract_content(child))
       
        # Join the extracted content list into a single markdown string
        return "\n\n".join(filter(None, content_list))

    def _extract_text_content(self, element):
        """Extract content from a paragraph tag."""
        return element.get_text(strip=True)

    def _extract_header_content(self, element):
        """Extract content from header tags (h1-h6) and convert to markdown format."""
        return "#" * int(element.name[1]) + " " + element.get_text(strip=True)

    def _extract_list_item_content(self, element):
        """Extract content from list item tags and convert to markdown format."""
        return "* " + element.get_text(strip=True)

    def _extract_link_content(self, element):
        """Extract content from anchor tags, converting them to markdown links."""
        text = element.get_text(strip=True)
        href = element.get('href', '')
        return f"[{text}]({href})"

    def _extract_code_content(self, element):
        """Extract content from inline code tags and convert to markdown format."""
        return f"`{element.get_text(strip=True)}`"

    def _extract_pre_content(self, element):
        """Extract content from code block tags and convert to markdown format."""
        return f"```\n{element.get_text()}\n```"


# WebScraper Class
class SingletonMeta(type):
    """Metaclass for the Singleton design pattern.

    Ensures that only one instance of a class inheriting this metaclass exists.
    """

    _instances = {}  # Store created instances

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class WebScraper(Scraper, metaclass=SingletonMeta):
    """Main WebScraper class for scraping content from websites and saving to a file.

    Inherits base scraper functionalities and uses a singleton pattern for unique instance handling.
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.content_parser = ContentParser()
        self.CONFIG = load_config()
        self.setup_data_directory()

    def setup_data_directory(self):
        """Sets up the data directory for saving scraped content."""
        if not os.path.exists(self.CONFIG["Scraper"]["DATA_DIR"]):
            os.makedirs(self.CONFIG["Scraper"]["DATA_DIR"])
            self.logger.info("Data directory created successfully.")
        else:
            self.logger.info("Data directory already exists.")

    @staticmethod
    def is_valid_url(url):
        """Validates the given URL.

        Args:
            url (str): The URL to validate.

        Returns:
            bool: True if URL is valid, otherwise False.
        """
        try:
            parsed_url = urlparse(url)
            return bool(parsed_url.netloc) and bool(parsed_url.scheme)
        except ValueError:
            return False

    def fetch_content(self, url):
        """Fetches content from the given URL using HTTP requests.

        Args:
            url (str): The URL to fetch content from.

        Returns:
            str: Fetched content if successful, otherwise None.
        """
        self.logger.info(f"Attempting to fetch content from {url}")
        headers = {"User-Agent": self.get_random_user_agent()}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if 200 <= response.status_code < 300:
                return response.text
            else:
                self.logger.warning(f"Received a non-2xx status code ({response.status_code}) from {url}")
                return None
        except RequestException as e:
            self.logger.error(f"Error fetching content from {url}: {e}")
            return None
   
    def parse_content(self, content):
        """Parses the fetched content using BeautifulSoup and extracts the meaningful data.

        Args:
            content (str): The fetched web content.

        Returns:
            dict: A dictionary containing the parsed data.
        """
        self.logger.info("Parsing the content.")
        soup = BeautifulSoup(content, 'html.parser')

        parsed_data = {
            "title": soup.title.string if soup.title else "",
            "metadata": {
                "description": soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else ""
            },
            "content": self.content_parser.extract_content(soup.body)  # Use ContentParser to extract content
        }

        self.logger.info("Content parsed successfully.")
        return parsed_data

    @staticmethod
    def generate_filename(url):
        """Generates a filename using a hash of the URL.

        Args:
            url (str): The URL to hash and generate the filename.

        Returns:
            str: The generated filename with a path.
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(load_config()["Scraper"]["DATA_DIR"], f"{url_hash}.md")  

    def save_to_file(self, url, content):
        """Saves the parsed content to a file.

        Args:
            url (str): The URL used to generate the filename.
            content (str): The parsed content to save.

        Returns:
            str: The filepath where content was saved if successful, otherwise None.
        """
        self.logger.info("Saving content to file.")
        filepath = self.generate_filename(url)
        try:
            with open(filepath, 'w', encoding='utf-8') as f: 
                f.write(content)
            self.logger.info(f"Content saved successfully to {filepath}.")
        except Exception as e:
            self.logger.error(f"Error saving content to {filepath}: {e}")
            return None
        return filepath

    def scrape_site(self, url):
        """Main method for orchestrating the entire scraping process.

        Args:
            url (str): The URL to scrape.

        Returns:
            dict: Contains a message indicating the outcome and, if successful, the filepath where content was saved.
        """
        self.logger.info(f"Starting scraping for URL: {url}")

        if not self.is_valid_url(url):
            self.logger.error("Provided URL is invalid.")
            return {"message": "Invalid URL", "data": ""}

        content = self.fetch_content(url)
        if not content:
            self.logger.error("Failed to fetch content from URL.")
            return {"message": "Failed to fetch content from URL", "data": ""}

        parsed_data = self.parse_content(content)
        parsed_content = parsed_data["content"]

        filepath = self.save_to_file(url, parsed_content)  
        if not filepath:
            self.logger.error("Failed to save content.")
            return {"message": "Failed to save content", "data": ""}

        self.logger.info("Scraping completed successfully.")
        return {"message": "Scraping completed successfully", "data": filepath}


# WebScraper Main function
def run_web_scraper(url):
    """
    Initializes a WebScraper instance and triggers the scraping process for the given URL.

    Args:
        url (str): The URL of the website to be scraped.

    Returns:
        dict: A dictionary containing the result of the scraping process. 
              This may include messages indicating success or failure and 
              potentially where the scraped data has been saved.
    """
    scraper = WebScraper()
    return scraper.scrape_site(url)


if __name__ == "__main__":
    # Try setting up logging. Logging is essential to track the progress 
    # and troubleshoot any issues that arise during the scraping process.
    if setup_logging():

        # Prompt the user for the URL to be scraped
        url = input("Enter URL to scrape: ")

        # Begin the scraping process
        result = run_web_scraper(url)

        # If the scraping was successful, display a success message with 
        # details about where the data was saved. Otherwise, display an error message.
        if result and result.get("message") == "Scraping completed successfully":
            print(f"Scraping complete! Saved to {result['data']}")
        else:
            print(result["message"])

    # If logging setup fails, exit the program with an error message.
    else:
        print("Failed to set up logging. Exiting.")
