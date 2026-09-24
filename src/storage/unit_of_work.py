"""Transaction boundary coordination across related persistence operations."""

from __future__ import annotations

from types import TracebackType

from sqlalchemy.orm import Session

from src.storage.repositories import (
    IngestionBatchRepository,
    MarketBarRepository,
    RawMarketDataRepository,
    ScreenerQueryRepository,
    ValidationIssueRepository,
)


class UnitOfWork:
    session: Session
    raw_market_data: RawMarketDataRepository
    ingestion_batches: IngestionBatchRepository
    validation_issues: ValidationIssueRepository
    market_bars: MarketBarRepository
    screener: ScreenerQueryRepository

    def __enter__(self) -> UnitOfWork:
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError
