# Medical Report Generator - RabbitMQ Worker

AI-powered medical report generation system using RabbitMQ message queue, MongoDB storage, and Redis caching.

## Overview

This system generates comprehensive medical reports by consuming requests from RabbitMQ, processing them with OpenAI GPT-4o, and publishing results back to the main backend. It uses MongoDB for persistent storage and Redis for caching previous inputs.

## Architecture

```
┌─────────────────┐
│  Main Backend   │
│   (Your API)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│              RabbitMQ Queues                     │
├─────────────────────────────────────────────────┤
│  report_generation_requests   (Input Queue)     │
│  report_generation_responses  (Output Queue)    │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────┐      ┌─────────┐
│  Report Worker  │─────▶│ MongoDB  │      │  Redis  │
│  (This Service) │      │(Storage) │      │ (Cache) │
└────────┬────────┘      └──────────┘      └─────────┘
         │
         ▼
┌─────────────────┐
│   OpenAI API    │
│    (GPT-4o)     │
└─────────────────┘
```

## Features

- **RabbitMQ Integration**: Consumes requests from main backend via message queue
- **AI Report Generation**: Uses OpenAI GPT-4o to create personalized health guides
- **MongoDB Storage**: Stores users and generated reports with unique IDs
- **Redis Caching**: Caches previous inputs and generated reports
- **Async Processing**: Non-blocking async/await architecture
- **Docker Support**: Complete docker-compose setup for local development
- **Reliable Messaging**: Durable queues with message persistence

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key

### 2. Installation

```bash
# Clone the repository
cd Core_Bloge_Generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Start Infrastructure Services

```bash
# Start MongoDB, Redis, and RabbitMQ
docker-compose up -d

# Verify services are running
docker-compose ps

# Access RabbitMQ Management UI: http://localhost:15672
# Username: guest, Password: guest
```

### 4. Import Knowledge Base

```bash
# Import health information into MongoDB
python -c "
import asyncio
from app.core.database import mongodb
from app.services.knowledge_base import KnowledgeBaseService

async def import_kb():
    await mongodb.connect()
    kb_service = KnowledgeBaseService(mongodb.db)
    count = await kb_service.import_from_files()
    print(f'Imported {count} knowledge base items')
    await mongodb.disconnect()

asyncio.run(import_kb())
"
```

### 5. Run the Worker

```bash
# Start the report generation worker
python -m app.worker
```

### 6. Test the System

In another terminal:

```bash
# Send a test request and wait for response
python test_rabbitmq_client.py
```

## Message Formats

### Request Message (sent to `report_generation_requests`)

```json
{
  "request_id": "unique-uuid-here",
  "user_id": "user-123",
  "patient": {
    "name": "John Doe",
    "age": 45,
    "sex": "male"
  },
  "labs": [...],
  "cvd_summary": {...},
  "assessment": {...},
  "plan": [...],
  "red_flags": [...],
  "resources_table": [...],
  "disclaimer": "..."
}
```

### Response Message (published to `report_generation_responses`)

```json
{
  "request_id": "unique-uuid-here",
  "user_id": "user-123",
  "report_id": "generated-report-uuid",
  "status": "success",
  "error_message": null,
  "timestamp": "2025-10-28T12:00:00Z"
}
```

## MongoDB Collections

### `users`
Stores user information:
```json
{
  "user_id": "user-123",
  "created_at": "2025-10-28T12:00:00Z",
  "updated_at": "2025-10-28T12:30:00Z"
}
```

### `medical_reports`
Stores generated reports:
```json
{
  "report_id": "report-uuid",
  "user_id": "user-123",
  "report_data": {...},
  "json_content": {...},
  "markdown_content": "...",
  "created_at": "2025-10-28T12:00:00Z",
  "generation_time_seconds": 45.2,
  "tokens_used": 3500,
  "estimated_cost": 0.05
}
```

### `knowledge_base`
Stores health information articles:
```json
{
  "id": "kb-001",
  "category": "weight_management",
  "title": "Healthy Weight Loss Guide",
  "content": "...",
  "source_url": "https://...",
  "verified_source": true
}
```

## Redis Cache Keys

- `input:{user_id}` - Cached user input data (TTL: 1 hour)
- `report:{report_id}` - Cached report data (TTL: 24 hours)

## Configuration

Edit `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=your-key-here

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=blog_generator

