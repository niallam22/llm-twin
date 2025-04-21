from typing import List, Optional

from pydantic import BaseModel, Field

# Pydantic schemas for inference API


class InferenceRequest(BaseModel):
    """Request model for the inference endpoint."""

    query: str = Field(..., description="The user query for the LLM.")
    collection_id: str = Field(..., description="collection_id to query")
    use_rag: bool = Field(True, description="Flag to indicate whether to use RAG or not.")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking.")


class InferenceResponse(BaseModel):
    """Response model for the inference endpoint."""

    answer: str = Field(..., description="The generated answer from the LLM.")
    context: Optional[List[str]] = Field(None, description="List of context snippets used for RAG, if applicable.")
