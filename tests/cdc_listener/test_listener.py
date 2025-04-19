# tests/cdc_listener/test_listener.py
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import asyncpg
import pytest

# Assuming src is in PYTHONPATH or using appropriate test setup
from src.cdc_listener import listener
from src.core.config import AppSettings

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


# Mock settings for testing
@pytest.fixture
def mock_settings(monkeypatch):
    mock_settings_obj = AppSettings(SUPABASE_DB_URL="postgresql://mock:mock@mock/mockdb", RABBITMQ_QUEUE_NAME="test_queue")
    # Patch the settings object within the listener module
    monkeypatch.setattr(listener, "settings", mock_settings_obj)
    return mock_settings_obj


@pytest.fixture
def mock_connection():
    """Fixture for a mocked asyncpg Connection."""
    connection = AsyncMock(spec=asyncpg.Connection)
    connection.add_listener = AsyncMock()
    connection.remove_listener = AsyncMock()
    connection.is_closed = MagicMock(return_value=False)
    connection.close = AsyncMock()
    return connection


# --- Test connect_db ---


async def test_connect_db_success(mock_settings, mock_connection):
    """Test successful database connection."""
    with patch("asyncpg.connect", new_callable=AsyncMock, return_value=mock_connection) as mock_connect:
        conn = await listener.connect_db()
        assert conn is mock_connection
        mock_connect.assert_awaited_once_with(mock_settings.SUPABASE_DB_URL)


async def test_connect_db_pg_error(mock_settings):
    """Test database connection failure due to PostgresError."""
    test_exception = asyncpg.PostgresError("DB connection failed")
    with patch("asyncpg.connect", new_callable=AsyncMock, side_effect=test_exception) as mock_connect:
        conn = await listener.connect_db()
        assert conn is None
        mock_connect.assert_awaited_once_with(mock_settings.SUPABASE_DB_URL)


async def test_connect_db_other_error(mock_settings):
    """Test database connection failure due to other Exception."""
    test_exception = Exception("Unexpected error")
    with patch("asyncpg.connect", new_callable=AsyncMock, side_effect=test_exception) as mock_connect:
        conn = await listener.connect_db()
        assert conn is None
        mock_connect.assert_awaited_once_with(mock_settings.SUPABASE_DB_URL)


# --- Test handle_notification ---


@patch("src.cdc_listener.listener.publish_to_rabbitmq")  # Mock the imported function
async def test_handle_notification_success(mock_publish, mock_settings):
    """Test successful handling of a valid JSON notification."""
    pid = 123
    channel = "data_changes"
    payload_dict = {"id": 1, "data": "some value", "operation": "INSERT"}
    payload_str = json.dumps(payload_dict)

    # Mock asyncio.to_thread to directly await the mocked publish function
    with patch("asyncio.to_thread", side_effect=lambda func, *args: func(*args)) as mock_to_thread:
        await listener.handle_notification(None, pid, channel, payload_str)

        # Check that publish_to_rabbitmq was called correctly via asyncio.to_thread
        mock_to_thread.assert_called_once()
        # Check the arguments passed to the original publish_to_rabbitmq
        mock_publish.assert_called_once_with(mock_settings.RABBITMQ_QUEUE_NAME, payload_str)


@patch("src.cdc_listener.listener.publish_to_rabbitmq")
async def test_handle_notification_invalid_json(mock_publish, mock_settings):
    """Test handling of an invalid JSON payload."""
    pid = 456
    channel = "data_changes"
    payload_str = "this is not json"

    with patch("asyncio.to_thread", side_effect=lambda func, *args: func(*args)):
        await listener.handle_notification(None, pid, channel, payload_str)
        mock_publish.assert_not_called()  # Should not attempt to publish invalid JSON


@patch("src.cdc_listener.listener.publish_to_rabbitmq")
async def test_handle_notification_publish_error(mock_publish, mock_settings):
    """Test handling when publishing to RabbitMQ fails."""
    pid = 789
    channel = "data_changes"
    payload_dict = {"id": 2, "data": "another value"}
    payload_str = json.dumps(payload_dict)
    test_exception = Exception("MQ connection error")
    mock_publish.side_effect = test_exception  # Make the mocked function raise an error

    with patch("asyncio.to_thread", side_effect=lambda func, *args: func(*args)) as mock_to_thread:
        # Should catch the exception and log it, not raise it
        await listener.handle_notification(None, pid, channel, payload_str)

        mock_to_thread.assert_called_once()
        mock_publish.assert_called_once_with(mock_settings.RABBITMQ_QUEUE_NAME, payload_str)


# --- Test listen_for_notifications ---


async def test_listen_for_notifications_starts_and_stops(mock_connection):
    """Test that the listener starts, waits, and cleans up."""
    channel_name = "data_changes"

    # Mock asyncio.sleep to raise an exception after the first call to break the loop
    with patch("asyncio.sleep", new_callable=AsyncMock, side_effect=asyncio.CancelledError("Stop loop")) as mock_sleep:
        with pytest.raises(asyncio.CancelledError):  # Expect the exception raised by sleep
            await listener.listen_for_notifications(mock_connection)

        mock_connection.add_listener.assert_awaited_once_with(channel_name, listener.handle_notification)
        mock_sleep.assert_awaited_once_with(1)  # Check that it tried to sleep
        mock_connection.remove_listener.assert_awaited_once_with(channel_name, listener.handle_notification)


async def test_listen_for_notifications_db_error(mock_connection):
    """Test handling of a database error during listening setup."""
    channel_name = "data_changes"
    test_exception = asyncpg.PostgresError("Listener setup failed")
    mock_connection.add_listener.side_effect = test_exception

    # The function should catch the error and log it, then proceed to finally
    await listener.listen_for_notifications(mock_connection)

    mock_connection.add_listener.assert_awaited_once_with(channel_name, listener.handle_notification)
    # remove_listener should still be called in finally block
    mock_connection.remove_listener.assert_awaited_once_with(channel_name, listener.handle_notification)


# Note: Testing the __main__ block directly is often omitted in unit tests
# as it involves orchestrating the event loop and handling KeyboardInterrupt.
# Testing the component functions (connect_db, handle_notification, listen_for_notifications)
# provides good coverage of the core logic.
