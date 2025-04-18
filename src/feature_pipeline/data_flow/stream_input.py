import json
import time
from datetime import datetime
from typing import Generic, Iterable, List, Optional, TypeVar

from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition

from src.core import get_logger
from src.core.mq import RabbitMQConnection
from src.feature_pipeline.config import settings

logger = get_logger(__name__)

DataT = TypeVar("DataT")
MessageT = TypeVar("MessageT")


class RabbitMQPartition(StatefulSourcePartition, Generic[DataT, MessageT]):
    """
    Class responsible for creating a connection between bytewax and rabbitmq that facilitates the transfer
    of data from mq to bytewax streaming piepline.
    Inherits StatefulSourcePartition for snapshot functionality that enables saving the state of the queue
    """

    def __init__(self, queue_name: str, resume_state: MessageT | None = None) -> None:
        self._in_flight_msg_ids = resume_state or set()
        self.queue_name = queue_name
        self.connection = RabbitMQConnection()
        self.connection.connect()
        self.channel = self.connection.get_channel()

    def next_batch(self, sched: Optional[datetime]) -> Iterable[DataT]:
        try:
            # Check if connection is closed and reopen if needed
            if not self.connection.is_connected():
                logger.info("RabbitMQ connection closed, attempting to reconnect...")
                self.connection.connect()
                self.channel = self.connection.get_channel()
                logger.info("Successfully reconnected to RabbitMQ")

            # Get message from queue
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)

            if method_frame:
                # Process valid message
                message_id = method_frame.delivery_tag
                self._in_flight_msg_ids.add(message_id)

                # Parse and return the message body
                return [json.loads(body)]
            else:
                # No message available - normal condition, not an error
                return []

        except json.JSONDecodeError as je:
            logger.error(f"Error decoding message as JSON: {str(je)}", queue_name=self.queue_name)
            # Consider adding dead-letter handling for invalid messages
            return []
        except Exception as e:
            logger.error(f"Error while fetching message from queue: {str(e)}", queue_name=self.queue_name)

            # Wait before retry (consider exponential backoff)
            time.sleep(10)

            try:
                # Attempt to re-establish connection
                logger.info("Attempting to reconnect to RabbitMQ...")
                self.connection.connect()
                self.channel = self.connection.get_channel()

                # Verify queue exists
                self.channel.queue_declare(queue=self.queue_name, passive=True)
                logger.info(f"Successfully reconnected to queue {self.queue_name}")
            except Exception as conn_err:
                logger.error(f"Failed to reconnect to RabbitMQ: {str(conn_err)}")

        return []

    def snapshot(self) -> MessageT:
        return self._in_flight_msg_ids

    def garbage_collect(self, state):
        closed_in_flight_msg_ids = state
        for msg_id in closed_in_flight_msg_ids:
            self.channel.basic_ack(delivery_tag=msg_id)
            self._in_flight_msg_ids.remove(msg_id)

    def close(self):
        self.channel.close()


class RabbitMQSource(FixedPartitionedSource):
    def list_parts(self) -> List[str]:
        return ["single partition"]

    def build_part(self, now: datetime, for_part: str, resume_state: MessageT | None = None) -> StatefulSourcePartition[DataT, MessageT]:
        return RabbitMQPartition(queue_name=settings.RABBITMQ_QUEUE_NAME)
