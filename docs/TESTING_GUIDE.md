# Testing Guide - Quick Start

## 🚀 Setup (First Time Only)

### 1. Install Test Dependencies

```bash
pip install -r requirements.txt
```

This installs pytest and related packages:
- `pytest` - Testing framework
- `pytest-asyncio` - For async tests
- `pytest-cov` - Code coverage reports

### 2. Make Sure Services are Running

```bash
# Start MongoDB
docker run -d --name mongodb \        
-p 27017:27017 \
-v /Users/miladsoleymani/Documents/work_space/MFM/Core_Bloge_Generator/mongodb-data:/data/db \
mongo:7.0

# Add OpenAI API key to .env (for slow tests)
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

---

## ✅ Running Tests

### Quick Test (Recommended to Start)

Run only fast tests (skip slow OpenAI tests):

```bash
pytest -m "not slow"
```

**Output:**
```
tests/test_health.py ✓✓                           2 passed
tests/test_knowledge_base.py ✓✓✓                 3 passed
tests/test_models.py ✓✓✓✓✓✓✓✓✓                   9 passed

============ 14 passed in 2.34s ============
```

---

### Run All Tests (Including Slow)

Run everything including OpenAI tests (30-60 seconds):

```bash
pytest
```

**Output:**
```
tests/test_health.py ✓✓                           2 passed
tests/test_knowledge_base.py ✓✓✓                 3 passed
tests/test_models.py ✓✓✓✓✓✓✓✓✓                   9 passed
tests/test_report_generation.py ✓✓✓✓✓✓           6 passed

============ 20 passed in 45.67s ============
```

---

### Run Specific Tests

```bash
# Test just health endpoints
pytest tests/test_health.py -v

# Test just models (unit tests)
pytest tests/test_models.py -v

# Test knowledge base functionality
pytest tests/test_knowledge_base.py -v

# Test a specific function
pytest tests/test_health.py::test_health_check -v
```

---

### Run with Verbose Output

```bash
# Show more details about each test
pytest -v

# Show print statements during tests
pytest -s

# Show both
pytest -v -s
```

---

### Run with Coverage Report

```bash
# Show coverage percentage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open the report in browser
open htmlcov/index.html
```

**Example Output:**
```
---------- coverage: platform darwin, python 3.11.5 -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/__init__.py                       1      0   100%
app/api/routes.py                    87     12    86%
app/core/config.py                   25      0   100%
app/core/database.py                 32      5    84%
app/models/schemas.py                45      0   100%
app/services/knowledge_base.py       58      8    86%
app/services/report_generator.py     78     15    81%
app/services/report_storage.py       45      7    84%
-----------------------------------------------------
TOTAL                               371     47    87%
```

---

## 📊 Understanding Test Results

### ✅ Passing Test
```
tests/test_health.py::test_health_check PASSED
```
Test ran successfully!

### ❌ Failing Test
```
tests/test_health.py::test_health_check FAILED
```
Test failed - see error details below

### ⊘ Skipped Test
```
tests/test_health.py::test_health_check SKIPPED
```
Test was skipped (usually marked with @pytest.mark.skip)

---

## 🏷️ Test Markers

Tests are organized with markers:

### Run Fast Tests Only
```bash
pytest -m "not slow"
```
Skips tests that call OpenAI (30-60 seconds each)

### Run Only Slow Tests
```bash
pytest -m slow
```
Only runs tests that call OpenAI API

### Run Unit Tests
```bash
pytest -m unit
```
Only pure unit tests (no external dependencies)

### Run Integration Tests
```bash
pytest -m integration
```
Tests that need MongoDB/external services

---

## 📁 Test Files Overview

### `test_health.py` - Health Checks (⚡ Fast)
```bash
pytest tests/test_health.py
```
- ✅ `/health` endpoint
- ✅ Root `/` endpoint

**Time:** < 1 second

---

### `test_models.py` - Model Validation (⚡ Fast)
```bash
pytest tests/test_models.py
```
- ✅ Patient model validation
- ✅ Lab result validation
- ✅ Assessment model
- ✅ Report model with nested objects

**Time:** < 1 second

---

### `test_knowledge_base.py` - KB Operations (⚡ Fast)
```bash
pytest tests/test_knowledge_base.py
```
- ✅ Import KB from markdown files
- ✅ Get available categories
- ✅ Retrieve KB content

**Time:** 1-2 seconds

---

### `test_report_generation.py` - Full Reports (🐢 Slow)
```bash
pytest tests/test_report_generation.py
```
- ✅ Generate complete report with OpenAI
- ✅ Retrieve report by ID
- ✅ Get markdown version
- ✅ Error handling (missing data, etc.)

**Time:** 30-60 seconds (calls OpenAI)

---

## 🎯 Common Testing Workflows

### During Development (Every Few Minutes)
```bash
# Run fast tests only
pytest -m "not slow"
```

### Before Committing Code
```bash
# Run all tests + coverage
pytest --cov=app
```

### Before Pull Request
```bash
# Run everything with verbose output
pytest -v --cov=app --cov-report=html
```

### Debugging a Failing Test
```bash
# Run one test with print statements
pytest tests/test_health.py::test_health_check -s -v

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```
pymongo.errors.ServerSelectionTimeoutError
```

