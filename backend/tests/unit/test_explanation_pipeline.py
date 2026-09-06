"""Unit tests for Evidence Module, Explanation Builder, and ReasoningProvider."""

from unittest.mock import AsyncMock, MagicMock
import pytest

from lapiq.domain.evidence.aggregator import EvidenceAggregator
from lapiq.domain.explanation.builder import ExplanationBuilder
from lapiq.domain.recommendation.models import (
    RecommendationResult,
    ScoredVariant,
    UserPreferences,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_variant_mock(laptop_id: int = 1, price: int = 55000, ram_gb: int = 16) -> MagicMock:
    laptop = MagicMock()
    laptop.id = laptop_id
    laptop.brand = "Asus"
    laptop.model_name = "VivoBook 15"
    laptop.is_available = True

    variant = MagicMock()
    variant.id = laptop_id * 10
    variant.laptop = laptop
    variant.current_price_inr = price
    variant.ram_gb = ram_gb
    variant.storage_gb = 512
    variant.weight_kg = 1.8
    return variant


def _make_prefs() -> UserPreferences:
    return UserPreferences(
        budget_inr=60000,
        use_case="college study and video editing",
        target_segment="Students",
    )


def _make_result(prefs: UserPreferences) -> RecommendationResult:
    variant = _make_variant_mock(laptop_id=1)
    scored = ScoredVariant(variant=variant, total_score=0.72, confidence_score=0.68)
    return RecommendationResult(
        request_id="test-req-001",
        preferences=prefs,
        ranked_variants=[scored],
        is_partial=False,
    )


# ---------------------------------------------------------------------------
# Evidence Module Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_evidence_aggregator_returns_normalized_items() -> None:
    """EvidenceAggregator must normalize raw repository data to expected keys."""
    mock_repo = AsyncMock()
    mock_repo.get_evidence_for_laptop.return_value = [
        {"source_type": "review", "summary_text": "Great display quality.", "sentiment_score": 0.8},
        {"source_type": "youtube", "summary_text": "Good battery life.", "sentiment_score": 0.7},
    ]

    aggregator = EvidenceAggregator(evidence_repo=mock_repo)
    items = await aggregator.get_structured_evidence(laptop_id=1)

    assert len(items) == 2
    assert items[0]["source_type"] == "review"
    assert items[0]["summary"] == "Great display quality."
    assert items[0]["sentiment"] == "0.8"


@pytest.mark.asyncio
async def test_evidence_aggregator_respects_max_items() -> None:
    """EvidenceAggregator must limit output to max_items parameter."""
    mock_repo = AsyncMock()
    mock_repo.get_evidence_for_laptop.return_value = [
        {"source_type": "review", "summary_text": f"Review {i}.", "sentiment_score": 0.5}
        for i in range(10)
    ]

    aggregator = EvidenceAggregator(evidence_repo=mock_repo)
    items = await aggregator.get_structured_evidence(laptop_id=1, max_items=3)

    assert len(items) == 3


# ---------------------------------------------------------------------------
# Explanation Builder Tests
# ---------------------------------------------------------------------------

def test_explanation_builder_produces_non_empty_context() -> None:
    """ExplanationBuilder.build must produce a non-empty summary text."""
    prefs = _make_prefs()
    result = _make_result(prefs)
    evidence_map = {1: [{"source_type": "review", "summary": "Solid performance.", "sentiment": "0.8"}]}

    builder = ExplanationBuilder()
    context = builder.build(result, evidence_map)

    assert context.request_id == "test-req-001"
    assert len(context.summary_text) > 50
    assert "Students" in context.summary_text
    assert "60,000" in context.summary_text


def test_explanation_builder_fallback_contains_markdown() -> None:
    """Fallback context must contain markdown headers and laptop details."""
    prefs = _make_prefs()
    result = _make_result(prefs)

    context = ExplanationBuilder().build_fallback(result)

    assert "## LapIQ Recommendations" in context.summary_text
    assert "VivoBook 15" in context.summary_text
    assert context.evidence_items == []
