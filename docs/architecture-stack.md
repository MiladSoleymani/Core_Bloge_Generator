# Blog Generator Architecture - Streamlined Stack

## Overview

This document describes the simplified Python-focused technology stack for the Blog/Medical Report Generator system.

## Architecture Stack

```
Backend: FastAPI
Cache: Redis
Queue: Celery + Redis (using Redis as broker)
Document DB: MongoDB (stores everything)
AI: OpenAI + LangChain
```

## Removed Components

- **PostgreSQL** - Not needed since we have existing user management system with API key validation
- **MinIO/S3** - Not needed at this stage, reports stored as text in MongoDB

---

## Component Details

### 1. FastAPI Backend

**Purpose:** Main Backend (API Gateway) layer

**Responsibilities:**
- Handles API routes and request/response
- Validates API keys via existing auth system
- Routes sync/async requests
- Request validation using Pydantic models
- Response formatting

**Key Features:**
- Async/await support for concurrent requests
- Automatic API documentation (Swagger/OpenAPI)
- Pydantic integration for data validation
- Fast performance
- Type hints support

**Example Implementation:**
```python
from fastapi import FastAPI, Depends, HTTPException, Header
import httpx

app = FastAPI()

async def validate_api_key(x_api_key: str = Header(...)):
    # Option A: Call existing auth API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://your-auth-system.com/validate",
            headers={"X-API-Key": x_api_key}
        )
        if response.status_code != 200:
            raise HTTPException(401, "Invalid API key")
        return response.json()

@app.post("/api/generate-report")
async def generate_report(
    request: ReportRequest,
    user = Depends(validate_api_key),
    redis: Redis = Depends(get_redis)
):
    # Check rate limit
    if not await check_rate_limit(redis, user["user_id"]):
        raise HTTPException(429, "Rate limit exceeded")

    # Process request...
    return result
```

---

### 2. Redis

**Purpose:** Cache Layer + Rate Limiting + Message Broker

**Use Cases:**

1. **Rate Limiting** (Primary use)
```python
async def check_rate_limit(redis_client, user_id: str, limit: int = 100):
    key = f"rate_limit:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
    count = await redis_client.incr(key)

    if count == 1:
        await redis_client.expire(key, 86400)  # 24 hours

    return count <= limit
```

2. **Session Cache** - Cache frequently accessed reports
```python
async def cache_report(redis_client, report_id: str, report: dict):
    await redis_client.setex(
        f"report:{report_id}",
        3600,  # 1 hour
        json.dumps(report)
    )
```

3. **Celery Broker** - Job queue for async tasks
4. **Celery Backend** - Store task results

**Key Features:**
- In-memory speed (microsecond latency)
- Multiple data structures (strings, hashes, lists, sets)
- Built-in expiration (TTL)
- Atomic operations for counters

---

### 3. Celery + Redis

**Purpose:** Async Job Queue + Background Task Processing

**Why Celery:**
- Python-native, integrates with FastAPI
- Distributed task execution
- Automatic retries and error handling
- Task scheduling (cron-like)
- Task chaining for complex workflows

**Configuration:**
```python
from celery import Celery

celery_app = Celery(
    'report_generator',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
)
```

