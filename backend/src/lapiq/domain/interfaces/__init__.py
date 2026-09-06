"""Domain abstract base class interfaces package."""

from lapiq.domain.interfaces.embedding_provider import EmbeddingProviderInterface
from lapiq.domain.interfaces.provider import (
    CatalogProviderInterface,
    EvidenceProviderInterface,
    PriceProviderInterface,
    ReasoningProviderInterface,
)
from lapiq.domain.interfaces.repository import (
    EvidenceRepositoryInterface,
    LaptopRepositoryInterface,
    PriceRepositoryInterface,
    VariantRepositoryInterface,
)

__all__ = [
    "LaptopRepositoryInterface",
    "VariantRepositoryInterface",
    "PriceRepositoryInterface",
    "EvidenceRepositoryInterface",
    "CatalogProviderInterface",
    "PriceProviderInterface",
    "EvidenceProviderInterface",
    "ReasoningProviderInterface",
    "EmbeddingProviderInterface",
]
