"""SQLAlchemy ORM models — persistence concerns only, no domain logic."""

from __future__ import annotations

import uuid

from sqlalchemy import UUID, BigInteger, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IngestionBatchModel(Base):
    __tablename__ = "ingestion_batches"

    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    source: Mapped[str] = mapped_column(String(64))
    requested_range: Mapped[str] = mapped_column(String(128))
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    records_received: Mapped[int] = mapped_column(Integer, default=0)
    records_valid: Mapped[int] = mapped_column(Integer, default=0)
    records_invalid: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)
    missing_interval_count: Mapped[int] = mapped_column(Integer, default=0)
    stale_response_count: Mapped[int] = mapped_column(Integer, default=0)
    idempotent_conflict_count: Mapped[int] = mapped_column(Integer, default=0)


class RawMarketDataModel(Base):
    __tablename__ = "raw_market_data"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    source: Mapped[str] = mapped_column(String(64))
    ticker: Mapped[str] = mapped_column(String(32))
    raw_payload: Mapped[str] = mapped_column(Text)
    received_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class ValidationIssueModel(Base):
    __tablename__ = "validation_issues"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    issue_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))
    ticker: Mapped[str] = mapped_column(String(32))
    timestamp: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(64))
    details: Mapped[str] = mapped_column(Text, default="")


class MarketBarModel(Base):
    __tablename__ = "market_bars"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(32))
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    interval: Mapped[str] = mapped_column(String(16))
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(64))
    ingestion_batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    validated: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_status: Mapped[str] = mapped_column(String(16), default="VALID")

    __table_args__ = (
        # ADR-004: idempotency enforced at DB boundary
        {"UniqueConstraint": ("ticker", "timestamp", "interval", "source")},
    )
