from fastapi import APIRouter, HTTPException, Request, status  # Added Request

from ...api.schemas.inference import InferenceRequest, InferenceResponse
from ...core import logger_utils
from ...inference_pipeline.llm_twin import LLMTwin

# FastAPI router for inference endpoints
router = APIRouter()
logger = logger_utils.get_logger(__name__)

# Instantiate LLMTwin globally - it's now lightweight after refactoring
# It mainly holds the prompt template logic.
llm_twin_instance = LLMTwin()


@router.post("/generate", response_model=InferenceResponse, status_code=status.HTTP_200_OK)
# @opik.track(name="api.generate_inference")  # Task 6.3.4: Add Opik tracking
async def generate_response(request: InferenceRequest, request_obj: Request):  # Added request_obj: Request
    """
    Generates a response using the LLM Twin model.
    Optionally uses RAG based on the request parameters.
    """
    logger.info(f"Received inference request: query='{request.query}', use_rag={request.use_rag}, collection_id={request.collection_id}")
    try:
        # Access pre-loaded components from app state
        llm_client = request_obj.app.state.llm_client  # Retrieve the new client
        # Removed retrieval of llm_pipeline and tokenizer

        # Check if the LLM client was initialized successfully during startup
        if not llm_client:
            logger.error("LLM Client (OpenAIClient) not available in app state. Check startup logs.")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM service is not ready.")

        # Call the async generate method, passing the llm_client
        result = await llm_twin_instance.generate(  # Add await
            query=request.query,
            llm_client=llm_client,  # Pass the client
            collection_id=request.collection_id,
            enable_rag=request.use_rag,
            # sample_for_evaluation=False # Assuming API calls aren't for evaluation sampling by default
        )

        # Task 6.3.4 (Implicit): Opik automatically captures inputs/outputs via decorator
        # We can add specific metadata if needed using opik_context
        # Prepare tags as a list of strings
        tags = ["api"]  # Base tags as strings
        if request.user_id:
            tags.append(f"user_id:{request.user_id}")  # Format user_id as a string tag

        # opik_context.update_current_trace(  # Correct usage
        #     metadata={
        #         "api_user_id": request.user_id,  # Keep in metadata too for easy viewing
        #         "rag_used": request.use_rag,
        #     },
        #     tags=tags,  # Pass the list of string tags
        # )

        # Task 6.3.5: Format the result into InferenceResponse
        response = InferenceResponse(
            answer=result.get("answer", "Error: No answer generated."),
            context=result.get("context"),  # Context might be None if RAG is disabled
        )
        logger.info(f"Generated response successfully for query: '{request.query}'")
        return response

    except Exception as e:
        logger.error(f"Error during inference generation for query '{request.query}': {e}", exc_info=True)
        # Task 6.3.5: Basic error handling
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate response: {str(e)}")
