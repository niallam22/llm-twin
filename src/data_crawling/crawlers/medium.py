import asyncio
from typing import Optional
from aws_lambda_powertools import Logger
from bs4 import BeautifulSoup, Tag
from core.db.documents import ArticleDocument, UserDocument # Assuming PostDocument might be needed, though ArticleDocument is used
from selenium.webdriver.common.by import By

from crawlers.base import BaseAbstractCrawler

logger = Logger(service="llm-twin-course/crawler")


class MediumCrawler(BaseAbstractCrawler):
    model = ArticleDocument

    def set_extra_driver_options(self, options) -> None:
        options.add_argument(r"--profile-directory=Profile 2")

    async def extract(self, link: str, user_info: Optional[dict] = None) -> None:
        logger.info(f"Starting scrapping Medium article: {link}")

        self.driver.get(link)
        await asyncio.to_thread(self.scroll_page) # Run blocking scroll_page in a thread

        page_source = await asyncio.to_thread(lambda: self.driver.page_source)
        soup = BeautifulSoup(page_source, "html.parser")

        # --- Extract Content ---
        title_element = soup.find("h1") # Simpler selector, adjust if needed
        subtitle_element = soup.find("h2") # Simpler selector, adjust if needed
        # Find the main article content - this often requires specific selectors
        # Example: article_body = soup.find('article') or soup.find('section')
        # For simplicity, using get_text() for now, but refine for better quality
        content_text = soup.get_text()

        title = title_element.text.strip() if title_element else "Untitled"
        subtitle = subtitle_element.text.strip() if subtitle_element else None

        # --- Extract Author ---
        # Placeholder for author extraction - needs refinement based on Medium's structure
        author_name = "Unknown Author"
        author_url = None
        # Attempt to find author link (heuristic) - Corrected find with function
        def find_author_href(href_value):
            return isinstance(href_value, str) and '/@' in href_value and '?' not in href_value

        author_link_element = soup.find('a', href=find_author_href)
        # Explicitly check if the found element is a Tag before accessing attributes
        if isinstance(author_link_element, Tag):
            author_name = author_link_element.text.strip() or author_name
            href = author_link_element.get('href')
            if isinstance(href, str): # Ensure href is a string before using startswith
                 # Construct full URL if relative
                 if href.startswith('/'):
                     author_url = f"https://medium.com{href}"
                 elif not href.startswith('http'):
                      # Handle potential unexpected formats, maybe log a warning
                      logger.warning(f"Unexpected author URL format found: {href}")
                      author_url = None # Or try to fix if possible
                 else:
                     author_url = href
            elif href:
                 logger.warning(f"Found non-string href attribute: {href}") # Log if href is not a string but exists

        # --- Get or Create User ---
        # Use user_info if provided, otherwise use extracted info
        if user_info and user_info.get("name"):
             user_doc = await UserDocument.get_or_create(
                 name=user_info["name"],
                 url=user_info.get("url"), # Pass URL if available in user_info
                 platform="medium", # Assuming platform is always medium here
                 # Add other fields from user_info if necessary
             )
        else:
             user_doc = await UserDocument.get_or_create(
                 name=author_name,
                 url=author_url,
                 platform="medium",
             )

        # --- Prepare Document ---
        data = {
            "Title": title,
            "Subtitle": subtitle,
            "Content": content_text, # Use extracted text
            # Add other relevant fields like publication date, claps, etc. if extractable
        }

        document_instance = self.model(
            platform="medium",
            content=data,
            link=link,
            author_id=user_doc.id, # Use the ID from the retrieved/created user
            # Add other metadata like crawled_at if needed by the model
        )

        # --- Save Document ---
        await self.save_documents([document_instance])
        logger.info(f"Successfully scraped and saved article to Supabase: {link}")

        # Close driver using thread to avoid blocking async event loop
        await asyncio.to_thread(self.driver.close)

    def login(self):
        """Log in to Medium with Google"""
        self.driver.get("https://medium.com/m/signin")
        self.driver.find_element(By.TAG_NAME, "a").click()
