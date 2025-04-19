# llm-twin-course/src/core/db/supabase_client.py
import contextlib
import logging
from typing import Any, AsyncGenerator, List, Optional  # Added List and Any

import asyncpg

from src.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Manages an asyncpg connection pool for interacting with the Supabase database.
    """

    _pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """
        Establishes the connection pool to the Supabase database.
        """
        if self._pool is None:
            try:
                logger.info("Creating Supabase connection pool...")
                self._pool = await asyncpg.create_pool(
                    dsn=settings.SUPABASE_DB_URL,
                    min_size=1,  # Minimum number of connections in the pool
                    max_size=10,  # Maximum number of connections in the pool
                )
                logger.info("Supabase connection pool created successfully.")
            except (asyncpg.PostgresError, OSError) as e:
                logger.error(f"Failed to create Supabase connection pool: {e}")
                # Re-raise the exception or handle it as appropriate
                raise ConnectionError(f"Failed to connect to Supabase: {e}") from e

    async def close(self) -> None:
        """
        Closes the connection pool.
        """
        if self._pool:
            logger.info("Closing Supabase connection pool...")
            await self._pool.close()
            self._pool = None
            logger.info("Supabase connection pool closed.")

    @contextlib.asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Provides a connection from the pool within an asynchronous context manager.

        Ensures the connection is released back to the pool afterwards.

        Raises:
            ConnectionError: If the connection pool has not been initialized.
            asyncpg.PostgresError: If acquiring a connection fails.
        """
        if self._pool is None:
            raise ConnectionError("Connection pool is not initialized. Call connect() first.")

        connection: Optional[asyncpg.Connection] = None
        try:
            connection = await self._pool.acquire()
            if connection is None:
                # Should not happen with default acquire settings unless timeout occurs quickly
                raise asyncpg.PostgresError("Failed to acquire connection from pool (returned None).")
            yield connection
        except asyncpg.PostgresError as e:
            logger.error(f"Error acquiring or using Supabase connection: {e}")
            raise  # Re-raise the original error
        finally:
            if connection:
                # return connection to pool
                await self._pool.release(connection)
                logger.debug("connection returned to pool")

    async def execute(self, sql: str, params: Optional[List[Any]] = None) -> str:
        """
        Executes a non-SELECT SQL statement (e.g., INSERT, UPDATE, DELETE).

        Args:
            sql: The SQL statement to execute.
            params: Optional list of parameters to pass to the statement.

        Returns:
            The status string returned by the database upon successful execution.

        Raises:
            ConnectionError: If the connection pool is not initialized.
            asyncpg.PostgresError: If the database execution fails.
        """
        if self._pool is None:
            raise ConnectionError("Connection pool is not initialized. Call connect() first.")

        try:
            async with self.get_connection() as conn:
                logger.debug(f"Executing SQL: {sql} with params: {params}")
                status = await conn.execute(sql, *params if params else [])
                logger.debug(f"Execution successful, status: {status}")
                return status
        except asyncpg.PostgresError as e:
            logger.error(f"Error executing SQL: {sql} with params: {params} - Error: {e}")
            # Re-raise the exception to allow higher-level handling
            raise

    async def fetch_one(self, sql: str, params: Optional[List[Any]] = None) -> Optional[asyncpg.Record]:
        """
        Executes a SELECT query and fetches the first result.

        Args:
            sql: The SELECT SQL statement to execute.
            params: Optional list of parameters to pass to the statement.

        Returns:
            An asyncpg.Record representing the first row found, or None if no rows match.

        Raises:
            ConnectionError: If the connection pool is not initialized.
            asyncpg.PostgresError: If the database execution fails.
        """
        if self._pool is None:
            raise ConnectionError("Connection pool is not initialized. Call connect() first.")

        try:
            async with self.get_connection() as conn:
                logger.debug(f"Fetching one with SQL: {sql} and params: {params}")
                record = await conn.fetchrow(sql, *params if params else [])
                logger.debug(f"Fetch one successful, record: {'Found' if record else 'None'}")
                return record
        except asyncpg.PostgresError as e:
            logger.error(f"Error fetching one with SQL: {sql}, params: {params} - Error: {e}")
            raise

    async def fetch_all(self, sql: str, params: Optional[List[Any]] = None) -> List[asyncpg.Record]:
        """
        Executes a SELECT query and fetches all results.

        Args:
            sql: The SELECT SQL statement to execute.
            params: Optional list of parameters to pass to the statement.

        Returns:
            A list of asyncpg.Record objects representing all rows found.

        Raises:
            ConnectionError: If the connection pool is not initialized.
            asyncpg.PostgresError: If the database execution fails.
        """
        if self._pool is None:
            raise ConnectionError("Connection pool is not initialized. Call connect() first.")

        try:
            async with self.get_connection() as conn:
                logger.debug(f"Fetching all with SQL: {sql} and params: {params}")
                records = await conn.fetch(sql, *params if params else [])
                logger.debug(f"Fetch all successful, {len(records)} records found.")
                return records
        except asyncpg.PostgresError as e:
            logger.error(f"Error fetching all with SQL: {sql}, params: {params} - Error: {e}")
            raise
