import asyncio
from typing import Any, Dict

from core.llm_clients import OpenAIClient
from core.logger_utils import get_logger

logger = get_logger(__name__)


# Define a static evaluation dataset
EVALUATION_DATASET = [
    {
        "query": "What is the capital of France?",
        "expected_output": "Paris",
    },
    {
        "query": "Explain the concept of RAG in LLMs.",
        "expected_output": "Retrieval-Augmented Generation (RAG) is a technique...",  # Placeholder, actual expected output might vary
    },
    {
        "query": "Write a short poem about programming.",
        "expected_output": "Code flows like rivers bright...",  # Placeholder
    },
]


async def _async_evaluation_task(x: Dict[str, Any]) -> Dict[str, Any]:
    """
    Internal asynchronous function to call the OpenAI API.
    """
    try:
        # Consider initializing the client once outside the task if possible,
        # but for simplicity with asyncio.run, we do it here.
        llm_client = OpenAIClient()  # Assumes API key is in env
        messages = [{"role": "user", "content": x["query"]}]
        answer = await llm_client.generate(messages=messages)
    except Exception as e:
        logger.error(f"Error during LLM generation for query '{x['query']}': {e}")
        answer = f"Error: {e}"  # Return error message as output

    return {
        "input": x["query"],
        "output": answer,
        "expected_output": x.get("expected_output", ""),
        "reference": x.get("expected_output", ""),
    }


def sync_evaluation_task(x: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper to run the async evaluation task.
    Needed for compatibility with opik.evaluation.evaluate if it expects a sync function.
    """
    return asyncio.run(_async_evaluation_task(x))


async def main() -> None:
    """
    Main asynchronous function to run the evaluation by calling the LLM directly.
    """
    logger.info("Starting LLM evaluation using static dataset and OpenAI client.")

    # Use the static dataset defined above
    dataset = EVALUATION_DATASET
    if not dataset:
        logger.error("Evaluation dataset is empty. Exiting.")
        return

    logger.info(f"Evaluating {len(dataset)} samples...")
    results = []
    for i, item in enumerate(dataset):
        logger.info(f"--- Sample {i + 1} ---")
        logger.info(f"Input Query: {item['query']}")
        result = sync_evaluation_task(item)  # Call the synchronous wrapper
        logger.info(f"LLM Output: {result['output']}")
        logger.info(f"Expected Output: {result['expected_output']}")
        results.append(result)
        logger.info("-----------------")

    logger.info("Evaluation complete.")
    # Optionally, save results to a file or perform further analysis
    # For now, just logging is sufficient to verify the task runs.


if __name__ == "__main__":
    # Main remains async because it calls the sync wrapper which internally uses asyncio.run.
    # Running the main async function using asyncio.run() is the correct approach here.
    asyncio.run(main())
