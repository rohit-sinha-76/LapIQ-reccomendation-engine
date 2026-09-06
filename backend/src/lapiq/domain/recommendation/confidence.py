"""Confidence Score calculation for recommendation results."""

import dataclasses

from lapiq.domain.recommendation.models import ScoredVariant, UserPreferences

MIN_CONFIDENCE_SCORE = 0.10
CONFIDENCE_THRESHOLD_HIGH = 0.75
CONFIDENCE_THRESHOLD_MED = 0.50

# Penalties
PENALTY_PARTIAL_RESULTS = 0.15
PENALTY_BUDGET_OVER_90_PCT_USED = 0.10


class ConfidenceScorer:
    """
    Computes confidence score for each ranked variant.

    Confidence reflects how well the recommendation satisfies stated preferences.
    It is purely deterministic. The LLM receives this value but never changes it.
    """

    def compute(
        self,
        scored: ScoredVariant,
        preferences: UserPreferences,
        is_partial: bool = False,
    ) -> ScoredVariant:
        """Assign confidence score to a pre-ranked ScoredVariant."""
        base = scored.total_score

        if is_partial:
            base -= PENALTY_PARTIAL_RESULTS

        price = getattr(scored.variant, "current_price_inr", 0)
        try:
            price_val = float(price)
        except (TypeError, ValueError):
            price_val = 0.0

        budget = float(preferences.budget_inr) if preferences.budget_inr else 0.0
        if budget > 0 and price_val / budget > 0.90:
            base -= PENALTY_BUDGET_OVER_90_PCT_USED

        confidence = max(round(base, 4), MIN_CONFIDENCE_SCORE)
        return dataclasses.replace(scored, confidence_score=confidence)
