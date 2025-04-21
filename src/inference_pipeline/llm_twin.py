import pprint

from langchain.prompts import PromptTemplate

from src.core import logger_utils
from src.core.config import settings  # Import from src.core config
from src.core.llm_clients import LLMClientInterface  # Import the new interface
from src.core.opik_utils import add_to_dataset_with_sampling
from src.core.rag.retriever import VectorRetriever

from .prompt_templates import InferenceTemplate

logger = logger_utils.get_logger(__name__)


class LLMTwin:
    def __init__(self) -> None:
        # Keep prompt template builder initialization if it's stateless
        self.prompt_template_builder = InferenceTemplate()

    # @opik.track(name="inference_pipeline.generate")
    async def generate(  # Make method async
        self,
        query: str,
        llm_client: LLMClientInterface,  # Add the new client parameter
        # qdrant_client: QdrantClient, # Removed - VectorRetriever handles its own client
        collection_id: str,
        enable_rag: bool = False,
        sample_for_evaluation: bool = False,
    ) -> dict:
        system_prompt, prompt_template = self.prompt_template_builder.create_template(enable_rag=enable_rag)
        prompt_template_variables = {"question": query}

        if enable_rag is True:
            # VectorRetriever initializes its own Qdrant client internally
            retriever = VectorRetriever(query=query)  # Removed db_client argument
            hits = await retriever.retrieve_top_k(
                k=settings.TOP_K, to_expand_to_n_queries=settings.EXPAND_N_QUERY, collection_id=collection_id
            )

            # Rerank returns list[str], join them for the prompt context
            context_list = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)
            context = "\n\n".join(context_list)  # Join the context strings
            prompt_template_variables["context"] = context  # Assign the joined string
        else:
            context_list = []
            context = None

        messages = self.format_prompt(system_prompt, prompt_template, prompt_template_variables)  # Only get messages now

        logger.debug(f"Prompt: {pprint.pformat(messages)}")
        # Pass the llm_client to call_llm_service
        answer = await self.call_llm_service(messages=messages, llm_client=llm_client)
        logger.debug(f"Answer: {answer}")

        # Removed token calculation as it's less reliable with external APIs
        # num_answer_tokens = compute_num_tokens(answer)

        # opik_context.update_current_trace(
        #     tags=["rag"],  # Keep tags
        #     metadata={
        #         "prompt_template": prompt_template.template,
        #         "prompt_template_variables": prompt_template_variables,
        #         "model_id": settings.OPENAI_MODEL_ID,  # Use OpenAI model ID
        #         # Removed embedding_model_id (more relevant to retriever)
        #         # Removed token counts
        #     },
        # )

        answer = {"answer": answer, "context": context_list}
        if sample_for_evaluation is True:
            add_to_dataset_with_sampling(
                item={"input": {"query": query}, "expected_output": answer},
                dataset_name="LLMTwinMonitoringDataset",
            )

        return answer

    # @opik.track(name="inference_pipeline.format_prompt")
    def format_prompt(
        self,
        system_prompt,
        prompt_template: PromptTemplate,
        prompt_template_variables: dict,
    ) -> list[dict[str, str]]:  # Update return type annotation
        prompt = prompt_template.format(**prompt_template_variables)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        return messages  # Return only messages

    # @opik.track(name="inference_pipeline.call_llm_service")  # Keep Opik tracking
    async def call_llm_service(  # Correct async definition
        self,
        messages: list[dict[str, str]],
        llm_client: LLMClientInterface,  # Correct parameter
    ) -> str:
        """Calls the injected LLM client to generate a response."""
        # Removed mock check as per task 7.4.8

        # Call the injected LLM client's generate method
        answer = await llm_client.generate(messages=messages)
        # Return the answer directly (strip() might not be needed depending on client)
        return answer  # Return the result from the client
