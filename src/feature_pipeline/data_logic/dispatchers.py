from core import get_logger
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
    PostEmbeddingHandler,
    RepositoryEmbeddingHandler,
)

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

        logger.info("Received CDC message.", table=table, operation=operation)

        model_instance: DataModel
        if table == "posts":
            model_instance = PostsRawModel(**data)
            model_instance.type = "posts"
        elif table == "articles":
            model_instance = ArticleRawModel(**data)
            model_instance.type = "articles"
        elif table == "repositories":
            model_instance = RepositoryRawModel(**data)
            model_instance.type = "repositories"
        else:
            logger.warning("Unsupported table type received.", table=table)
            raise ValueError(f"Unsupported table type: {table}")

        # Assign table and operation from the envelope
        model_instance.table = table
        model_instance.operation = operation

        # Ensure entry_id is populated (assuming it's in the 'data' dict)
        if 'id' in data: # Common primary key name
             model_instance.entry_id = data['id']
        elif 'entry_id' not in data: # Check if already set by model init
             logger.warning("Could not determine entry_id from data.", data=data)
             # Handle cases where ID might be missing or named differently if necessary

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
    cleaning_factory = CleaningHandlerFactory()

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
    cleaning_factory = ChunkingHandlerFactory

    @classmethod
    def dispatch_chunker(cls, data_model: DataModel) -> list[DataModel]:
        data_type = data_model.type
        handler = cls.cleaning_factory.create_handler(data_type)
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
        if data_type == "posts":
            return PostEmbeddingHandler()
        elif data_type == "articles":
            return ArticleEmbeddingHandler()
        elif data_type == "repositories":
            return RepositoryEmbeddingHandler()
        else:
            raise ValueError("Unsupported data type")


class EmbeddingDispatcher:
    cleaning_factory = EmbeddingHandlerFactory

    @classmethod
    def dispatch_embedder(cls, data_model: DataModel) -> DataModel:
        data_type = data_model.type
        handler = cls.cleaning_factory.create_handler(data_type)
        embedded_chunk_model = handler.embedd(data_model)

        logger.info(
            "Chunk embedded successfully.",
            data_type=data_type,
            embedding_len=len(embedded_chunk_model.embedded_content),  # type: ignore[attr-defined]
        )

        return embedded_chunk_model
