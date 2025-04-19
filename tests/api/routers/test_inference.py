# tests/api/routers/test_inference.py
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

# Assuming src is in PYTHONPATH or using appropriate test setup
from src.api.routers import inference  # Import the router module
from src.core.llm_clients import LLMClientInterface  # For type hinting mock

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


# Mock the global LLMTwin instance used in the router
@pytest.fixture(autouse=True)
def mock_llm_twin_generate():
    # Patch the generate method of the globally instantiated llm_twin_instance
    with patch("src.api.routers.inference.llm_twin_instance.generate", new_callable=AsyncMock) as mock_generate:
        yield mock_generate


# Mock opik decorator to avoid actual tracking during tests
@pytest.fixture(autouse=True)
def mock_opik_track():
    # Patch the opik.track decorator so it just returns the original function
    def no_op_decorator(*args, **kwargs):
        def wrapper(func):
            return func

        return wrapper

    with patch("opik.track", side_effect=no_op_decorator) as mock_track:
        yield mock_track


# Mock opik_context to verify calls if needed
@pytest.fixture
def mock_opik_context():
    with patch("src.api.routers.inference.opik_context", new_callable=MagicMock) as mock_context:
        mock_context.update_current_trace = MagicMock()
        yield mock_context


@pytest.fixture
def mock_llm_client():
    """Fixture for a mocked LLMClientInterface."""
    client = AsyncMock(spec=LLMClientInterface)
    return client


@pytest.fixture(scope="module")
def test_app():
    """Create a FastAPI instance with the inference router for testing."""
    app = FastAPI()
    # Simulate app state being available (will be populated in tests)
    app.state.llm_client = None
    app.include_router(inference.router)
    return app


@pytest.fixture
def client(test_app, mock_llm_client):
    """
    Create a TestClient and set up the app state for a typical successful test.
    Individual tests can override app.state if needed.
    """
    test_app.state.llm_client = mock_llm_client  # Set the client for most tests
    return TestClient(test_app)


# --- Test /generate Endpoint ---


async def test_generate_success_with_rag(client, mock_llm_twin_generate, mock_llm_client, mock_opik_context):
    """Test successful generation with RAG enabled."""
    query = "What is RAG?"
    expected_answer = "RAG is Retrieval-Augmented Generation."
    expected_context = ["Context 1", "Context 2"]
    mock_llm_twin_generate.return_value = {"answer": expected_answer, "context": expected_context}

    payload = {"query": query, "use_rag": True, "user_id": "user123"}
    response = client.post("/generate", json=payload)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["answer"] == expected_answer
    assert response_data["context"] == expected_context

    mock_llm_twin_generate.assert_awaited_once_with(query=query, llm_client=mock_llm_client, enable_rag=True)
    # Verify opik context update
    mock_opik_context.update_current_trace.assert_called_once_with(
        metadata={"api_user_id": "user123", "rag_used": True}, tags=["api", "user_id:user123"]
    )


async def test_generate_success_without_rag(client, mock_llm_twin_generate, mock_llm_client, mock_opik_context):
    """Test successful generation with RAG disabled."""
    query = "Tell me a joke."
    expected_answer = "Why don't scientists trust atoms? Because they make up everything!"
    mock_llm_twin_generate.return_value = {
        "answer": expected_answer,
        "context": None,  # RAG disabled
    }

    payload = {"query": query, "use_rag": False}  # No user_id
    response = client.post("/generate", json=payload)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["answer"] == expected_answer
    assert response_data["context"] is None

    mock_llm_twin_generate.assert_awaited_once_with(query=query, llm_client=mock_llm_client, enable_rag=False)
    # Verify opik context update without user_id
    mock_opik_context.update_current_trace.assert_called_once_with(
        metadata={"api_user_id": None, "rag_used": False},
        tags=["api"],  # Only base tag
    )


async def test_generate_llm_client_not_ready(test_app, mock_llm_twin_generate):
    """Test generation when LLM client is not available in app state."""
    # Override app state for this specific test
    test_app.state.llm_client = None
    client_no_llm = TestClient(test_app)  # Create client with modified state

    payload = {"query": "Test query", "use_rag": True}
    response = client_no_llm.post("/generate", json=payload)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "LLM service is not ready" in response.json()["detail"]
    mock_llm_twin_generate.assert_not_awaited()  # Should fail before calling generate


async def test_generate_llm_twin_error(client, mock_llm_twin_generate, mock_llm_client):
    """Test generation when llm_twin_instance.generate raises an exception."""
    query = "This will fail."
    test_exception = Exception("LLM Twin internal error")
    mock_llm_twin_generate.side_effect = test_exception

    payload = {"query": query, "use_rag": False}
    response = client.post("/generate", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to generate response" in response.json()["detail"]
    assert "LLM Twin internal error" in response.json()["detail"]

    mock_llm_twin_generate.assert_awaited_once_with(query=query, llm_client=mock_llm_client, enable_rag=False)


async def test_generate_missing_answer_in_result(client, mock_llm_twin_generate, mock_llm_client):
    """Test generation when the result dict from generate is missing 'answer'."""
    query = "Where is the answer?"
    mock_llm_twin_generate.return_value = {
        "context": ["Some context"]  # Missing 'answer' key
    }

    payload = {"query": query, "use_rag": True}
    response = client.post("/generate", json=payload)

    # It should still return 200 OK but with a default error message in the answer field
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "Error: No answer generated." in response_data["answer"]
    assert response_data["context"] == ["Some context"]

    mock_llm_twin_generate.assert_awaited_once_with(query=query, llm_client=mock_llm_client, enable_rag=True)
