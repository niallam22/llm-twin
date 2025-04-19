from typing import Optional
from urllib.parse import urlparse

from aws_lambda_powertools import Logger
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers.html2text import Html2TextTransformer

from src.core.db.documents import ArticleDocument, UserDocument
from src.core.db.supabase_client import SupabaseClient
from src.data_crawling.crawlers.base import BaseCrawler

logger = Logger(service="llm-twin-course/crawler")


class CustomArticleCrawler(BaseCrawler):
    model = ArticleDocument

    def __init__(self) -> None:
        super().__init__()

    async def extract(self, link: str, db_client: SupabaseClient, user: Optional[UserDocument] = None) -> None:
        # The check for existing documents is handled by save_documents -> get_or_create
        # logger.info(f"Attempting to scrape article: {link}") # Optional: Change log message

        logger.info(f"Starting scrapping article: {link}")

        loader = AsyncHtmlLoader([link])
        docs = loader.load()

        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        doc_transformed = docs_transformed[0]

        content = {
            "Title": doc_transformed.metadata.get("title"),
            "Subtitle": doc_transformed.metadata.get("description"),
            "Content": doc_transformed.page_content,
            "language": doc_transformed.metadata.get("language"),
        }

        parsed_url = urlparse(link)
        platform = parsed_url.netloc

        instance = self.model(
            content=content,
            link=link,
            platform=platform,
            author_id=user.id if user else None,
        )
        await self.save_documents([instance], db_client=db_client)

        logger.info(f"Finished scrapping custom article: {link}")
