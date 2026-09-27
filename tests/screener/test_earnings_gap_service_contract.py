from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime

import pytest

from src.domain import (
    EarningsGapScreenerRequest,
    MarketBar,
    ValidationStatus,
)
from src.screener.earnings_gap import EarningsGapQueryService

pytestmark = pytest.mark.unit


@dataclass
class FakeRepository:
    bars: list[MarketBar]
    calls: list[tuple[list[str], datetime, datetime, int]] = field(default_factory=list)

    def earnings_gap_candidates(
        self,
        tickers: list[str],
        start: datetime,
        end: datetime,
        lookback_days: int,
        interval: str = "1d",
    ) -> list[MarketBar]:
        self.calls.append((tickers, start, end, lookback_days))
        return self.bars


@dataclass
class FakeCalendarFetcher:
    gap_dates: dict[str, set[date]] = field(default_factory=dict)

    def fetch_gap_dates(self, ticker: str, start: date, end: date) -> set[date]:
        return self.gap_dates.get(ticker, set())


def _bar(
    ticker: str,
    timestamp: datetime,
    open_: float,
    close: float,
    volume: float,
) -> MarketBar:
    return MarketBar(
        ticker=ticker,
        timestamp=timestamp,
        interval="1d",
        open=open_,
        high=close,
        low=open_,
        close=close,
        volume=volume,
        source="yfinance",
        ingestion_batch_id=uuid.uuid4(),
        validated=True,
        validation_status=ValidationStatus.VALID,
    )


def _request() -> EarningsGapScreenerRequest:
    return EarningsGapScreenerRequest(
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        end_date=datetime(2026, 1, 3, tzinfo=UTC),
        minimum_gap=5.0,
        minimum_volume=1_000_000.0,
        ticker_universe=["AAPL"],
    )


def test_earnings_gap_query_service_returns_empty_list_from_empty_repository() -> None:
    repository = FakeRepository(bars=[])
    calendar = FakeCalendarFetcher(gap_dates={"AAPL": {date(2026, 1, 2)}})

    result = EarningsGapQueryService(repository, calendar).run(_request())

    assert result == []
    assert repository.calls == [
        (
            ["AAPL"],
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2026, 1, 3, tzinfo=UTC),
            20,
        )
    ]


def test_earnings_gap_query_service_computes_metrics_via_calculators() -> None:
    # prior bar: close=100.0, volume=1_000_000
    # earnings bar: open=110.0 → gap=10%, close=115.5 → close_return=5%, volume=2_000_000 → rvol=2.0
    prior = _bar("AAPL", datetime(2026, 1, 1, tzinfo=UTC), 95.0, 100.0, 1_000_000.0)
    earnings = _bar("AAPL", datetime(2026, 1, 2, tzinfo=UTC), 110.0, 115.5, 2_000_000.0)
    repository = FakeRepository(bars=[prior, earnings])
    calendar = FakeCalendarFetcher(gap_dates={"AAPL": {date(2026, 1, 2)}})

    results = EarningsGapQueryService(repository, calendar).run(_request())

    earnings_row = next(r for r in results if r.date == datetime(2026, 1, 2, tzinfo=UTC))
    assert earnings_row.ticker == "AAPL"
    assert earnings_row.validated is True
    assert earnings_row.gap_percent == pytest.approx(10.0)
    assert earnings_row.relative_volume == pytest.approx(2.0)
    assert earnings_row.close_return == pytest.approx(5.0)


def test_earnings_gap_query_service_results_contain_only_validated_bars() -> None:
    bar = _bar("AAPL", datetime(2026, 1, 2, tzinfo=UTC), 100.0, 105.0, 1_000_000.0)
    repository = FakeRepository(bars=[bar])
    calendar = FakeCalendarFetcher(gap_dates={"AAPL": {date(2026, 1, 2)}})

    results = EarningsGapQueryService(repository, calendar).run(_request())

    assert all(row.validated for row in results)
