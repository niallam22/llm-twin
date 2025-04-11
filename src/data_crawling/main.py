import asyncio
from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from core import lib
from core.db.documents import UserDocument
from crawlers import CustomArticleCrawler, GithubCrawler, LinkedInCrawler
from dispatcher import CrawlerDispatcher

logger = Logger(service="llm-twin-course/crawler")

_dispatcher = CrawlerDispatcher()
_dispatcher.register("medium", CustomArticleCrawler)
_dispatcher.register("linkedin", LinkedInCrawler)
_dispatcher.register("github", GithubCrawler)


async def handler(event, context: LambdaContext | None = None) -> dict[str, Any]:
    first_name, last_name = lib.split_user_full_name(event.get("user"))

    user = await UserDocument.get_or_create(first_name=first_name, last_name=last_name)

    link = event.get("link")
    crawler = _dispatcher.get_crawler(link)

    if crawler:
        try:
            await crawler.extract(link=link, user=user)
            return {"statusCode": 200, "body": "Link processed successfully"}
        except Exception as e:
            logger.exception("Error during crawler extraction")
            return {"statusCode": 500, "body": f"An error occurred during extraction: {str(e)}"}
    else:
        logger.warning(f"No suitable crawler found for link: {link}")
        return {"statusCode": 400, "body": f"No suitable crawler found for link: {link}"}


if __name__ == "__main__":
    event = {
        "user": "Paul Iuztin",
        "link": "https://www.linkedin.com/in/vesaalexandru/",
    }
    asyncio.run(handler(event, None))
