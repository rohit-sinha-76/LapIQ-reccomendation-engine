"""Unit tests for EvaluationRunner."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import pytest

from lapiq.application.evaluation.runner import EvaluationRunner
from lapiq.domain.recommendation.engine import RecommendationEngine
from lapiq.domain.recommendation.models import RecommendationResult, ScoredVariant


def _make_scored(sku: str, score: float = 0.85) -> ScoredVariant:
    variant = MagicMock()
    variant.sku = sku
    return ScoredVariant(variant=variant, total_score=score, confidence_score=0.80)


@pytest.mark.asyncio
async def test_evaluation_runner_calculates_top1_and_top3_accuracy() -> None:
    """EvaluationRunner must run personas and compute accurate Top-1 and Top-3 metrics."""
    eval_dir = Path(__file__).parent
    with open(eval_dir / "personas.json", "r", encoding="utf-8") as f:
        personas = json.load(f)
    with open(eval_dir / "expected_results.json", "r", encoding="utf-8") as f:
        expected = json.load(f)

    mock_engine = AsyncMock(spec=RecommendationEngine)

    # Persona 1 mock result (matches top1 SKU-STU-1)
    res1 = RecommendationResult(
        request_id="eval-p-student-1",
        preferences=MagicMock(),
        ranked_variants=[_make_scored("SKU-STU-1"), _make_scored("SKU-STU-2")],
    )
    # Persona 2 mock result (matches top1 SKU-GAM-1)
    res2 = RecommendationResult(
        request_id="eval-p-gamer-1",
        preferences=MagicMock(),
        ranked_variants=[_make_scored("SKU-GAM-1"), _make_scored("SKU-GAM-2")],
    )

    mock_engine.recommend.side_effect = [res1, res2]

    runner = EvaluationRunner(engine=mock_engine)
    metrics = await runner.evaluate_personas(personas, expected)

    assert metrics.total_personas == 2
    assert metrics.top1_correct_count == 2
    assert metrics.top3_correct_count == 2
    assert metrics.top1_accuracy_percent == 100.0
    assert metrics.top3_accuracy_percent == 100.0
