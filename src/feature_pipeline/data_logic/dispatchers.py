from models.base import DataModel
from models.raw import ArticleRawModel, PostsRawModel, RepositoryRawModel

from data_logic.chunking_data_handlers import (
    ArticleChunkingHandler,
    ChunkingDataHandler,
    PostChunkingHandler,
    RepositoryChunkingHandler,
)
from data_logic.cleaning_data_handlers import (
    ArticleCleaningHandler,
    CleaningDataHandler,
    PostCleaningHandler,
    RepositoryCleaningHandler,
)
from data_logic.embedding_data_handlers import (
    ArticleEmbeddingHandler,
    EmbeddingDataHandler,
    # PostEmbeddingHandler,
    # RepositoryEmbeddingHandler,
)
from src.core import get_logger

logger = get_logger(__name__)


class RawDispatcher:
    @staticmethod
    def handle_mq_message(message: dict) -> DataModel:
        table = message.get("table")
        operation = message.get("operation")
        data = message.get("data")

        if not table or not operation or data is None:
            logger.error("Invalid CDC message format received.", message=message)
            raise ValueError("Invalid CDC message format: missing 'table', 'operation', or 'data'")

        entry_id = data.get("id")  # TODO: update db to use entry_id instead of id
        model_instance: DataModel
        if table == "posts":
            model_instance = PostsRawModel(**data, type=table, entry_id=entry_id)
        elif table == "articles":
            model_instance = ArticleRawModel(**data, type=table, entry_id=entry_id)
        elif table == "repositories":
            model_instance = RepositoryRawModel(**data, type=table, entry_id=entry_id)
        else:
            logger.warning("Unsupported table type received.", table=table)
            raise ValueError(f"Unsupported table type: {table}")
        logger.info(f"success model {model_instance}", table=table, operation=operation, type=table)
        return model_instance


class CleaningHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> CleaningDataHandler:
        if data_type == "posts":
            return PostCleaningHandler()
        elif data_type == "articles":
            return ArticleCleaningHandler()
        elif data_type == "repositories":
            return RepositoryCleaningHandler()
        else:
            raise ValueError("Unsupported data type")


class CleaningDispatcher:
    cleaning_factory = CleaningHandlerFactory

    @classmethod
    def dispatch_cleaner(cls, data_model: DataModel) -> DataModel:
        data_type = data_model.type
        handler = cls.cleaning_factory.create_handler(data_type)
        clean_model = handler.clean(data_model)

        logger.info(
            "Data cleaned successfully.",
            data_type=data_type,
            cleaned_content_len=len(clean_model.cleaned_content),  # type: ignore[attr-defined]
        )

        return clean_model


class ChunkingHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> ChunkingDataHandler:
        if data_type == "posts":
            return PostChunkingHandler()
        elif data_type == "articles":
            return ArticleChunkingHandler()
        elif data_type == "repositories":
            return RepositoryChunkingHandler()
        else:
            raise ValueError("Unsupported data type")


class ChunkingDispatcher:
    chunking_factory = ChunkingHandlerFactory

    @classmethod
    def dispatch_chunker(cls, data_model: DataModel) -> list[DataModel]:
        data_type = data_model.type
        handler = cls.chunking_factory.create_handler(data_type)
        chunk_models = handler.chunk(data_model)

        logger.info(
            "Cleaned content chunked successfully.",
            num=len(chunk_models),
            data_type=data_type,
        )

        return chunk_models


class EmbeddingHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> EmbeddingDataHandler:
        # if data_type == "posts":
        #     return PostEmbeddingHandler()
        if data_type == "articles":
            return ArticleEmbeddingHandler()
        # elif data_type == "repositories":
        #     return RepositoryEmbeddingHandler()
        else:
            raise ValueError("Unsupported data type")


class EmbeddingDispatcher:
    embedding_factory = EmbeddingHandlerFactory

    @classmethod
    def dispatch_embedder(cls, data_model: DataModel) -> DataModel:
        data_type = data_model.type
        handler = cls.embedding_factory.create_handler(data_type)
        embedded_chunk_model = handler.embedd(data_model)

        logger.info(
            "Chunk embedded successfully.",
            data_type=data_type,
            embedding_len=len(embedded_chunk_model.embedded_content),  # type: ignore[attr-defined]
        )

        return embedded_chunk_model