**Task Example:**
```python
@celery_app.task(bind=True, max_retries=3)
def generate_report_async(self, patient_data: dict, categories: list, user_id: str):
    try:
        # Update progress
        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100})

        # Fetch KB content from MongoDB
        kb_content = get_kb_content(categories)

        self.update_state(state='PROGRESS', meta={'current': 30, 'total': 100})

        # Generate reports with OpenAI
        reports = generate_all_category_reports(kb_content, categories)

        self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100})

        # Save to MongoDB
        report_id = save_report_to_db(patient_data, reports, user_id)

        return {"status": "completed", "report_id": report_id}

    except Exception as e:
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

---

### 4. MongoDB

**Purpose:** Document Database - Stores all data

**Collections:**

#### Collection 1: `knowledge_base`
Stores health information resources with content

```python
{
    "_id": ObjectId("..."),
    "file_name": "weightloss_healthylifestyle.md",
    "title": "Weight Loss - A Healthy Approach",
    "category": "weight_management",
    "applies_to": ["obesity", "diabetes", "heart_disease"],
    "summary_length_words": 500,
    "source_url": "https://www.betterhealth.vic.gov.au/...",
    "verified_source": true,
    "last_updated": ISODate("2025-01-15"),
    "status": "active",
    "content": "# Weight Loss\n\nFull markdown content here..."
}
```

**Indexes:**
```python
await knowledge_base.create_index([("category", 1)])
await knowledge_base.create_index([("status", 1)])
```

#### Collection 2: `medical_reports`
Stores generated reports with embedded files

```python
{
    "_id": ObjectId("..."),
    "report_id": "uuid-here",
    "user_id": "user-uuid",
    "created_at": ISODate("2025-10-27T10:30:00Z"),
    "status": "completed",

    "patient": {
        "name": "John Doe",
        "age": 45,
        "sex": "M"
    },

    "labs": [...],
    "cvd_summary": {...},
    "assessment": {...},
    "plan": [...],
    "red_flags": [...],
    "resources_table": [...],

    "category_reports": [
        {
            "category": "weight_management",
            "text": "Full report text with inline links...",
            "sources": ["https://..."]
        }
    ],

    "disclaimer": "...",

    "generated_files": {
        "json": "{...full json...}",
        "markdown": "# Medical Report\n\nFull markdown...",
        "pdf": null  // Generated on-demand
    },

    "generation_time_seconds": 45.2,
    "model_used": "gpt-4o",
    "total_tokens": 8500,
    "cost_usd": 0.15
}
```

**Indexes:**
```python
await medical_reports.create_index([("user_id", 1), ("created_at", -1)])
await medical_reports.create_index([("report_id", 1)], unique=True)
await medical_reports.create_index([("status", 1)])
```

#### Collection 3: `rate_limits` (Optional)
Rate limiting can be in Redis, but MongoDB for persistence

```python
{
    "_id": ObjectId("..."),
    "api_key": "user-api-key",
    "resource": "generate_report",
    "quota_limit": 100,  // per month
    "quota_used": 45,
    "reset_date": ISODate("2025-11-01"),
    "last_request": ISODate("2025-10-27T10:30:00Z")
}
```

**Why MongoDB:**
- Flexible schema for varying report structures
- Nested documents (patient → labs → reports)
- Fast document retrieval
- Horizontal scaling with sharding
- JSON-native, works with Pydantic models
- Can store text files directly (no need for MinIO at this stage)

**Database Operations:**
```python
from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
db = mongo_client["blog_generator"]

# Fetch KB content
async def get_kb_content_for_category(category: str) -> str:
    cursor = db.knowledge_base.find({"category": category, "status": "active"})
    content_parts = []

    async for item in cursor:
        content_parts.append(f"# {item['title']}\n\n{item['content']}\n\n---\n")

    return "\n".join(content_parts)

# Save report
async def save_report(report: MedicalReport, user_id: str) -> str:
    report_dict = report.dict()
    report_dict["user_id"] = user_id
    report_dict["report_id"] = str(uuid.uuid4())
    report_dict["generated_files"] = {
        "json": report.json(indent=2),
        "markdown": generate_markdown(report)
    }

    result = await db.medical_reports.insert_one(report_dict)
    return str(result.inserted_id)
```

---

### 5. OpenAI + LangChain

**Purpose:** AI Model - Core content generation

**Why OpenAI:**
- GPT-4o for high-quality medical/health content
- Structured outputs with JSON mode
- Large context window (128k tokens)
- Function calling capabilities

**Why LangChain:**
- Model abstraction (easy to switch between providers)
- Reusable prompt templates
- Pydantic output parsers
- RAG (Retrieval-Augmented Generation) chains
- Conversation memory

**Basic Usage:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
parser = JsonOutputParser(pydantic_object=CategoryReport)

system_msg = SystemMessage(content="You are a health information assistant...")
human_msg = HumanMessage(content=f"Generate report for {category}...")

response = llm.invoke([system_msg, human_msg])
parsed_output = parser.parse(response.content)
```

**Advanced: RAG Pipeline**
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

# Load knowledge base into vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=knowledge_base_docs,
    embedding=embeddings
)

# Create retrieval chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
)

result = qa_chain.invoke({"query": f"Generate advice for {patient}"})
```

---

## Complete Request Flow

### Sync Request Flow
```
1. User → FastAPI (POST /api/generate-report + API key)
2. FastAPI → Existing Auth System (validate API key)
3. FastAPI → Redis (check rate limit)
4. FastAPI → MongoDB (fetch KB content)
5. FastAPI → OpenAI (generate category reports)
6. FastAPI → MongoDB (save report)
7. FastAPI → User (return report immediately)
```

### Async Request Flow
```
1. User → FastAPI (POST /api/generate-report?async=true + API key)
2. FastAPI → Existing Auth System (validate API key)
3. FastAPI → Redis (check rate limit)
4. FastAPI → Celery (queue task, return job_id)
5. FastAPI → User (return {"job_id": "...", "status": "queued"})

