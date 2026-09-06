"""Unit tests for RecommendationInspector."""

from unittest.mock import MagicMock

from lapiq.domain.recommendation.models import ScoredVariant, UserPreferences
from lapiq.domain.scoring.inspector import RecommendationInspector, ScoringBreakdown


def _make_scored_variant(
    total_score: float = 0.85,
    perf_score: float = 0.90,
    val_score: float = 0.80,
    segment_score: float = 0.85,
    conf_score: float = 0.82,
    price: int = 55000,
    weight: float = 1.7,
    battery: float = 60.0,
) -> ScoredVariant:
    laptop = MagicMock()
    laptop.brand = "ASUS"
    laptop.model_name = "VivoBook 15"

    variant = MagicMock()
    variant.id = 10
    variant.sku = "SKU-10"
    variant.current_price_inr = price
    variant.weight_kg = weight
    variant.battery_whr = battery
    variant.laptop = laptop

    return ScoredVariant(
        variant=variant,
        total_score=total_score,
        performance_score=perf_score,
        value_score=val_score,
        segment_fit_score=segment_score,
        confidence_score=conf_score,
    )


def test_inspector_returns_all_required_fields() -> None:
    """Inspector must return a ScoringBreakdown with all dimensional fields populated."""
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")
    scored = _make_scored_variant()

    inspector = RecommendationInspector()
    breakdown = inspector.inspect(scored, rank=1, total_candidates=3, preferences=prefs)

    assert isinstance(breakdown, ScoringBreakdown)
    assert breakdown.performance_score == 0.90
    assert breakdown.value_score == 0.80
    assert breakdown.final_score == 0.85
    assert breakdown.confidence_score == 0.82
    assert 0.0 <= breakdown.battery_score <= 1.0
    assert 0.0 <= breakdown.portability_score <= 1.0
    assert 0.0 <= breakdown.budget_fit <= 1.0
    assert len(breakdown.reason_selected) > 10
    assert len(breakdown.reason_others_lost) > 10


def test_inspector_reason_others_lost_non_empty_multiple_candidates() -> None:
    """When multiple candidates exist, reason_others_lost must explain why others lost."""
    prefs = UserPreferences(budget_inr=60000, use_case="gaming", target_segment="Gamers")
    scored = _make_scored_variant()

    inspector = RecommendationInspector()
    breakdown_rank1 = inspector.inspect(scored, rank=1, total_candidates=5, preferences=prefs)
    breakdown_rank2 = inspector.inspect(scored, rank=2, total_candidates=5, preferences=prefs)

    assert "Outperformed 4 other candidate" in breakdown_rank1.reason_others_lost
    assert "Ranked behind higher picks" in breakdown_rank2.reason_others_lost


def test_inspector_single_candidate_reason() -> None:
    """When only 1 candidate exists, reason_others_lost must state filter result."""
    prefs = UserPreferences(budget_inr=60000, use_case="coding", target_segment="Professionals")
    scored = _make_scored_variant()

    inspector = RecommendationInspector()
    breakdown = inspector.inspect(scored, rank=1, total_candidates=1, preferences=prefs)

    assert "No other eligible candidate passed" in breakdown.reason_others_lost
