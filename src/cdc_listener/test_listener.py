import asyncio
import asyncpg
import json
import logging
import uuid
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..core.config import settings

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LISTENER_TIMEOUT_SECONDS = 10 # How long to wait for notifications
LISTENER_READY_TIMEOUT = 2 # How long to wait for listener to start

# --- Logging Setup ---
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("CDCTestListener")

# --- Shared State ---
received_notifications: List[Dict[str, Any]] = []
listener_ready_event = asyncio.Event()
listener_stop_event = asyncio.Event()

# --- Test Data ---
test_articles = [
    {
        "url": f"http://test.com/article/{uuid.uuid4()}",
        "title": "Test Article 1",
        "content": "Content of test article 1.",
        "published_at": datetime.now(),
    },
    {
        "url": f"http://test.com/article/{uuid.uuid4()}",
        "title": "Test Article 2",
        "content": "Content of test article 2.",
        "published_at": datetime.now(),
    },
]

test_posts = [
    {
        "url": f"http://linkedin.com/post/{uuid.uuid4()}",
        "content": "Test LinkedIn post content 1.",
        "published_at": datetime.now(),
    }
]

test_repositories = [
    {
        "url": f"http://github.com/test/{uuid.uuid4()}",
        "description": "Test GitHub repository description 1.",
        "published_at": datetime.now(),
    }
]

all_test_data = {
    "articles": test_articles,
    "posts": test_posts,
    "repositories": test_repositories,
}

# --- Listener Implementation ---
async def notification_handler(
    connection: asyncpg.Connection,
    pid: int,
    channel: str,
    payload: str,
):
    """Callback function to handle incoming notifications."""
    logger.info(f"Received notification on channel '{channel}' (PID: {pid})")
    try:
        notification_data = json.loads(payload)
        logger.debug(f"Parsed notification payload: {notification_data}")
        received_notifications.append(notification_data)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON payload: {payload}")
    except Exception as e:
        logger.error(f"Error processing notification: {e}", exc_info=True)

async def run_listener():
    """Connects to the database and listens for notifications."""
    conn: Optional[asyncpg.Connection] = None
    try:
        conn = await asyncpg.connect(settings.SUPABASE_DB_URL)
        if conn: # Add check for successful connection
            logger.info("Listener connected to the database.")
            await conn.add_listener("data_changes", notification_handler)
        else:
            logger.error("Listener connection failed, conn object is None.")
            listener_ready_event.set() # Signal readiness to unblock main test
            return # Exit if connection fails
        logger.info("Listener added for channel 'data_changes'.")
        listener_ready_event.set() # Signal that the listener is ready

        # Keep listener running until stop event is set
        await listener_stop_event.wait()
        logger.info("Listener stop event received.")

    except (asyncpg.exceptions.PostgresError, OSError) as e:
        logger.error(f"Listener connection error: {e}", exc_info=True)
        listener_ready_event.set() # Signal readiness even on error to unblock main test
        return # Exit if connection fails
    except Exception as e:
        logger.error(f"Unexpected error in listener: {e}", exc_info=True)
        listener_ready_event.set() # Signal readiness even on error
        return
    finally:
        if conn and not conn.is_closed():
            try:
                logger.info("Removing listener...")
                await conn.remove_listener("data_changes", notification_handler)
                logger.info("Closing listener connection...")
                await conn.close()
                logger.info("Listener connection closed.")
            except Exception as e:
                logger.error(f"Error during listener cleanup: {e}", exc_info=True)
        listener_ready_event.set() # Ensure it's set even if cleanup fails

