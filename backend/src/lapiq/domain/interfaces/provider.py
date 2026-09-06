"""Abstract base classes defining external provider interfaces for LapIQ."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence


class CatalogProviderInterface(ABC):
    """Abstract interface for external laptop product catalog fetching."""

    @abstractmethod
    async def fetch_catalog(self) -> Sequence[dict[str, str]]:
        """Fetch raw product catalog snapshots from external source."""
        pass


class PriceProviderInterface(ABC):
    """Abstract interface for external price monitoring feeds."""

    @abstractmethod
    async def fetch_latest_prices(self, skus: Sequence[str]) -> Sequence[dict[str, int]]:
        """Fetch real-time price updates for given SKUs."""
        pass


class EvidenceProviderInterface(ABC):
    """Abstract interface for external review/YouTube/Reddit evidence extraction."""

    @abstractmethod
    async def fetch_evidence(self, laptop_name: str) -> Sequence[dict[str, str]]:
        """Fetch structured review evidence summaries from external sources."""
        pass


class ReasoningProviderInterface(ABC):
    """Abstract interface for streaming natural-language explanations (Gemini API)."""

    @abstractmethod
    async def stream_explanation(self, prompt_context: str) -> AsyncIterator[str]:
        """Stream explanation chunks given structured recommendation context."""
        pass
