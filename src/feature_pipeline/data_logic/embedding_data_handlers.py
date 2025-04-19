from abc import ABC, abstractmethod
from typing import List

import numpy as np
from models.base import DataModel
from models.chunk import ArticleChunkModel
from models.embedded_chunk import (
    ArticleEmbeddedChunkModel,
)
from openai import OpenAI

from src.core import get_logger
from src.feature_pipeline.config import settings
from src.feature_pipeline.utils.embeddings import embedd_text

logger = get_logger(__name__)


class EmbeddingDataHandler(ABC):
    """
    Abstract class for all embedding data handlers.
    All data transformations logic for the embedding step is done here
    """

    @abstractmethod
    def embedd(self, data_model: DataModel) -> DataModel:
        pass


# class PostEmbeddingHandler(EmbeddingDataHandler):
#     def embedd(self, data_model: PostChunkModel) -> PostEmbeddedChunkModel:
#         return PostEmbeddedChunkModel(
#             entry_id=data_model.entry_id,
#             platform=data_model.platform,
#             chunk_id=data_model.chunk_id,
#             chunk_content=data_model.chunk_content,
#             embedded_content=embedd_text(data_model.chunk_content),
#             author_id=data_model.author_id,
#             type=data_model.type,
#         )


class ArticleEmbeddingHandler(EmbeddingDataHandler):
    def embedd(self, data_model: ArticleChunkModel) -> ArticleEmbeddedChunkModel:
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.embeddings.create(
                input=data_model.chunk_content,
                model=settings.EMBEDDING_MODEL_ID,
            )
            # Extract the list of floats
            embedding_list: List[float] = response.data[0].embedding
            # Convert to NumPy array
            embedding_array: np.ndarray = embedd_text(data_model.chunk_content)

        except Exception as e:
            logger.error(f"Failed embedding article chunk {data_model.chunk_id}: {e}", exc_info=True)
            raise
        logger.info(f"Article embedding handle embedding array {embedding_array}")
        return ArticleEmbeddedChunkModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            link=data_model.link,
            chunk_content=data_model.chunk_content,
            chunk_id=data_model.chunk_id,
            embedded_content=embedding_array,
            author_id=data_model.author_id,
            type=data_model.type,
        )


# class RepositoryEmbeddingHandler(EmbeddingDataHandler):
#     def embedd(self, data_model: RepositoryChunkModel) -> RepositoryEmbeddedChunkModel:
#         return RepositoryEmbeddedChunkModel(
#             entry_id=data_model.entry_id,
#             name=data_model.name,
#             link=data_model.link,
#             chunk_id=data_model.chunk_id,
#             chunk_content=data_model.chunk_content,
#             embedded_content=embedd_text(data_model.chunk_content),
#             owner_id=data_model.owner_id,
#             type=data_model.type,
#         )
