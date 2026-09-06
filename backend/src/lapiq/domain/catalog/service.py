"""Catalog Module domain service for searching and managing laptop metadata."""

from typing import Optional, Sequence
from lapiq.domain.interfaces.repository import LaptopRepositoryInterface, VariantRepositoryInterface
from lapiq.infrastructure.database.models import Laptop, Variant


class CatalogService:
    """Domain service managing laptop catalog queries and specification filtering."""

    def __init__(
        self,
        laptop_repo: LaptopRepositoryInterface,
        variant_repo: VariantRepositoryInterface,
    ) -> None:
        self.laptop_repo = laptop_repo
        self.variant_repo = variant_repo

    async def get_laptop_details(self, laptop_id: int) -> Optional[Laptop]:
        """Get laptop details including all variants."""
        return await self.laptop_repo.get_by_id(laptop_id)

    async def find_candidates_for_budget(
        self,
        max_budget_inr: int,
        min_ram_gb: int = 8,
        target_segment: Optional[str] = None,
    ) -> Sequence[Variant]:
        """Search variants matching budget and segment criteria."""
        return await self.variant_repo.get_candidates(
            max_price=max_budget_inr,
            min_ram_gb=min_ram_gb,
            segment=target_segment,
        )
