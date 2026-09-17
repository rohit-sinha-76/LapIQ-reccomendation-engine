"""Async database session factory and lifecycle management using SQLAlchemy 2.x."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from lapiq.core.config import settings

engine_kwargs: dict[str, Any] = {
    "echo": settings.environment == "development",
}

if "sqlite" not in settings.database_url:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(
    settings.database_url,
    **engine_kwargs,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    """Dependency injector yield for FastAPI async database session."""
    async with async_session_factory() as session:
        yield session
