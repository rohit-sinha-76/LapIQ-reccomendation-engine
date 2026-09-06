"""Recommendation Inspector — provides deterministic scoring breakdowns and selection rationale."""

from dataclasses import dataclass
from typing import Sequence

from lapiq.domain.recommendation.models import ScoredVariant, UserPreferences


@dataclass(frozen=True)
class ScoringBreakdown:
    """Complete dimensional score breakdown and inspector rationale for a laptop."""

    performance_score: float
    value_score: float
    battery_score: float
    portability_score: float
    budget_fit: float
    final_score: float
    confidence_score: float
    reason_selected: str
    reason_others_lost: str


class RecommendationInspector:
    """
    Inspects scored candidates to generate deterministic selection rationale.
    
    Explains on every recommendation why a laptop won (reason_selected) and
    why other candidates lost (reason_others_lost). Pure deterministic domain logic.
    """

    def inspect(
        self,
        scored: ScoredVariant,
        rank: int,
        total_candidates: int,
        preferences: UserPreferences,
    ) -> ScoringBreakdown:
        """
        Inspect a single ScoredVariant and produce a complete ScoringBreakdown.

        Args:
            scored: The candidate variant with computed ranking scores.
            rank: 1-indexed rank position among top picks.
            total_candidates: Count of total eligible candidates.
            preferences: Stated user preferences.

        Returns:
            ScoringBreakdown with all dimensional scores and rationale strings.
        """
        v = scored.variant

        # Calculate dimension sub-scores
        battery_whr = float(getattr(v, "battery_whr", 50.0) or 50.0)
        weight_kg = float(getattr(v, "weight_kg", 1.8) or 1.8)

        battery_score = round(min(battery_whr / 99.9, 1.0), 4)
        portability_score = round(max(1.0 - (weight_kg / 2.5), 0.0), 4)

        budget = preferences.budget_inr
        price = v.current_price_inr
        budget_diff = (price - budget) / budget if budget > 0 else 0.0
        budget_fit = round(max(0.0, 1.0 - max(0.0, budget_diff)), 4)

        # Generate reason_selected
        brand = v.laptop.brand if v.laptop else "Laptop"
        model = v.laptop.model_name if v.laptop else f"SKU {v.sku}"
        
        if rank == 1:
            reason_selected = (
                f"Top pick for {preferences.target_segment} segment: highest combined performance "
                f"({scored.performance_score:.2f}) and value score ({scored.value_score:.2f}) "
                f"within INR {budget:,} budget."
            )
        else:
            reason_selected = (
                f"Rank #{rank} match for {preferences.target_segment}: solid specifications with "
                f"a final score of {scored.total_score:.2f}."
            )

        # Generate reason_others_lost
        if total_candidates <= 1:
            reason_others_lost = "No other eligible candidate passed business rules filtering."
        elif rank == 1:
            reason_others_lost = (
                f"Outperformed {total_candidates - 1} other candidate(s) due to superior "
                f"segment fit ({scored.segment_fit_score:.2f}) and price headroom."
            )
        else:
            reason_others_lost = (
                f"Ranked behind higher picks due to lower comparative total score "
                f"({scored.total_score:.2f})."
            )

        return ScoringBreakdown(
            performance_score=scored.performance_score,
            value_score=scored.value_score,
            battery_score=battery_score,
            portability_score=portability_score,
            budget_fit=budget_fit,
            final_score=scored.total_score,
            confidence_score=scored.confidence_score,
            reason_selected=reason_selected,
            reason_others_lost=reason_others_lost,
        )
