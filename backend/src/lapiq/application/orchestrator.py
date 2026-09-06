"""Recommendation Orchestrator — coordinates the full online request lifecycle."""

import logging
import uuid

from lapiq.domain.evidence.aggregator import EvidenceAggregator
from lapiq.domain.explanation.builder import ExplanationBuilder, ExplanationContext
from lapiq.domain.interfaces.provider import ReasoningProviderInterface
from lapiq.domain.interfaces.repository import VariantRepositoryInterface
from lapiq.domain.recommendation.engine import RecommendationEngine
from lapiq.domain.recommendation.models import RecommendationResult, ScoredVariant, UserPreferences
from lapiq.infrastructure.cache.redis_cache import RedisCacheManager

logger = logging.getLogger(__name__)


class RecommendationOrchestrator:
    """
    Application-layer orchestrator for the online recommendation request path.

    Online Path (12 steps per architecture.md):
    1. Receive parsed UserPreferences from Intent Parser.
    2. Update session cache (conversation state).
    3. Run RecommendationEngine (fully deterministic pipeline).
    4. Store RecommendationResult in Redis request cache (for SSE stream access).
    5. Return ranked laptop response to API layer.

    SSE Explanation Path (triggered after API response):
    6. Load result from request cache.
    7. Retrieve evidence from EvidenceAggregator.
    8. Build ExplanationContext via ExplanationBuilder.
    9. Stream via ReasoningProvider (Gemini) or fallback.
    """

    def __init__(
        self,
        recommendation_engine: RecommendationEngine,
        evidence_aggregator: EvidenceAggregator,
        explanation_builder: ExplanationBuilder,
        reasoning_provider: ReasoningProviderInterface,
        cache_manager: RedisCacheManager,
        variant_repo: VariantRepositoryInterface,
    ) -> None:
        self.recommendation_engine = recommendation_engine
        self.evidence_aggregator = evidence_aggregator
        self.explanation_builder = explanation_builder
        self.reasoning_provider = reasoning_provider
        self.cache_manager = cache_manager
        self.variant_repo = variant_repo

    async def run_recommendation(self, preferences: UserPreferences) -> RecommendationResult:
        """Run the deterministic recommendation pipeline and cache the result."""
        request_id = str(uuid.uuid4())

        result = await self.recommendation_engine.recommend(
            request_id=request_id,
            preferences=preferences,
            top_n=3,
        )

        # Store result context in Redis for SSE stream retrieval (request cache).
        # Scores are stored so stream_for_request_id can rebuild the result without
        # re-running a full DB candidate query — only variant fetches by ID.
        await self.cache_manager.set_json(
            f"request:{request_id}",
            {
                "request_id": request_id,
                "segment": preferences.target_segment,
                "use_case": preferences.use_case,
                "budget": preferences.budget_inr,
                "min_ram_gb": preferences.min_ram_gb,
                "scored_variants": [
                    {
                        "variant_id": sv.variant.id,
                        "total_score": sv.total_score,
                        "performance_score": sv.performance_score,
                        "value_score": sv.value_score,
                        "segment_fit_score": sv.segment_fit_score,
                        "confidence_score": sv.confidence_score,
                    }
                    for sv in result.ranked_variants
                ],
            },
            ttl_seconds=3600,
        )

        return result

    async def stream_explanation(self, result: RecommendationResult):
        """
        Assemble context and stream explanation. Yields string chunks.

        Falls back to deterministic markdown if ReasoningProvider raises.
        """
        evidence_by_laptop: dict[int, list[dict[str, str]]] = {}
        for scored in result.ranked_variants:
            laptop_id = scored.variant.laptop.id
            evidence_by_laptop[laptop_id] = await self.evidence_aggregator.get_structured_evidence(
                laptop_id=laptop_id
            )

        context: ExplanationContext = self.explanation_builder.build(result, evidence_by_laptop)

        try:
            async for chunk in self.reasoning_provider.stream_explanation(context.summary_text):
                yield chunk
        except Exception:
            fallback_context = self.explanation_builder.build_fallback(result)
            yield fallback_context.summary_text

    async def stream_for_request_id(self, request_id: str):
        """
        Reconstruct recommendation context from Redis cache and stream explanation.

        Called by the SSE endpoint. Reads the request cache written by run_recommendation,
        re-fetches variants by ID (already pre-filtered and ranked), reassembles
        RecommendationResult with stored scores, then delegates to stream_explanation.

        Yields:
            str chunks for SSE. Yields a single error event string if cache is missing.
        """
        cached = await self.cache_manager.get_json(f"request:{request_id}")
        if not cached:
            logger.error(
                "SSE stream requested for unknown or expired request_id",
                extra={"request_id": request_id},
            )
            yield "[LapIQ] Explanation context not found or expired."
            return

        preferences = UserPreferences(
            budget_inr=int(cached["budget"]),
            use_case=str(cached["use_case"]),
            target_segment=str(cached["segment"]),
            min_ram_gb=int(cached.get("min_ram_gb", 8)),
        )

        scored_variants: list[ScoredVariant] = []
        for entry in cached.get("scored_variants", []):
            variant = await self.variant_repo.get_by_id(int(entry["variant_id"]))
            if variant is None:
                logger.warning(
                    "Variant not found during SSE context rebuild",
                    extra={"variant_id": entry["variant_id"], "request_id": request_id},
                )
                continue
            scored_variants.append(
                ScoredVariant(
                    variant=variant,
                    total_score=float(entry["total_score"]),
                    performance_score=float(entry["performance_score"]),
                    value_score=float(entry["value_score"]),
                    segment_fit_score=float(entry["segment_fit_score"]),
                    confidence_score=float(entry["confidence_score"]),
                )
            )

        result = RecommendationResult(
            request_id=request_id,
            preferences=preferences,
            ranked_variants=scored_variants,
            is_partial=len(scored_variants) < 3,
        )

        async for chunk in self.stream_explanation(result):
            yield chunk