Background:
6. Celery Worker → MongoDB (fetch KB content)
7. Celery Worker → OpenAI (generate reports)
8. Celery Worker → MongoDB (save report)
9. Celery Worker → Redis (update task status)

Later:
10. User → FastAPI (GET /api/job-status/{job_id})
11. FastAPI → Redis/Celery (check task status)
12. FastAPI → MongoDB (fetch report if completed)
13. FastAPI → User (return report)
```

---

## API Endpoints

### Generate Report (Sync)
```
POST /api/generate-report
Headers: X-API-Key: <user-api-key>
Body:
{
    "patient": {
        "name": "John Doe",
        "age": 45,
        "sex": "M"
    },
    "labs": [...],
    "categories": ["weight_management", "blood_pressure"]
}

Response:
{
    "report_id": "uuid",
    "status": "completed",
    "report": {...}
}
```

### Generate Report (Async)
```
POST /api/generate-report?async=true
Headers: X-API-Key: <user-api-key>
Body: (same as sync)

Response:
{
    "job_id": "celery-task-id",
    "status": "queued"
}
```

### Check Job Status
```
GET /api/job-status/{job_id}
Headers: X-API-Key: <user-api-key>

Response:
{
    "job_id": "...",
    "status": "processing",  // queued, processing, completed, failed
    "progress": 60,  // percentage
    "result": null  // or report data if completed
}
```

### Get Report
```
GET /api/reports/{report_id}
Headers: X-API-Key: <user-api-key>

Response:
{
    "report_id": "...",
    "patient": {...},
    "category_reports": [...],
    "generated_files": {
        "json": "...",
        "markdown": "..."
    }
}
```

---

## Deployment Architecture

### Development
```
- FastAPI: localhost:8000
- Redis: localhost:6379
- MongoDB: localhost:27017
- Celery Worker: 1 worker process
```

### Production (Docker Compose)
```yaml
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - mongodb
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  celery_worker:
    build: ./api
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - redis
      - mongodb
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

---

## When to Add Components Later

### Add PostgreSQL when:
- Need complex relational queries across users/reports/permissions
- Want ACID guarantees for financial transactions (billing)
- Need full-text search across structured metadata
- Scale to multiple services needing shared metadata registry

### Add MinIO/S3 when:
- Reports include large images/charts (>1MB per report)
- Generate and store PDFs (not on-demand generation)
- Need user file uploads (lab results PDFs, medical images)
- Want CDN for fast global file delivery
- Storage costs in MongoDB become expensive (>10GB of files)

### Add RabbitMQ (instead of Redis as broker) when:
- Need complex message routing patterns
- Need guaranteed message delivery with persistence
- Need message priorities and dead-letter queues
- Celery tasks become mission-critical

---

## Benefits of This Stack

✅ Fewer components to manage
✅ Lower infrastructure costs
✅ Faster to deploy and test
✅ Still scalable for early stage
✅ Easy to add PostgreSQL/MinIO later
✅ Python-native (consistent language across stack)
✅ Integrates with existing auth system

## Trade-offs

⚠️ MongoDB stores both data + files (less separation of concerns)
⚠️ No dedicated file storage (but fine for text-based reports)
⚠️ Rate limiting in Redis (not persistent across restarts, but usually fine)
⚠️ Limited to text-based files (JSON, Markdown) until MinIO added

---

## Technology Versions (Recommended)

- Python: 3.11+
- FastAPI: 0.104+
- Redis: 7.0+
- MongoDB: 7.0+
- Celery: 5.3+
- LangChain: 0.1+
- OpenAI SDK: 1.0+
- Motor (async MongoDB): 3.3+
- Pydantic: 2.0+

---

## Next Steps

1. Set up development environment with Docker Compose
2. Implement FastAPI backend with basic endpoints
3. Configure Celery with Redis broker
4. Set up MongoDB collections and indexes
5. Integrate with existing auth system
6. Implement OpenAI + LangChain report generation
7. Add monitoring and logging
8. Deploy to production environment
