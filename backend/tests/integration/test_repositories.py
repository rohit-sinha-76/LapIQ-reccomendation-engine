"""Integration tests for SQLAlchemy 2.x repositories with sqlite/in-memory or mock session."""

from unittest.mock import AsyncMock, MagicMock
import pytest

from lapiq.infrastructure.database.repositories import (
    PostgresLaptopRepository,
    PostgresVariantRepository,
)


@pytest.mark.asyncio
async def test_postgres_laptop_repository_get_by_id() -> None:
    """Verify PostgresLaptopRepository query execution."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    repo = PostgresLaptopRepository(session=mock_session)
    laptop = await repo.get_by_id(laptop_id=999)

    assert laptop is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_postgres_variant_repository_get_candidates() -> None:
    """Verify PostgresVariantRepository get_candidates query execution."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    repo = PostgresVariantRepository(session=mock_session)
    candidates = await repo.get_candidates(max_price=60000, min_ram_gb=8)

    assert candidates == []
    mock_session.execute.assert_called_once()
