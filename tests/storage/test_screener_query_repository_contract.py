from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.domain import ValidationStatus
from src.storage.models import Base, MarketBarModel
from src.storage.repositories import ScreenerQueryRepository

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


def _market_bar_model(ticker: str, validated: bool) -> MarketBarModel:
    return MarketBarModel(
        ticker=ticker,
        timestamp=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        interval="1m",
        open=100.0,
        high=102.0,
        low=99.0,
        close=101.0,
        volume=1200.0,
        source="yfinance",
        ingestion_batch_id=uuid.uuid4(),
        validated=validated,
        validation_status=ValidationStatus.VALID.value,
    )


def test_screener_query_repository_reads_only_validated_market_bars(engine: Engine) -> None:
    with Session(engine) as session:
        session.add_all(
            [
                _market_bar_model("AAPL", validated=True),
                _market_bar_model("MSFT", validated=False),
            ]
        )
        session.commit()

        repository = ScreenerQueryRepository(session)
        results = repository.earnings_gap_candidates(
            tickers=["AAPL", "MSFT"],
            start=datetime(2026, 1, 2, 0, 0, tzinfo=UTC),
            end=datetime(2026, 1, 3, 0, 0, tzinfo=UTC),
            lookback_days=20,
        )

    assert [result.ticker for result in results] == ["AAPL"]
    assert all(result.validated for result in results)


def test_screener_query_repository_returns_empty_list_when_filters_match_no_bars(
    engine: Engine,
) -> None:
    with Session(engine) as session:
        session.add(_market_bar_model("AAPL", validated=True))
        session.commit()

        repository = ScreenerQueryRepository(session)
        results = repository.earnings_gap_candidates(
            tickers=["TSLA"],
            start=datetime(2026, 1, 2, 0, 0, tzinfo=UTC),
            end=datetime(2026, 1, 3, 0, 0, tzinfo=UTC),
            lookback_days=20,
        )

    assert results == []
