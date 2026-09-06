"""Unit tests for the deterministic Recommendation Engine pipeline components."""

from unittest.mock import MagicMock

from lapiq.domain.recommendation.business_rules import BusinessRulesFilter
from lapiq.domain.recommendation.confidence import ConfidenceScorer
from lapiq.domain.recommendation.models import ScoredVariant, UserPreferences
from lapiq.domain.recommendation.policy import RecommendationPolicy
from lapiq.domain.recommendation.ranking import RankingEngine

# ---------------------------------------------------------------------------
# Helpers: build minimal fake ORM objects without hitting the database
# ---------------------------------------------------------------------------


def _make_cpu(benchmark: int = 15000) -> MagicMock:
    cpu = MagicMock()
    cpu.benchmark_score = benchmark
    return cpu


def _make_gpu(benchmark: int = 10000, is_integrated: bool = False) -> MagicMock:
    gpu = MagicMock()
    gpu.benchmark_score = benchmark
    gpu.is_integrated = is_integrated
    return gpu


def _make_display() -> MagicMock:
    display = MagicMock()
    display.size_inches = 15.6
    return display


def _make_laptop(is_available: bool = True) -> MagicMock:
    laptop = MagicMock()
    laptop.is_available = is_available
    return laptop


def _make_variant(
    price: int = 55000,
    ram_gb: int = 16,
    is_in_stock: bool = True,
    laptop_available: bool = True,
    weight_kg: float = 1.8,
    cpu_benchmark: int = 15000,
    gpu_benchmark: int = 10000,
    gpu_integrated: bool = False,
) -> MagicMock:
    variant = MagicMock()
    variant.current_price_inr = price
    variant.ram_gb = ram_gb
    variant.is_in_stock = is_in_stock
    variant.weight_kg = weight_kg
    variant.laptop = _make_laptop(laptop_available)
    variant.cpu = _make_cpu(cpu_benchmark)
    variant.gpu = _make_gpu(gpu_benchmark, gpu_integrated)
    variant.display = _make_display()
    return variant


# ---------------------------------------------------------------------------
# Business Rules Tests
# ---------------------------------------------------------------------------


def test_business_rules_filters_out_of_stock() -> None:
    """Variants marked out of stock must be excluded."""
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")
    variant = _make_variant(is_in_stock=False, price=55000)

    result = BusinessRulesFilter().apply([variant], prefs)
    assert len(result) == 0


def test_business_rules_filters_discontinued() -> None:
    """Variants belonging to discontinued laptops must be excluded."""
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")
    variant = _make_variant(laptop_available=False, price=55000)

    result = BusinessRulesFilter().apply([variant], prefs)
    assert len(result) == 0


def test_business_rules_allows_within_budget_with_buffer() -> None:
    """Variants up to 5% over budget must pass the budget rule."""
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")
    # 60000 * 1.05 = 63000; price 62000 should pass
    variant = _make_variant(price=62000, is_in_stock=True, laptop_available=True)

    result = BusinessRulesFilter().apply([variant], prefs)
    assert len(result) == 1


def test_business_rules_rejects_over_budget_with_buffer() -> None:
    """Variants more than 5% over budget must be rejected."""
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")
    variant = _make_variant(price=65000, is_in_stock=True, laptop_available=True)

    result = BusinessRulesFilter().apply([variant], prefs)
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Ranking Engine Tests
# ---------------------------------------------------------------------------


def test_ranking_engine_scores_within_range() -> None:
    """All score components must be in [0.0, 1.0] and total in [0.0, 1.0]."""
    prefs = UserPreferences(
        budget_inr=80000, use_case="gaming", target_segment="Gamers", requires_dedicated_gpu=True
    )
    variant = _make_variant(price=70000, ram_gb=16, cpu_benchmark=20000, gpu_benchmark=18000)

    scored = RankingEngine().score(variant, prefs)

    assert 0.0 <= scored.total_score <= 1.0
    assert 0.0 <= scored.performance_score <= 1.0
    assert 0.0 <= scored.value_score <= 1.0
    assert 0.0 <= scored.segment_fit_score <= 1.0


def test_ranking_engine_higher_benchmark_gives_higher_performance_score() -> None:
    """Variant with higher CPU/GPU benchmark must score higher on performance."""
    prefs = UserPreferences(budget_inr=100000, use_case="gaming", target_segment="Gamers")
    low_perf = _make_variant(cpu_benchmark=5000, gpu_benchmark=4000)
    high_perf = _make_variant(cpu_benchmark=25000, gpu_benchmark=20000)

    low_scored = RankingEngine().score(low_perf, prefs)
    high_scored = RankingEngine().score(high_perf, prefs)

    assert high_scored.performance_score > low_scored.performance_score


# ---------------------------------------------------------------------------
# Confidence Scorer Tests
# ---------------------------------------------------------------------------


def test_confidence_scorer_partial_results_penalty() -> None:
    """Partial result flag must reduce confidence by PENALTY_PARTIAL_RESULTS."""
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")
    variant = _make_variant()
    scored = ScoredVariant(variant=variant, total_score=0.70, confidence_score=0.0)

    normal = ConfidenceScorer().compute(scored, prefs, is_partial=False)
    scored2 = ScoredVariant(variant=variant, total_score=0.70, confidence_score=0.0)
    partial = ConfidenceScorer().compute(scored2, prefs, is_partial=True)

    assert partial.confidence_score < normal.confidence_score


def test_confidence_scorer_minimum_floor() -> None:
    """Confidence score must never go below MIN_CONFIDENCE_SCORE."""
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")
    variant = _make_variant(price=58000)
    scored = ScoredVariant(variant=variant, total_score=0.05, confidence_score=0.0)

    result = ConfidenceScorer().compute(scored, prefs, is_partial=True)

    assert result.confidence_score >= 0.10


# ---------------------------------------------------------------------------
# Recommendation Policy Tests
# ---------------------------------------------------------------------------


def test_recommendation_policy_limits_to_top_n() -> None:
    """Policy must return at most top_n candidates."""
    variant = _make_variant()
    candidates = [
        ScoredVariant(variant=variant, total_score=0.9, confidence_score=0.9),
        ScoredVariant(variant=variant, total_score=0.8, confidence_score=0.8),
        ScoredVariant(variant=variant, total_score=0.7, confidence_score=0.7),
        ScoredVariant(variant=variant, total_score=0.6, confidence_score=0.6),
        ScoredVariant(variant=variant, total_score=0.5, confidence_score=0.5),
    ]

    result = RecommendationPolicy().select(candidates, top_n=3)
    assert len(result) == 3


def test_recommendation_policy_caps_at_max_n() -> None:
    """Policy must cap at MAX_TOP_N even if higher top_n is requested."""
    variant = _make_variant()
    candidates = [
        ScoredVariant(variant=variant, total_score=0.9, confidence_score=0.9),
        ScoredVariant(variant=variant, total_score=0.8, confidence_score=0.8),
        ScoredVariant(variant=variant, total_score=0.7, confidence_score=0.7),
        ScoredVariant(variant=variant, total_score=0.6, confidence_score=0.6),
        ScoredVariant(variant=variant, total_score=0.5, confidence_score=0.5),
        ScoredVariant(variant=variant, total_score=0.4, confidence_score=0.4),
    ]

    result = RecommendationPolicy().select(candidates, top_n=10)
    assert len(result) <= 5
