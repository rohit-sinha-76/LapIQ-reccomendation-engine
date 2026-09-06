"""Recommendation Engine — orchestrates candidate retrieval through to ranked output."""

from lapiq.domain.catalog.service import CatalogService
from lapiq.domain.recommendation.business_rules import BusinessRulesFilter
from lapiq.domain.recommendation.confidence import ConfidenceScorer
from lapiq.domain.recommendation.models import RecommendationResult, UserPreferences
from lapiq.domain.recommendation.policy import RecommendationPolicy
from lapiq.domain.recommendation.ranking import RankingEngine


class RecommendationEngine:
    """
    Core recommendation engine: fully deterministic. LLM not involved.

    Pipeline steps:
    1. Retrieve variant candidates from Catalog (via CatalogService).
    2. Apply Business Rules (availability, budget, discontinued filter).
    3. Score each candidate with RankingEngine (performance, value, segment fit).
    4. Sort descending by total_score.
    5. Assign confidence scores via ConfidenceScorer.
    6. Select final top-N via RecommendationPolicy.
    """

    def __init__(
        self,
        catalog_service: CatalogService,
        business_rules: BusinessRulesFilter,
        ranking_engine: RankingEngine,
        confidence_scorer: ConfidenceScorer,
        policy: RecommendationPolicy,
    ) -> None:
        self.catalog_service = catalog_service
        self.business_rules = business_rules
        self.ranking_engine = ranking_engine
        self.confidence_scorer = confidence_scorer
        self.policy = policy

    async def recommend(
        self,
        request_id: str,
        preferences: UserPreferences,
        top_n: int = 3,
    ) -> RecommendationResult:
        """
        Execute the full recommendation pipeline.

        Always produces a result. Returns is_partial=True if fewer candidates
        exist than top_n requested.
        """
        candidates = await self.catalog_service.find_candidates_for_budget(
            max_budget_inr=preferences.budget_inr,
            min_ram_gb=preferences.min_ram_gb,
            target_segment=preferences.target_segment,
        )

        eligible = self.business_rules.apply(candidates, preferences)

        # Fallback: If strict segment/RAM filter returns 0 candidates, relax segment/RAM criteria
        if not eligible:
            candidates = await self.catalog_service.find_candidates_for_budget(
                max_budget_inr=int(preferences.budget_inr * 1.20),
                min_ram_gb=4,
                target_segment=None,
            )
            eligible = self.business_rules.apply(candidates, preferences)

        is_partial = len(eligible) < top_n

        scored = [self.ranking_engine.score(v, preferences) for v in eligible]
        scored.sort(key=lambda sv: sv.total_score, reverse=True)

        scored_with_confidence = [
            self.confidence_scorer.compute(sv, preferences, is_partial) for sv in scored
        ]

        final = self.policy.select(scored_with_confidence, top_n=top_n)

        return RecommendationResult(
            request_id=request_id,
            preferences=preferences,
            ranked_variants=final,
            is_partial=is_partial,
        )