# Redis
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=3600

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_REQUEST_QUEUE=report_generation_requests
RABBITMQ_RESPONSE_QUEUE=report_generation_responses
RABBITMQ_PREFETCH_COUNT=1

# Worker
WORKER_NAME=report_worker
MAX_RETRIES=3
```

## Integration with Your Backend

### Sending Requests (Python Example)

```python
import pika
import json
import uuid

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Create request
request = {
    "request_id": str(uuid.uuid4()),
    "user_id": "user-123",
    "patient": {...},
    "labs": [...],
    # ... other fields
}

# Publish to queue
channel.basic_publish(
    exchange='',
    routing_key='report_generation_requests',
    body=json.dumps(request),
    properties=pika.BasicProperties(
        delivery_mode=2,  # persistent
    )
)

connection.close()
```

### Receiving Responses (Python Example)

```python
import pika
import json

def callback(ch, method, properties, body):
    response = json.loads(body)

    if response['status'] == 'success':
        report_id = response['report_id']
        # Fetch full report from MongoDB if needed
        print(f"Report generated: {report_id}")
    else:
        print(f"Error: {response['error_message']}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.basic_consume(
    queue='report_generation_responses',
    on_message_callback=callback
)

channel.start_consuming()
```

## Docker Deployment

### Build and Run with Docker

```bash
# Build the worker image
docker build -t report-worker .

# Run with docker-compose (uncomment worker service in docker-compose.yml)
docker-compose up -d
```

### Environment Variables in Docker

Pass your OpenAI API key:

```bash
docker-compose up -d --build
```

Or set in docker-compose.yml:

```yaml
worker:
  environment:
    OPENAI_API_KEY: your-key-here
```

## Monitoring

### RabbitMQ Management UI

Access: http://localhost:15672 (guest/guest)

- View queue depths
- Monitor message rates
- Check consumer connections
- Manage queues and exchanges

### Logs

```bash
# View worker logs
docker-compose logs -f worker

# View RabbitMQ logs
docker-compose logs -f rabbitmq
```

### MongoDB

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017

use blog_generator

# Check users
db.users.find().pretty()

# Check reports
db.medical_reports.find().pretty()

# Check knowledge base
db.knowledge_base.countDocuments()
```

### Redis

```bash
# Connect to Redis
redis-cli

# Check cached inputs
KEYS input:*

# Check cached reports
KEYS report:*

# View cache entry
GET input:user-123
```

## Performance

- **Request Processing**: 30-60 seconds per report (depends on categories)
- **Concurrent Workers**: Scale horizontally by running multiple workers
- **Message Throughput**: Limited by OpenAI API rate limits
- **Cache Hit Rate**: ~70-80% for repeated user inputs

## Troubleshooting

### Worker Not Consuming Messages

```bash
# Check RabbitMQ connection
docker-compose logs rabbitmq

# Verify queues exist
curl -u guest:guest http://localhost:15672/api/queues
```

### MongoDB Connection Failed

```bash
# Check MongoDB is running
docker-compose ps mongodb

# Test connection
mongosh mongodb://localhost:27017
```

### Redis Connection Failed

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
```

### OpenAI API Errors

- Verify API key in `.env`
- Check rate limits
- Monitor token usage

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_worker.py

# Run with coverage
pytest --cov=app
```

### Adding New Features

1. Add new Pydantic models in `app/models/schemas.py`
2. Update worker logic in `app/worker.py`
3. Add tests in `tests/`
4. Update documentation

## Project Structure

```
Core_Bloge_Generator/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   └── database.py        # MongoDB connection
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── rabbitmq_service.py    # RabbitMQ operations
│   │   ├── redis_service.py       # Redis caching
│   │   ├── knowledge_base.py      # KB management
│   │   ├── report_generator.py    # AI generation
│   │   └── report_storage.py      # MongoDB storage
│   └── worker.py              # Main worker application
├── data/
│   ├── knowledgebase/         # Health information
│   └── sample_reports/        # Test data
├── tests/                     # Test suite
├── docker-compose.yml         # Infrastructure setup
├── Dockerfile                 # Worker container
├── requirements.txt           # Dependencies
├── test_rabbitmq_client.py    # Test client
└── README_RABBITMQ.md        # This file
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review configuration in `.env`
3. Test individual services
4. Check RabbitMQ Management UI

## License

[Add your license here]
