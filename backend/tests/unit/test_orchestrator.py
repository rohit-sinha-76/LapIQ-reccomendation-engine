"""Unit tests for RecommendationEngine orchestrator and execution flow."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from lapiq.application.orchestrator import RecommendationOrchestrator
from lapiq.domain.recommendation.business_rules import BusinessRulesFilter
from lapiq.domain.recommendation.confidence import ConfidenceScorer
from lapiq.domain.recommendation.engine import RecommendationEngine
from lapiq.domain.recommendation.models import UserPreferences
from lapiq.domain.recommendation.policy import RecommendationPolicy
from lapiq.domain.recommendation.ranking import RankingEngine


def _make_mock_variant() -> MagicMock:
    laptop = MagicMock()
    laptop.id = 1
    laptop.brand = "ASUS"
    laptop.model_name = "VivoBook 15"
    laptop.is_available = True

    cpu = MagicMock()
    cpu.benchmark_score = 18000

    gpu = MagicMock()
    gpu.benchmark_score = 5000
    gpu.is_integrated = True

    variant = MagicMock()
    variant.id = 10
    variant.laptop = laptop
    variant.cpu = cpu
    variant.gpu = gpu
    variant.current_price_inr = 55000
    variant.ram_gb = 16
    variant.weight_kg = 1.7
    variant.is_in_stock = True
    return variant


@pytest.mark.asyncio
async def test_recommendation_engine_full_run() -> None:
    """Verify RecommendationEngine.recommend completes end-to-end with mock catalog."""
    mock_catalog = AsyncMock()
    mock_variant = _make_mock_variant()
    mock_catalog.find_candidates_for_budget.return_value = [mock_variant]

    engine = RecommendationEngine(
        catalog_service=mock_catalog,
        business_rules=BusinessRulesFilter(),
        ranking_engine=RankingEngine(),
        confidence_scorer=ConfidenceScorer(),
        policy=RecommendationPolicy(),
    )

    prefs = UserPreferences(
        budget_inr=60000,
        use_case="study and coding",
        target_segment="Students",
    )

    result = await engine.recommend(request_id="req-123", preferences=prefs, top_n=3)

    assert result.request_id == "req-123"
    assert len(result.ranked_variants) == 1
    assert result.ranked_variants[0].variant.id == 10


@pytest.mark.asyncio
async def test_orchestrator_run_recommendation() -> None:
    """Verify RecommendationOrchestrator runs recommendation and caches result."""
    mock_engine = AsyncMock()
    mock_evidence = AsyncMock()
    mock_builder = MagicMock()
    mock_provider = AsyncMock()
    mock_cache = AsyncMock()

    mock_result = MagicMock()
    mock_result.ranked_variants = []
    mock_engine.recommend.return_value = mock_result

    orchestrator = RecommendationOrchestrator(
        recommendation_engine=mock_engine,
        evidence_aggregator=mock_evidence,
        explanation_builder=mock_builder,
        reasoning_provider=mock_provider,
        cache_manager=mock_cache,
        variant_repo=AsyncMock(),
    )

    prefs = UserPreferences(
        budget_inr=60000,
        use_case="study",
        target_segment="Students",
    )

    res = await orchestrator.run_recommendation(preferences=prefs)
    assert res == mock_result
    mock_cache.set_json.assert_called_once()
