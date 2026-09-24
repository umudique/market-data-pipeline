"""Transaction boundary coordination across related persistence operations."""

from __future__ import annotations

from collections.abc import Callable
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
    session_factory: Callable[[], Session] | None

    def __init__(self) -> None:
        self.session_factory = None

    def __enter__(self) -> UnitOfWork:
        session_factory = self.session_factory
        if session_factory is None:
            from src.storage.database import SessionFactory

            session_factory = SessionFactory

        self.session = session_factory()
        self.raw_market_data = RawMarketDataRepository(self.session)
        self.ingestion_batches = IngestionBatchRepository(self.session)
        self.validation_issues = ValidationIssueRepository(self.session)
        self.market_bars = MarketBarRepository(self.session)
        self.screener = ScreenerQueryRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
