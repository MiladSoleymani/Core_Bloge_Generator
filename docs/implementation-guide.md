# Implementation Guide - Step 1

## Overview

This is the first implementation step of the Medical Report Generator system. It includes:

- FastAPI backend with RESTful API endpoints
- MongoDB integration for knowledge base and report storage
- OpenAI + LangChain for AI-powered report generation
- Knowledge base loader from markdown files
- Report generation and storage in JSON/Markdown formats

## Project Structure

```
Core_Bloge_Generator/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration settings
│   │   └── database.py            # MongoDB connection
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── knowledge_base.py      # Knowledge base loader
│   │   ├── report_generator.py    # AI report generation
│   │   └── report_storage.py      # Report storage service
│   └── utils/
│       └── __init__.py
├── data/
│   ├── knowledgebase/             # Markdown knowledge base files
│   │   ├── metadata.json
│   │   └── *.md files
│   └── sample_reports/            # Sample patient data
│       └── Kushagra mandwal.json
├── docs/
│   ├── architecture-stack.md      # Architecture documentation
│   └── implementation-guide.md    # This file
├── .env                           # Environment variables (not in git)
├── .env.example                   # Environment template
├── .gitignore
├── requirements.txt               # Python dependencies
└── README.md

```

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- MongoDB (running locally or remotely)
- Redis (optional for now, needed for Celery later)
- OpenAI API Key

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=your-actual-openai-api-key-here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=blog_generator
```

### 4. Start MongoDB

Make sure MongoDB is running:

```bash
# Using Homebrew on macOS:
brew services start mongodb-community

# Or using Docker:
docker run -d -p 27017:27017 --name mongodb mongo:7
```

### 5. Start the Application

```bash
# From project root
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### 1. Health Check
```
GET /health
```

### 2. Import Knowledge Base
```
POST /api/knowledge-base/import
```

Import markdown files from `data/knowledgebase/` into MongoDB.

**Response:**
```json
{
  "status": "success",
  "imported_count": 14
}
```

### 3. Get Available Categories
```
GET /api/knowledge-base/categories
```

Get list of available knowledge base categories.

**Response:**
```json
{
  "categories": [
    "healthy_eating",
    "weight_management",
    "blood_pressure",
    "alcohol",
    "first_nations"
  ]
}
```

### 4. Generate Report
```
POST /api/generate-report
```

Generate a complete medical report with AI-generated category guides.

**Request Body:**
```json
{
  "patient": {
    "name": "John Doe",
    "age": 33,
    "sex": "male"
  },
  "labs": [...],
  "cvd_summary": {...},
  "assessment": {...},
  "plan": [...],
  "red_flags": [...],
  "resources_table": [
    {
      "category": "healthy_eating",
      "title": "...",
      "url": "..."
    },
    {
      "category": "weight_management",
      "title": "...",
      "url": "..."
    }
  ],
  "disclaimer": "..."
}
```

**Response:**
```json
{
  "report_id": "uuid-here",
  "status": "completed",
  "report": {
    "patient": {...},
    "labs": [...],
    "category_reports": [
      {
        "category": "healthy_eating",
        "text": "Generated report with inline links...",
        "sources": ["https://..."]
      }
    ],
    ...
  }
}
```

### 5. Get Report by ID
```
GET /api/reports/{report_id}
```

Retrieve a previously generated report.

### 6. Get Report Markdown
```
GET /api/reports/{report_id}/markdown
```

Get the markdown version of a report.

**Response:**
```json
{
  "content": "# Medical Report: John Doe\n\n..."
}
```

## Testing the System

### Step 1: Import Knowledge Base

```bash
curl -X POST http://localhost:8000/api/knowledge-base/import
```

### Step 2: Generate a Report

```bash
curl -X POST http://localhost:8000/api/generate-report \
  -H "Content-Type: application/json" \
  -d @data/sample_reports/Kushagra\ mandwal.json
```

Or use the interactive API docs at http://localhost:8000/docs

### Step 3: Retrieve the Report

```bash
curl http://localhost:8000/api/reports/{report_id}
```

## Key Features Implemented

### 1. Knowledge Base Management
- **File-based storage**: Markdown files with metadata.json
- **MongoDB sync**: Import KB content to database
- **Category-based retrieval**: Get all content for a category

### 2. AI Report Generation
- **OpenAI GPT-4o integration**: High-quality content generation
- **LangChain framework**: Structured prompts and output parsing
- **Pydantic validation**: Type-safe data handling
- **Inline source links**: Markdown-formatted citations

### 3. Report Storage
- **MongoDB storage**: Flexible document database
- **Multiple formats**: JSON, Markdown (PDF on-demand later)
- **Metadata tracking**: Generation time, tokens, cost
- **User association**: Reports linked to user IDs

### 4. RESTful API
- **FastAPI framework**: Modern, fast, auto-docs
- **Async/await**: Non-blocking database operations
- **Type validation**: Request/response models
- **Error handling**: Proper HTTP status codes

## What's Next (Future Enhancements)

### Step 2: Authentication & Authorization
- Integrate with existing auth system
- API key validation
- User-specific rate limiting

### Step 3: Redis Integration
- Session caching
- Rate limiting
- Request queue

### Step 4: Celery Integration
- Async report generation
- Background task processing
- Job status tracking
- Progress updates

### Step 5: Additional Features
- PDF generation
- File uploads (lab results)
- MinIO/S3 integration
- Email notifications
- Report templates
- Batch processing

## Troubleshooting

### MongoDB Connection Error
```
Error: Could not connect to MongoDB
```
**Solution:** Make sure MongoDB is running on port 27017

### OpenAI API Error
```
Error: Invalid API key
```
**Solution:** Check your `.env` file has correct OPENAI_API_KEY

### Import Error
```
ModuleNotFoundError: No module named 'app'
```
**Solution:** Run from project root, not from app/ directory

### Knowledge Base Not Found
```
Error: No knowledge base content found
```
**Solution:** Run the import endpoint first: `POST /api/knowledge-base/import`

## Development Tips

### Run in Development Mode
```bash
# Auto-reload on code changes
uvicorn app.main:app --reload
```

### Check MongoDB Data
```bash
# Connect to MongoDB
mongosh

# Switch to database
use blog_generator

# Show collections
show collections

# Query knowledge base
db.knowledge_base.find().pretty()

# Query reports
db.medical_reports.find().pretty()
```

### View Logs
The application prints logs to console. Key log messages:
- "Connected to MongoDB..."
- "Imported N knowledge base items..."
- "Generating reports for categories: [...]"
- "Report generated successfully in X.XXs"

## Performance Notes

- **First request**: May be slower due to model initialization
- **Subsequent requests**: Faster with cached connections
- **Report generation time**: Typically 30-60 seconds depending on categories
- **Knowledge base import**: One-time operation, ~1-2 seconds

## Security Considerations

⚠️ **For Production:**
- Add API authentication
- Configure CORS properly
- Use environment-specific configs
- Enable HTTPS
- Add rate limiting
- Validate user permissions
- Sanitize inputs
- Add request logging
- Use secrets management

## Support

For issues or questions:
1. Check the logs
2. Review the architecture documentation
3. Test with the interactive API docs at `/docs`
4. Verify MongoDB and OpenAI connectivity
