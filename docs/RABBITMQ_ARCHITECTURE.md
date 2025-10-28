# RabbitMQ-Based Architecture

## System Overview

The Medical Report Generator has been transformed from a FastAPI REST API into a microservice that communicates via RabbitMQ message queues. This architecture enables asynchronous, decoupled processing of report generation requests.

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                        Main Backend                           │
│                     (Your Application)                        │
│                                                               │
│  ┌─────────────┐         ┌──────────────┐                   │
│  │   API       │         │   Business   │                   │
│  │ Endpoints   │────────▶│    Logic     │                   │
│  └─────────────┘         └──────┬───────┘                   │
│                                  │                            │
└──────────────────────────────────┼────────────────────────────┘
                                   │
                                   │ Publish Request
                                   ▼
┌───────────────────────────────────────────────────────────────┐
│                         RabbitMQ                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │        Queue: report_generation_requests                │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │ │
│  │  │Message 1│  │Message 2│  │Message 3│  │Message 4│  │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │       Queue: report_generation_responses                │ │
│  │  ┌─────────┐  ┌─────────┐                              │ │
│  │  │Response │  │Response │                              │ │
│  │  └─────────┘  └─────────┘                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
                    │                        ▲
                    │ Consume                │ Publish Response
                    ▼                        │
┌───────────────────────────────────────────────────────────────┐
│              Report Generation Worker                         │
│            (This Microservice)                                │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Worker Components                       │   │
│  │                                                      │   │
│  │  ┌─────────────┐      ┌─────────────┐             │   │
│  │  │  RabbitMQ   │      │   Redis     │             │   │
│  │  │  Consumer   │──────│   Cache     │             │   │
│  │  └──────┬──────┘      └─────────────┘             │   │
│  │         │                                          │   │
│  │         │                                          │   │
│  │         ▼                                          │   │
│  │  ┌─────────────┐                                  │   │
│  │  │  Request    │                                  │   │
│  │  │  Processor  │                                  │   │
│  │  └──────┬──────┘                                  │   │
│  │         │                                          │   │
│  │         ├──────────┬──────────┬──────────┐       │   │
│  │         ▼          ▼          ▼          ▼       │   │
│  │  ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │   │
│  │  │Knowledge │ │Report  │ │MongoDB │ │OpenAI  │ │   │
│  │  │   Base   │ │Storage │ │Service │ │  API   │ │   │
│  │  └──────────┘ └────────┘ └────────┘ └────────┘ │   │
│  │                                                  │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   MongoDB    │ │    Redis     │ │  OpenAI API  │
│  (Storage)   │ │   (Cache)    │ │   (AI/ML)    │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Component Details

### 1. Main Backend (Your Application)

**Responsibilities:**
- Receives requests from end users
- Validates and formats data
- Publishes requests to RabbitMQ
- Listens for responses from RabbitMQ
- Returns results to end users

**Integration Points:**
- Publishes to: `report_generation_requests` queue
- Consumes from: `report_generation_responses` queue

### 2. RabbitMQ Message Broker

**Queues:**

#### `report_generation_requests`
- **Purpose**: Receives report generation requests
- **Properties**: Durable, persistent messages
- **Message Format**: JSON with ReportGenerationRequest schema
- **TTL**: No expiration (until processed)

#### `report_generation_responses`
- **Purpose**: Delivers report generation results
- **Properties**: Durable, persistent messages
- **Message Format**: JSON with ReportGenerationResponse schema
- **TTL**: 24 hours (configurable)

**Configuration:**
- Exchange: Default (direct)
- Routing: Queue name as routing key
- Acknowledgement: Manual ack after processing
- Prefetch: 1 message per worker

### 3. Report Generation Worker

**Core Services:**

#### RabbitMQ Consumer Service
- Connects to RabbitMQ
- Consumes messages from request queue
- Acknowledges processed messages
- Publishes responses to response queue

#### Redis Cache Service
- Caches user inputs (TTL: 1 hour)
- Caches generated reports (TTL: 24 hours)
- Provides fast access to recent data
- Reduces database queries

#### Request Processor
- Parses incoming messages
- Validates request data
- Coordinates report generation
- Handles errors and retries

#### Knowledge Base Service
- Loads health information from MongoDB
- Aggregates content by category
- Provides context for AI generation

#### Report Generator
- Integrates with OpenAI GPT-4o
- Generates category-specific reports
- Creates friendly, personalized content
- Includes inline source citations

#### MongoDB Service
- Stores users and reports
- Provides persistence layer
- Indexed for fast queries
- Handles concurrent writes

### 4. Data Stores

#### MongoDB Collections

**users**
```javascript
{
  _id: ObjectId,
  user_id: "user-123",          // Unique user identifier
  created_at: ISODate,
  updated_at: ISODate
}
```
Indexes: `user_id` (unique), `created_at`

**medical_reports**
```javascript
{
  _id: ObjectId,
  report_id: "report-uuid",     // Unique report identifier
  user_id: "user-123",          // Owner reference
  report_data: {...},           // Full MedicalReport object
  json_content: {...},          // JSON representation
  markdown_content: "...",      // Markdown format
  created_at: ISODate,
  generation_time_seconds: 45.2,
  tokens_used: 3500,
  estimated_cost: 0.05
}
```
Indexes: `report_id` (unique), `user_id + created_at`

**knowledge_base**
```javascript
{
  _id: ObjectId,
  id: "kb-001",
  category: "weight_management",
  title: "...",
  content: "...",
  source_url: "...",
  verified_source: true,
  last_updated: ISODate,
  status: "active"
}
```
Indexes: `id` (unique), `category`, `status`

#### Redis Keys

- `input:{user_id}` - Cached user input
- `report:{report_id}` - Cached generated report

