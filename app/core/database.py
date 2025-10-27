"""Database connections and utilities."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class MongoDB:
    """MongoDB connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Connect to MongoDB."""
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_db_name]
        print(f"Connected to MongoDB at {settings.mongodb_url}")

    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    async def create_indexes(self):
        """Create database indexes."""
        if not self.db:
            raise RuntimeError("Database not connected")

        # Knowledge base indexes
        await self.db.knowledge_base.create_index([("category", 1)])
        await self.db.knowledge_base.create_index([("status", 1)])
        await self.db.knowledge_base.create_index([("id", 1)], unique=True)

        # Medical reports indexes
        await self.db.medical_reports.create_index([("user_id", 1), ("created_at", -1)])
        await self.db.medical_reports.create_index([("report_id", 1)], unique=True)
        await self.db.medical_reports.create_index([("status", 1)])

        print("Database indexes created successfully")


# Global database instance
mongodb = MongoDB()


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if not mongodb.db:
        await mongodb.connect()
    return mongodb.db
