"""Redis service for caching previous inputs."""

import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisService:
    """Redis service for caching operations."""

    def __init__(self):
        """Initialize Redis service."""
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Establish connection to Redis."""
        try:
            logger.info(f"Connecting to Redis at {settings.redis_url}")
            self.client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close connection to Redis."""
        try:
            if self.client:
                await self.client.close()
                logger.info("Disconnected from Redis")
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from Redis cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in Redis cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: from settings)
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            ttl = ttl or settings.redis_cache_ttl
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            logger.debug(f"Cached key {key} with TTL {ttl}s")
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            raise

    async def delete(self, key: str):
        """
        Delete key from Redis cache.

        Args:
            key: Cache key to delete
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            await self.client.delete(key)
            logger.debug(f"Deleted key {key} from cache")
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking key {key} in Redis: {e}")
            return False

    async def cache_input(self, user_id: str, input_data: dict):
        """
        Cache user input data.

        Args:
            user_id: User identifier
            input_data: Input data to cache
        """
        cache_key = f"input:{user_id}"
        await self.set(cache_key, input_data)

    async def get_cached_input(self, user_id: str) -> Optional[dict]:
        """
        Get cached user input data.

        Args:
            user_id: User identifier

        Returns:
            Cached input data or None
        """
        cache_key = f"input:{user_id}"
        return await self.get(cache_key)

    async def cache_report(self, report_id: str, report_data: dict):
        """
        Cache generated report.

        Args:
            report_id: Report identifier
            report_data: Report data to cache
        """
        cache_key = f"report:{report_id}"
        # Cache reports for longer (24 hours)
        await self.set(cache_key, report_data, ttl=86400)

    async def get_cached_report(self, report_id: str) -> Optional[dict]:
        """
        Get cached report data.

        Args:
            report_id: Report identifier

        Returns:
            Cached report data or None
        """
        cache_key = f"report:{report_id}"
        return await self.get(cache_key)


# Global Redis service instance
redis_service = RedisService()
