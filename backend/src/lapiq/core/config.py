"""Application configuration settings using Pydantic BaseSettings."""

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """LapIQ configuration settings loaded from environment variables."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="development", description="Execution environment")
    log_level: str = Field(default="INFO", description="Logging level")
    secret_key: str = Field(
        description="Application secret key — must be set via environment variable. No default.",
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://lapiq:lapiq_dev_password@localhost:5432/lapiq_db",
        description="Async PostgreSQL connection string",
    )

    # Cache
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # LLM Reasoning Provider
    gemini_api_key: str = Field(default="", description="Gemini API Key for google-genai SDK")

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )


settings = Settings()