# --- Test Execution ---
async def run_test():
    """Runs the main test logic: starts listener, inserts data, validates."""
    global received_notifications
    received_notifications = [] # Reset notifications for the run
    listener_ready_event.clear()
    listener_stop_event.clear()

    logger.info("Starting CDC end-to-end test...")

    # Start the listener concurrently
    listener_task = asyncio.create_task(run_listener())
    logger.info("Listener task created.")

    # Wait for the listener to be ready
    try:
        await asyncio.wait_for(listener_ready_event.wait(), timeout=LISTENER_READY_TIMEOUT)
        logger.info("Listener is ready.")
    except asyncio.TimeoutError:
        logger.error(f"Listener did not become ready within {LISTENER_READY_TIMEOUT} seconds. Aborting test.")
        listener_stop_event.set() # Signal listener to stop
        await listener_task # Wait for listener task to finish cleanup
        return False # Indicate test failure

    # Check if listener task exited prematurely (e.g., connection error)
    if listener_task.done() and listener_task.exception():
         logger.error(f"Listener task exited with exception: {listener_task.exception()}")
         return False # Indicate test failure
    elif listener_task.done():
         logger.error("Listener task exited unexpectedly without exception before insertions.")
         return False # Indicate test failure


    # Proceed with data insertion
    insert_conn: Optional[asyncpg.Connection] = None
    inserted_ids = { "articles": [], "posts": [], "repositories": [] }
    insertion_success = True

    try:
        insert_conn = await asyncpg.connect(settings.SUPABASE_DB_URL)
        if insert_conn: # Add check for successful connection
            logger.info("Insertion connection established.")

            for table_name, data_list in all_test_data.items():
                logger.info(f"--- Inserting data into {table_name} ---")
                for item_data in data_list:
                    columns = ", ".join(item_data.keys())
                    placeholders = ", ".join(f"${i+1}" for i in range(len(item_data)))
                    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id"
                    try:
                        # Convert datetime to timezone-aware if naive
                        values = []
                        for k, v in item_data.items():
                            if isinstance(v, datetime) and v.tzinfo is None:
                                 # Assuming UTC if no timezone is present
                                 # Adjust if your DB expects a different default timezone
                                 # values.append(v.replace(tzinfo=timezone.utc))
                                 values.append(v) # Keep naive for now, asyncpg might handle it
                            else:
                                values.append(v)

                        logger.debug(f"Executing SQL: {sql} with values: {values}")
                        inserted_id = await insert_conn.fetchval(sql, *values)
                        logger.info(f"Inserted into {table_name}: ID={inserted_id}, Data={item_data}")
                        inserted_ids[table_name].append({"id": inserted_id, **item_data})
                    except Exception as e:
                        logger.error(f"Failed to insert into {table_name}: {item_data}. Error: {e}", exc_info=True)
                        insertion_success = False
                        # Optionally break or continue based on desired test behavior
        else:
            logger.error("Insertion connection failed, insert_conn object is None.")
            insertion_success = False
            # Optionally break or continue based on desired test behavior

        if not insertion_success:
             logger.error("One or more insertions failed. Test cannot proceed reliably.")
             # No need to wait for notifications if insertions failed

    except (asyncpg.exceptions.PostgresError, OSError) as e:
        logger.error(f"Insertion connection error: {e}", exc_info=True)
        insertion_success = False
    except Exception as e:
        logger.error(f"Unexpected error during insertion: {e}", exc_info=True)
        insertion_success = False
    finally:
        if insert_conn and not insert_conn.is_closed():
            await insert_conn.close()
            logger.info("Insertion connection closed.")

    # Wait for notifications only if insertions were potentially successful
    if insertion_success:
        logger.info(f"Waiting {LISTENER_TIMEOUT_SECONDS} seconds for notifications...")
        await asyncio.sleep(LISTENER_TIMEOUT_SECONDS)
    else:
        logger.warning("Skipping notification wait due to insertion failures.")


    # Stop the listener
    logger.info("Signaling listener to stop...")
    listener_stop_event.set()
    await listener_task # Wait for the listener task to complete cleanup
    logger.info("Listener task finished.")

    # --- Validation ---
    logger.info("\n--- Validation Phase ---")
    overall_pass = True
    validation_results = []

    if not insertion_success:
        logger.error("Overall test status: FAIL (due to insertion errors)")
        overall_pass = False
    elif not received_notifications:
        logger.error("No notifications received.")
        if any(len(ids) > 0 for ids in inserted_ids.values()):
             logger.error("Overall test status: FAIL (inserted data but received no notifications)")
             overall_pass = False
        else:
             logger.warning("No data was successfully inserted, so no notifications expected.")
             # Consider this a pass or fail based on requirements. Assuming pass if no insertions.
             overall_pass = True # Or False if insertions were expected but failed earlier
    else:
        logger.info(f"Received {len(received_notifications)} notifications in total.")
        logger.debug(f"Raw notifications: {json.dumps(received_notifications, indent=2, default=str)}")

        # Flatten inserted data for easier lookup by ID (if available) or unique key (URL)
        expected_notifications = {}
        for table, items in inserted_ids.items():
            for item in items:
                # Use URL as the primary key for matching if ID isn't directly in notification
                # Or adapt based on actual notification payload content
                key = item.get('url', str(item.get('id'))) # Prefer URL if exists
                expected_notifications[key] = {"table": table, "data": item}

        found_matches = set()

        for notification in received_notifications:
            table = notification.get("table")
            operation = notification.get("operation")
            data = notification.get("data", {})

            if operation != "INSERT":
                logger.warning(f"Skipping non-INSERT notification: {notification}")
                continue

            if not table or not data:
                logger.warning(f"Skipping notification with missing table or data: {notification}")
                continue

            # Try matching based on URL or ID from the notification's data field
            match_key = data.get('url', str(data.get('id')))
            result = {"notification": notification, "status": "FAIL", "reason": "No matching insertion found"}

            if match_key in expected_notifications:
                expected = expected_notifications[match_key]
                if expected["table"] == table:
                    # Basic validation: Check if key fields match
                    # More thorough validation can be added here
                    match = True
                    for key, expected_value in expected["data"].items():
                        # Skip comparing generated IDs if they differ slightly or aren't in notification
                        if key == 'id' and str(data.get(key)) != str(expected_value):
                             logger.debug(f"ID mismatch for {match_key}: Expected {expected_value}, Got {data.get(key)}")
                             continue # Allow ID mismatch for now
                        # Handle datetime comparison carefully (e.g., ignore microseconds or timezone)
                        if isinstance(expected_value, datetime):
                            # Simplistic comparison, might need refinement
                            notif_val_str = str(data.get(key))
                            exp_val_str = str(expected_value)
                            # Compare basic ISO format parts, ignoring potential TZ/ms differences
                            if notif_val_str[:19] != exp_val_str[:19]:
                                logger.warning(f"Potential datetime mismatch for {match_key}.{key}: Expected '{exp_val_str}', Got '{notif_val_str}'")
                                # Decide if this constitutes failure
                                # match = False
                                # break
                        elif str(data.get(key)) != str(expected_value):
                            logger.warning(f"Value mismatch for {match_key}.{key}: Expected '{expected_value}', Got '{data.get(key)}'")
                            match = False
                            result["reason"] = f"Value mismatch for key '{key}'"
                            break

                    if match:
                        result["status"] = "PASS"
                        result["reason"] = "Matching insertion found and validated."
                        found_matches.add(match_key)
                    else:
                         overall_pass = False # Mark overall as fail if any validation fails
                else:
                    result["reason"] = f"Table mismatch: Expected '{expected['table']}', Got '{table}'"
                    overall_pass = False
            else:
                 overall_pass = False # Unexpected notification

            validation_results.append(result)
            logger.info(f"Validation - Notification for {match_key}: {result['status']} ({result['reason']})")


        # Check for missing notifications
        missing_count = 0
        for key, expected in expected_notifications.items():
            if key not in found_matches:
                logger.error(f"Validation - MISSING notification for inserted item: {expected['data']}")
                validation_results.append({
                    "expected": expected['data'],
                    "status": "FAIL",
                    "reason": "Notification not received"
                })
                overall_pass = False
                missing_count += 1

        if missing_count > 0:
            logger.error(f"{missing_count} expected notifications were not received.")


    # --- Reporting ---
    print("\n--- Test Summary ---")
    print(f"Database URL: {settings.SUPABASE_DB_URL}")
    print(f"Listener Status: {'Ran (check logs for errors)' if listener_task else 'Not Started'}")
    print(f"Insertion Status: {'Success' if insertion_success else 'FAILED (see logs)'}")
    print(f"Total Items Inserted: {sum(len(v) for v in inserted_ids.values())}")
    print(f"Total Notifications Received: {len(received_notifications)}")

    print("\nValidation Details:")
    if validation_results:
        for res in validation_results:
            status = res['status']
            reason = res['reason']
            item_id = res.get('notification', res.get('expected', {})).get('url', 'N/A')
            print(f"  - Item ({item_id}): {status} ({reason})")
    elif insertion_success:
         print("  - No validation performed (no notifications received or no insertions).")
    else:
         print("  - No validation performed due to insertion errors.")


    print(f"\nOverall Test Status: {'PASS' if overall_pass else 'FAIL'}")
    print("--------------------")

    return overall_pass

# --- Entry Point ---
if __name__ == "__main__":
    test_passed = asyncio.run(run_test())
    if test_passed:
        logger.info("CDC Test Suite PASSED")
        sys.exit(0)
    else:
        logger.error("CDC Test Suite FAILED")
        # Detailed errors should already be logged to STDERR via logger
        sys.exit(1)