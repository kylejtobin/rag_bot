# rag_bot - A Retrieval Augmented Generative Chatbot

rag_bot provides a dev-ready architecture for developers to build advanced conversational agents using retrieval augmented generation (RAG). The project combines modern frameworks like FastAPI, Docker, and LangChain to deliver a robust platform for chatbots that can have more informed, contextual conversations by retrieving and referencing external knowledge.

## 🎯 **Purpose and Value**

This project aims to enable developers to quickly build and deploy RAG chatbots that can:

- Have more engaging, dynamic conversations powered by large language models.
- Retrieve relevant information from custom knowledge sources to make conversations more helpful and factual.
- Learn continuously from new conversations and information sources.

It provides a solutions accelerator for teams looking to implement production-grade RAG chatbots that go beyond just chit-chat to deliver value across industries like customer support, e-commerce, finance, and more.

## 🚀 Getting Started

### Prerequisites

To use this project, you will need:

- Docker and Docker Compose installed  
- Python 3.7+
- An OpenAI API key

### Setup  

To set up the project:

1. Clone this repository to your local machine.

2. Rename `.env.example` to `.env` and add your OpenAI API key.  

3. In `docker-compose.yml`, update the `volumes` path for `RAG_BOT_QDRANT` to a local folder where you want persistent storage for the vector database.

4. Build the Docker images:
   ```bash
    docker-compose build
    ```
5. Start the services:
   ```bash
   docker-compose up -d
   ```
The services will now be running at:

- FastAPI server: [http://localhost:8000](http://localhost:8000)
- Gradio UI: [http://localhost:7860](http://localhost:7860)
- Qdrant: [http://localhost:6333](http://localhost:6333)

## 🏗 **Architecture Overview**

The rag_bot architecture consists of the following key components:

- FastAPI - High performance REST API framework. Handles HTTP requests and routes them to application logic.
- Gradio - Interface for interacting with the bot via GUI.
- Qdrant - Vector database for storing document embeddings and enabling similarity search.
- AgentHandler - Orchestrates the initialization and execution of the conversational agent.
- Tools - Custom tools that extend the capabilities of the agent.

## 🧰 **Detailed Component Analysis**
Let's take a closer look at some of the key components:

### FastAPI
FastAPI provides a robust web framework for handling the API routes and HTTP requests/responses.

Some key advantages:

- Built on modern Python standards like type hints and ASGI.
- Extremely fast - benchmarked to be faster than NodeJS and Go.
- Automatic interactive docs using OpenAPI standards.
- In this project, main.py initializes the application and sets up the /chat endpoint which is the gateway for users to interact with the bot.

### AgentHandler
This class located at src/agent/agent_handler.py is responsible for setting up and running the conversational agent.

It handles:

- Loading configuration and environment variables
- Initializing the OpenAI model
- Setting up conversation history memory
- Loading prompt templates to guide bot behavior
- Constructing the ZeroShotAgent with proper tools and configurations
- Routing user input to the agent and returning responses

To ensure efficient resource usage, it employs a singleton pattern where only one instance of the AgentHandler is created per application lifecycle.

### Tools
The tools module provides a way to easily extend the agent's capabilities by integrating external libraries, APIs, and custom logic.

Tools like the SerpAPI search wrapper and document searcher enable the agent to have contextual conversations by finding relevant information on-the-fly.

Developers can build on top of the included tools or create new ones based on their unique needs.

### Prompt Engineering
Well-crafted prompt templates are key to guiding the agent's persona, tone, and functionality. Prompt engineering is an iterative process that requires lots of testing and refinement.

The project includes sample prompt files covering the prefix, suffix, and input variables. Developers can use these as a starting point and customize them further for their specific chatbot requirements.

## 🚢 **Deployment and Usage**
Once the Docker containers are up and running, you can start chatting with the bot via:

- The **interactive Swagger docs** at [http://localhost:8000/docs](http://localhost:8000/docs)
- The **Gradio web interface** at [http://localhost:7860](http://localhost:7860)


## 🛠 **Customization and Extendability**
While the project provides a solid architecture, there are ample opportunities for customization and extensibility:

- Data Sources - Integrate additional knowledge sources like databases, internal company documents etc.
- Models - Experiment with different language models based on your conversational requirements.
- Tools - Build new tools to extend the agent's capabilities like calendars, weather data, translations etc.
- Prompts - Refine and optimize prompts for your chatbot's persona and use cases.
- Visual Interface - Develop custom graphical interfaces tailored to your needs.
- API Integration - Build on top of the FastAPI backend to integrate with other services.
