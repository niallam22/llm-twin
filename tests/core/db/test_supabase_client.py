# tests/core/db/test_supabase_client.py
from unittest.mock import AsyncMock, MagicMock, patch

import asyncpg
import pytest

from src.core.config import AppSettings  # Import AppSettings for mocking

# Assuming src is in PYTHONPATH or using appropriate test setup
from src.core.db.supabase_client import SupabaseClient

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


# Mock settings for testing
@pytest.fixture
def mock_settings(monkeypatch):
    # Use monkeypatch to temporarily replace settings
    mock_settings_obj = AppSettings(SUPABASE_DB_URL="postgresql://mock:mock@mock/mockdb")
    monkeypatch.setattr("src.core.db.supabase_client.settings", mock_settings_obj)
    return mock_settings_obj


@pytest.fixture
def supabase_client():
    """Fixture to create a SupabaseClient instance for each test."""
    client = SupabaseClient()
    # Ensure the pool is reset for each test
    client._pool = None
    return client


@pytest.fixture
def mock_pool():
    """Fixture for a mocked asyncpg Pool."""
    pool = AsyncMock(spec=asyncpg.Pool)
    pool.acquire = AsyncMock()
    pool.release = AsyncMock()
    pool.close = AsyncMock()
    return pool


@pytest.fixture
def mock_connection():
    """Fixture for a mocked asyncpg Connection."""
    connection = AsyncMock(spec=asyncpg.Connection)
    connection.execute = AsyncMock(return_value="INSERT 1")
    connection.fetchrow = AsyncMock()
    connection.fetch = AsyncMock()
    return connection


# --- Test Connect / Close ---


async def test_connect_success(supabase_client, mock_settings, mock_pool):
    """Test successful connection pool creation."""
    with patch("asyncpg.create_pool", new_callable=AsyncMock, return_value=mock_pool) as mock_create_pool:
        await supabase_client.connect()
        mock_create_pool.assert_awaited_once_with(
            dsn=mock_settings.SUPABASE_DB_URL,
            min_size=1,
            max_size=10,
        )
        assert supabase_client._pool is mock_pool


async def test_connect_failure(supabase_client, mock_settings):
    """Test connection pool creation failure."""
    test_exception = asyncpg.PostgresError("Connection failed")
    with patch("asyncpg.create_pool", new_callable=AsyncMock, side_effect=test_exception) as mock_create_pool:
        with pytest.raises(ConnectionError, match="Failed to connect to Supabase: Connection failed"):
            await supabase_client.connect()
        mock_create_pool.assert_awaited_once()
        assert supabase_client._pool is None


async def test_close_pool(supabase_client, mock_pool):
    """Test closing the connection pool."""
    supabase_client._pool = mock_pool  # Simulate connected state
    await supabase_client.close()
    mock_pool.close.assert_awaited_once()
    assert supabase_client._pool is None


async def test_close_pool_not_connected(supabase_client):
    """Test closing when not connected (should do nothing)."""
    # _pool is None by default in fixture
    await supabase_client.close()
    # No error should be raised, and nothing should be called


# --- Test get_connection ---


async def test_get_connection_success(supabase_client, mock_pool, mock_connection):
    """Test successfully acquiring and releasing a connection."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection

    async with supabase_client.get_connection() as conn:
        assert conn is mock_connection
        # Simulate using the connection
        await conn.execute("SELECT 1")

    mock_pool.acquire.assert_awaited_once()
    mock_pool.release.assert_awaited_once_with(mock_connection)
    mock_connection.execute.assert_awaited_once_with("SELECT 1")


async def test_get_connection_not_initialized(supabase_client):
    """Test getting connection when pool is not initialized."""
    with pytest.raises(ConnectionError, match="Connection pool is not initialized"):
        async with supabase_client.get_connection():
            pass  # pragma: no cover


async def test_get_connection_acquire_fails(supabase_client, mock_pool):
    """Test failure during connection acquisition."""
    supabase_client._pool = mock_pool
    test_exception = asyncpg.PostgresError("Failed to acquire")
    mock_pool.acquire.side_effect = test_exception

    with pytest.raises(asyncpg.PostgresError, match="Failed to acquire"):
        async with supabase_client.get_connection():
            pass  # pragma: no cover

    mock_pool.acquire.assert_awaited_once()
    mock_pool.release.assert_not_awaited()  # Release should not be called if acquire failed


# --- Test execute ---


async def test_execute_success(supabase_client, mock_pool, mock_connection):
    """Test successful execute call."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    sql = "INSERT INTO test (col) VALUES ($1)"
    params = ["value1"]

    status = await supabase_client.execute(sql, params)

    assert status == "INSERT 1"
    mock_connection.execute.assert_awaited_once_with(sql, *params)
    mock_pool.release.assert_awaited_once_with(mock_connection)


