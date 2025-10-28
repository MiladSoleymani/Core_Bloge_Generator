"""Test client for sending requests to the RabbitMQ worker."""

import json
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
import pika
from aio_pika import connect_robust, Message, DeliveryMode


async def send_report_request(sample_file: str):
    """
    Send a report generation request via RabbitMQ.

    Args:
        sample_file: Path to sample patient data JSON file
    """
    # Load sample data
    with open(sample_file, 'r') as f:
        data = json.load(f)

    # Create request message
    request = {
        "request_id": str(uuid.uuid4()),
        "user_id": "test_user_123",
        **data
    }

    print(f"Sending request: {request['request_id']}")
    print(f"User ID: {request['user_id']}")
    print(f"Patient: {request['patient']['name']}")

    # Connect to RabbitMQ
    connection = await connect_robust("amqp://guest:guest@localhost:5672/")
    channel = await connection.channel()

    # Declare queue
    await channel.declare_queue("report_generation_requests", durable=True)

    # Publish message
    message = Message(
        body=json.dumps(request).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        content_type="application/json"
    )

    await channel.default_exchange.publish(
        message,
        routing_key="report_generation_requests"
    )

    print("✓ Request sent successfully!")
    print(f"Waiting for response on queue: report_generation_responses")

    await connection.close()

    return request["request_id"]


async def listen_for_response(timeout: int = 120):
    """
    Listen for response messages from the worker.

    Args:
        timeout: Maximum time to wait for response in seconds
    """
    print(f"\nListening for responses (timeout: {timeout}s)...")

    connection = await connect_robust("amqp://guest:guest@localhost:5672/")
    channel = await connection.channel()

    # Declare response queue
    response_queue = await channel.declare_queue(
        "report_generation_responses",
        durable=True
    )

    print(f"Connected to queue: {response_queue.name}")

    try:
        # Use wait_for for Python 3.10 compatibility
        async def consume_response():
            async with response_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        response = json.loads(message.body.decode())

                        print("\n" + "=" * 60)
                        print("RESPONSE RECEIVED")
                        print("=" * 60)
                        print(f"Request ID: {response['request_id']}")
                        print(f"User ID: {response['user_id']}")
                        print(f"Status: {response['status']}")

                        if response['status'] == 'success':
                            print(f"Report ID: {response['report_id']}")
                            print(f"✓ Report generated successfully!")
                        else:
                            print(f"✗ Error: {response.get('error_message', 'Unknown error')}")

                        print(f"Timestamp: {response['timestamp']}")
                        print("=" * 60)

                        # Exit after receiving first response
                        return

        await asyncio.wait_for(consume_response(), timeout=timeout)

    except asyncio.TimeoutError:
        print(f"\n✗ Timeout: No response received within {timeout} seconds")

    finally:
        await connection.close()


async def test_full_workflow():
    """Test the complete request-response workflow."""
    print("=" * 60)
    print("TESTING RABBITMQ REPORT GENERATION WORKFLOW")
    print("=" * 60)

    # Find sample data file
    sample_file = Path("data/sample_reports/Kushagra mandwal.json")

    if not sample_file.exists():
        print(f"✗ Sample file not found: {sample_file}")
        print("Please ensure sample data exists in data/sample_reports/")
        return

    # Send request
    request_id = await send_report_request(str(sample_file))

    # Listen for response
    await listen_for_response(timeout=120)

    print("\n✓ Test completed!")


def test_connection():
    """Test basic RabbitMQ connection."""
    try:
        print("Testing RabbitMQ connection...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        channel = connection.channel()

        # Declare queues
        channel.queue_declare(queue='report_generation_requests', durable=True)
        channel.queue_declare(queue='report_generation_responses', durable=True)

        print("✓ Successfully connected to RabbitMQ!")
        print("✓ Queues declared")

        connection.close()
        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nMake sure RabbitMQ is running:")
        print("  docker-compose up -d rabbitmq")
        return False


async def main():
    """Main entry point."""
    # Test connection first
    if not test_connection():
        return

    print("\n")

    # Run full workflow test
    await test_full_workflow()


if __name__ == "__main__":
    asyncio.run(main())
