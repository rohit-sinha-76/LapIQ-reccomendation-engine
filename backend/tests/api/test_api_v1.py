"""API v1 endpoints integration tests using httpx.AsyncClient."""

import pytest
from httpx import ASGITransport, AsyncClient

from lapiq.api.main import app


@pytest.mark.asyncio
async def test_api_root_endpoint() -> None:
    """Verify GET / returns expected status payload."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "LapIQ API v3.1", "status": "running"}


@pytest.mark.asyncio
async def test_health_check_endpoint() -> None:
    """Verify GET /api/v1/health returns ok status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "3.1.0"}


@pytest.mark.asyncio
async def test_stream_explanation_endpoint_headers() -> None:
    """Verify GET /api/v1/recommend/{id}/stream sets SSE headers with X-Accel-Buffering disabled."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/recommend/test-req-123/stream")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert response.headers["x-accel-buffering"] == "no"
