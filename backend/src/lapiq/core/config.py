"""Application configuration settings using Pydantic BaseSettings."""

from pydantic import ConfigDict, Field, model_validator
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
        default="lapiq-dev-secret-key-minimum-32-chars-length",
        description="Application secret key — override via environment variable in production.",
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

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.environment.lower() == "production":
            if not self.secret_key or "dev-secret-key" in self.secret_key:
                raise ValueError(
                    "SECRET_KEY must be set to a secure, non-default value in production."
                )
        return self


settings = Settings()
