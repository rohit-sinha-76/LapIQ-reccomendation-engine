"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lapiq.api.v1.router import api_v1_router
from lapiq.core.config import settings

app = FastAPI(
    title="LapIQ API",
    description="Laptop Purchase Intelligence Platform (India)",
    version="3.1.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url=None,
)

cors_origins = ["*"] if settings.environment == "development" else settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint for status verification."""
    return {"message": "LapIQ API v3.1", "status": "running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness health check endpoint."""
    return {"status": "ok", "version": "3.1.0"}


@app.get("/api/meta")
async def get_meta() -> dict[str, int]:
    """Return total indexed laptop count for header status pill."""
    return {"total_indexed": 669}
