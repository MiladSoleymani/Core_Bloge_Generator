# Test Suite

Comprehensive test suite for the Medical Report Generator API using pytest.

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Code coverage reports

### Prerequisites

- MongoDB running (for integration tests)
- OpenAI API key in `.env` (for slow tests that call OpenAI)

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Test health endpoints only
pytest tests/test_health.py

# Test knowledge base
pytest tests/test_knowledge_base.py

# Test models
pytest tests/test_models.py
```

### Run Specific Tests

```bash
# Run a single test function
pytest tests/test_health.py::test_health_check

# Run tests matching a pattern
pytest -k "health"
```

### Run Tests by Marker

```bash
# Run only fast tests (exclude slow tests)
pytest -m "not slow"

# Run only slow tests (that call OpenAI)
pytest -m slow

# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Run with Verbose Output

```bash
# Show more details
pytest -v

# Show print statements
pytest -s

# Show local variables on failure
pytest -l
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── test_health.py              # Health check tests (fast)
├── test_knowledge_base.py      # KB import/retrieval tests
├── test_models.py              # Pydantic model tests (unit)
└── test_report_generation.py  # Report generation tests (slow)
```

## Test Categories

### Unit Tests (`test_models.py`)
- ✅ Fast (< 1 second)
- ✅ No external dependencies
- Tests Pydantic models validation

```bash
pytest tests/test_models.py
```

### Fast Integration Tests
- ✅ Quick (< 5 seconds)
- Tests API endpoints without AI calls

```bash
pytest tests/test_health.py tests/test_knowledge_base.py
```

### Slow Tests (marked with `@pytest.mark.slow`)
- ⏱️ Slow (30-60 seconds)
- Calls OpenAI API
- Tests full report generation

```bash
pytest -m slow
```

## Fixtures

Available fixtures (defined in `conftest.py`):

### `client`
Async HTTP client for testing API endpoints.

```python
@pytest.mark.asyncio
async def test_example(client):
    response = await client.get("/health")
    assert response.status_code == 200
```

### `db`
MongoDB test database connection. Automatically cleaned up after tests.

```python
@pytest.mark.asyncio
async def test_example(db):
    await db.collection.insert_one({"test": "data"})
```

### `sample_patient_data`
Pre-configured sample patient data for testing report generation.

```python
def test_example(sample_patient_data):
    assert "patient" in sample_patient_data
```

## Writing New Tests

### Basic Test Structure

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_my_endpoint(client: AsyncClient):
    """Test description."""
    response = await client.get("/my-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### Mark Slow Tests

If your test calls OpenAI or takes > 30 seconds:

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_slow_operation(client):
    """This test takes a long time."""
    response = await client.post("/slow-endpoint", timeout=120.0)
    assert response.status_code == 200
```

### Test with Sample Data

```python
@pytest.mark.asyncio
async def test_with_data(client, sample_patient_data):
    """Test with fixture data."""
    response = await client.post("/api/generate-report", json=sample_patient_data)
    assert response.status_code == 200
```

## Test Markers

Custom markers defined in `pytest.ini`:

- `@pytest.mark.slow` - Tests taking > 30 seconds
- `@pytest.mark.integration` - Tests requiring external services
- `@pytest.mark.unit` - Pure unit tests

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mongodb:
        image: mongo:7
        ports:
          - 27017:27017

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run fast tests
        run: pytest -m "not slow"

      - name: Run coverage
        run: pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests Fail to Connect to MongoDB

```bash
# Make sure MongoDB is running
docker ps

# Or start it
docker run -d -p 27017:27017 --name mongodb mongo:7
```

### Async Tests Not Running

Make sure `pytest-asyncio` is installed:
```bash
pip install pytest-asyncio
```

### OpenAI API Errors in Slow Tests

Check your `.env` file has valid `OPENAI_API_KEY`:
```bash
cat .env | grep OPENAI_API_KEY
```

### Import Errors

Run tests from project root:
```bash
# Good
pytest

# Bad
cd tests && pytest  # Won't find app module
```

## Best Practices

1. **Run fast tests frequently**
   ```bash
   pytest -m "not slow"
   ```

2. **Run slow tests before commits**
   ```bash
   pytest -m slow
   ```

3. **Check coverage regularly**
   ```bash
   pytest --cov=app
   ```

4. **Use descriptive test names**
   - Good: `test_generate_report_with_missing_categories`
   - Bad: `test_report1`

5. **One assertion concept per test**
   - Each test should test one thing
   - Makes failures easier to diagnose

6. **Use fixtures for common setup**
   - Don't repeat setup code
   - Add new fixtures to `conftest.py`

## Coverage Goals

Target coverage: **80%+**

Check current coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

## Quick Reference

```bash
# Most common commands
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest -m "not slow"               # Fast tests only
pytest --cov=app                   # With coverage
pytest tests/test_health.py        # Single file
pytest -k "health"                 # Match pattern
pytest --lf                        # Last failed
pytest --maxfail=1                 # Stop after first failure
```
