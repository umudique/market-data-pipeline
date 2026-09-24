"""Repository layer — all SQL in one place, no domain logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from src.domain import (
    BatchStatus,
    IngestionBatch,
    IssueSeverity,
    IssueType,
    MarketBar,
    ValidationIssue,
    ValidationStatus,
)
from src.storage.models import (
    IngestionBatchModel,
    MarketBarModel,
    RawMarketDataModel,
    ValidationIssueModel,
)


class RawMarketDataRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_raw(self, batch_id: uuid.UUID, source: str, ticker: str, payload: str) -> None:
        self._session.add(
            RawMarketDataModel(
                batch_id=batch_id,
                source=source,
                ticker=ticker,
                raw_payload=payload,
                received_at=datetime.now(UTC),
            )
        )


class IngestionBatchRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, batch: IngestionBatch) -> None:
        self._session.add(self._to_model(batch))

    def update(self, batch: IngestionBatch) -> None:
        model = self._session.get(IngestionBatchModel, batch.batch_id)
        if model is None:
            self.save(batch)
            return

        model.source = batch.source
        model.requested_range = batch.requested_range
        model.started_at = batch.started_at or datetime.now(UTC)
        model.completed_at = batch.completed_at
        model.status = batch.status.value
        model.records_received = batch.records_received
        model.records_valid = batch.records_valid
        model.records_invalid = batch.records_invalid
        model.duplicate_count = batch.duplicate_count
        model.missing_interval_count = batch.missing_interval_count
        model.stale_response_count = batch.stale_response_count
        model.idempotent_conflict_count = batch.idempotent_conflict_count

    def get_by_id(self, batch_id: uuid.UUID) -> IngestionBatch | None:
        model = self._session.get(IngestionBatchModel, batch_id)
        if model is None:
            return None
        return self._to_domain(model)

    def list_recent(self, limit: int = 20) -> list[IngestionBatch]:
        statement = (
            select(IngestionBatchModel).order_by(IngestionBatchModel.started_at.desc()).limit(limit)
        )
        return [self._to_domain(model) for model in self._session.scalars(statement)]

    @staticmethod
    def _to_model(batch: IngestionBatch) -> IngestionBatchModel:
        return IngestionBatchModel(
            batch_id=batch.batch_id,
            source=batch.source,
            requested_range=batch.requested_range,
            started_at=batch.started_at or datetime.now(UTC),
            completed_at=batch.completed_at,
            status=batch.status.value,
            records_received=batch.records_received,
            records_valid=batch.records_valid,
            records_invalid=batch.records_invalid,
            duplicate_count=batch.duplicate_count,
            missing_interval_count=batch.missing_interval_count,
            stale_response_count=batch.stale_response_count,
            idempotent_conflict_count=batch.idempotent_conflict_count,
        )

    @staticmethod
    def _to_domain(model: IngestionBatchModel) -> IngestionBatch:
        return IngestionBatch(
            batch_id=model.batch_id,
            source=model.source,
            requested_range=model.requested_range,
            started_at=model.started_at,
            completed_at=model.completed_at,
            status=BatchStatus(model.status),
            records_received=model.records_received,
            records_valid=model.records_valid,
            records_invalid=model.records_invalid,
            duplicate_count=model.duplicate_count,
            missing_interval_count=model.missing_interval_count,
            stale_response_count=model.stale_response_count,
            idempotent_conflict_count=model.idempotent_conflict_count,
        )


class ValidationIssueRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_all(self, issues: list[ValidationIssue]) -> None:
        self._session.add_all([self._to_model(issue) for issue in issues])

    def list_by_batch(self, batch_id: uuid.UUID) -> list[ValidationIssue]:
        statement = (
            select(ValidationIssueModel)
            .where(ValidationIssueModel.batch_id == batch_id)
            .order_by(ValidationIssueModel.id)
        )
        return [self._to_domain(model) for model in self._session.scalars(statement)]

    @staticmethod
    def _to_model(issue: ValidationIssue) -> ValidationIssueModel:
        return ValidationIssueModel(
            batch_id=issue.batch_id,
            issue_type=issue.issue_type.value,
            severity=issue.severity.value,
            ticker=issue.ticker,
            timestamp=issue.timestamp,
            source=issue.source,
            details=issue.details,
        )

    @staticmethod
    def _to_domain(model: ValidationIssueModel) -> ValidationIssue:
        return ValidationIssue(
            issue_type=IssueType(model.issue_type),
            severity=IssueSeverity(model.severity),
            ticker=model.ticker,
            timestamp=model.timestamp,
            batch_id=model.batch_id,
            source=model.source,
            details=model.details,
        )


class MarketBarRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_all(self, bars: list[MarketBar]) -> int:
        """Insert bars; return count of idempotent conflicts ignored."""
        if not bars:
            return 0

        rows = [self._to_row(bar) for bar in bars]
        statement = (
            insert(MarketBarModel)
            .values(rows)
            .on_conflict_do_nothing(index_elements=["ticker", "timestamp", "interval", "source"])
        )
        result = cast(CursorResult[object], self._session.execute(statement))
        inserted_count = result.rowcount or 0
        return len(bars) - inserted_count

    def list_by_ticker(
        self,
        ticker: str,
        start: datetime,
        end: datetime,
    ) -> list[MarketBar]:
        statement = (
            select(MarketBarModel)
            .where(
                MarketBarModel.ticker == ticker,
                MarketBarModel.timestamp >= start,
                MarketBarModel.timestamp <= end,
            )
            .order_by(MarketBarModel.timestamp)
        )
        return [self._to_domain(model) for model in self._session.scalars(statement)]

    @staticmethod
    def _to_row(bar: MarketBar) -> dict[str, object]:
        return {
            "ticker": bar.ticker,
            "timestamp": bar.timestamp,
            "interval": bar.interval,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
            "source": bar.source,
            "ingestion_batch_id": bar.ingestion_batch_id,
            "validated": bar.validated,
            "validation_status": bar.validation_status.value,
        }

    @staticmethod
    def _to_domain(model: MarketBarModel) -> MarketBar:
        return MarketBar(
            ticker=model.ticker,
            timestamp=model.timestamp,
            interval=model.interval,
            open=model.open,
            high=model.high,
            low=model.low,
            close=model.close,
            volume=model.volume,
            source=model.source,
            ingestion_batch_id=model.ingestion_batch_id,
            validated=model.validated,
            validation_status=ValidationStatus(model.validation_status),
        )


class ScreenerQueryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def earnings_gap_candidates(
        self,
        tickers: list[str],
        start: datetime,
        end: datetime,
        lookback_days: int,
    ) -> list[MarketBar]:
        statement = (
            select(MarketBarModel)
            .where(
                MarketBarModel.ticker.in_(tickers),
                MarketBarModel.timestamp >= start,
                MarketBarModel.timestamp <= end,
                MarketBarModel.validated.is_(True),
            )
            .order_by(MarketBarModel.ticker, MarketBarModel.timestamp)
        )
        return [MarketBarRepository._to_domain(model) for model in self._session.scalars(statement)]
