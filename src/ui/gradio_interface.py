# /app/src/ui/gradio_interface.py
import gradio as gr
import requests

FASTAPI_URL = "http://fastapi:8000/chat/"  # This is the URL of your FastAPI service inside the Docker network

def chat_with_bot(user_input: str) -> str:
    """Function to interface with Gradio that chats with the agent through the FastAPI service."""
    response = requests.post(FASTAPI_URL, json={"user_input": user_input})
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return "Error communicating with the agent."

# Gradio Interface
iface = gr.Interface(
    fn=chat_with_bot, 
    inputs="text", 
    outputs="text"
)

# If this script is run directly, launch the Gradio app
if __name__ == "__main__":
    iface.launch(server_port=7860, server_name="0.0.0.0")
