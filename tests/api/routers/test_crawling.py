# tests/api/routers/test_crawling.py
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

# Assuming src is in PYTHONPATH or using appropriate test setup
from src.api.routers import crawling  # Import the router module
from src.core.db.documents import ArticleDocument, UserDocument  # Needed for mocking class methods
from src.data_crawling.dispatcher import NoCrawlerFoundError

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
def test_app():
    """Create a FastAPI instance with the crawling router for testing."""
    app = FastAPI()
    app.include_router(crawling.router)
    return app


@pytest.fixture(scope="module")
def client(test_app):
    """Create a TestClient for the FastAPI app."""
    return TestClient(test_app)


@pytest.fixture
def mock_user():
    """Fixture for a mocked UserDocument instance."""
    user = MagicMock(spec=UserDocument)
    user.id = uuid4()
    return user


@pytest.fixture
def mock_crawler():
    """Fixture for a mocked BaseCrawler instance."""
    crawler = AsyncMock()
    crawler.extract = AsyncMock()  # Mock the extract method
    return crawler


# --- Test /crawl/link Endpoint ---


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
@patch("src.api.routers.crawling.CrawlerDispatcher")
async def test_crawl_link_success(mock_dispatcher_cls, mock_get_or_create, client, mock_user, mock_crawler):
    """Test successful link crawl submission."""
    mock_get_or_create.return_value = mock_user
    mock_dispatcher_instance = mock_dispatcher_cls.return_value
    mock_dispatcher_instance.get_crawler.return_value = mock_crawler

    test_link = "https://example.com/article"
    payload = {"link": test_link, "user_info": {"username": "testuser"}}

    response = client.post("/crawl/link", json=payload)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"status": "Crawl submitted"}
    mock_get_or_create.assert_awaited_once_with(username="testuser")
    mock_dispatcher_cls.assert_called_once()
    mock_dispatcher_instance.get_crawler.assert_called_once_with(test_link)
    mock_crawler.extract.assert_awaited_once_with(link=test_link, author_id=mock_user.id)


