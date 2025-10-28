"""Setup script for initializing the worker environment."""

import asyncio
import sys
from pathlib import Path

from app.core.database import mongodb
from app.services.knowledge_base import KnowledgeBaseService


async def import_knowledge_base():
    """Import knowledge base from markdown files."""
    print("Importing knowledge base...")

    try:
        await mongodb.connect()
        kb_service = KnowledgeBaseService(mongodb.db)

        # Check if already imported
        existing_count = await mongodb.db.knowledge_base.count_documents({})

        if existing_count > 0:
            print(f"Knowledge base already exists with {existing_count} items.")
            response = input("Do you want to re-import? (y/N): ").lower()

            if response == 'y':
                # Clear existing
                await mongodb.db.knowledge_base.delete_many({})
                print("Cleared existing knowledge base.")
            else:
                print("Skipping import.")
                await mongodb.disconnect()
                return

        # Import
        count = await kb_service.import_from_files()
        print(f"✓ Successfully imported {count} knowledge base items")

        # Verify import
        categories = await mongodb.db.knowledge_base.distinct("category")
        print(f"✓ Categories available: {', '.join(categories)}")

    except Exception as e:
        print(f"✗ Error importing knowledge base: {e}")
        sys.exit(1)
    finally:
        await mongodb.disconnect()


async def verify_connections():
    """Verify all service connections."""
    print("\nVerifying connections...")

    # MongoDB
    try:
        await mongodb.connect()
        await mongodb.db.command("ping")
        print("✓ MongoDB connection successful")
        await mongodb.disconnect()
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

    # Redis
    try:
        from app.services.redis_service import redis_service
        await redis_service.connect()
        await redis_service.client.ping()
        print("✓ Redis connection successful")
        await redis_service.disconnect()
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False

    # RabbitMQ
    try:
        from app.services.rabbitmq_service import rabbitmq_service
        await rabbitmq_service.connect()
        print("✓ RabbitMQ connection successful")
        await rabbitmq_service.disconnect()
    except Exception as e:
        print(f"✗ RabbitMQ connection failed: {e}")
        return False

    return True


def check_environment():
    """Check environment configuration."""
    print("Checking environment...")

    from app.core.config import get_settings
    settings = get_settings()

    checks = [
        ("OpenAI API Key", bool(settings.openai_api_key)),
        ("MongoDB URL", bool(settings.mongodb_url)),
        ("Redis URL", bool(settings.redis_url)),
        ("RabbitMQ URL", bool(settings.rabbitmq_url)),
        ("Knowledge Base Dir", settings.kb_dir.exists()),
    ]

    all_good = True
    for name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
        if not result:
            all_good = False

    if not all_good:
        print("\n✗ Some configuration is missing. Please check your .env file.")
        return False

    return True


async def create_indexes():
    """Create database indexes."""
    print("\nCreating database indexes...")

    try:
        await mongodb.connect()
        await mongodb.create_indexes()
        print("✓ Database indexes created")
        await mongodb.disconnect()
    except Exception as e:
        print(f"✗ Error creating indexes: {e}")
        return False

    return True


async def main():
    """Main setup routine."""
    print("=" * 60)
    print("MEDICAL REPORT GENERATOR - WORKER SETUP")
    print("=" * 60)
    print()

    # Check environment
    if not check_environment():
        sys.exit(1)

    print()

    # Verify connections
    if not await verify_connections():
        print("\n✗ Connection verification failed.")
        print("\nMake sure all services are running:")
        print("  docker-compose up -d")
        sys.exit(1)

    print()

    # Create indexes
    if not await create_indexes():
        sys.exit(1)

    print()

    # Import knowledge base
    await import_knowledge_base()

    print()
    print("=" * 60)
    print("✓ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("You can now start the worker:")
    print("  python -m app.worker")
    print()
    print("Or test with the client:")
    print("  python test_rabbitmq_client.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
