import sys
from pathlib import Path

# To mimic using multiple Python modules, such as 'core' and 'feature_pipeline',
# we will add the './src' directory to the PYTHONPATH. This is not intended for
# production use cases but for development and educational purposes.
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.append(ROOT_DIR)

import asyncio  # Import asyncio

from llm_twin import LLMTwin

# from transformers import pipeline, AutoTokenizer # Removed imports
from src.core import logger_utils

# Import settings from the core config now
from src.core.llm_clients import OpenAIClient  # Import OpenAIClient

# Note: patch_localhost() might not be needed if inference_settings already point to localhost
# settings.patch_localhost() # Commented out - check inference_settings defaults

logger = logger_utils.get_logger(__name__)
logger.info(f"Added the following directory to PYTHONPATH to simulate multiple modules: {ROOT_DIR}")
# logger.warning( # Commented out - using local inference_settings
#     "Patched settings to work with 'localhost' URLs. \
#     Remove the 'settings.patch_localhost()' call from above when deploying or running inside Docker."
# )


async def main():
    # Instantiate OpenAIClient
    logger.info("Initializing OpenAI client for standalone test...")
    try:
        llm_client = OpenAIClient()
        logger.info("OpenAI client initialized successfully.")
    except Exception as e:
        logger.exception(f"Failed to initialize OpenAI client: {e}")
        sys.exit(1)  # Exit if client fails to initialize

    inference_endpoint = LLMTwin()  # Instantiate without mock

    query = """
Hello I am Paul Iusztin.
        
Could you draft an article paragraph discussing RAG? 
I'm particularly interested in how to design a RAG system.
        """

    # Call generate asynchronously, passing the client
    response = await inference_endpoint.generate(
        query=query,
        llm_client=llm_client,  # Pass the client
        enable_rag=True,
        sample_for_evaluation=True,  # Keep sampling for testing if desired
    )

    logger.info("=" * 50)
    logger.info(f"Query: {query}")
    logger.info("=" * 50)
    logger.info(f"Answer: {response.get('answer', 'N/A')}")  # Use .get for safety
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())  # Run the async main function
