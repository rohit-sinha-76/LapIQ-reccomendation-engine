"""SQLAlchemy 2.x ORM models for LapIQ database schema."""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class CPU(Base):
    """CPU hardware specifications."""

    __tablename__ = "cpus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    core_count: Mapped[int] = mapped_column(Integer, nullable=False)
    thread_count: Mapped[int] = mapped_column(Integer, nullable=False)
    base_clock_ghz: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    boost_clock_ghz: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    benchmark_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GPU(Base):
    """GPU hardware specifications."""

    __tablename__ = "gpus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    vram_gb: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_integrated: Mapped[bool] = mapped_column(nullable=False, default=False)
    benchmark_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Display(Base):
    """Display panel specifications."""

    __tablename__ = "displays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    size_inches: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    resolution: Mapped[str] = mapped_column(String(50), nullable=False)
    refresh_rate_hz: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    panel_type: Mapped[str] = mapped_column(String(50), nullable=False, default="IPS")
    is_touchscreen: Mapped[bool] = mapped_column(nullable=False, default=False)
    brightness_nits: Mapped[int] = mapped_column(Integer, nullable=False, default=250)


class Laptop(Base):
    """Laptop entity representing a base laptop model."""

    __tablename__ = "laptops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    series: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_segment: Mapped[str] = mapped_column(String(50), nullable=False)
    is_available: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    variants: Mapped[list["Variant"]] = relationship("Variant", back_populates="laptop")


class Variant(Base):
    """Specific SKU/configuration variant of a laptop."""

    __tablename__ = "variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    laptop_id: Mapped[int] = mapped_column(Integer, ForeignKey("laptops.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    cpu_id: Mapped[int] = mapped_column(Integer, ForeignKey("cpus.id"), nullable=False)
    gpu_id: Mapped[int] = mapped_column(Integer, ForeignKey("gpus.id"), nullable=False)
    display_id: Mapped[int] = mapped_column(Integer, ForeignKey("displays.id"), nullable=False)
    ram_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    os_type: Mapped[str] = mapped_column(String(50), nullable=False, default="Windows 11")
    current_price_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    is_in_stock: Mapped[bool] = mapped_column(nullable=False, default=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    laptop: Mapped["Laptop"] = relationship("Laptop", back_populates="variants")
    cpu: Mapped["CPU"] = relationship("CPU")
    gpu: Mapped["GPU"] = relationship("GPU")
    display: Mapped["Display"] = relationship("Display")
    prices: Mapped[list["PriceSnapshot"]] = relationship("PriceSnapshot", back_populates="variant")


class PriceSnapshot(Base):
    """Historical price snapshot for a variant."""

    __tablename__ = "price_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("variants.id"), nullable=False)
    price_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    seller_name: Mapped[str] = mapped_column(String(100), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    variant: Mapped["Variant"] = relationship("Variant", back_populates="prices")


class ReviewEvidence(Base):
    """Structured evidence aggregated from external sources (reviews, YouTube, Reddit)."""

    __tablename__ = "review_evidences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    laptop_id: Mapped[int] = mapped_column(Integer, ForeignKey("laptops.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
