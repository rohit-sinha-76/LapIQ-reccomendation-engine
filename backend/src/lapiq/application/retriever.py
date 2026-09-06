"""Hybrid Retriever — combines pgvector cosine similarity with SQL budget & segment filtering."""

import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from lapiq.domain.interfaces.repository import VariantRepositoryInterface
from lapiq.domain.recommendation.models import UserPreferences
from lapiq.infrastructure.database.models import Laptop, Variant

logger = logging.getLogger(__name__)

# ARCHITECTURE NOTE: At 200 rows, SQL filtering alone is faster.
# pgvector demonstrates a retrieval architecture that scales to 10,000+
# variants without structural changes. This is an intentional design decision.


class HybridRetriever:
    """
    Application-layer retriever that combines SQL relational filtering with
    pgvector cosine similarity search on the variant embedding column.

    Retrieval flow:
    1. Filter variants by max price (budget + 5% buffer) and minimum RAM.
    2. Filter by laptop availability and target segment.
    3. If query_embedding is supplied, order candidates by vector cosine distance.
    4. Otherwise, order candidates by current price ascending.
    """

    def __init__(
        self,
        session: AsyncSession,
        variant_repo: VariantRepositoryInterface | None = None,
    ) -> None:
        self.session = session
        self.variant_repo = variant_repo

    async def retrieve_candidates(
        self,
        preferences: UserPreferences,
        query_embedding: list[float] | None = None,
        limit: int = 50,
    ) -> Sequence[Variant]:
        """
        Retrieve candidate variants using hybrid relational + vector similarity retrieval.

        Args:
            preferences: Parsed user preferences (budget, segment, min RAM).
            query_embedding: Optional 1536-dim float vector for semantic search.
            limit: Maximum candidate pool size to pass to deterministic scoring.

        Returns:
            Sequence of Variant entity models with eager-loaded laptop/CPU/GPU models.
        """
        max_budget = int(preferences.budget_inr * 1.05)

        query = (
            select(Variant)
            .join(Variant.laptop)
            .options(
                selectinload(Variant.laptop),
                selectinload(Variant.cpu),
                selectinload(Variant.gpu),
                selectinload(Variant.display),
            )
            .where(
                Variant.current_price_inr <= max_budget,
                Variant.ram_gb >= preferences.min_ram_gb,
                Variant.is_in_stock.is_(True),
                Laptop.is_available.is_(True),
            )
        )

        if preferences.target_segment:
            query = query.where(Laptop.target_segment == preferences.target_segment)

        if query_embedding is not None and hasattr(Variant, "embedding"):
            # Use pgvector cosine distance operator (<=>)
            query = query.order_by(Variant.embedding.cosine_distance(query_embedding))
        else:
            query = query.order_by(Variant.current_price_inr.asc())

        query = query.limit(limit)

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(
                "hybrid_retrieval_failed",
                extra={
                    "error_type": type(e).__name__,
                    "error": str(e),
                    "budget": preferences.budget_inr,
                    "segment": preferences.target_segment,
                },
            )
            raise
