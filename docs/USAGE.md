# Quick Usage Guide

## Getting Started (5 Minutes)

### 1. Setup Environment

```bash
# Activate virtual environment
source env/bin/activate

# Ensure MongoDB is running
docker ps | grep mongodb
# If not running:
docker start mongodb
# Or create new:
docker run -d --name mongodb -p 27017:27017 mongo:7.0
```

### 2. Start the Application

```bash
# Start FastAPI server
python -m app.main

# Server will start at: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### 3. Import Knowledge Base

```bash
# Using curl
curl -X POST http://localhost:8000/api/knowledge-base/import

# Or visit: http://localhost:8000/docs and click "Try it out"
```

## Basic API Usage

### Generate a Medical Report

```bash
curl -X POST http://localhost:8000/api/generate-report \
  -H "Content-Type: application/json" \
  -d @data/sample_reports/Kushagra\ mandwal.json
```

### Get Available Categories

```bash
curl http://localhost:8000/api/knowledge-base/categories
```

### Retrieve a Report

```bash
# Get JSON report
curl http://localhost:8000/api/reports/{report_id}

# Get Markdown version
curl http://localhost:8000/api/reports/{report_id}/markdown
```

## Testing

```bash
# Run all fast tests (recommended during development)
pytest -m "not slow"

# Run all tests including OpenAI API calls
pytest

# Run specific test file
pytest tests/test_health.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app
```

## Common Commands

```bash
# Check API health
curl http://localhost:8000/health

# View MongoDB data
docker exec -it mongodb mongosh
> use blog_generator
> db.medical_reports.find().pretty()
> db.knowledge_base.find().pretty()

# Stop/Start services
docker stop mongodb
docker start mongodb

# View application logs
python -m app.main  # Logs appear in console
```

## Development Mode

```bash
# Run with auto-reload on code changes
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive interfaces to:
- Test all API endpoints
- View request/response schemas
- See example data
- Execute API calls directly from the browser

## Project Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check API health status |
| `/api/knowledge-base/import` | POST | Import knowledge base from files |
| `/api/knowledge-base/categories` | GET | Get available categories |
| `/api/generate-report` | POST | Generate medical report |
| `/api/reports/{report_id}` | GET | Get report by ID (JSON) |
| `/api/reports/{report_id}/markdown` | GET | Get report in Markdown format |

## Configuration

All configuration is in `.env` file:

```bash
# Required
OPENAI_API_KEY=your-key-here

# Optional (defaults shown)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=blog_generator
API_PORT=8000
```

## Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# Check MongoDB logs
docker logs mongodb

# Restart MongoDB
docker restart mongodb
```

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Import Errors
```bash
# Ensure virtual environment is activated
source env/bin/activate

# Verify installation
pip list | grep fastapi
pip list | grep motor
```

## Next Steps

1. **Explore Sample Data**: Check `data/sample_reports/` for example patient data
2. **Read API Docs**: Full API documentation at http://localhost:8000/docs
3. **View Knowledge Base**: See `data/knowledgebase/` for health information sources
4. **Run Tests**: Ensure everything works with `pytest -m "not slow"`

## Quick Reference

```bash
# Complete workflow
source env/bin/activate
docker start mongodb
python -m app.main
# Visit: http://localhost:8000/docs
```

For detailed documentation, see:
- **README.md** - Full project overview
- **docs/TESTING_GUIDE.md** - Comprehensive testing guide
- **docs/architecture-stack.md** - Technical architecture
- **docs/implementation-guide.md** - Implementation details
