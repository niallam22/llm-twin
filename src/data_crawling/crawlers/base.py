import time
from abc import ABC, abstractmethod
from tempfile import mkdtemp
from typing import List
from uuid import UUID

from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.core.db.supabase_client import SupabaseClient


class BaseCrawler(ABC):
    model: type[BaseModel]  # Changed from BaseDocument
    author_id: UUID | None = None  # To store author_id passed during extraction

    @abstractmethod
    async def extract(self, link: str, author_id: UUID | None = None, **kwargs) -> None:
        """
        Extracts content from the given link.
        Specific implementations should create document instances using self.model
        and include self.author_id if it's provided.
        """
        self.author_id = author_id  # Store author_id for potential use in subclasses/save_documents
        ...

    async def save_documents(self, documents: List[BaseModel], db_client: SupabaseClient) -> None:
        """Saves a list of documents using the model's async bulk_insert."""
        await self.model.bulk_insert(documents, db_client=db_client)  # type: ignore[attr-defined] # Specific models have bulk_insert


class BaseAbstractCrawler(BaseCrawler, ABC):
    def __init__(self, scroll_limit: int = 5) -> None:
        options = webdriver.ChromeOptions()

        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9226")

        self.set_extra_driver_options(options)

        self.scroll_limit = scroll_limit
        self.driver = webdriver.Chrome(
            options=options,
        )

    def set_extra_driver_options(self, options: Options) -> None:
        pass

    def login(self) -> None:
        pass

    def scroll_page(self) -> None:
        """Scroll through the LinkedIn page based on the scroll limit."""
        current_scroll = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or (self.scroll_limit and current_scroll >= self.scroll_limit):
                break
            last_height = new_height
            current_scroll += 1