async def test_crawl_link_missing_user_info(client):
    """Test link crawl with missing user info."""
    payload = {"link": "https://example.com/article", "user_info": {}}
    response = client.post("/crawl/link", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User info" in response.json()["detail"]


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
async def test_crawl_link_user_error(mock_get_or_create, client):
    """Test link crawl when user retrieval/creation fails."""
    mock_get_or_create.side_effect = Exception("DB error")
    payload = {"link": "https://example.com/article", "user_info": {"username": "testuser"}}
    response = client.post("/crawl/link", json=payload)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error processing user information" in response.json()["detail"]


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
@patch("src.api.routers.crawling.CrawlerDispatcher")
async def test_crawl_link_no_crawler_found(mock_dispatcher_cls, mock_get_or_create, client, mock_user):
    """Test link crawl when no suitable crawler is found."""
    mock_get_or_create.return_value = mock_user
    mock_dispatcher_instance = mock_dispatcher_cls.return_value
    mock_dispatcher_instance.get_crawler.side_effect = NoCrawlerFoundError("No crawler")

    test_link = "invalid-link-format"
    payload = {"link": test_link, "user_info": {"username": "testuser"}}
    response = client.post("/crawl/link", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No crawler found" in response.json()["detail"]
    mock_dispatcher_instance.get_crawler.assert_called_once_with(test_link)


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
@patch("src.api.routers.crawling.CrawlerDispatcher")
async def test_crawl_link_dispatcher_error(mock_dispatcher_cls, mock_get_or_create, client, mock_user):
    """Test link crawl when the dispatcher itself raises an error."""
    mock_get_or_create.return_value = mock_user
    mock_dispatcher_instance = mock_dispatcher_cls.return_value
    mock_dispatcher_instance.get_crawler.side_effect = Exception("Dispatcher internal error")

    test_link = "https://example.com/article"
    payload = {"link": test_link, "user_info": {"username": "testuser"}}
    response = client.post("/crawl/link", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error finding crawler" in response.json()["detail"]


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
@patch("src.api.routers.crawling.CrawlerDispatcher")
async def test_crawl_link_extract_error(mock_dispatcher_cls, mock_get_or_create, client, mock_user, mock_crawler):
    """Test link crawl when the crawler's extract method fails."""
    mock_get_or_create.return_value = mock_user
    mock_dispatcher_instance = mock_dispatcher_cls.return_value
    mock_dispatcher_instance.get_crawler.return_value = mock_crawler
    mock_crawler.extract.side_effect = Exception("Extraction failed")

    test_link = "https://example.com/article"
    payload = {"link": test_link, "user_info": {"username": "testuser"}}
    response = client.post("/crawl/link", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to extract content" in response.json()["detail"]
    mock_crawler.extract.assert_awaited_once()


# --- Test /crawl/raw_text Endpoint ---


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
@patch("src.api.routers.crawling.ArticleDocument.save", new_callable=AsyncMock)
@patch("src.api.routers.crawling.uuid.uuid4")  # Mock uuid4 used for link generation
async def test_crawl_raw_text_success(mock_uuid4, mock_save, mock_get_or_create, client, mock_user):
    """Test successful raw text submission."""
    mock_get_or_create.return_value = mock_user
    mock_generated_uuid = uuid4()
    mock_uuid4.return_value = mock_generated_uuid

    payload = {
        "text": "This is raw text.",
        "user_info": {"platform_user_id": "pid123"},
        "metadata": {"source_platform": "manual", "original_url": "http://original.url"},
    }

    response = client.post("/crawl/raw_text", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    # Check the structure and status, document_id will be dynamic
    response_data = response.json()
    assert response_data["status"] == "Raw text submitted"
    assert "document_id" in response_data
    # Try parsing the UUID to ensure it's valid
    doc_id = UUID(response_data["document_id"])

    mock_get_or_create.assert_awaited_once_with(platform_user_id="pid123")
    mock_uuid4.assert_not_called()  # Should use original_url from metadata
    mock_save.assert_awaited_once()

    # Verify the content passed to save
    saved_instance = mock_save.call_args.kwargs.get("instance")
    assert isinstance(saved_instance, ArticleDocument)
    assert saved_instance.content == {"text": "This is raw text."}
    assert saved_instance.author_id == str(mock_user.id)
    assert saved_instance.platform == "manual"
    assert saved_instance.link == "http://original.url"
    assert saved_instance.id == doc_id  # Check the ID matches the one returned


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
@patch("src.api.routers.crawling.ArticleDocument.save", new_callable=AsyncMock)
@patch("src.api.routers.crawling.uuid.uuid4")  # Mock uuid4 used for link generation
async def test_crawl_raw_text_success_no_metadata_url(mock_uuid4, mock_save, mock_get_or_create, client, mock_user):
    """Test successful raw text submission without original_url in metadata."""
    mock_get_or_create.return_value = mock_user
    mock_generated_uuid = uuid4()
    mock_uuid4.return_value = mock_generated_uuid

    payload = {
        "text": "Another raw text.",
        "user_info": {"username": "raw_user"},
        "metadata": {"source_platform": "test_source"},  # No original_url
    }

    response = client.post("/crawl/raw_text", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["status"] == "Raw text submitted"
    doc_id = UUID(response_data["document_id"])

    mock_get_or_create.assert_awaited_once_with(username="raw_user")
    mock_uuid4.assert_called_once()  # Should be called as original_url is missing
    mock_save.assert_awaited_once()

    saved_instance = mock_save.call_args.kwargs.get("instance")
    assert isinstance(saved_instance, ArticleDocument)
    assert saved_instance.content == {"text": "Another raw text."}
    assert saved_instance.author_id == str(mock_user.id)
    assert saved_instance.platform == "test_source"
    assert saved_instance.link == f"raw_text:{mock_generated_uuid}"  # Check generated link
    assert saved_instance.id == doc_id


async def test_crawl_raw_text_missing_user_info(client):
    """Test raw text submission with missing user info."""
    payload = {"text": "Some text", "user_info": {}}
    response = client.post("/crawl/raw_text", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User info" in response.json()["detail"]


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
async def test_crawl_raw_text_user_error(mock_get_or_create, client):
    """Test raw text submission when user retrieval/creation fails."""
    mock_get_or_create.side_effect = Exception("DB error")
    payload = {"text": "Some text", "user_info": {"username": "testuser"}}
    response = client.post("/crawl/raw_text", json=payload)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error processing user information" in response.json()["detail"]


@patch("src.api.routers.crawling.UserDocument.get_or_create", new_callable=AsyncMock)
@patch("src.api.routers.crawling.ArticleDocument.save", new_callable=AsyncMock)
async def test_crawl_raw_text_save_error(mock_save, mock_get_or_create, client, mock_user):
    """Test raw text submission when saving the document fails."""
    mock_get_or_create.return_value = mock_user
    mock_save.side_effect = Exception("Save failed")

    payload = {"text": "Some text", "user_info": {"username": "testuser"}}
    response = client.post("/crawl/raw_text", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to save raw text document" in response.json()["detail"]
    mock_save.assert_awaited_once()  # Ensure save was attempted
