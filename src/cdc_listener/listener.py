import asyncio
import json
import logging

import asyncpg

from src.core.config import settings
from src.core.mq import publish_to_rabbitmq

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def connect_db():
    """Establishes an asynchronous connection to the database."""
    conn = None
    try:
        conn = await asyncpg.connect(settings.SUPABASE_DB_URL)
        logging.info("Successfully connected to the database.")
        return conn
    except asyncpg.PostgresError as e:
        logging.error(f"Failed to connect to database: {e}")
        return None
    except Exception as e:
        # Catch other potential exceptions during connection setup
        logging.error(f"An unexpected error occurred during database connection: {e}")
        return None


# Callback function to handle notifications
async def handle_notification(connection, pid, channel, payload):
    logging.info(f"Received notification on channel '{channel}':")
    try:
        # Assuming payload is JSON string, attempt to parse it
        data = json.loads(payload)
        logging.info(f"  PID: {pid}, Payload: {json.dumps(data, indent=2)}")

        # Use queue name from settings
        queue_name = settings.RABBITMQ_QUEUE_NAME
        try:
            # Run the synchronous publish function in a separate thread
            # Pass the original payload string, not the parsed data dict
            await asyncio.to_thread(publish_to_rabbitmq, queue_name, payload)
            logging.info(f"Successfully published notification payload to queue '{queue_name}'.")
        except Exception as e:
            logging.error(f"Failed to publish notification to queue '{queue_name}': {e}")

    except json.JSONDecodeError:
        logging.warning(f"  PID: {pid}, Payload is not valid JSON: {payload}")
    except Exception as e:
        logging.error(f"  Error processing notification: {e}")


async def listen_for_notifications(conn):
    """Listens for notifications on the specified channel."""
    channel_name = "data_changes"  # Channel defined in migration 0006
    try:
        await conn.add_listener(channel_name, handle_notification)
        logging.info(f"Started listening on channel '{channel_name}'...")
        # Keep the listener running indefinitely until interrupted
        # In a real application, you'd have better shutdown handling (e.g., signals)
        while True:
            await asyncio.sleep(1)  # Keep the coroutine alive
    except asyncpg.PostgresError as e:
        logging.error(f"Database error while listening: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in listener: {e}")
    finally:
        # Attempt to remove listener on exit, though this might not always run
        # if the process is killed abruptly.
        try:
            await conn.remove_listener(channel_name, handle_notification)
            logging.info(f"Stopped listening on channel '{channel_name}'.")
        except Exception as e:
            logging.error(f"Error removing listener: {e}")


if __name__ == "__main__":

    async def main():
        logging.info("Starting CDC listener...")
        conn = None
        try:
            conn = await connect_db()
            if conn:
                # Start listening for notifications
                await listen_for_notifications(conn)
            else:
                logging.error("Could not establish database connection. Listener exiting.")
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt received, shutting down listener.")
        except Exception as e:
            logging.error(f"Unhandled exception in main: {e}")
        finally:
            if conn and not conn.is_closed():
                await conn.close()
                logging.info("Database connection closed.")
            logging.info("Listener stopped.")

    # Use asyncio.run() which handles the event loop lifecycle
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Catch KeyboardInterrupt here as well if asyncio.run doesn't fully handle it
        # depending on the Python version and specific setup.
        logging.info("Application terminated by user.")
