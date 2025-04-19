import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from src.api.key_validation import get_api_key
from src.api.routers.crawling import router as crawling_router
from src.api.routers.inference import router as inference_router
from src.core.db.qdrant import QdrantDatabaseConnector
from src.core.db.supabase_client import SupabaseClient
from src.data_crawling.crawlers import CustomArticleCrawler, GithubCrawler, LinkedInCrawler, MediumCrawler
from src.data_crawling.dispatcher import CrawlerDispatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Use lifespan context manager for startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Variables to hold initialized resources ---
    qdrant_connector_instance: QdrantDatabaseConnector | None = None
    supabase_client_instance: SupabaseClient | None = None

    # Startup: Load models and clients
    logger.info("API starting up...")
    app.state.qdrant_client = None
    app.state.llm_client = None
    app.state.supabase_client = None

    try:
        logger.info("Initializing Crawler Dispatcher...")
        crawler_dispatcher_instance = CrawlerDispatcher()
        # Register your crawlers here
        # Option 1: Use CustomArticleCrawler for Medium (as in your data_crawling/main.py)
        crawler_dispatcher_instance.register("medium", CustomArticleCrawler)
        # Option 2: Use the specific MediumCrawler (Selenium-based)
        # Uncomment this line and comment the one above if you prefer MediumCrawler
        crawler_dispatcher_instance.register("medium", MediumCrawler)

        crawler_dispatcher_instance.register(
            "linkedin", LinkedInCrawler
        )  # LinkedIn crawler might be problematic due to login/scraping policies
        crawler_dispatcher_instance.register("github", GithubCrawler)
        # Add more registrations if needed

        app.state.crawler_dispatcher = crawler_dispatcher_instance
        logger.info("Crawler Dispatcher initialized and configured.")
    except Exception as e:
        logger.exception(f"Failed to initialize Crawler Dispatcher: {e}")

    # Load Qdrant Client
    try:
        logger.info("Initializing Qdrant client...")
        qdrant_connector_instance = QdrantDatabaseConnector()  # Instantiate connector
        app.state.qdrant_client = qdrant_connector_instance._instance  # Store the actual client instance
        if app.state.qdrant_client:
            # Perform a simple check like getting cluster info
            # cluster_info = app.state.qdrant_client.get_cluster_info()
            # logger.info(f"Qdrant client initialized successfully. Cluster info: {cluster_info}")
            logger.info("Qdrant client initialized successfully.")  # Keep it simple for now
        else:
            logger.error("Failed to initialize Qdrant client instance.")
    except Exception as e:
        logger.exception(f"Error initializing Qdrant client: {e}")
        # Depending on severity, might want to raise exception to stop startup

    # Load OpenAI Client
    try:
        logger.info("Initializing OpenAI client...")
        # Need to import OpenAIClient if not already done at the top
        from src.core.llm_clients import OpenAIClient  # Added import here for safety

        app.state.llm_client = OpenAIClient()  # Instantiate the client
        logger.info("OpenAI client initialized successfully.")
    except ValueError as e:  # Catch specific error for missing key
        logger.error(f"Configuration error initializing OpenAI client: {e}")
        # Keep app.state.llm_client as None
    except Exception as e:
        logger.exception(f"Failed to initialize OpenAI client: {e}")
        # Keep app.state.llm_client as None

    # --- Initialize Supabase Client Pool ---
    try:
        supabase_client_instance = SupabaseClient()
        await supabase_client_instance.connect()
        app.state.supabase_client = supabase_client_instance
        logger.info("Supabase client pool initialized successfully.")
    except Exception as e:
        logger.exception(f"Failed to initialise postgres db client: {e}")

    yield  # API runs here

    # Shutdown: Cleanup
    logger.info("API shutting down...")

    if qdrant_connector_instance:
        try:
            qdrant_connector_instance.close()
            logger.info("Qdrant connection closed.")
        except Exception as e:
            logger.error(f"Error closing Qdrant connector: {e}")

    if supabase_client_instance:
        try:
            await supabase_client_instance.close()
            logger.info("Supabase client pool closed.")
        except Exception as e:
            logger.error(f"Error closing Supabase client pool: {e}")

    # OpenAI client (using httpx) doesn't require explicit closing,
    # as the underlying transport is managed automatically.
    # Removed cleanup for local pipeline and tokenizer.

    logger.info("API shutdown complete.")


app = FastAPI(lifespan=lifespan, dependencies=[Depends(get_api_key)])  # Pass lifespan to FastAPI app

app.include_router(crawling_router)
app.include_router(inference_router, prefix="/inference", tags=["inference"])


@app.get("/")
async def root():
    return {"message": "API is running"}
