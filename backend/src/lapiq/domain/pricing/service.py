"""Pricing Module domain service managing laptop price evaluations and stats."""

from typing import Optional
from lapiq.domain.interfaces.repository import PriceRepositoryInterface, VariantRepositoryInterface
from lapiq.infrastructure.cache.redis_cache import RedisCacheManager


class PricingService:
    """Domain service managing price lookup, price history, and price caching."""

    def __init__(
        self,
        price_repo: PriceRepositoryInterface,
        variant_repo: VariantRepositoryInterface,
        cache_manager: Optional[RedisCacheManager] = None,
    ) -> None:
        self.price_repo = price_repo
        self.variant_repo = variant_repo
        self.cache_manager = cache_manager

    async def get_variant_price(self, variant_id: int) -> int:
        """
        Get latest price for a variant.

        Uses price cache if Redis is available. Falls back to database.
        """
        cache_key = f"price:{variant_id}"
        if self.cache_manager:
            cached_price = await self.cache_manager.get_json(cache_key)
            if cached_price is not None and isinstance(cached_price, int):
                return cached_price

        variant = await self.variant_repo.get_by_id(variant_id)
        if not variant:
            return 0

        price = variant.current_price_inr
        if self.cache_manager:
            await self.cache_manager.set_json(cache_key, price, ttl_seconds=3600)

        return price
