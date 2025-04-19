import re

from aws_lambda_powertools import Logger

from .crawlers.base import BaseCrawler

logger = Logger(service="llm-twin-course/crawler")


class NoCrawlerFoundError(Exception):
    """Custom exception raised when no suitable crawler is found for a URL."""

    pass


class CrawlerDispatcher:
    def __init__(self) -> None:
        self._crawlers = {}

    def register(self, domain: str, crawler: type[BaseCrawler]) -> None:
        self._crawlers[r"https://(www\.)?{}.com/*".format(re.escape(domain))] = crawler

    def get_crawler(self, url: str) -> BaseCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()
        # If no pattern matches after checking all registered crawlers
        logger.error(f"No crawler found for URL: {url}")
        raise NoCrawlerFoundError(f"No crawler registered for URL pattern matching: {url}")
