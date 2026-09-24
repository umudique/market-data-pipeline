"""Repository layer — all SQL in one place, no domain logic."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from src.domain import EarningsGapResult, IngestionBatch, MarketBar, ValidationIssue


class RawMarketDataRepository:
    def __init__(self, session: Session) -> None:
        raise NotImplementedError

    def save_raw(self, batch_id: uuid.UUID, source: str, ticker: str, payload: str) -> None:
        raise NotImplementedError


class IngestionBatchRepository:
    def __init__(self, session: Session) -> None:
        raise NotImplementedError

    def save(self, batch: IngestionBatch) -> None:
        raise NotImplementedError

    def update(self, batch: IngestionBatch) -> None:
        raise NotImplementedError

    def get_by_id(self, batch_id: uuid.UUID) -> IngestionBatch | None:
        raise NotImplementedError

    def list_recent(self, limit: int = 20) -> list[IngestionBatch]:
        raise NotImplementedError


class ValidationIssueRepository:
    def __init__(self, session: Session) -> None:
        raise NotImplementedError

    def save_all(self, issues: list[ValidationIssue]) -> None:
        raise NotImplementedError

    def list_by_batch(self, batch_id: uuid.UUID) -> list[ValidationIssue]:
        raise NotImplementedError


class MarketBarRepository:
    def __init__(self, session: Session) -> None:
        raise NotImplementedError

    def upsert_all(self, bars: list[MarketBar]) -> int:
        """Insert bars; return count of idempotent conflicts ignored."""
        raise NotImplementedError

    def list_by_ticker(
        self,
        ticker: str,
        start: datetime,
        end: datetime,
    ) -> list[MarketBar]:
        raise NotImplementedError


class ScreenerQueryRepository:
    def __init__(self, session: Session) -> None:
        raise NotImplementedError

    def earnings_gap_candidates(
        self,
        tickers: list[str],
        start: datetime,
        end: datetime,
        lookback_days: int,
    ) -> list[EarningsGapResult]:
        raise NotImplementedError
