"""Evaluation Runner — offline standalone persona accuracy benchmark framework."""

import logging
from typing import Any

from lapiq.application.evaluation.metrics import AccuracyMetrics
from lapiq.domain.recommendation.engine import RecommendationEngine
from lapiq.domain.recommendation.models import UserPreferences

logger = logging.getLogger(__name__)


class EvaluationRunner:
    """
    Offline evaluation framework executing persona test suites.

    Measures Top-1 and Top-3 accuracy metrics on predefined persona profiles.
    Runs the pure deterministic engine with zero DB, Redis, or LLM network calls.
    """

    def __init__(self, engine: RecommendationEngine) -> None:
        self.engine = engine

    async def evaluate_personas(
        self,
        personas: list[dict[str, Any]],
        expected_results: dict[str, dict[str, Any]],
    ) -> AccuracyMetrics:
        """
        Run recommendation evaluation over a list of persona profiles.

        Args:
            personas: List of persona user preference profiles.
            expected_results: Map of persona_id to expected Top-1 and Top-3 SKU/ID lists.

        Returns:
            AccuracyMetrics object containing top-1 and top-3 accuracy percentages.
        """
        total = len(personas)
        top1_correct = 0
        top3_correct = 0
        persona_results: list[dict[str, str | bool | float]] = []

        for p in personas:
            persona_id = str(p["id"])
            prefs = UserPreferences(
                budget_inr=int(p["budget_inr"]),
                use_case=str(p["use_case"]),
                target_segment=str(p["segment"]),
                min_ram_gb=int(p.get("min_ram_gb", 8)),
                requires_dedicated_gpu=bool(p.get("requires_dedicated_gpu", False)),
                prefers_lightweight=bool(p.get("prefers_lightweight", False)),
            )

            result = await self.engine.recommend(
                request_id=f"eval-{persona_id}",
                preferences=prefs,
                top_n=3,
            )

            expected = expected_results.get(persona_id, {})
            expected_top1_sku = str(expected.get("top1_sku", ""))
            expected_top3_skus = [str(sku) for sku in expected.get("top3_skus", [])]

            actual_skus = [sv.variant.sku for sv in result.ranked_variants]
            actual_top1_sku = actual_skus[0] if actual_skus else ""

            is_top1_match = bool(actual_top1_sku and actual_top1_sku == expected_top1_sku)
            is_top3_match = bool(
                actual_top1_sku and any(sku in expected_top3_skus for sku in actual_skus)
            )

            if is_top1_match:
                top1_correct += 1
            if is_top3_match:
                top3_correct += 1

            persona_results.append(
                {
                    "persona_id": persona_id,
                    "persona_name": str(p.get("name", persona_id)),
                    "top1_match": is_top1_match,
                    "top3_match": is_top3_match,
                    "actual_top1": actual_top1_sku,
                    "expected_top1": expected_top1_sku,
                }
            )

        top1_pct = round((top1_correct / total * 100.0) if total > 0 else 0.0, 2)
        top3_pct = round((top3_correct / total * 100.0) if total > 0 else 0.0, 2)

        return AccuracyMetrics(
            total_personas=total,
            top1_correct_count=top1_correct,
            top3_correct_count=top3_correct,
            top1_accuracy_percent=top1_pct,
            top3_accuracy_percent=top3_pct,
            persona_results=persona_results,
        )
