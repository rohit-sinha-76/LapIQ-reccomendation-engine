"""Evidence domain module — structured evidence aggregation from review sources."""

from typing import Optional, Sequence
from lapiq.domain.interfaces.repository import EvidenceRepositoryInterface


class EvidenceAggregator:
    """
    Domain service that retrieves and normalizes structured evidence items.

    Evidence sources: professional reviews, YouTube summaries, Reddit discussions.
    The aggregator fetches from the database repository only — no live web calls.
    Live fetching is handled exclusively by EvidenceProvider in the offline pipeline.
    """

    def __init__(self, evidence_repo: EvidenceRepositoryInterface) -> None:
        self.evidence_repo = evidence_repo

    async def get_structured_evidence(
        self, laptop_id: int, max_items: int = 5
    ) -> list[dict[str, str]]:
        """
        Retrieve aggregated evidence items for a laptop from the database.

        Returns list of normalized evidence dicts with keys:
        source_type, summary_text, sentiment_score.
        """
        items = await self.evidence_repo.get_evidence_for_laptop(laptop_id)
        normalized: list[dict[str, str]] = []

        for item in items[:max_items]:
            normalized.append({
                "source_type": item.get("source_type", "review"),
                "summary": item.get("summary_text", ""),
                "sentiment": str(item.get("sentiment_score", "0.0")),
            })

        return normalized
