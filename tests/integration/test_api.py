import httpx
import pytest
import shutil
import time
import os


# Define the base URL of your FastAPI application
BASE_URL = "http://RAG_BOT_FASTAPI:8000"

# ToDo: Support multi-chat sessions and then make integration tests run in parallel

# This is a fixture is used by process_scraped_document test to copy a test file to the src directory
@pytest.fixture(scope="function")
def copy_scrapped_file():
    source = "tests/test-data/test-scrapped-doc.md"
    destination = "src/scraper/scraped_data/test-scrapped-doc.md"
    
    # Ensure the destination directory exists (if it doesn't, you might want to create it)
    shutil.copy(source, destination)

    yield  # This is where the test will be executed


def test_scrapper():
    with httpx.Client() as client: 
        response = client.post(f"{BASE_URL}/scrape/", json={"url": "https://github.com/kylejtobin/rag_bot"})
        assert response.status_code == 200

# Warning: This test is dependent on the previous test scraping data. Should figure out a way to do this in a more robust way
def test_process_scraped_document(copy_scrapped_file):
    with httpx.Client(timeout=15.0) as client: 
        response = client.post(
            f"{BASE_URL}/process-documents/", 
            json={
                "source_dir": "/app/src/scraper/scraped_data",
                "collection_name": "techdocs"
            }
        )
        assert response.status_code == 200

def test_basic_chat_hi_no_rag():
    time.sleep(2) # Give bot time between tests. Need to add support from multi-chat
    with httpx.Client(timeout=30.0) as client: # Chat response can take a while
        response = client.post(f"{BASE_URL}/chat/", json={ "user_input": "Simply respond with hi" })
        assert response.status_code == 200

# This is dependent on the previous tests creating data in qdrant. Should figure out a way to do this in a more robust way
# Idea: Create a fixture that runs before all tests and creates the data in qdrant
def test_chat_with_rag():
    time.sleep(2) # Give bot time between tests
    with httpx.Client(timeout=60.0) as client: # Chat response can take a while
        response = client.post(f"{BASE_URL}/chat/", json={ "user_input": "What are the basic steps to get rag_bot up and running?" })
        assert response.status_code == 200