**Fix:**
```bash
# Check if MongoDB is running
docker ps | grep mongo

# Start MongoDB if not running
docker run -d -p 27017:27017 --name mongodb mongo:7
```

---

### OpenAI API Error in Slow Tests
```
openai.error.AuthenticationError: Invalid API key
```

**Fix:**
```bash
# Add your API key to .env
echo "OPENAI_API_KEY=sk-your-actual-key" >> .env

# Verify it's set
cat .env | grep OPENAI_API_KEY
```

---

### Import Errors
```
ModuleNotFoundError: No module named 'app'
```

**Fix:**
```bash
# Make sure you're in project root
pwd  # Should end with: Core_Bloge_Generator

# Run tests from project root
pytest

# NOT from inside tests/ directory
```

---

### No Tests Found
```
collected 0 items
```

**Fix:**
```bash
# Make sure pytest can find tests
pytest --collect-only

# Check pytest.ini configuration
cat pytest.ini
```

---

## 📈 CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

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
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run fast tests
        run: pytest -m "not slow" --cov=app

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 💡 Tips & Best Practices

### 1. Run Fast Tests Frequently
```bash
# During development, run this often
pytest -m "not slow"
```

### 2. Check Coverage Regularly
```bash
# Aim for 80%+ coverage
pytest --cov=app --cov-report=term-missing
```

### 3. Use Pytest Watch for Auto-Testing
```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run tests on file changes
ptw -- -m "not slow"
```

### 4. Debug with ipdb
```bash
# Install ipdb
pip install ipdb

# Add breakpoint in test
import ipdb; ipdb.set_trace()

# Run test
pytest tests/test_health.py -s
```

### 5. Parallel Testing (Faster)
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto  # Uses all CPU cores
```

---

## 📚 More Information

- **Full Test Documentation:** `tests/README.md`
- **Pytest Docs:** https://docs.pytest.org/
- **Pytest-asyncio:** https://pytest-asyncio.readthedocs.io/

---

## ✨ Quick Reference

```bash
# Most common commands
pytest                      # Run all tests
pytest -m "not slow"       # Fast tests only
pytest -v                  # Verbose output
pytest -s                  # Show print statements
pytest --cov=app          # With coverage
pytest -x                  # Stop on first failure
pytest -k "health"        # Run tests matching pattern
pytest tests/test_health.py  # Run specific file
pytest --lf               # Run last failed tests
pytest --maxfail=2        # Stop after 2 failures
```

---

## 🎉 You're Ready!

Start with:
```bash
pytest -m "not slow"
```

This will run all fast tests and show you everything is working! 🚀
