"""Unit tests for CatalogService, PricingService, and worker jobs."""

from unittest.mock import AsyncMock

import pytest

from lapiq.domain.catalog.service import CatalogService
from lapiq.domain.pricing.service import PricingService
from lapiq.infrastructure.worker.jobs import sync_prices_job


@pytest.mark.asyncio
async def test_catalog_service_find_candidates() -> None:
    """Verify CatalogService delegates query to variant repository."""
    mock_laptop_repo = AsyncMock()
    mock_variant_repo = AsyncMock()
    mock_variant_repo.get_candidates.return_value = []

    service = CatalogService(laptop_repo=mock_laptop_repo, variant_repo=mock_variant_repo)
    candidates = await service.find_candidates_for_budget(
        max_budget_inr=60000, target_segment="Students"
    )

    assert candidates == []
    mock_variant_repo.get_candidates.assert_called_once_with(
        max_price=60000,
        min_ram_gb=8,
        segment="Students",
    )


@pytest.mark.asyncio
async def test_pricing_service_cache_hit() -> None:
    """Verify PricingService returns cached price when present in Redis."""
    mock_price_repo = AsyncMock()
    mock_variant_repo = AsyncMock()
    mock_cache = AsyncMock()
    mock_cache.get_json.return_value = 45000

    service = PricingService(
        price_repo=mock_price_repo,
        variant_repo=mock_variant_repo,
        cache_manager=mock_cache,
    )
    price = await service.get_variant_price(variant_id=1)

    assert price == 45000
    mock_cache.get_json.assert_called_once_with("price:1")
    mock_variant_repo.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_sync_prices_job_cache_invalidation() -> None:
    """Verify sync_prices_job triggers Redis retrieval cache invalidation."""
    mock_cache = AsyncMock()
    mock_cache.invalidate.return_value = 3

    await sync_prices_job(cache_manager=mock_cache)
    mock_cache.invalidate.assert_called_once_with("retrieval:*")
