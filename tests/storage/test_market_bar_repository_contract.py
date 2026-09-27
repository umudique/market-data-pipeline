from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.domain import MarketBar, ValidationStatus
from src.storage.models import Base
from src.storage.repositories import MarketBarRepository

pytestmark = pytest.mark.integration


@pytest.fixture
def engine(postgres_url: str) -> Iterator[Engine]:
    db_engine = create_engine(postgres_url)
    Base.metadata.create_all(db_engine)
    try:
        yield db_engine
    finally:
        Base.metadata.drop_all(db_engine)
        db_engine.dispose()


def _bar(batch_id: uuid.UUID, timestamp: datetime | None = None) -> MarketBar:
    return MarketBar(
        ticker="AAPL",
        timestamp=timestamp or datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        interval="1m",
        open=100.0,
        high=102.0,
        low=99.0,
        close=101.0,
        volume=1200.0,
        source="yfinance",
        ingestion_batch_id=batch_id,
        validated=True,
        validation_status=ValidationStatus.VALID,
    )


def test_market_bar_repository_list_tickers_returns_distinct_sorted(engine: Engine) -> None:
    batch_id = uuid.uuid4()
    bars = [
        MarketBar(
            ticker=t,
            timestamp=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
            interval="1d",
            open=100.0,
            high=102.0,
            low=99.0,
            close=101.0,
            volume=1000.0,
            source="yfinance",
            ingestion_batch_id=batch_id,
            validated=True,
            validation_status=ValidationStatus.VALID,
        )
        for t in ["TSLA", "AAPL", "MSFT", "AAPL"]  # AAPL duplicate intentional
    ]

    with Session(engine) as session:
        repository = MarketBarRepository(session)
        repository.upsert_all(bars)
        session.commit()
        tickers = repository.list_tickers()

    assert tickers == ["AAPL", "MSFT", "TSLA"]


def test_market_bar_repository_upsert_counts_idempotent_conflicts(engine: Engine) -> None:
    batch_id = uuid.uuid4()
    bars = [
        _bar(batch_id, datetime(2026, 1, 2, 14, 30, tzinfo=UTC)),
        _bar(batch_id, datetime(2026, 1, 2, 14, 31, tzinfo=UTC)),
    ]

    with Session(engine) as session:
        repository = MarketBarRepository(session)

        assert repository.upsert_all(bars) == 0
        session.commit()
        assert repository.upsert_all(bars) == 2
        session.commit()

        stored = repository.list_by_ticker(
            "AAPL",
            start=datetime(2026, 1, 2, 14, 29, tzinfo=UTC),
            end=datetime(2026, 1, 2, 14, 32, tzinfo=UTC),
        )

    assert stored == bars
    assert all(bar.validated for bar in stored)
