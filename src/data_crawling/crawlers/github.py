import os
import shutil
import subprocess
import tempfile
from typing import Optional

from aws_lambda_powertools import Logger

from src.core.db.documents import RepositoryDocument, UserDocument
from src.core.db.supabase_client import SupabaseClient
from src.data_crawling.crawlers.base import BaseCrawler

logger = Logger(service="llm-twin-course/crawler")


class GithubCrawler(BaseCrawler):
    model = RepositoryDocument

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")) -> None:
        super().__init__()
        self._ignore = ignore

    async def extract(self, link: str, db_client: SupabaseClient, user_info: Optional[dict] = None) -> None:
        logger.info(f"Starting scrapping GitHub repository: {link}")

        repo_name = link.rstrip("/").split("/")[-1]

        local_temp = tempfile.mkdtemp()

        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])

            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])

            tree = {}
            for root, dirs, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self._ignore):
                    continue

                for file in files:
                    if file.endswith(self._ignore):
                        continue
                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        tree[file_path] = f.read().replace(" ", "")

            # Extract owner username from link
            try:
                owner_username = link.rstrip("/").split("/")[-2]
            except IndexError:
                logger.error(f"Could not extract owner username from link: {link}")
                # Handle error appropriately, maybe raise or return
                return  # Or raise specific error

            # Get or create the user document
            user_document = await UserDocument.get_or_create(db_client=db_client, cls=UserDocument, username=owner_username)
            if not user_document:
                logger.error(f"Could not get or create user: {owner_username}")
                # Handle error appropriately
                return  # Or raise specific error

            instance = self.model(name=repo_name, link=link, content=tree, owner_id=user_document.id)
            await self.save_documents([instance], db_client=db_client)

        except Exception:
            raise
        finally:
            shutil.rmtree(local_temp)

        logger.info(f"Finished scrapping GitHub repository: {link}")
