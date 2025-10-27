# Medical Report Generator

AI-powered medical report generation system with personalized health guides.

## Overview

This system generates comprehensive medical reports by combining patient data, lab results, and assessments with AI-generated health information guides. It uses OpenAI GPT-4o to create personalized, friendly summaries from a curated knowledge base of verified health resources.

## Features

- 🤖 **AI-Powered Reports**: Generate personalized health guides using OpenAI GPT-4o
- 📚 **Knowledge Base**: Curated health information from verified sources
- 📊 **Comprehensive Reports**: Include patient data, labs, CVD risk, assessments, and plans
- 📝 **Multiple Formats**: Generate reports in JSON and Markdown formats
- 🔗 **Source Citations**: All recommendations include inline links to verified sources
- 🗄️ **MongoDB Storage**: Flexible document storage for reports and knowledge base
- ⚡ **FastAPI Backend**: Modern, fast, async API with automatic documentation

## Quick Start

### 1. Prerequisites

- Python 3.11+
- MongoDB (local or remote)
- OpenAI API Key

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
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

### 3. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7

# Or using Homebrew (macOS)
brew services start mongodb-community
```

### 4. Run the Application

```bash
# Start the FastAPI server
python -m app.main

# The API will be available at:
# - http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### 5. Test the System

```bash
# Run the test script
python test_api.py

# Or use the interactive API docs at http://localhost:8000/docs
```

## Project Structure

```
Core_Bloge_Generator/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── core/              # Configuration and database
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic
│   └── utils/             # Helper functions
├── data/
│   ├── knowledgebase/     # Health information markdown files
│   └── sample_reports/    # Sample patient data
├── docs/                   # Documentation
│   ├── architecture-stack.md
│   └── implementation-guide.md
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── test_api.py           # API test script
└── README.md             # This file
```

## API Endpoints

### Health Check
```
GET /health
```

### Import Knowledge Base
```
POST /api/knowledge-base/import
```

### Get Categories
```
GET /api/knowledge-base/categories
```

### Generate Report
```
POST /api/generate-report
Content-Type: application/json

{
  "patient": {...},
  "labs": [...],
  "assessment": {...},
  "resources_table": [...]
}
```

### Get Report
```
GET /api/reports/{report_id}
```

### Get Report Markdown
```
GET /api/reports/{report_id}/markdown
```

## Documentation

- **[Architecture & Stack](docs/architecture-stack.md)** - Detailed technology stack explanation
- **[Implementation Guide](docs/implementation-guide.md)** - Setup and usage instructions
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (when server is running)

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB (with Motor async driver)
- **AI**: OpenAI GPT-4o + LangChain
- **Validation**: Pydantic v2
- **Cache**: Redis (future)
- **Queue**: Celery (future)

## Example Usage

```python
import requests

# 1. Import knowledge base
response = requests.post("http://localhost:8000/api/knowledge-base/import")

# 2. Generate report
with open("data/sample_reports/Kushagra mandwal.json") as f:
    patient_data = f.read()

response = requests.post(
    "http://localhost:8000/api/generate-report",
    headers={"Content-Type": "application/json"},
    data=patient_data
)

report = response.json()
print(f"Report ID: {report['report_id']}")

# 3. Retrieve markdown
response = requests.get(
    f"http://localhost:8000/api/reports/{report['report_id']}/markdown"
)
markdown = response.json()["content"]
print(markdown)
```

## Knowledge Base

The system includes verified health information from:

- **Healthy Eating**: Australian Guide to Healthy Eating, Heart Foundation resources
- **Weight Management**: Better Health Victoria, RACGP guidelines
- **Blood Pressure**: Heart Foundation, Stroke Foundation
- **Alcohol**: NHMRC guidelines, support services
- **First Nations Health**: Aboriginal-specific health resources

All resources are stored as markdown files in `data/knowledgebase/` with metadata.

## Development

### Run in Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Check MongoDB Data
```bash
mongosh
use blog_generator
db.medical_reports.find().pretty()
```

### Run Tests
```bash
python test_api.py
```

## Roadmap

### Current (Step 1) ✅
- FastAPI backend
- MongoDB integration
- OpenAI report generation
- Knowledge base management
- Basic API endpoints

### Next Steps
- [ ] Authentication & authorization integration
- [ ] Redis caching and rate limiting
- [ ] Celery async task processing
- [ ] PDF generation
- [ ] File upload support (lab results)
- [ ] MinIO/S3 integration
- [ ] Email notifications
- [ ] Batch processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Support

For issues or questions, please check:
1. The [Implementation Guide](docs/implementation-guide.md)
2. The [Architecture Documentation](docs/architecture-stack.md)
3. The interactive API docs at `/docs`

## Acknowledgments

- OpenAI for GPT-4o API
- FastAPI framework
- MongoDB and Motor driver
- LangChain framework
- All health information sources cited in the knowledge base
