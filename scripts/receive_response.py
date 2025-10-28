"""
Receive report generation responses from RabbitMQ.

This script demonstrates how to consume responses from the worker
service in your main backend.

Usage:
    python scripts/receive_response.py
    python scripts/receive_response.py --host rabbitmq-server
"""

import pika
import json
import argparse
from datetime import datetime


def callback(ch, method, properties, body):
    """
    Process received response message.

    Args:
        ch: Channel
        method: Delivery method
        properties: Message properties
        body: Message body
    """
    try:
        response = json.loads(body)

        print(f"\n{'='*60}")
        print("RESPONSE RECEIVED")
        print(f"{'='*60}")
        print(f"Request ID: {response.get('request_id', 'N/A')}")
        print(f"User ID: {response.get('user_id', 'N/A')}")
        print(f"Status: {response.get('status', 'N/A')}")

        if response.get('status') == 'success':
            print(f"Report ID: {response.get('report_id', 'N/A')}")
            print("\n✓ Report generated successfully!")
            print(f"\nYou can now retrieve the full report from MongoDB using:")
            print(f"  Report ID: {response.get('report_id')}")
        else:
            error_msg = response.get('error_message', 'Unknown error')
            print(f"\n✗ Report generation failed")
            print(f"Error: {error_msg}")

        print(f"\nTimestamp: {response.get('timestamp', 'N/A')}")
        print(f"{'='*60}\n")

    except json.JSONDecodeError as e:
        print(f"✗ Error decoding message: {e}")
    except Exception as e:
        print(f"✗ Error processing message: {e}")


def receive_responses(host: str = 'localhost', timeout: int = None):
    """
    Listen for report generation responses.

    Args:
        host: RabbitMQ host (default: localhost)
        timeout: Stop after timeout seconds (default: run forever)
    """
    print(f"Connecting to RabbitMQ at {host}...")

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host)
    )
    channel = connection.channel()

    # Declare queue (ensure it exists)
    channel.queue_declare(queue='report_generation_responses', durable=True)

    print(f"✓ Connected successfully!")
    print(f"\nListening for responses on queue: report_generation_responses")
    print("Press Ctrl+C to stop\n")
    print(f"{'='*60}")

    # Set up consumer
    channel.basic_consume(
        queue='report_generation_responses',
        on_message_callback=callback,
        auto_ack=True  # Automatically acknowledge messages
    )

    try:
        # Start consuming
        if timeout:
            # Consume with timeout
            connection.process_data_events(time_limit=timeout)
        else:
            # Consume forever
            channel.start_consuming()
    except KeyboardInterrupt:
        print("\n\nStopping consumer...")
        channel.stop_consuming()
    finally:
        connection.close()
        print("Disconnected from RabbitMQ")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Receive report generation responses from RabbitMQ'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='RabbitMQ host (default: localhost)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        help='Stop after N seconds (default: run forever)'
    )

    args = parser.parse_args()

    try:
        receive_responses(host=args.host, timeout=args.timeout)
    except pika.exceptions.AMQPConnectionError:
        print("\n✗ Error: Could not connect to RabbitMQ")
        print("Make sure RabbitMQ is running:")
        print("  docker-compose up -d rabbitmq")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()
