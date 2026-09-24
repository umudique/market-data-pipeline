from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from src.domain import EarningsGapResult, EarningsGapScreenerRequest
from src.screener.earnings_gap import EarningsGapQueryService

pytestmark = pytest.mark.unit


@dataclass
class FakeRepository:
    results: list[EarningsGapResult]
    calls: list[tuple[list[str], datetime, datetime, int]] = field(default_factory=list)

    def earnings_gap_candidates(
        self,
        tickers: list[str],
        start: datetime,
        end: datetime,
        lookback_days: int,
    ) -> list[EarningsGapResult]:
        self.calls.append((tickers, start, end, lookback_days))
        return self.results


def _request() -> EarningsGapScreenerRequest:
    return EarningsGapScreenerRequest(
        start_date=datetime(2026, 1, 2, tzinfo=UTC),
        end_date=datetime(2026, 1, 3, tzinfo=UTC),
        minimum_gap=5.0,
        minimum_volume=1_000_000.0,
        ticker_universe=["AAPL"],
    )


def test_earnings_gap_query_service_returns_empty_list_from_empty_repository() -> None:
    repository = FakeRepository(results=[])

    result = EarningsGapQueryService(repository).run(_request())

    assert result == []
    assert repository.calls == [
        (
            ["AAPL"],
            datetime(2026, 1, 2, tzinfo=UTC),
            datetime(2026, 1, 3, tzinfo=UTC),
            20,
        )
    ]


def test_earnings_gap_query_service_returns_validated_repository_results() -> None:
    expected = EarningsGapResult(
        ticker="AAPL",
        date=datetime(2026, 1, 2, tzinfo=UTC),
        gap_percent=10.0,
        relative_volume=2.0,
        close_return=5.0,
        validated=True,
    )
    repository = FakeRepository(results=[expected])

    result = EarningsGapQueryService(repository).run(_request())

    assert result == [expected]
    assert all(row.validated for row in result)
