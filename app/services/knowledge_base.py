"""Knowledge base management service."""

import json
from pathlib import Path
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.schemas import KnowledgeBaseItem
from app.core.config import get_settings

settings = get_settings()


class KnowledgeBaseService:
    """Service for managing knowledge base content."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize service."""
        self.db = db
        self.kb_collection = db.knowledge_base

    async def load_metadata(self) -> List[KnowledgeBaseItem]:
        """Load knowledge base metadata from JSON file."""
        metadata_path = settings.kb_metadata_path

        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        with open(metadata_path, "r") as f:
            data = json.load(f)

        return [KnowledgeBaseItem(**item) for item in data]

    async def load_markdown_content(self, file_name: str) -> str:
        """Load markdown content from file."""
        file_path = settings.kb_dir / file_name

        if not file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    async def import_to_database(self) -> int:
        """Import knowledge base from files to MongoDB."""
        metadata_items = await self.load_metadata()
        imported_count = 0

        for item in metadata_items:
            # Load markdown content
            content = await self.load_markdown_content(item.file_name)

            # Create document with content
            doc = item.model_dump()
            doc["content"] = content

            # Upsert to database
            await self.kb_collection.update_one(
                {"id": item.id}, {"$set": doc}, upsert=True
            )
            imported_count += 1

        print(f"Imported {imported_count} knowledge base items to database")
        return imported_count

    async def get_by_category(self, category: str, status: str = "draft") -> List[Dict]:
        """Get all knowledge base items for a category."""
        cursor = self.kb_collection.find({"category": category, "status": status})
        items = []

        async for item in cursor:
            items.append(item)

        return items

    async def get_content_for_category(self, category: str) -> str:
        """Get aggregated content for a category."""
        items = await self.get_by_category(category)

        if not items:
            return ""

        content_parts = []
        for item in items:
            content_parts.append(f"# {item['title']}\n\n")
            content_parts.append(f"Source: {item['source_url']}\n\n")
            content_parts.append(f"{item['content']}\n\n")
            content_parts.append("---\n\n")

        return "".join(content_parts)

    async def get_unique_categories(self) -> List[str]:
        """Get list of unique categories in knowledge base."""
        categories = await self.kb_collection.distinct("category", {"status": "draft"})
        return categories

    async def get_by_id(self, kb_id: str) -> Dict | None:
        """Get knowledge base item by ID."""
        return await self.kb_collection.find_one({"id": kb_id})
