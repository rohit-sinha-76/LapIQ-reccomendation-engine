"""Ranking Engine — fully deterministic score calculation. No LLM involvement."""

from lapiq.domain.recommendation.models import ScoredVariant, UserPreferences
from lapiq.infrastructure.database.models import Variant

CPU_BENCHMARK_CEILING = 30000
GPU_BENCHMARK_CEILING = 25000

WEIGHT_MIN_KG = 1.5
WEIGHT_MAX_KG = 2.5

SEGMENT_GPU_SEGMENTS = {"Gamers", "Creators"}


def _get_num(val, default: float) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


class RankingEngine:
    """
    Produces deterministic scores for each candidate variant.

    All scores normalize in [0.0, 1.0].
    LLM is never consulted here. All scores are deterministic and reproducible.
    """

    def score(self, variant: Variant, preferences: UserPreferences) -> ScoredVariant:
        """Compute all score components for a single variant candidate."""
        performance = self._compute_performance(variant, preferences)
        value = self._compute_value(variant, preferences)
        segment_fit = self._compute_segment_fit(variant, preferences)

        if preferences.target_segment in SEGMENT_GPU_SEGMENTS or preferences.requires_dedicated_gpu:
            w_perf, w_val, w_fit = 0.55, 0.20, 0.25
        else:
            w_perf, w_val, w_fit = 0.45, 0.30, 0.25

        total = w_perf * performance + w_val * value + w_fit * segment_fit

        return ScoredVariant(
            variant=variant,
            total_score=round(total, 4),
            performance_score=round(performance, 4),
            value_score=round(value, 4),
            segment_fit_score=round(segment_fit, 4),
        )

    def _compute_performance(self, variant: Variant, preferences: UserPreferences) -> float:
        """Normalize CPU + GPU benchmark scores."""
        cpu_bench = _get_num(getattr(getattr(variant, "cpu", None), "benchmark_score", 0), 0.0)
        gpu_bench = _get_num(getattr(getattr(variant, "gpu", None), "benchmark_score", 0), 0.0)

        cpu_score = min(max(cpu_bench / CPU_BENCHMARK_CEILING, 0.0), 1.0)
        gpu_score = min(max(gpu_bench / GPU_BENCHMARK_CEILING, 0.0), 1.0)

        return (cpu_score * 0.5) + (gpu_score * 0.5)

    def _compute_value(self, variant: Variant, preferences: UserPreferences) -> float:
        """Score value based on price headroom, RAM, and storage."""
        budget = _get_num(preferences.budget_inr, 60000.0)
        price = _get_num(getattr(variant, "current_price_inr", 50000), 50000.0)
        ram_gb = _get_num(getattr(variant, "ram_gb", 8), 8.0)
        storage_gb = _get_num(getattr(variant, "storage_gb", 512), 512.0)

        if budget <= 0 or price > budget:
            price_score = 0.0
        else:
            price_score = max(1.0 - (price / budget), 0.0)

        ram_score = min(max((ram_gb - 8.0) / 24.0, 0.0), 1.0)

        return (0.5 * price_score) + (0.5 * ram_score)

    def _compute_segment_fit(self, variant: Variant, preferences: UserPreferences) -> float:
        """Score variant suitability against declared user segment and preferences."""
        score = 0.5  # Baseline fit

        segment = preferences.target_segment
        is_integrated = getattr(getattr(variant, "gpu", None), "is_integrated", True)
        has_dedicated_gpu = not is_integrated
        weight_kg = _get_num(getattr(variant, "weight_kg", 1.8), 1.8)

        if segment in SEGMENT_GPU_SEGMENTS and has_dedicated_gpu:
            score += 0.3
        elif segment not in SEGMENT_GPU_SEGMENTS and is_integrated:
            score += 0.2

        if preferences.prefers_lightweight:
            weight_score = 1.0 - min(
                max((weight_kg - WEIGHT_MIN_KG) / (WEIGHT_MAX_KG - WEIGHT_MIN_KG), 0.0), 1.0
            )
            score += 0.2 * weight_score

        return min(score, 1.0)
