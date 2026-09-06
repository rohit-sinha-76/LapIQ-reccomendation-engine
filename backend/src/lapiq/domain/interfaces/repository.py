"""Abstract base classes defining repository interfaces for domain entities."""

from abc import ABC, abstractmethod
from typing import Optional, Sequence
from lapiq.infrastructure.database.models import CPU, GPU, Display, Laptop, PriceSnapshot, Variant


class LaptopRepositoryInterface(ABC):
    """Abstract interface for Laptop entity data access."""

    @abstractmethod
    async def get_by_id(self, laptop_id: int) -> Optional[Laptop]:
        """Retrieve laptop entity by primary key."""
        pass

    @abstractmethod
    async def get_all_active(self) -> Sequence[Laptop]:
        """Retrieve all currently active laptop entities."""
        pass

    @abstractmethod
    async def search_by_segment(self, segment: str) -> Sequence[Laptop]:
        """Filter laptops by target segment."""
        pass


class VariantRepositoryInterface(ABC):
    """Abstract interface for Variant entity data access."""

    @abstractmethod
    async def get_by_id(self, variant_id: int) -> Optional[Variant]:
        """Retrieve variant by primary key."""
        pass

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Variant]:
        """Retrieve variant by unique SKU string."""
        pass

    @abstractmethod
    async def get_candidates(
        self,
        max_price: int,
        min_ram_gb: int = 8,
        segment: Optional[str] = None,
    ) -> Sequence[Variant]:
        """Filter variant candidates matching budget and minimum specification criteria."""
        pass


class PriceRepositoryInterface(ABC):
    """Abstract interface for PriceSnapshot entity data access."""

    @abstractmethod
    async def get_latest_price(self, variant_id: int) -> Optional[PriceSnapshot]:
        """Retrieve the most recent price snapshot for a given variant."""
        pass

    @abstractmethod
    async def get_price_history(self, variant_id: int, limit: int = 30) -> Sequence[PriceSnapshot]:
        """Retrieve historical price snapshots for price trend analysis."""
        pass


class EvidenceRepositoryInterface(ABC):
    """Abstract interface for review evidence data access."""

    @abstractmethod
    async def get_evidence_for_laptop(self, laptop_id: int) -> Sequence[dict[str, str]]:
        """Retrieve aggregated review evidence items for a laptop."""
        pass
