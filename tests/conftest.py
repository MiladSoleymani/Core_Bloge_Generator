"""Pytest configuration and fixtures."""

import pytest
import asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.core.config import get_settings

settings = get_settings()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db():
    """Get database connection for tests."""
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[f"{settings.mongodb_db_name}_test"]
    yield database
    # Cleanup: drop test database after tests
    await client.drop_database(f"{settings.mongodb_db_name}_test")
    client.close()


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "patient": {
            "name": "Test Patient",
            "age": 35,
            "sex": "male"
        },
        "labs": [
            {
                "category": "biochemistry",
                "test_name": "Sodium",
                "value": "140",
                "unit": "mmol/L",
                "reference_range": "135-145",
                "flag": "normal"
            }
        ],
        "cvd_summary": {
            "five_year_risk_percent": 5.0,
            "risk_level": "low",
            "interpretation": "Low risk",
            "modifiable_risk_factors": ["diet"],
            "risk_reduction_advice": ["healthy eating"]
        },
        "assessment": {
            "summary": "Test assessment",
            "family_history": "None",
            "lifestyle": {
                "smoking": "Never smoked",
                "alcohol": "None",
                "diet": "Balanced",
                "physical_activity": "Moderate"
            }
        },
        "plan": [
            {
                "advice": "Continue healthy lifestyle",
                "kb_resource_id": "test_resource"
            }
        ],
        "red_flags": [],
        "resources_table": [
            {
                "category": "healthy_eating",
                "title": "Test Resource",
                "url": "https://example.com"
            }
        ],
        "disclaimer": "Test disclaimer"
    }