## Message Flow

### Request Flow

1. **Main Backend** receives user request
2. Creates `ReportGenerationRequest` message
3. Publishes to `report_generation_requests` queue
4. Returns acknowledgement to user

### Processing Flow

1. **Worker** consumes message from queue
2. Parses and validates request
3. Checks Redis cache for previous input
4. Caches current input in Redis
5. Ensures user exists in MongoDB
6. Fetches knowledge base content
7. Calls OpenAI API to generate reports
8. Stores report in MongoDB
9. Caches report in Redis
10. Publishes response to `report_generation_responses` queue
11. Acknowledges message to RabbitMQ

### Response Flow

1. **Main Backend** consumes response from queue
2. Parses response message
3. If success: retrieves full report from MongoDB/Redis
4. Returns result to end user
5. Acknowledges message to RabbitMQ

## Data Models

### ReportGenerationRequest
```python
{
  "request_id": str,        # Unique request ID (UUID)
  "user_id": str,           # User identifier
  "patient": {...},         # Patient information
  "labs": [...],            # Lab results
  "cvd_summary": {...},     # CVD risk summary
  "assessment": {...},      # Clinical assessment
  "plan": [...],            # Treatment plan
  "red_flags": [...],       # Clinical warnings
  "resources_table": [...], # Reference resources
  "disclaimer": str         # Legal disclaimer
}
```

### ReportGenerationResponse
```python
{
  "request_id": str,        # Original request ID
  "user_id": str,           # User identifier
  "report_id": str,         # Generated report ID (UUID)
  "status": str,            # "success" or "failed"
  "error_message": str,     # Error details (if failed)
  "timestamp": datetime     # Response timestamp
}
```

## Scaling Strategy

### Horizontal Scaling

**Multiple Workers:**
```
Main Backend → RabbitMQ → Worker 1 ─┐
                        → Worker 2 ─┤→ MongoDB
                        → Worker 3 ─┘   Redis
```

- Start multiple worker instances
- Each consumes from same queue
- RabbitMQ distributes messages (round-robin)
- Prefetch count controls concurrency

**Scaling Commands:**
```bash
# Scale to 3 workers
docker-compose up -d --scale worker=3

# Or run multiple instances
python -m app.worker &
python -m app.worker &
python -m app.worker &
```

### Load Distribution

- **Request Queue**: Round-robin distribution
- **Response Queue**: All backends consume
- **MongoDB**: Handles concurrent writes
- **Redis**: Thread-safe operations
- **OpenAI**: Rate limit per worker

## Error Handling

### Retry Mechanism

1. Message not acknowledged on error
2. RabbitMQ requeues message
3. Another worker (or same) retries
4. Max retries configurable (default: 3)

### Dead Letter Queue (Optional)

```python
# Configure DLQ for failed messages
channel.queue_declare(
    'report_generation_requests_dlq',
    durable=True
)
```

### Error Response

```json
{
  "request_id": "...",
  "user_id": "...",
  "report_id": "",
  "status": "failed",
  "error_message": "OpenAI API rate limit exceeded"
}
```

## Monitoring & Observability

### Metrics to Track

**RabbitMQ:**
- Queue depth
- Message rate (in/out)
- Consumer count
- Acknowledgement rate

**Worker:**
- Processing time per request
- Success/failure rate
- OpenAI API latency
- Cache hit rate

**MongoDB:**
- Query performance
- Connection pool usage
- Document counts

**Redis:**
- Cache hit/miss ratio
- Memory usage
- Eviction rate

### Health Checks

```python
# Worker health check
async def health_check():
    checks = {
        'rabbitmq': await rabbitmq_service.ping(),
        'mongodb': await mongodb.ping(),
        'redis': await redis_service.ping()
    }
    return all(checks.values())
```

## Security Considerations

### Message Security

- Use TLS for RabbitMQ connections
- Encrypt sensitive data in messages
- Validate message signatures
- Implement message expiration

### Access Control

- RabbitMQ user authentication
- MongoDB access control
- Redis password protection
- Network isolation (VPC)

### Data Privacy

- Anonymize patient data
- Encrypt data at rest (MongoDB)
- Secure API keys in environment
- Audit log all operations

## Performance Characteristics

### Throughput

- **Single Worker**: 1-2 reports/minute
- **3 Workers**: 3-6 reports/minute
- **Bottleneck**: OpenAI API rate limits

### Latency

- **Queue latency**: < 100ms
- **Processing time**: 30-60 seconds
- **Cache retrieval**: < 10ms
- **MongoDB query**: < 50ms

### Resource Usage

**Per Worker:**
- CPU: 20-30% (during generation)
- Memory: 200-300 MB
- Network: 50-100 KB/s

## Advantages Over REST API

1. **Decoupling**: Backend and worker independent
2. **Scalability**: Easy horizontal scaling
3. **Reliability**: Message persistence and retry
4. **Async**: Non-blocking processing
5. **Load Leveling**: Queue absorbs traffic spikes
6. **Fault Tolerance**: Worker failures don't lose requests

## Migration Path

### From FastAPI to RabbitMQ

1. ✓ Install RabbitMQ infrastructure
2. ✓ Implement worker services
3. ✓ Update data models
4. ✓ Add Redis caching
5. Parallel run both systems
6. Migrate traffic gradually
7. Decommission REST API

## Future Enhancements

1. **Priority Queues**: Urgent vs. normal requests
2. **Dead Letter Queue**: Handle failed messages
3. **Message Routing**: Route by category/user type
4. **Batch Processing**: Combine multiple requests
5. **Result Caching**: Skip regeneration for identical requests
6. **Webhooks**: Push results instead of polling
7. **GraphQL**: Flexible report queries
8. **Streaming**: Progressive report generation
