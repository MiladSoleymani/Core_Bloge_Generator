"""API routes for report generation."""

import time
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.schemas import ReportRequest, GenerateReportResponse, MedicalReport
from app.core.database import get_database
from app.services.knowledge_base import KnowledgeBaseService
from app.services.report_generator import ReportGeneratorService
from app.services.report_storage import ReportStorageService

router = APIRouter()


@router.post("/generate-report", response_model=GenerateReportResponse)
async def generate_report(
    request: ReportRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Generate a medical report with AI-generated category guides.

    This endpoint:
    1. Extracts unique categories from the request's resources_table
    2. Fetches knowledge base content for each category from MongoDB
    3. Uses OpenAI to generate friendly, one-page summaries for each category
    4. Assembles the complete medical report
    5. Saves to MongoDB as JSON and Markdown
    6. Returns the report ID and complete report

    Args:
        request: Report request with patient data, labs, assessment, etc.
        db: MongoDB database instance

    Returns:
        GenerateReportResponse with report_id, status, and complete report
    """
    start_time = time.time()

    try:
        # Initialize services
        kb_service = KnowledgeBaseService(db)
        generator = ReportGeneratorService()
        storage = ReportStorageService(db)

        # Extract unique categories from resources_table
        categories = list(set(resource.category for resource in request.resources_table))

        if not categories:
            raise HTTPException(
                status_code=400,
                detail="No categories found in resources_table. Cannot generate reports.",
            )

        print(f"Generating reports for categories: {categories}")

        # Fetch knowledge base content for each category
        categories_content = {}
        for category in categories:
            content = await kb_service.get_content_for_category(category)
            if content:
                categories_content[category] = content
            else:
                print(f"Warning: No content found for category '{category}'")

        if not categories_content:
            raise HTTPException(
                status_code=404,
                detail="No knowledge base content found for any of the requested categories",
            )

        # Generate category reports using AI
        category_reports = await generator.generate_reports_for_categories(
            categories_content
        )

        # Assemble complete medical report
        report = MedicalReport(
            patient=request.patient,
            labs=request.labs,
            cvd_summary=request.cvd_summary,
            assessment=request.assessment,
            plan=request.plan,
            red_flags=request.red_flags,
            resources_table=request.resources_table,
            category_reports=category_reports,
            disclaimer=request.disclaimer,
        )

        # Generate JSON and Markdown representations
        json_content = report.model_dump_json(indent=2)
        markdown_content = generator.generate_markdown(report)

        # Calculate generation time
        generation_time = time.time() - start_time

        # Save to database (using 'system' as user_id for now)
        report_id = await storage.save_report(
            report=report,
            user_id="system",  # TODO: Replace with actual user_id from auth
            json_content=json_content,
            markdown_content=markdown_content,
            generation_time=generation_time,
            model_used="gpt-4o",
            total_tokens=0,  # TODO: Track actual token usage
            cost_usd=0.0,  # TODO: Calculate actual cost
        )

        print(f"Report generated successfully in {generation_time:.2f}s")

        return GenerateReportResponse(
            report_id=report_id, status="completed", report=report
        )

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get a generated report by ID.

    Args:
        report_id: Report UUID
        db: MongoDB database instance

    Returns:
        Report document including generated files
    """
    storage = ReportStorageService(db)
    report = await storage.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Remove MongoDB _id field for JSON serialization
    if "_id" in report:
        del report["_id"]

    return report


@router.get("/reports/{report_id}/markdown")
async def get_report_markdown(
    report_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get the markdown version of a report.

    Args:
        report_id: Report UUID
        db: MongoDB database instance

    Returns:
        Markdown content as plain text
    """
    storage = ReportStorageService(db)
    report = await storage.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    markdown_content = report.get("generated_files", {}).get("markdown", "")

    if not markdown_content:
        raise HTTPException(status_code=404, detail="Markdown content not found")

    return {"content": markdown_content}


@router.post("/knowledge-base/import")
async def import_knowledge_base(
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Import knowledge base from markdown files to MongoDB.

    This is a utility endpoint to populate the MongoDB knowledge base
    from the markdown files in data/knowledgebase/.

    Args:
        db: MongoDB database instance

    Returns:
        Number of items imported
    """
    kb_service = KnowledgeBaseService(db)

    try:
        count = await kb_service.import_to_database()
        return {"status": "success", "imported_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/categories")
async def get_categories(
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get list of available knowledge base categories.

    Args:
        db: MongoDB database instance

    Returns:
        List of category names
    """
    kb_service = KnowledgeBaseService(db)
    categories = await kb_service.get_unique_categories()
    return {"categories": categories}
