"""Main worker application for processing report generation requests."""

import asyncio
import logging
import uuid
import time
from datetime import datetime
from typing import Optional

from app.core.config import get_settings
from app.core.database import mongodb
from app.services.rabbitmq_service import rabbitmq_service
from app.services.redis_service import redis_service
from app.services.knowledge_base import KnowledgeBaseService
from app.services.report_generator import ReportGeneratorService
from app.models.schemas import (
    ReportGenerationRequest,
    ReportGenerationResponse,
    MedicalReport,
    StoredUser,
    StoredReport,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


class ReportWorker:
    """Worker for processing report generation requests."""

    def __init__(self):
        """Initialize worker."""
        self.kb_service: Optional[KnowledgeBaseService] = None
        self.report_generator: Optional[ReportGeneratorService] = None

    async def startup(self):
        """Initialize all services."""
        try:
            logger.info("Starting up worker services...")

            # Connect to MongoDB
            await mongodb.connect()
            await mongodb.create_indexes()

            # Connect to RabbitMQ
            await rabbitmq_service.connect()

            # Connect to Redis
            await redis_service.connect()

            # Initialize knowledge base service
            self.kb_service = KnowledgeBaseService(mongodb.db)

            # Initialize report generator
            self.report_generator = ReportGeneratorService()

            logger.info("All worker services started successfully")
        except Exception as e:
            logger.error(f"Failed to start worker services: {e}")
            raise

    async def shutdown(self):
        """Cleanup all services."""
        try:
            logger.info("Shutting down worker services...")

            await rabbitmq_service.disconnect()
            await redis_service.disconnect()
            await mongodb.disconnect()

            logger.info("All worker services shut down successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def process_request(self, message_body: dict, message):
        """
        Process a report generation request.

        Args:
            message_body: The parsed message body
            message: The raw message object
        """
        request_id = message_body.get("request_id", "unknown")
        user_id = message_body.get("user_id", "unknown")
        start_time = time.time()

        try:
            logger.info(f"Processing request {request_id} for user {user_id}")

            # Parse request
            request = ReportGenerationRequest(**message_body)

            # Check Redis cache for previous input
            cached_input = await redis_service.get_cached_input(user_id)
            if cached_input:
                logger.info(f"Found cached input for user {user_id}")

            # Cache current input
            await redis_service.cache_input(user_id, message_body)

            # Ensure user exists in database
            await self._ensure_user_exists(user_id)

            # Generate report
            report_id = str(uuid.uuid4())
            report = await self._generate_report(request, report_id)

            # Calculate generation metrics
            generation_time = time.time() - start_time

            # Store report in MongoDB
            await self._store_report(
                report_id=report_id,
                user_id=user_id,
                report=report,
                generation_time=generation_time
            )

            # Cache report in Redis
            await redis_service.cache_report(report_id, report.model_dump())

            # Send success response
            response = ReportGenerationResponse(
                request_id=request_id,
                user_id=user_id,
                report_id=report_id,
                status="success"
            )

            await rabbitmq_service.publish_response(response.model_dump(mode='json'))

            logger.info(
                f"Successfully processed request {request_id} in {generation_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}", exc_info=True)

            # Send failure response
            response = ReportGenerationResponse(
                request_id=request_id,
                user_id=user_id,
                report_id="",
                status="failed",
                error_message=str(e)
            )

            await rabbitmq_service.publish_response(response.model_dump(mode='json'))

    async def _ensure_user_exists(self, user_id: str):
        """
        Ensure user exists in database.

        Args:
            user_id: User identifier
        """
        users_collection = mongodb.db.users

        existing_user = await users_collection.find_one({"user_id": user_id})

        if not existing_user:
            user = StoredUser(user_id=user_id)
            await users_collection.insert_one(user.model_dump())
            logger.info(f"Created new user: {user_id}")
        else:
            # Update last access time
            await users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"updated_at": datetime.utcnow()}}
            )

    async def _generate_report(
        self,
        request: ReportGenerationRequest,
        report_id: str
    ) -> MedicalReport:
        """
        Generate medical report.

        Args:
            request: Report generation request
            report_id: Report identifier

        Returns:
            Generated medical report
        """
        # Extract unique categories
        categories = list(set(resource.category for resource in request.resources_table))
        logger.info(f"Generating report for categories: {categories}")

        # Create medical report structure
        report_data = {
            "patient": request.patient.model_dump(),
            "labs": [lab.model_dump() for lab in request.labs],
            "cvd_summary": request.cvd_summary.model_dump() if request.cvd_summary else None,
            "assessment": request.assessment.model_dump(),
            "plan": [item.model_dump() for item in request.plan],
            "red_flags": [flag.model_dump() for flag in request.red_flags],
            "resources_table": [resource.model_dump() for resource in request.resources_table],
            "disclaimer": request.disclaimer,
        }

        # Get knowledge base content for each category
        categories_content = {}
        for category in categories:
            content = await self.kb_service.get_content_for_category(category)
            if content:
                categories_content[category] = content

        # Generate category reports using AI
        category_reports = await self.report_generator.generate_reports_for_categories(categories_content)

        report_data["category_reports"] = [
            report.model_dump() for report in category_reports
        ]

        return MedicalReport(**report_data)

    async def _store_report(
        self,
        report_id: str,
        user_id: str,
        report: MedicalReport,
        generation_time: float
    ):
        """
        Store report in MongoDB.

        Args:
            report_id: Report identifier
            user_id: User identifier
            report: Medical report
            generation_time: Time taken to generate report
        """
        reports_collection = mongodb.db.medical_reports

        stored_report = StoredReport(
            report_id=report_id,
            user_id=user_id,
            report_data=report,
            json_content=report.model_dump(),
            generation_time_seconds=generation_time
        )

        await reports_collection.insert_one(stored_report.model_dump())
        logger.info(f"Stored report {report_id} for user {user_id}")

    async def run(self):
        """Run the worker."""
        logger.info("Worker starting...")

        try:
            await self.startup()

            # Start consuming messages
            await rabbitmq_service.consume_messages(self.process_request)

        except KeyboardInterrupt:
            logger.info("Worker interrupted by user")
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
        finally:
            await self.shutdown()


async def main():
    """Main entry point."""
    worker = ReportWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
