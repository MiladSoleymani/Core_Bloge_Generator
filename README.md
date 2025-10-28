# Medical Report Generator - RabbitMQ Worker

AI-powered medical report generation microservice using RabbitMQ, MongoDB, and Redis.

## Overview

This microservice generates comprehensive medical reports with personalized health guides using OpenAI GPT-4o. It consumes requests from RabbitMQ queues, processes them asynchronously, and publishes results back to your main backend.

## Architecture

```
Main Backend → RabbitMQ → Worker → MongoDB
                  ↑          ↓       Redis
                  └──────────┘
```

**Key Components:**
- **RabbitMQ**: Message queue for async communication
- **MongoDB**: Persistent storage for users and reports
- **Redis**: Caching layer for inputs and reports
- **OpenAI GPT-4o**: AI-powered report generation
- **Python Worker**: Async message processor

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API key

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 3. Start Infrastructure

```bash
# Start MongoDB, Redis, RabbitMQ
docker-compose up -d

# Verify services
docker-compose ps
```

### 4. Initialize System

```bash
# Run setup script
python tests/setup_worker.py
```

### 5. Start Worker

```bash
# Start processing requests
python -m app.worker
```

### 6. Test

```bash
# Send test request (in another terminal)
python tests/test_rabbitmq_client.py
```

## Features

- ✅ **Async Processing**: Non-blocking message queue architecture
- ✅ **AI-Powered**: OpenAI GPT-4o generates personalized health guides
- ✅ **Scalable**: Run multiple workers for horizontal scaling
- ✅ **Persistent**: MongoDB storage with user and report tracking
- ✅ **Fast**: Redis caching for previous inputs and reports
- ✅ **Reliable**: Message persistence and automatic retry
- ✅ **Decoupled**: Independent from main backend

## Message Format

### Request (sent to `report_generation_requests`)

```json
{
  "request_id": "uuid",
  "user_id": "user-123",
  "patient": {...},
  "labs": [...],
  "assessment": {...},
  "plan": [...],
  "resources_table": [...]
}
```

### Response (received from `report_generation_responses`)

```json
{
  "request_id": "uuid",
  "user_id": "user-123",
  "report_id": "generated-uuid",
  "status": "success",
  "timestamp": "2025-10-28T12:00:00Z"
}
```

## Integration Example

### Send Request (Python)

```python
import pika
import json
import uuid

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

request = {
    "request_id": str(uuid.uuid4()),
    "user_id": "user-123",
    # ... your data
}

channel.basic_publish(
    exchange='',
    routing_key='report_generation_requests',
    body=json.dumps(request)
)
```

### Receive Response

```python
def callback(ch, method, properties, body):
    response = json.loads(body)
    print(f"Report ID: {response['report_id']}")

channel.basic_consume(
    queue='report_generation_responses',
    on_message_callback=callback
)
channel.start_consuming()
```

## Configuration

Edit `.env`:

```bash
OPENAI_API_KEY=your-key-here
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

## Monitoring

- **RabbitMQ UI**: http://localhost:15672 (guest/guest)
- **MongoDB**: `mongosh mongodb://localhost:27017`
- **Redis**: `redis-cli`

## Scaling

Run multiple workers:

```bash
# Terminal 1
python -m app.worker

# Terminal 2
python -m app.worker

# Terminal 3
python -m app.worker
```

Or with Docker:

```bash
docker-compose up -d --scale worker=3
```

## Project Structure

```
Core_Bloge_Generator/
├── app/
│   ├── worker.py                  # Main worker application
│   ├── core/
│   │   ├── config.py              # Configuration
│   │   └── database.py            # MongoDB connection
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   └── services/
│       ├── rabbitmq_service.py    # RabbitMQ operations
│       ├── redis_service.py       # Redis caching
│       ├── report_generator.py    # AI generation
│       ├── knowledge_base.py      # KB management
│       └── report_storage.py      # MongoDB storage
├── data/
│   ├── knowledgebase/             # Health information
│   └── sample_reports/            # Test data
├── docs/
│   ├── QUICKSTART.md              # 5-minute setup guide
│   ├── README_RABBITMQ.md         # Full documentation
│   └── RABBITMQ_ARCHITECTURE.md   # Architecture details
├── tests/
│   ├── setup_worker.py            # Initialization script
│   ├── test_rabbitmq_client.py    # Test client
│   └── test_*.py                  # Unit tests
├── notebooks/
│   └── generate_specialized_reports.ipynb  # Research prototype
├── docker-compose.yml             # Infrastructure setup
├── Dockerfile                     # Worker container
└── requirements.txt               # Dependencies
```

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Full Documentation](docs/README_RABBITMQ.md)** - Complete guide
- **[Architecture](docs/RABBITMQ_ARCHITECTURE.md)** - Technical details

## Development

### Run Tests

```bash
pytest tests/
```

### View Logs

```bash
# Docker services
docker-compose logs -f

# Worker
python -m app.worker  # See output in terminal
```

### Database Operations

```bash
# MongoDB
mongosh mongodb://localhost:27017
use blog_generator
db.medical_reports.find()

# Redis
redis-cli
KEYS *
```

## Troubleshooting

### Services Not Starting

```bash
docker-compose down
docker-compose up -d
docker-compose ps
```

### Worker Connection Failed

1. Check `.env` configuration
2. Verify services: `docker-compose ps`
3. Check logs: `docker-compose logs rabbitmq`

### Knowledge Base Empty

```bash
python tests/setup_worker.py
```

## Performance

- **Processing Time**: 30-60 seconds per report
- **Throughput**: 1-2 reports/minute per worker
- **Scalability**: Linear with number of workers
- **Cache Hit Rate**: ~70-80% for repeated requests

## Production Deployment

1. Use managed services:
   - CloudAMQP for RabbitMQ
   - MongoDB Atlas
   - Redis Cloud

2. Configure TLS/SSL for all connections

3. Set up monitoring and alerting

4. Deploy workers as containers (Kubernetes, ECS, etc.)

5. Configure autoscaling based on queue depth

## Technology Stack

- **Python 3.11+** - Application runtime
- **RabbitMQ** - Message broker
- **MongoDB** - Document database
- **Redis** - In-memory cache
- **OpenAI GPT-4o** - AI model
- **LangChain** - AI framework
- **Pydantic** - Data validation
- **Docker** - Containerization

## License

[Add your license here]

## Support

For questions and issues:
1. Check documentation in `docs/`
2. Review logs and monitoring tools
3. Test individual components

## Acknowledgments

- OpenAI for GPT-4o API
- Health information sources cited in knowledge base
- Open source libraries and frameworks
