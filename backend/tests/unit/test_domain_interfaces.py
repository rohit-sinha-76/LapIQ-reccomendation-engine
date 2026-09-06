"""Unit tests for domain interfaces and RedisCacheManager instantiation."""

import pytest
from lapiq.domain.interfaces import (
    CatalogProviderInterface,
    LaptopRepositoryInterface,
    ReasoningProviderInterface,
    VariantRepositoryInterface,
)
from lapiq.infrastructure.cache.redis_cache import RedisCacheManager


def test_domain_interfaces_subclass_check() -> None:
    """Verify ABC contracts cannot be directly instantiated."""
    with pytest.raises(TypeError):
        LaptopRepositoryInterface()  # type: ignore[abstract]

    with pytest.raises(TypeError):
        VariantRepositoryInterface()  # type: ignore[abstract]

    with pytest.raises(TypeError):
        CatalogProviderInterface()  # type: ignore[abstract]

    with pytest.raises(TypeError):
        ReasoningProviderInterface()  # type: ignore[abstract]


def test_redis_cache_manager_instantiation() -> None:
    """Verify RedisCacheManager initializes with default settings."""
    manager = RedisCacheManager()
    assert manager.redis_url.startswith("redis://")
