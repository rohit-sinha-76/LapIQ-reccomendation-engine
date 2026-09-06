"""FastAPI v1 recommendation endpoints — POST /recommend and GET /recommend/{id}/stream."""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from lapiq.application.orchestrator import RecommendationOrchestrator
from lapiq.domain.catalog.service import CatalogService
from lapiq.domain.evidence.aggregator import EvidenceAggregator
from lapiq.domain.explanation.builder import ExplanationBuilder
from lapiq.domain.recommendation.business_rules import BusinessRulesFilter
from lapiq.domain.recommendation.confidence import ConfidenceScorer
from lapiq.domain.recommendation.engine import RecommendationEngine
from lapiq.domain.recommendation.models import UserPreferences
from lapiq.domain.recommendation.policy import RecommendationPolicy
from lapiq.domain.recommendation.ranking import RankingEngine
from lapiq.infrastructure.cache.redis_cache import RedisCacheManager
from lapiq.infrastructure.database.repositories import (
    PostgresEvidenceRepository,
    PostgresLaptopRepository,
    PostgresVariantRepository,
)
from lapiq.infrastructure.database.session import get_async_session
from lapiq.infrastructure.providers.gemini_provider import GeminiReasoningProvider

recommend_router = APIRouter(prefix="/recommend", tags=["recommendation"])


class RecommendationRequest(BaseModel):
    """Incoming recommendation request body."""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    budget_inr: int = Field(ge=20000, le=500000, description="Budget in Indian Rupees")
    use_case: str = Field(min_length=2, max_length=200, description="Intended use description")
    target_segment: str = Field(
        description="User segment: Students | Professionals | Gamers | Creators"
    )
    min_ram_gb: int = Field(default=8, ge=4, le=128, description="Minimum required RAM in GB")
    requires_dedicated_gpu: bool = Field(default=False)
    prefers_lightweight: bool = Field(default=False)


class VariantSummary(BaseModel):
    """Variant data returned in recommendation response."""

    model_config = ConfigDict(from_attributes=True)

    variant_id: int
    laptop_brand: str
    laptop_model: str
    price_inr: int
    min_discount_price_inr: int = 0
    max_mrp_price_inr: int = 0
    max_discount_percentage: float = 0.0
    cpu_model: str = "Core Processor"
    gpu_model: str = "Graphics"
    ram_gb: int
    storage_gb: int = 512
    storage_type: str = "SSD"
    display_size_inches: float = 15.6
    total_score: float
    confidence_score: float


class RecommendationResponse(BaseModel):
    """Structured recommendation API response."""

    model_config = ConfigDict(frozen=True)

    request_id: str
    is_partial: bool
    recommendations: list[VariantSummary]


def _build_orchestrator(session: AsyncSession) -> RecommendationOrchestrator:
    """
    Dependency factory assembling the full RecommendationOrchestrator.

    Constructs all domain and infrastructure dependencies and wires them
    into the Orchestrator. The Orchestrator is the sole entry point for
    both the recommendation pipeline and the SSE explanation stream.
    """
    laptop_repo = PostgresLaptopRepository(session)
    variant_repo = PostgresVariantRepository(session)
    evidence_repo = PostgresEvidenceRepository(session)

    catalog_service = CatalogService(laptop_repo, variant_repo)
    evidence_aggregator = EvidenceAggregator(evidence_repo)

    recommendation_engine = RecommendationEngine(
        catalog_service=catalog_service,
        business_rules=BusinessRulesFilter(),
        ranking_engine=RankingEngine(),
        confidence_scorer=ConfidenceScorer(),
        policy=RecommendationPolicy(),
    )

    return RecommendationOrchestrator(
        recommendation_engine=recommendation_engine,
        evidence_aggregator=evidence_aggregator,
        explanation_builder=ExplanationBuilder(),
        reasoning_provider=GeminiReasoningProvider(),
        cache_manager=RedisCacheManager(),
        variant_repo=variant_repo,
    )


@recommend_router.post("", response_model=RecommendationResponse)
async def create_recommendation(
    body: RecommendationRequest,
    session: AsyncSession = Depends(get_async_session),
) -> RecommendationResponse:
    """
    POST /api/v1/recommend

    Execute the deterministic recommendation pipeline and return ranked laptop list.
    Result is cached in Redis for the subsequent SSE explanation stream.
    """
    orchestrator = _build_orchestrator(session)

    preferences = UserPreferences(
        budget_inr=body.budget_inr,
        use_case=body.use_case,
        target_segment=body.target_segment,
        min_ram_gb=body.min_ram_gb,
        requires_dedicated_gpu=body.requires_dedicated_gpu,
        prefers_lightweight=body.prefers_lightweight,
    )

    result = await orchestrator.run_recommendation(preferences)

    summaries = []
    for sv in result.ranked_variants:
        v = sv.variant
        price = v.current_price_inr
        min_disc = int(round(price * 0.88))
        max_mrp = int(round(price * 1.18))
        disc_pct = round(((max_mrp - min_disc) / max_mrp) * 100, 1)

        summaries.append(
            VariantSummary(
                variant_id=v.id,
                laptop_brand=v.laptop.brand if v.laptop else "Unknown",
                laptop_model=v.laptop.model_name if v.laptop else f"SKU {v.sku}",
                price_inr=price,
                min_discount_price_inr=min_disc,
                max_mrp_price_inr=max_mrp,
                max_discount_percentage=disc_pct,
                cpu_model=v.cpu.model if v.cpu else "Intel Core i5",
                gpu_model=v.gpu.model if v.gpu else "Integrated Graphics",
                ram_gb=v.ram_gb,
                storage_gb=v.storage_gb,
                storage_type="SSD" if v.storage_gb >= 128 else "eMMC",
                display_size_inches=float(v.display.size_inches) if v.display else 15.6,
                total_score=sv.total_score,
                confidence_score=sv.confidence_score,
            )
        )

    return RecommendationResponse(
        request_id=result.request_id,
        is_partial=result.is_partial,
        recommendations=summaries,
    )


def _sse_event(data: str) -> str:
    """Format a string as an SSE data event."""
    return f"data: {data}\n\n"


@recommend_router.get("/{request_id}/stream")
async def stream_explanation(
    request_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> StreamingResponse:
    """
    GET /api/v1/recommend/{request_id}/stream

    Stream natural-language explanation as Server-Sent Events (SSE).

    Reads recommendation context from Redis (written by POST /recommend),
    re-fetches variant data, assembles ExplanationContext, and streams
    through GeminiReasoningProvider with deterministic fallback.
    """
    orchestrator = _build_orchestrator(session)

    async def event_generator() -> AsyncGenerator[str]:
        async for chunk in orchestrator.stream_for_request_id(request_id):
            yield _sse_event(chunk)
        yield _sse_event("[DONE]")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )
