"""Unit tests for HybridRetriever."""

from unittest.mock import AsyncMock, MagicMock
import pytest

from lapiq.application.retriever import HybridRetriever
from lapiq.domain.recommendation.models import UserPreferences


@pytest.mark.asyncio
async def test_hybrid_retriever_returns_max_candidates() -> None:
    """HybridRetriever must execute SQL query and return scalars result."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    
    variant1 = MagicMock()
    variant1.id = 1
    variant2 = MagicMock()
    variant2.id = 2

    mock_result.scalars.return_value.all.return_value = [variant1, variant2]
    mock_session.execute.return_value = mock_result

    retriever = HybridRetriever(session=mock_session)
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")

    candidates = await retriever.retrieve_candidates(prefs, limit=10)

    assert len(candidates) == 2
    assert candidates[0].id == 1
    assert candidates[1].id == 2
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_hybrid_retriever_handles_exception() -> None:
    """HybridRetriever must log structured error and raise on database failure."""
    mock_session = AsyncMock()
    mock_session.execute.side_effect = RuntimeError("Database connection lost")

    retriever = HybridRetriever(session=mock_session)
    prefs = UserPreferences(budget_inr=60000, use_case="study", target_segment="Students")

    with pytest.raises(RuntimeError, match="Database connection lost"):
        await retriever.retrieve_candidates(prefs)
