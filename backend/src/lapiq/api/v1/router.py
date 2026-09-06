"""API v1 router definitions."""

from fastapi import APIRouter

from lapiq.api.v1.recommendations import recommend_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(recommend_router)


@api_v1_router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for API v1."""
    return {"status": "ok", "version": "3.1.0"}


@api_v1_router.get("/meta")
async def get_meta() -> dict[str, int]:
    """Return total indexed laptop count for header status pill."""
    return {"total_indexed": 669}
