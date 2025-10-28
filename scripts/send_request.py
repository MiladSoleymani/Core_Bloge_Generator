"""
Send a report generation request to RabbitMQ.

This script demonstrates how to send a report generation request
from your main backend to the worker service via RabbitMQ.

Usage:
    python scripts/send_request.py
    python scripts/send_request.py --sample-file data/sample_reports/your_file.json
"""

import pika
import json
import uuid
import argparse
from pathlib import Path


def load_sample_data(file_path: str = None) -> dict:
    """Load sample patient data from file or return default."""
    if file_path and Path(file_path).exists():
        with open(file_path, 'r') as f:
            return json.load(f)

    # Default sample data
    return {
        "patient": {
            "name": "John Doe",
            "age": 45,
            "sex": "male"
        },
        "labs": [
            {
                "category": "biochemistry",
                "test_name": "Sodium",
                "value": "140",
                "unit": "mmol/L",
                "reference_range": "135-145",
                "flag": "normal"
            },
            {
                "category": "lipids",
                "test_name": "Total Cholesterol",
                "value": "5.2",
                "unit": "mmol/L",
                "reference_range": "<5.5",
                "flag": "normal"
            }
        ],
        "cvd_summary": {
            "five_year_risk_percent": 8.5,
            "risk_level": "moderate",
            "interpretation": "Moderate cardiovascular risk",
            "modifiable_risk_factors": [
                "High cholesterol",
                "Physical inactivity"
            ],
            "risk_reduction_advice": [
                "Increase physical activity",
                "Improve diet",
                "Monitor blood pressure"
            ]
        },
        "assessment": {
            "summary": "Patient shows moderate cardiovascular risk with room for lifestyle improvements.",
            "family_history": "Father had heart attack at age 60",
            "lifestyle": {
                "smoking": "Never smoked",
                "alcohol": "Social drinker (1-2 drinks per week)",
                "diet": "Mixed diet, occasional fast food",
                "physical_activity": "Sedentary, desk job, minimal exercise"
            }
        },
        "plan": [
            {
                "advice": "Start regular physical activity - aim for 150 minutes per week",
                "kb_resource_id": "physical_activity_guidelines"
            },
            {
                "advice": "Adopt heart-healthy eating pattern",
                "kb_resource_id": "healthy_eating_aghe"
            },
            {
                "advice": "Monitor blood pressure regularly",
                "kb_resource_id": "blood_pressure_monitoring"
            }
        ],
        "red_flags": [],
        "resources_table": [
            {
                "category": "healthy_eating",
                "title": "Australian Guide to Healthy Eating",
                "url": "https://www.eatforhealth.gov.au/"
            },
            {
                "category": "blood_pressure",
                "title": "Blood Pressure Guidelines",
                "url": "https://www.heartfoundation.org.au/"
            },
            {
                "category": "weight_management",
                "title": "Healthy Weight Guide",
                "url": "https://www.betterhealth.vic.gov.au/"
            }
        ],
        "disclaimer": "This report is based on the provided clinical data and risk calculator outputs. It is intended for informational purposes and should not replace professional medical advice. Please consult your healthcare provider for personalized recommendations."
    }


def send_request(host: str = 'localhost', user_id: str = None, sample_file: str = None):
    """
    Send a report generation request to RabbitMQ.

    Args:
        host: RabbitMQ host (default: localhost)
        user_id: User identifier (default: auto-generated)
        sample_file: Path to sample data file (optional)
    """
    # Generate IDs
    request_id = str(uuid.uuid4())
    user_id = user_id or f"user_{uuid.uuid4().hex[:8]}"

    print(f"Connecting to RabbitMQ at {host}...")

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host)
    )
    channel = connection.channel()

    # Declare queue (ensure it exists)
    channel.queue_declare(queue='report_generation_requests', durable=True)

    # Load sample data
    sample_data = load_sample_data(sample_file)

    # Create request
    request = {
        "request_id": request_id,
        "user_id": user_id,
        **sample_data
    }

    print(f"\n{'='*60}")
    print("SENDING REQUEST")
    print(f"{'='*60}")
    print(f"Request ID: {request_id}")
    print(f"User ID: {user_id}")
    print(f"Patient: {request['patient']['name']}")
    print(f"Age: {request['patient']['age']}")
    print(f"Categories: {len(request['resources_table'])} resources")
    print(f"{'='*60}\n")

    # Publish message
    channel.basic_publish(
        exchange='',
        routing_key='report_generation_requests',
        body=json.dumps(request),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            content_type='application/json'
        )
    )

    print("✓ Request sent successfully!")
    print(f"\nRequest ID: {request_id}")
    print("\nTo receive the response, run:")
    print("  python scripts/receive_response.py")

    connection.close()

    return request_id


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Send report generation request to RabbitMQ'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='RabbitMQ host (default: localhost)'
    )
    parser.add_argument(
        '--user-id',
        help='User identifier (default: auto-generated)'
    )
    parser.add_argument(
        '--sample-file',
        help='Path to sample data JSON file'
    )

    args = parser.parse_args()

    try:
        send_request(
            host=args.host,
            user_id=args.user_id,
            sample_file=args.sample_file
        )
    except pika.exceptions.AMQPConnectionError:
        print("\n✗ Error: Could not connect to RabbitMQ")
        print("Make sure RabbitMQ is running:")
        print("  docker-compose up -d rabbitmq")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()
