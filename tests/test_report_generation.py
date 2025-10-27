"""Test report generation endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_generate_report_missing_categories(client: AsyncClient, sample_patient_data):
    """Test generating report with empty resources_table."""
    data = sample_patient_data.copy()
    data["resources_table"] = []

    response = await client.post("/api/generate-report", json=data, timeout=120.0)
    assert response.status_code == 400
    assert "No categories found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_report_no_kb_content(client: AsyncClient, sample_patient_data):
    """Test generating report when knowledge base is empty."""
    response = await client.post(
        "/api/generate-report",
        json=sample_patient_data,
        timeout=120.0
    )
    # Should fail because KB is not imported yet
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
@pytest.mark.slow
async def test_generate_report_success(client: AsyncClient, sample_patient_data):
    """Test successful report generation (slow test - uses OpenAI)."""
    # First import knowledge base
    import_response = await client.post("/api/knowledge-base/import")
    assert import_response.status_code == 200

    # Generate report
    response = await client.post(
        "/api/generate-report",
        json=sample_patient_data,
        timeout=120.0
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "report_id" in data
    assert "status" in data
    assert data["status"] == "completed"
    assert "report" in data

    # Check report structure
    report = data["report"]
    assert "patient" in report
    assert "labs" in report
    assert "assessment" in report
    assert "category_reports" in report
    assert len(report["category_reports"]) > 0

    # Check category report structure
    category_report = report["category_reports"][0]
    assert "category" in category_report
    assert "text" in category_report
    assert "sources" in category_report

    return data["report_id"]


@pytest.mark.asyncio
async def test_get_report_not_found(client: AsyncClient):
    """Test getting non-existent report."""
    response = await client.get("/api/reports/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.slow
async def test_get_report_success(client: AsyncClient, sample_patient_data):
    """Test retrieving a generated report."""
    # First import KB and generate report
    await client.post("/api/knowledge-base/import")
    gen_response = await client.post(
        "/api/generate-report",
        json=sample_patient_data,
        timeout=120.0
    )
    assert gen_response.status_code == 200
    report_id = gen_response.json()["report_id"]

    # Retrieve the report
    response = await client.get(f"/api/reports/{report_id}")
    assert response.status_code == 200
    data = response.json()

    assert "report_id" in data
    assert data["report_id"] == report_id
    assert "patient" in data
    assert "category_reports" in data


@pytest.mark.asyncio
async def test_get_markdown_not_found(client: AsyncClient):
    """Test getting markdown for non-existent report."""
    response = await client.get("/api/reports/nonexistent-id/markdown")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.slow
async def test_get_markdown_success(client: AsyncClient, sample_patient_data):
    """Test retrieving markdown version of report."""
    # First import KB and generate report
    await client.post("/api/knowledge-base/import")
    gen_response = await client.post(
        "/api/generate-report",
        json=sample_patient_data,
        timeout=120.0
    )
    assert gen_response.status_code == 200
    report_id = gen_response.json()["report_id"]

    # Get markdown version
    response = await client.get(f"/api/reports/{report_id}/markdown")
    assert response.status_code == 200
    data = response.json()

    assert "content" in data
    markdown = data["content"]
    assert len(markdown) > 0
    assert "# Medical Report:" in markdown
    assert "## Patient Information" in markdown
