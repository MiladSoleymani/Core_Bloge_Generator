"""Report storage service for MongoDB."""

import uuid
from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.schemas import MedicalReport


class ReportStorageService:
    """Service for storing and retrieving medical reports."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize service."""
        self.db = db
        self.reports_collection = db.medical_reports

    async def save_report(
        self,
        report: MedicalReport,
        user_id: str,
        json_content: str,
        markdown_content: str,
        generation_time: float,
        model_used: str,
        total_tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> str:
        """Save a medical report to MongoDB.

        Args:
            report: Complete medical report
            user_id: User ID who generated the report
            json_content: JSON string representation
            markdown_content: Markdown representation
            generation_time: Time taken to generate in seconds
            model_used: AI model name used
            total_tokens: Total tokens used
            cost_usd: Estimated cost in USD

        Returns:
            Report ID (UUID)
        """
        report_id = str(uuid.uuid4())

        # Create document
        doc = report.model_dump()
        doc["report_id"] = report_id
        doc["user_id"] = user_id
        doc["created_at"] = datetime.utcnow()
        doc["status"] = "completed"

        # Add generated files
        doc["generated_files"] = {
            "json": json_content,
            "markdown": markdown_content,
            "pdf": None,  # Generated on-demand
        }

        # Add metadata
        doc["generation_time_seconds"] = generation_time
        doc["model_used"] = model_used
        doc["total_tokens"] = total_tokens
        doc["cost_usd"] = cost_usd

        # Insert to database
        await self.reports_collection.insert_one(doc)

        print(f"Saved report with ID: {report_id}")
        return report_id

    async def get_report(self, report_id: str) -> Optional[dict]:
        """Get a report by ID.

        Args:
            report_id: Report UUID

        Returns:
            Report document or None if not found
        """
        return await self.reports_collection.find_one({"report_id": report_id})

    async def get_user_reports(
        self, user_id: str, limit: int = 10, skip: int = 0
    ) -> list:
        """Get reports for a user.

        Args:
            user_id: User ID
            limit: Max number of reports to return
            skip: Number of reports to skip

        Returns:
            List of report documents
        """
        cursor = (
            self.reports_collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
            .skip(skip)
        )

        reports = []
        async for report in cursor:
            reports.append(report)

        return reports

    async def delete_report(self, report_id: str) -> bool:
        """Delete a report.

        Args:
            report_id: Report UUID

        Returns:
            True if deleted, False if not found
        """
        result = await self.reports_collection.delete_one({"report_id": report_id})
        return result.deleted_count > 0
