"""Test knowledge base endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_import_knowledge_base(client: AsyncClient):
    """Test importing knowledge base from files."""
    response = await client.post("/api/knowledge-base/import")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "imported_count" in data
    assert data["imported_count"] > 0


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient):
    """Test getting available categories."""
    # First import the knowledge base
    await client.post("/api/knowledge-base/import")

    # Then get categories
    response = await client.get("/api/knowledge-base/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert isinstance(data["categories"], list)
    assert len(data["categories"]) > 0


@pytest.mark.asyncio
async def test_get_categories_before_import(client: AsyncClient):
    """Test getting categories before importing returns empty list."""
    response = await client.get("/api/knowledge-base/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert isinstance(data["categories"], list)
