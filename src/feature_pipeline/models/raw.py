from typing import Optional

from models.base import DataModel
from src.core import get_logger

logger = get_logger(__name__)


class RepositoryRawModel(DataModel):
    name: str
    link: str
    content: dict
    owner_id: str


class ArticleRawModel(DataModel):
    platform: str
    url: str
    content: str
    author_id: str
    collection_id: str


class PostsRawModel(DataModel):
    platform: str
    content: dict
    author_id: str | None = None
    image: Optional[str] = None
