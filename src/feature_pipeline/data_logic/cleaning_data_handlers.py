from abc import ABC, abstractmethod

from models.base import DataModel
from models.clean import ArticleCleanedModel, PostCleanedModel, RepositoryCleanedModel
from models.raw import ArticleRawModel, PostsRawModel, RepositoryRawModel
from utils.cleaning import clean_text


class CleaningDataHandler(ABC):
    """
    Abstract class for all cleaning data handlers.
    All data transformations logic for the cleaning step is done here
    """

    @abstractmethod
    def clean(self, data_model: DataModel) -> DataModel:
        pass


class PostCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: PostsRawModel) -> PostCleanedModel:
        joined_text = "".join(data_model.content.values()) if data_model and data_model.content else None

        return PostCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            cleaned_content=clean_text(joined_text),
            author_id=data_model.author_id,
            image=data_model.image if data_model.image else None,
            type=data_model.type,
        )


class ArticleCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: ArticleRawModel) -> ArticleCleanedModel:
        # joined_text = (
        #     "".join(data_model.content.values()) if data_model and data_model.content else None
        # )

        return ArticleCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            link=data_model.url,
            cleaned_content=data_model.content,  # clean_text(joined_text),
            author_id=data_model.author_id,
            type=data_model.type,
            collection_id=data_model.collection_id,
        )


class RepositoryCleaningHandler(CleaningDataHandler):
    def clean(self, data_model: RepositoryRawModel) -> RepositoryCleanedModel:
        joined_text = "".join(data_model.content.values()) if data_model and data_model.content else None

        return RepositoryCleanedModel(
            entry_id=data_model.entry_id,
            name=data_model.name,
            link=data_model.link,
            cleaned_content=clean_text(joined_text),
            owner_id=data_model.owner_id,
            type=data_model.type,
        )
