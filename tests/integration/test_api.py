import httpx
import pytest
import time

# ToDo: Support multi-chat sessions and then make integration tests run in parallel

# Define the base URL of your FastAPI application
BASE_URL = "http://localhost:8000"


def test_basic_chat_hi_no_rag():
    time.sleep(2) # Give bot time between tests. Need to add support from multi-chat
    with httpx.Client(timeout=30.0) as client: # Chat response can take a while
        response = client.post(f"{BASE_URL}/chat/", json={ "user_input": "Simply respond with hi" })
        assert response.status_code == 200

def test_chat_with_rag():
    time.sleep(2) # Give bot time between tests
    with httpx.Client(timeout=45.0) as client: # Chat response can take a while
        response = client.post(f"{BASE_URL}/chat/", json={ "user_input": "What are the basic steps to get rag_bot up and running?" })
        assert response.status_code == 200