"""add_ticker_universe_and_interval_to_ingestion_batches

Revision ID: a1b2c3d4e5f6
Revises: 3cdf0ab6e0e0
Create Date: 2026-09-27 14:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "3cdf0ab6e0e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingestion_batches",
        sa.Column("ticker_universe", sa.String(length=1024), nullable=False, server_default=""),
    )
    op.add_column(
        "ingestion_batches",
        sa.Column("interval", sa.String(length=16), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("ingestion_batches", "interval")
    op.drop_column("ingestion_batches", "ticker_universe")
