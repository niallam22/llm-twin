import logging
import sys
from pathlib import Path

import requests

# To mimic using multiple Python modules, such as 'core' and 'feature_pipeline',
# we will add the './src' directory to the PYTHONPATH. This is not intended for
# production use cases but for development and educational purposes.
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.append(ROOT_DIR)

# from core.config import settings # No longer needed directly?
# from llm_twin import LLMTwin # No longer instantiating directly


import gradio as gr

# from inference_pipeline.llm_twin import LLMTwin # Removed

# llm_twin = LLMTwin(mock=False) # Removed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the API endpoint URL (adjust if not using Docker Compose)
API_ENDPOINT = "http://api:80/generate"
# API_ENDPOINT = "http://localhost:8000/generate" # Use this if running locally without Docker


def predict(message: str, history: list[list[str]], author: str) -> str:
    """
    Generates a response using the LLM Twin, simulating a conversation with your digital twin.

    Args:
        message (str): The user's input message or question.
        history (List[List[str]]): Previous conversation history between user and twin.
        about_me (str): Personal context about the user to help personalize responses.

    Returns:
        str: The LLM Twin's generated response.
    """

    query = f"I am {author}. Write about: {message}"
    payload = {"query": query, "use_rag": True}  # Assuming use_rag=True is desired for UI

    logger.info(f"Sending request to {API_ENDPOINT} with payload: {payload}")

    try:
        response = requests.post(API_ENDPOINT, json=payload, timeout=120)  # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        response_data = response.json()
        logger.info(f"Received response: {response_data}")
        return response_data.get("answer", "Error: Could not parse answer from response.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling API endpoint {API_ENDPOINT}: {e}")
        return f"Error: Could not connect to the inference API. Details: {e}"
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"


demo = gr.ChatInterface(
    predict,
    textbox=gr.Textbox(
        placeholder="Chat with your LLM Twin",
        label="Message",
        container=False,
        scale=7,
    ),
    additional_inputs=[
        gr.Textbox(
            "Paul Iusztin",
            label="Who are you?",
        )
    ],
    title="Your LLM Twin",
    description="""
    Chat with your personalized LLM Twin! This AI assistant will help you write content incorporating your style and voice.
    """,
    theme="soft",
    examples=[
        [
            "Draft a post about RAG systems.",
            "Paul Iusztin",
        ],
        [
            "Draft an article paragraph about vector databases.",
            "Paul Iusztin",
        ],
        [
            "Draft a post about LLM chatbots.",
            "Paul Iusztin",
        ],
    ],
    cache_examples=False,
)


if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, share=True)
