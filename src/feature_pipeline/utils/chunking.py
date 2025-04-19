# from langchain.text_splitter import (
#     RecursiveCharacterTextSplitter,
#     SentenceTransformersTokenTextSplitter,
# )

# from src.feature_pipeline.config import settings


# def chunk_text(text: str) -> list[str]:
#     character_splitter = RecursiveCharacterTextSplitter(separators=["\n\n"], chunk_size=500, chunk_overlap=0)
#     text_split = character_splitter.split_text(text)

#     token_splitter = SentenceTransformersTokenTextSplitter(
#         chunk_overlap=50,
#         tokens_per_chunk=settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
#         model_name=settings.EMBEDDING_MODEL_ID,
#     )
#     chunks = []

#     for section in text_split:
#         chunks.extend(token_splitter.split_text(section))

#     return chunks

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.logger_utils import get_logger

logger = get_logger(__name__)

from src.feature_pipeline.config import settings  # Keep settings for model nameg

# Get the tokenizer for the OpenAI model

try:
    enc = tiktoken.encoding_for_model(settings.EMBEDDING_MODEL_ID)
except KeyError:
    logger.warning(f"Tiktoken encoding not found for model {settings.EMBEDDING_MODEL_ID}, using cl100k_base.")
    enc = tiktoken.get_encoding("cl100k_base")  # Fallback for ada-002, gpt-3.5/4


def length_function_tiktoken(text: str) -> int:
    """Calculate length based on tiktoken tokens."""
    return len(enc.encode(text))


def chunk_text(text: str) -> list[str]:
    """Chunks text based on OpenAI token limits using tiktoken."""

    # Define chunk size in TOKENS, aiming below the API limit (e.g., 8191)

    # Use RecursiveCharacterTextSplitter with the tiktoken length function
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE_TOKENS,
        chunk_overlap=settings.CHUNK_OVERLAP_TOKENS,
        length_function=length_function_tiktoken,
        separators=["\n\n", "\n", " ", ""],  # Common separators
    )

    chunks = text_splitter.split_text(text)
    return chunks
