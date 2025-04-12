# Removed asyncio, Any, aws_lambda_powertools, LambdaContext, core.lib, UserDocument, Logger
# Kept imports needed for dispatcher registration
from .crawlers import CustomArticleCrawler, GithubCrawler, LinkedInCrawler
from .dispatcher import CrawlerDispatcher

_dispatcher = CrawlerDispatcher()
_dispatcher.register("medium", CustomArticleCrawler)
_dispatcher.register("linkedin", LinkedInCrawler)
_dispatcher.register("github", GithubCrawler)

# Removed Lambda handler function and __main__ block
