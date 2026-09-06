"""Recommendation Policy — deterministic top-N selection from ranked candidates."""

from lapiq.domain.recommendation.models import ScoredVariant

DEFAULT_TOP_N = 3
MAX_TOP_N = 5
MIN_CONFIDENCE_TO_INCLUDE = 0.10


class RecommendationPolicy:
    """
    Selects the final top-N recommendations from the ranked and confidence-scored list.

    Selection rules:
    - Maximum top_n candidates returned (default 3, max 5).
    - Only candidates with confidence_score >= MIN_CONFIDENCE_TO_INCLUDE are included.
    - Input list must already be sorted descending by total_score before calling.
    """

    def select(
        self,
        scored_variants: list[ScoredVariant],
        top_n: int = DEFAULT_TOP_N,
    ) -> list[ScoredVariant]:
        """Select top-N eligible candidates from a pre-sorted scored list."""
        capped_top_n = min(top_n, MAX_TOP_N)
        eligible = [
            sv for sv in scored_variants if sv.confidence_score >= MIN_CONFIDENCE_TO_INCLUDE
        ]
        return eligible[:capped_top_n]
