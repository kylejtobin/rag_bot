# /app/src/main.py

# Primary Components
from fastapi import FastAPI

# Internal Modules
from src.api.routes import router
from src.utils.config import load_config, setup_environment_variables
from src.agent.agent_handler import get_agent_handler  # Dependency function and AgentHandler for the application

import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(name)s - %(funcName)s - %(message)s",
    stream=sys.stdout,
)

# Load configuration and set up environment variables
config = load_config()
setup_environment_variables(config)

# Initialize the FastAPI application
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """
    Actions to be performed when the application starts up.
    Currently initializes the AgentHandler. Extend this function if more startup logic is needed.
    """
    app.agent_instance = get_agent_handler()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup actions to be performed when the application shuts down.
    Extend this function if any cleanup logic for components like AgentHandler is required.
    """
    pass

# Include the API router
app.include_router(router)
