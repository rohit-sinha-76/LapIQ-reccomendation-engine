"""Initial database schema migration for LapIQ.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-21 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create cpus table
    op.create_table(
        'cpus',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('brand', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('core_count', sa.Integer(), nullable=False),
        sa.Column('thread_count', sa.Integer(), nullable=False),
        sa.Column('base_clock_ghz', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('boost_clock_ghz', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('benchmark_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create gpus table
    op.create_table(
        'gpus',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('brand', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('vram_gb', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_integrated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('benchmark_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create displays table
    op.create_table(
        'displays',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('size_inches', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('resolution', sa.String(length=50), nullable=False),
        sa.Column('refresh_rate_hz', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('panel_type', sa.String(length=50), nullable=False, server_default='IPS'),
        sa.Column('is_touchscreen', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('brightness_nits', sa.Integer(), nullable=False, server_default='250'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create laptops table
    op.create_table(
        'laptops',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=False),
        sa.Column('model_name', sa.String(length=200), nullable=False),
        sa.Column('series', sa.String(length=100), nullable=True),
        sa.Column('target_segment', sa.String(length=50), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create variants table
    op.create_table(
        'variants',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('laptop_id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('cpu_id', sa.Integer(), nullable=False),
        sa.Column('gpu_id', sa.Integer(), nullable=False),
        sa.Column('display_id', sa.Integer(), nullable=False),
        sa.Column('ram_gb', sa.Integer(), nullable=False),
        sa.Column('storage_gb', sa.Integer(), nullable=False),
        sa.Column('weight_kg', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('os_type', sa.String(length=50), nullable=False, server_default='Windows 11'),
        sa.Column('current_price_inr', sa.Integer(), nullable=False),
        sa.Column('is_in_stock', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.ForeignKeyConstraint(['laptop_id'], ['laptops.id'], ),
        sa.ForeignKeyConstraint(['cpu_id'], ['cpus.id'], ),
        sa.ForeignKeyConstraint(['gpu_id'], ['gpus.id'], ),
        sa.ForeignKeyConstraint(['display_id'], ['displays.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku')
    )

    # Create price_snapshots table
    op.create_table(
        'price_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('variant_id', sa.Integer(), nullable=False),
        sa.Column('price_inr', sa.Integer(), nullable=False),
        sa.Column('seller_name', sa.String(length=100), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create review_evidences table
    op.create_table(
        'review_evidences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('laptop_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('sentiment_score', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['laptop_id'], ['laptops.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('review_evidences')
    op.drop_table('price_snapshots')
    op.drop_table('variants')
    op.drop_table('laptops')
    op.drop_table('displays')
    op.drop_table('gpus')
    op.drop_table('cpus')
