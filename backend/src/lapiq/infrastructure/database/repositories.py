"""PostgreSQL implementations of domain repository interfaces using SQLAlchemy 2.x."""

import logging
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from lapiq.domain.interfaces.repository import (
    EvidenceRepositoryInterface,
    LaptopRepositoryInterface,
    VariantRepositoryInterface,
)
from lapiq.infrastructure.database.models import Laptop, ReviewEvidence, Variant

logger = logging.getLogger(__name__)


class PostgresLaptopRepository(LaptopRepositoryInterface):
    """PostgreSQL database repository for Laptop entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, laptop_id: int) -> Laptop | None:
        query = select(Laptop).options(selectinload(Laptop.variants)).where(Laptop.id == laptop_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_active(self) -> Sequence[Laptop]:
        query = (
            select(Laptop)
            .options(selectinload(Laptop.variants))
            .where(Laptop.is_available.is_(True))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_by_segment(self, segment: str) -> Sequence[Laptop]:
        query = (
            select(Laptop)
            .options(selectinload(Laptop.variants))
            .where(Laptop.target_segment == segment, Laptop.is_available.is_(True))
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class PostgresVariantRepository(VariantRepositoryInterface):
    """PostgreSQL database repository for Variant entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, variant_id: int) -> Variant | None:
        query = (
            select(Variant)
            .options(
                selectinload(Variant.laptop),
                selectinload(Variant.cpu),
                selectinload(Variant.gpu),
                selectinload(Variant.display),
            )
            .where(Variant.id == variant_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Variant | None:
        query = (
            select(Variant)
            .options(
                selectinload(Variant.laptop),
                selectinload(Variant.cpu),
                selectinload(Variant.gpu),
                selectinload(Variant.display),
            )
            .where(Variant.sku == sku)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_candidates(
        self,
        max_price: int,
        min_ram_gb: int = 8,
        segment: str | None = None,
    ) -> Sequence[Variant]:
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
                Variant.current_price_inr <= max_price,
                Variant.ram_gb >= min_ram_gb,
                Variant.is_in_stock.is_(True),
                Laptop.is_available.is_(True),
            )
        )
        if segment:
            query = query.where(Laptop.target_segment == segment)

        result = await self.session.execute(query)
        return result.scalars().all()


class PostgresEvidenceRepository(EvidenceRepositoryInterface):
    """
    PostgreSQL repository for ReviewEvidence entities.

    Provides structured evidence items for a given laptop to support
    the EvidenceAggregator in assembling explanation context.
    Evidence is read-only from the online path. Writing occurs only
    in the offline worker pipeline.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_evidence_for_laptop(self, laptop_id: int) -> Sequence[dict[str, str]]:
        """
        Retrieve all ReviewEvidence rows for a laptop, ordered by creation date descending.

        Returns normalized dicts with keys: source_type, summary_text, sentiment_score.
        Keys match the fields EvidenceAggregator expects when normalizing to structured items.
        """
        query = (
            select(ReviewEvidence)
            .where(ReviewEvidence.laptop_id == laptop_id)
            .order_by(ReviewEvidence.created_at.desc())
        )
        result = await self.session.execute(query)
        rows: Sequence[ReviewEvidence] = result.scalars().all()

        return [
            {
                "source_type": row.source_type,
                "summary_text": row.summary_text,
                "sentiment_score": str(row.sentiment_score),
            }
            for row in rows
        ]
