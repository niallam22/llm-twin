import uuid # Added import
from fastapi import APIRouter, status, HTTPException
from uuid import UUID

from src.api.schemas.crawler import LinkCrawlRequest, RawTextCrawlRequest # Import schema needed later
from src.core.db.documents import UserDocument, ArticleDocument # Import needed later
from src.data_crawling.dispatcher import CrawlerDispatcher, NoCrawlerFoundError # Import needed later

router = APIRouter(
    prefix="/crawl",
    tags=["Crawling"],
)
# Endpoint implementation will go here later
@router.post("/link", status_code=status.HTTP_202_ACCEPTED)
async def crawl_link(request: LinkCrawlRequest):
    """
    Accepts a link and user info, finds the appropriate crawler,
    and initiates the crawling process.
    Returns HTTP 202 Accepted immediately as crawling might be asynchronous.
    """
    # Implementation details for tasks 4.3.2 - 4.3.6 will follow

    # Task 4.3.2: Get or create user
    try:
        user_data = request.user_info.model_dump(exclude_none=True)
        if not user_data:
             # Handle case where no user info is provided, maybe create an anonymous user or raise error
             # For now, let's assume some user info is usually expected or handle anonymous case later
             # Depending on UserDocument.get_or_create implementation, empty dict might work or fail
             # Let's raise an error if no user info is given for clarity.
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User info (platform_user_id or username) is required.")

        user = await UserDocument.get_or_create(**user_data)
        if not user: # Should not happen with get_or_create but good practice
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not get or create user.")

    except Exception as e: # Catch potential DB errors or other issues
        # Log the error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing user information: {e}")

    # Task 4.3.3: Instantiate dispatcher
    # TODO: Optimize CrawlerDispatcher instantiation if needed (e.g., using Depends or lifespan)
    dispatcher = CrawlerDispatcher()

    # Task 4.3.4: Get crawler for the link
    try:
        crawler = dispatcher.get_crawler(str(request.link))
    except NoCrawlerFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No crawler found for link: {request.link}"
        )
    except Exception as e: # Catch potential errors in dispatcher logic
        # Log the error e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding crawler: {e}"
        )

    # Task 4.3.5: Call crawler extract method
    try:
        # Note: We are calling extract but not awaiting a result directly here.
        # The actual saving/processing might happen within the crawler's extract method
        # or be dispatched to a background task later.
        # For now, we just initiate it.
        await crawler.extract(link=str(request.link), author_id=user.id)

        # Task 4.3.6: Return success response
        # Since the status code is 202 Accepted, we just confirm submission.
        return {"status": "Crawl submitted"}

    except Exception as e:
        # Log the error e
        # Catch potential errors during the extraction process itself
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract content: {e}"
        )


@router.post("/raw_text", status_code=status.HTTP_201_CREATED)
async def crawl_raw_text(request: RawTextCrawlRequest):
    """
    Accepts raw text content and user info, creates an ArticleDocument directly.
    """
    # Task 4.4.2: Get or create user
    try:
        user_data = request.user_info.model_dump(exclude_none=True)
        if not user_data:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User info (platform_user_id or username) is required.")

        user = await UserDocument.get_or_create(**user_data)
        if not user:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not get or create user.")

    except Exception as e:
        # Log the error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing user information: {e}")

    # Task 4.4.3: Determine target model and data
    # Assuming raw text maps to ArticleDocument for simplicity
    platform = "raw_text"
    url = None
    if request.metadata:
        platform = request.metadata.get("source_platform", "raw_text")
        url = request.metadata.get("original_url") # Can be None

    # Task 4.4.4: Instantiate ArticleDocument (Corrected based on documents.py)
    # Use url from metadata for link, generate placeholder if None
    link_value = url if url else f"raw_text:{uuid.uuid4()}"
    # Store raw text within the content dictionary
    content_dict = {"text": request.text}
    # Note: Removed metadata= parameter as it's not in ArticleDocument model

    doc = ArticleDocument(
        content=content_dict,
        author_id=str(user.id), # Ensure author_id is string if needed by model/DB mapping
        platform=platform,
        link=link_value
    )

    # Task 4.4.5: Save document (Corrected call to class method)
    try:
        # Pass the instance to the class method save
        await ArticleDocument.save(instance=doc)
    except Exception as e:
        # Log the error e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save raw text document: {e}"
        )

    # Task 4.4.6: Return success response
    return {"status": "Raw text submitted", "document_id": str(doc.id)}