import pprint

import opik
from langchain.prompts import PromptTemplate
from opik import opik_context
from prompt_templates import InferenceTemplate
from utils import compute_num_tokens

from core import logger_utils
from core.config import settings  # Import from core config
from core.llm_clients import LLMClientInterface  # Import the new interface
from core.opik_utils import add_to_dataset_with_sampling
from core.rag.retriever import VectorRetriever

logger = logger_utils.get_logger(__name__)


class LLMTwin:
    # Removed __init__ method - components will be passed to generate
    # def __init__(self, mock: bool = False) -> None:
    #     self._mock = mock
    #     self.prompt_template_builder = InferenceTemplate()
    #     # Initialization moved to startup event
    #     # self._local_llm_pipeline, self._tokenizer = self.build_local_pipeline()

    # Removed build_sagemaker_predictor method entirely

    # Removed build_local_pipeline - logic moved to API startup
    # def build_local_pipeline(self): ...

    def __init__(self) -> None:
        # Keep prompt template builder initialization if it's stateless
        self.prompt_template_builder = InferenceTemplate()

    @opik.track(name="inference_pipeline.generate")
    async def generate(  # Make method async
        self,
        query: str,
        llm_client: LLMClientInterface,  # Add the new client parameter
        # qdrant_client: QdrantClient, # Removed - VectorRetriever handles its own client
        enable_rag: bool = False,
        sample_for_evaluation: bool = False,
    ) -> dict:
        system_prompt, prompt_template = self.prompt_template_builder.create_template(enable_rag=enable_rag)
        prompt_template_variables = {"question": query}

        if enable_rag is True:
            # VectorRetriever initializes its own Qdrant client internally
            retriever = VectorRetriever(query=query)  # Removed db_client argument
            hits = retriever.retrieve_top_k(k=settings.TOP_K, to_expand_to_n_queries=settings.EXPAND_N_QUERY)
            # Rerank returns list[str], join them for the prompt context
            context_list = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)
            context = "\n\n".join(context_list)  # Join the context strings
            prompt_template_variables["context"] = context  # Assign the joined string
        else:
            context = None

        messages = self.format_prompt(system_prompt, prompt_template, prompt_template_variables)  # Only get messages now

        logger.debug(f"Prompt: {pprint.pformat(messages)}")
        # Pass the llm_client to call_llm_service
        answer = await self.call_llm_service(messages=messages, llm_client=llm_client)  # Add await
        logger.debug(f"Answer: {answer}")

        # Removed token calculation as it's less reliable with external APIs
        # num_answer_tokens = compute_num_tokens(answer)
        opik_context.update_current_trace(
            tags=["rag"],  # Keep tags
            metadata={
                "prompt_template": prompt_template.template,
                "prompt_template_variables": prompt_template_variables,
                "model_id": settings.OPENAI_MODEL_ID,  # Use OpenAI model ID
                # Removed embedding_model_id (more relevant to retriever)
                # Removed token counts
            },
        )

        answer = {"answer": answer, "context": context}
        if sample_for_evaluation is True:
            add_to_dataset_with_sampling(
                item={"input": {"query": query}, "expected_output": answer},
                dataset_name="LLMTwinMonitoringDataset",
            )

        return answer

    @opik.track(name="inference_pipeline.format_prompt")
    def format_prompt(
        self,
        system_prompt,
        prompt_template: PromptTemplate,
        prompt_template_variables: dict,
    ) -> list[dict[str, str]]:  # Update return type annotation
        prompt = prompt_template.format(**prompt_template_variables)

        num_system_prompt_tokens = compute_num_tokens(system_prompt)
        # Removed truncation logic based on old MAX_INPUT_TOKENS
        # prompt, prompt_num_tokens = truncate_text_to_max_tokens(prompt, max_tokens=settings.MAX_INPUT_TOKENS - num_system_prompt_tokens)
        # total_input_tokens = num_system_prompt_tokens + prompt_num_tokens # Removed token calculation
        total_input_tokens = None  # Set to None or remove usage if not needed elsewhere

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        return messages  # Return only messages

    @opik.track(name="inference_pipeline.call_llm_service")  # Keep Opik tracking
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
