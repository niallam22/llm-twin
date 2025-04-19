from typing import Self

import pika
from pika.exceptions import AMQPConnectionError, UnroutableError  # Import specific exceptions

from src.core.config import settings
from src.core.logger_utils import get_logger

logger = get_logger(__file__)


class RabbitMQConnection:
    """Singleton class to manage RabbitMQ connection."""

    _instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        virtual_host: str = "/",
        fail_silently: bool = False,
        **kwargs,
    ) -> None:
        self.host = host or settings.RABBITMQ_HOST
        self.port = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_DEFAULT_USERNAME
        self.password = password or settings.RABBITMQ_DEFAULT_PASSWORD
        self.virtual_host = virtual_host
        self.fail_silently = fail_silently
        self._connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=credentials,
                )
            )
        except AMQPConnectionError as e:  # Use imported exception
            logger.exception("Failed to connect to RabbitMQ:")
            if not self.fail_silently:
                raise e

    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_open

    def get_channel(self):
        if self.is_connected():
            assert self._connection is not None  # Added assertion
            return self._connection.channel()

    def close(self):
        if self.is_connected():
            assert self._connection is not None  # Added assertion
            self._connection.close()
            self._connection = None
            print("Closed RabbitMQ connection")


def publish_to_rabbitmq(queue_name: str, data: str):
    """Publish data to a RabbitMQ queue."""
    try:
        # Create an instance of RabbitMQConnection
        rabbitmq_conn = RabbitMQConnection()

        # Establish connection
        with rabbitmq_conn:
            channel = rabbitmq_conn.get_channel()
            if channel is None:
                logger.error("Failed to get RabbitMQ channel. Aborting publish.")
                return  # Or raise an exception

            # Ensure the queue exists
            channel.queue_declare(queue=queue_name, durable=True)

            # Delivery confirmation
            channel.confirm_delivery()

            # Send data to the queue
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=data,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )
    except UnroutableError:  # Use imported exception
        logger.warning("Message could not be routed")
    except Exception:
        logger.exception("Error publishing to RabbitMQ.")


if __name__ == "__main__":
    publish_to_rabbitmq("test_queue", "Hello, World!")
