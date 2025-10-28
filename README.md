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
python setup_worker.py
```

### 5. Start Worker

```bash
# Start processing requests
python -m app.worker
```

### 6. Test

```bash
# Send test request (in another terminal)
python scripts/send_request.py

# Or use full test client
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

## Integration Scripts

Use the provided scripts to integrate with your backend:

```bash
# Send a report request
python scripts/send_request.py --user-id user-123

# Listen for responses
python scripts/receive_response.py

# Check saved reports in database
python scripts/check_database.py --list-reports

# Get specific report
python scripts/check_database.py --report-id <report-id>

# View report as markdown
python scripts/check_database.py --report-id <report-id> --markdown
```

See `scripts/README.md` for detailed usage and integration examples.

## Configuration

Edit `.env`:

```bash
OPENAI_API_KEY=your-key-here
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

## Monitoring

### RabbitMQ Management UI
- **URL**: http://localhost:15672
- **Login**: guest / guest
- **Monitor**: Queue depths, message rates, consumers

### Check Reports in Database

```bash
# View all reports
python scripts/check_database.py

# Show statistics
python scripts/check_database.py --stats

# List reports
python scripts/check_database.py --list-reports

# Get specific report
python scripts/check_database.py --report-id <id>
```

### MongoDB Shell

```bash
mongosh mongodb://localhost:27017
use blog_generator
db.medical_reports.find().pretty()
db.users.find().pretty()
```

### Redis

```bash
redis-cli
KEYS *
GET input:user-123
```

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
├── scripts/
│   ├── send_request.py            # Send requests to RabbitMQ
│   ├── receive_response.py        # Receive responses
│   ├── check_database.py          # Check reports in DB
│   └── README.md                  # Scripts documentation
├── data/
│   ├── knowledgebase/             # Health information
│   └── sample_reports/            # Test data
├── docs/
│   ├── QUICKSTART.md              # 5-minute setup guide
│   ├── README_RABBITMQ.md         # Full documentation
│   ├── RABBITMQ_ARCHITECTURE.md   # Architecture details
│   └── MIGRATION_SUMMARY.md       # Migration guide
├── tests/
│   ├── test_rabbitmq_client.py    # Integration test
│   ├── test_models.py             # Unit tests
│   └── test_*.py                  # Other tests
├── setup_worker.py                # System initialization
├── docker-compose.yml             # Infrastructure setup
├── Dockerfile                     # Worker container
├── HOW_TO_CHECK_REPORTS.md        # Database guide
└── requirements.txt               # Dependencies
```

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Full Documentation](docs/README_RABBITMQ.md)** - Complete guide
- **[Architecture](docs/RABBITMQ_ARCHITECTURE.md)** - Technical details
- **[Migration Summary](docs/MIGRATION_SUMMARY.md)** - What changed from FastAPI
- **[How to Check Reports](HOW_TO_CHECK_REPORTS.md)** - Database queries and tools
- **[Scripts Guide](scripts/README.md)** - Integration scripts

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

### Check Database

```bash
# Python script (recommended)
python scripts/check_database.py --list-reports
python scripts/check_database.py --report-id <id>

# MongoDB shell
mongosh mongodb://localhost:27017
use blog_generator
db.medical_reports.find().pretty()

# Redis
redis-cli
KEYS *
```

See **[HOW_TO_CHECK_REPORTS.md](HOW_TO_CHECK_REPORTS.md)** for complete guide.

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
python setup_worker.py
```

### Check if Reports are Saving

```bash
# View all saved reports
python scripts/check_database.py --list-reports

# Check database statistics
python scripts/check_database.py --stats
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