async def test_execute_no_params(supabase_client, mock_pool, mock_connection):
    """Test successful execute call without parameters."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    sql = "DELETE FROM test"

    await supabase_client.execute(sql)

    mock_connection.execute.assert_awaited_once_with(sql)  # No extra args
    mock_pool.release.assert_awaited_once_with(mock_connection)


async def test_execute_failure(supabase_client, mock_pool, mock_connection):
    """Test execute failure."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    test_exception = asyncpg.PostgresError("Insert failed")
    mock_connection.execute.side_effect = test_exception
    sql = "INSERT INTO test (col) VALUES ($1)"
    params = ["value1"]

    with pytest.raises(asyncpg.PostgresError, match="Insert failed"):
        await supabase_client.execute(sql, params)

    mock_connection.execute.assert_awaited_once_with(sql, *params)
    mock_pool.release.assert_awaited_once_with(mock_connection)  # Release should still happen


# --- Test fetch_one ---


async def test_fetch_one_success(supabase_client, mock_pool, mock_connection):
    """Test successful fetch_one call returning a record."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    mock_record = MagicMock(spec=asyncpg.Record)
    mock_connection.fetchrow.return_value = mock_record
    sql = "SELECT * FROM test WHERE id = $1"
    params = [1]

    record = await supabase_client.fetch_one(sql, params)

    assert record is mock_record
    mock_connection.fetchrow.assert_awaited_once_with(sql, *params)
    mock_pool.release.assert_awaited_once_with(mock_connection)


async def test_fetch_one_none(supabase_client, mock_pool, mock_connection):
    """Test successful fetch_one call returning None."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    mock_connection.fetchrow.return_value = None
    sql = "SELECT * FROM test WHERE id = $1"
    params = [99]

    record = await supabase_client.fetch_one(sql, params)

    assert record is None
    mock_connection.fetchrow.assert_awaited_once_with(sql, *params)
    mock_pool.release.assert_awaited_once_with(mock_connection)


async def test_fetch_one_failure(supabase_client, mock_pool, mock_connection):
    """Test fetch_one failure."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    test_exception = asyncpg.PostgresError("Select failed")
    mock_connection.fetchrow.side_effect = test_exception
    sql = "SELECT * FROM test WHERE id = $1"
    params = [1]

    with pytest.raises(asyncpg.PostgresError, match="Select failed"):
        await supabase_client.fetch_one(sql, params)

    mock_connection.fetchrow.assert_awaited_once_with(sql, *params)
    mock_pool.release.assert_awaited_once_with(mock_connection)


# --- Test fetch_all ---


async def test_fetch_all_success(supabase_client, mock_pool, mock_connection):
    """Test successful fetch_all call."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    mock_records = [MagicMock(spec=asyncpg.Record), MagicMock(spec=asyncpg.Record)]
    mock_connection.fetch.return_value = mock_records
    sql = "SELECT * FROM test"

    records = await supabase_client.fetch_all(sql)

    assert records == mock_records
    mock_connection.fetch.assert_awaited_once_with(sql)
    mock_pool.release.assert_awaited_once_with(mock_connection)


async def test_fetch_all_empty(supabase_client, mock_pool, mock_connection):
    """Test successful fetch_all call returning an empty list."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    mock_connection.fetch.return_value = []
    sql = "SELECT * FROM test WHERE status = $1"
    params = ["nonexistent"]

    records = await supabase_client.fetch_all(sql, params)

    assert records == []
    mock_connection.fetch.assert_awaited_once_with(sql, *params)
    mock_pool.release.assert_awaited_once_with(mock_connection)


async def test_fetch_all_failure(supabase_client, mock_pool, mock_connection):
    """Test fetch_all failure."""
    supabase_client._pool = mock_pool
    mock_pool.acquire.return_value = mock_connection
    test_exception = asyncpg.PostgresError("Select all failed")
    mock_connection.fetch.side_effect = test_exception
    sql = "SELECT * FROM test"

    with pytest.raises(asyncpg.PostgresError, match="Select all failed"):
        await supabase_client.fetch_all(sql)

    mock_connection.fetch.assert_awaited_once_with(sql)
    mock_pool.release.assert_awaited_once_with(mock_connection)
