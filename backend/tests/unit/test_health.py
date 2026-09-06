"""Unit tests for core health check functionality."""

import pytest
from lapiq.api.v1.router import health_check


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Verify health check returns expected status and version."""
    result = await health_check()
    assert result == {"status": "ok", "version": "3.1.0"}
