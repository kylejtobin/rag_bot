import httpx
import pytest


# Define the base URL of your FastAPI application
BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_basic_chat_hi_no_rag():
    async with httpx.AsyncClient(timeout=10.0) as client: # Chat response can take a while
        response = await client.post(f"{BASE_URL}/chat/", json={ "user_input": "Hi" })
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_chat_with_rag():
    async with httpx.AsyncClient(timeout=30.0) as client: # Chat response can take a while
        response = await client.post(f"{BASE_URL}/chat/", json={ "user_input": "What are the basic steps to get rag_bot up and running?" })
        assert response.status_code == 200