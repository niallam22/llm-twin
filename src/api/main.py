import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers.crawling import router as crawling_router
from src.api.routers.inference import router as inference_router

# Assuming settings are loaded correctly from the core config
from src.core.db.qdrant import QdrantDatabaseConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Use lifespan context manager for startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models and clients
    logger.info("API starting up...")
    app.state.qdrant_client = None
    app.state.llm_client = None  # Initialize new client state
    # Remove old state initializations
    # app.state.llm_pipeline = None
    # app.state.tokenizer = None

    # Load Qdrant Client
    try:
        logger.info("Initializing Qdrant client...")
        qdrant_connector = QdrantDatabaseConnector()  # Instantiate connector
        app.state.qdrant_client = qdrant_connector._instance  # Store the actual client instance
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

    # Removed local LLM Pipeline and Tokenizer loading logic

    yield  # API runs here

    # Shutdown: Cleanup
    logger.info("API shutting down...")
    # Qdrant client using HTTP typically doesn't require explicit close.
    # If using gRPC or other connections, add cleanup here.
    # e.g., if qdrant_connector had a close method:
    # if 'qdrant_connector' in locals() and hasattr(qdrant_connector, 'close'):
    #     try:
    #         qdrant_connector.close()
    #         logger.info("Qdrant connector closed.")
    #     except Exception as e:
    #         logger.error(f"Error closing Qdrant connector: {e}")

    # OpenAI client (using httpx) typically doesn't require explicit closing,
    # as the underlying transport is managed automatically.
    # Removed cleanup for local pipeline and tokenizer.

    logger.info("API shutdown complete.")


app = FastAPI(lifespan=lifespan)  # Pass lifespan to FastAPI app

app.include_router(crawling_router)
app.include_router(inference_router, prefix="/inference", tags=["inference"])


@app.get("/")
async def root():
    return {"message": "API is running"}
