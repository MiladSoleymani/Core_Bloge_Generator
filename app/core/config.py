"""Application configuration."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000

    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "blog_generator"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 3600  # 1 hour default TTL

    # RabbitMQ Configuration
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_request_queue: str = "report_generation_requests"
    rabbitmq_response_queue: str = "report_generation_responses"
    rabbitmq_prefetch_count: int = 1

    # Worker Configuration
    worker_name: str = "report_worker"
    max_retries: int = 3

    # Logging
    log_level: str = "INFO"

    # Project paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data"
    kb_dir: Path = data_dir / "knowledgebase"
    kb_metadata_path: Path = kb_dir / "metadata.json"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
