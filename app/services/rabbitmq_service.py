"""RabbitMQ service for consuming and publishing messages."""

import json
import asyncio
import logging
from typing import Callable, Optional
from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractQueue

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RabbitMQService:
    """RabbitMQ service for handling message queue operations."""

    def __init__(self):
        """Initialize RabbitMQ service."""
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[AbstractRobustChannel] = None
        self.request_queue: Optional[AbstractQueue] = None
        self.response_queue_name: str = settings.rabbitmq_response_queue

    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            logger.info(f"Connecting to RabbitMQ at {settings.rabbitmq_url}")
            self.connection = await connect_robust(settings.rabbitmq_url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=settings.rabbitmq_prefetch_count)

            # Declare request queue (consumer)
            self.request_queue = await self.channel.declare_queue(
                settings.rabbitmq_request_queue,
                durable=True
            )

            # Declare response queue (publisher)
            await self.channel.declare_queue(
                settings.rabbitmq_response_queue,
                durable=True
            )

            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self):
        """Close connection to RabbitMQ."""
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")

    async def consume_messages(self, callback: Callable):
        """
        Consume messages from the request queue.

        Args:
            callback: Async function to process messages
        """
        if not self.request_queue:
            raise RuntimeError("RabbitMQ not connected. Call connect() first.")

        logger.info(f"Starting to consume messages from {settings.rabbitmq_request_queue}")

        async with self.request_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        # Parse message body
                        body = json.loads(message.body.decode())
                        logger.info(f"Received message: {body.get('request_id', 'unknown')}")

                        # Process message with callback
                        await callback(body, message)

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)

    async def publish_response(self, response_data: dict):
        """
        Publish response message to the response queue.

        Args:
            response_data: Dictionary containing response data
        """
        if not self.channel:
            raise RuntimeError("RabbitMQ not connected. Call connect() first.")

        try:
            message = Message(
                body=json.dumps(response_data).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json"
            )

            await self.channel.default_exchange.publish(
                message,
                routing_key=self.response_queue_name
            )

            logger.info(f"Published response: {response_data.get('request_id', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to publish response: {e}")
            raise


# Global RabbitMQ service instance
rabbitmq_service = RabbitMQService()
