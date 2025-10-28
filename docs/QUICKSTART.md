# Quick Start Guide - RabbitMQ Worker

Get the Medical Report Generator worker running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Python 3.11+ installed
- OpenAI API key

## Step-by-Step Setup

### 1. Clone and Setup Environment (1 min)

```bash
cd Core_Bloge_Generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

### 2. Start Infrastructure (1 min)

```bash
# Start MongoDB, Redis, RabbitMQ
docker-compose up -d

# Verify services
docker-compose ps

# Should show:
# - report_generator_mongodb (port 27017)
# - report_generator_redis (port 6379)
# - report_generator_rabbitmq (ports 5672, 15672)
```

### 3. Initialize System (1 min)

```bash
# Run setup script
python setup_worker.py

# This will:
# - Verify connections
# - Create database indexes
# - Import knowledge base
```

### 4. Start Worker (30 sec)

```bash
# Start the worker
python -m app.worker

# You should see:
# Worker starting...
# Connected to MongoDB
# Connected to RabbitMQ
# Connected to Redis
# Starting to consume messages...
```

### 5. Test the System (1 min)

Open a new terminal:

```bash
# Activate virtual environment
source venv/bin/activate

# Run test client
python test_rabbitmq_client.py

# This will:
# - Send a test request
# - Wait for response
# - Display results
```

## What You Get

After setup, you have:

1. **RabbitMQ** running at:
   - AMQP: `localhost:5672`
   - Management UI: http://localhost:15672 (guest/guest)

2. **MongoDB** running at:
   - Connection: `localhost:27017`
   - Database: `blog_generator`
   - Collections: `users`, `medical_reports`, `knowledge_base`

3. **Redis** running at:
   - Connection: `localhost:6379`

4. **Worker** consuming messages from:
   - Input queue: `report_generation_requests`
   - Output queue: `report_generation_responses`

## Message Format

### Send Request (Your Backend)

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
    "patient": {
        "name": "John Doe",
        "age": 45,
        "sex": "male"
    },
    "labs": [...],
    "assessment": {...},
    # ... other fields (see sample data)
}

channel.basic_publish(
    exchange='',
    routing_key='report_generation_requests',
    body=json.dumps(request)
)

connection.close()
```

### Receive Response

```python
def callback(ch, method, properties, body):
    response = json.loads(body)
    print(f"Report ID: {response['report_id']}")
    print(f"Status: {response['status']}")

channel.basic_consume(
    queue='report_generation_responses',
    on_message_callback=callback,
    auto_ack=True
)

channel.start_consuming()
```

## Monitoring

### RabbitMQ Management UI

Visit: http://localhost:15672
- Username: `guest`
- Password: `guest`

View:
- Queue depths
- Message rates
- Active consumers

### MongoDB

```bash
mongosh mongodb://localhost:27017

use blog_generator

# Check users
db.users.find()

# Check reports
db.medical_reports.find().sort({created_at: -1}).limit(5)

# Check knowledge base
db.knowledge_base.countDocuments()
```

### Redis

```bash
redis-cli

# Check cached inputs
KEYS input:*

# Check cached reports
KEYS report:*

# View specific cache
GET input:user-123
```

## Troubleshooting

### Services Not Starting

```bash
# Check Docker logs
docker-compose logs mongodb
docker-compose logs redis
docker-compose logs rabbitmq

# Restart services
docker-compose restart
```

### Worker Not Connecting

1. Check `.env` file has correct URLs
2. Verify services are running: `docker-compose ps`
3. Check worker logs for error messages

### Knowledge Base Import Failed

```bash
# Check data directory exists
ls data/knowledgebase/

# Manually import
python setup_worker.py
```

### OpenAI API Errors

1. Verify API key in `.env`
2. Check OpenAI account has credits
3. Monitor rate limits

## Next Steps

1. **Read Full Documentation**
   - `README_RABBITMQ.md` - Complete guide
   - `docs/RABBITMQ_ARCHITECTURE.md` - Architecture details

2. **Integrate with Your Backend**
   - Implement RabbitMQ publisher
   - Implement response consumer
   - Handle error cases

3. **Scale the System**
   - Run multiple workers
   - Configure load balancing
   - Monitor performance

4. **Production Deployment**
   - Use managed RabbitMQ (CloudAMQP)
   - Use MongoDB Atlas
   - Use Redis Cloud
   - Configure TLS/SSL
   - Set up monitoring

## Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Start worker
python -m app.worker

# Run test
python test_rabbitmq_client.py

# Setup/reset
python setup_worker.py

# Install dependencies
pip install -r requirements.txt
```

## File Structure

```
Core_Bloge_Generator/
├── app/
│   ├── worker.py              # Main worker application
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   └── database.py        # MongoDB connection
│   ├── services/
│   │   ├── rabbitmq_service.py    # RabbitMQ operations
│   │   ├── redis_service.py       # Redis caching
│   │   ├── report_generator.py    # AI generation
│   │   └── knowledge_base.py      # KB management
│   └── models/
│       └── schemas.py         # Data models
├── data/
│   ├── knowledgebase/         # Health information
│   └── sample_reports/        # Test data
├── docker-compose.yml         # Infrastructure setup
├── setup_worker.py            # Initialization script
├── test_rabbitmq_client.py    # Test client
└── README_RABBITMQ.md        # Full documentation
```

## Support

Having issues? Check:

1. All services running: `docker-compose ps`
2. Worker logs: Check terminal output
3. RabbitMQ UI: http://localhost:15672
4. MongoDB: `mongosh mongodb://localhost:27017`
5. Redis: `redis-cli ping`

## Resources

- **RabbitMQ**: https://www.rabbitmq.com/
- **MongoDB**: https://www.mongodb.com/
- **Redis**: https://redis.io/
- **OpenAI**: https://platform.openai.com/

---

**Ready to generate reports?** Run `python -m app.worker` and send your first request!
