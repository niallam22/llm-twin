import asyncio
from typing import Any, Dict

from llm_twin import LLMTwin

from core.config import settings
from core.llm_clients import OpenAIClient
from core.logger_utils import get_logger

# Reuse the static dataset definition (or define a specific one for RAG)
# For simplicity, let's assume EVALUATION_DATASET is defined similarly or imported
from .evaluate import EVALUATION_DATASET  # Import from evaluate.py

# Removed opik imports
# from opik.evaluation import evaluate
# from opik.evaluation.metrics import (
#     ContextPrecision,
#     ContextRecall,
#     Hallucination,
# )

settings.patch_localhost()

logger = get_logger(__name__)
logger.warning(
    "Patched settings to work with 'localhost' URLs. \
    Remove the 'settings.patch_localhost()' call from above when deploying or running inside Docker."
)


async def _async_evaluation_task(x: Dict[str, Any]) -> Dict[str, Any]:
    """
    Internal asynchronous function to call the LLM Twin with RAG enabled.
    """
    try:
        llm_client = OpenAIClient()  # Assumes API key is in env
        inference_pipeline = LLMTwin()  # Instantiates retriever internally
        result = await inference_pipeline.generate(
            query=x["query"],
            enable_rag=True,
            llm_client=llm_client,  # Pass the client instance
        )
        answer = result["answer"]
        context = result["context"]
    except Exception as e:
        logger.error(f"Error during RAG generation for query '{x['query']}': {e}")
        answer = f"Error: {e}"
        context = []  # Provide empty context on error

    return {
        "input": x["query"],
        "output": answer,
        "context": context,
        "expected_output": x.get("expected_output", ""),
        "reference": x.get("expected_output", ""),
    }


def sync_evaluation_task(x: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper to run the async RAG evaluation task.
    """
    return asyncio.run(_async_evaluation_task(x))


async def main() -> None:
    """
    Main asynchronous function to run the RAG evaluation.
    """
    logger.info("Starting RAG evaluation using static dataset and OpenAI client.")

    # Use the static dataset defined/imported above
    dataset = EVALUATION_DATASET
    if not dataset:
        logger.error("Evaluation dataset is empty. Exiting.")
        return

    logger.info(f"Evaluating {len(dataset)} samples with RAG...")
    results = []
    for i, item in enumerate(dataset):
        logger.info(f"--- RAG Sample {i + 1} ---")
        logger.info(f"Input Query: {item['query']}")
        result = sync_evaluation_task(item)  # Call the synchronous wrapper
        logger.info(f"LLM Output: {result['output']}")
        logger.info(f"Retrieved Context: {result['context']}")
        logger.info(f"Expected Output: {result['expected_output']}")
        results.append(result)
        logger.info("----------------------")

    logger.info("RAG Evaluation complete.")
    # Optionally, save results or perform RAG-specific metric calculations manually


if __name__ == "__main__":
    asyncio.run(main())
