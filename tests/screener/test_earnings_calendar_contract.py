from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.screener.earnings_calendar import EarningsCalendarFetcher

pytestmark = pytest.mark.unit


def _fake_earnings_df(*datetimes: datetime) -> pd.DataFrame:
    idx = pd.DatetimeIndex([pd.Timestamp(dt) for dt in datetimes])
    return pd.DataFrame({"EPS Estimate": [None] * len(idx)}, index=idx)


class _FakeYFinance(ModuleType):
    """Minimal yfinance stub for unit tests."""

    def __init__(self, mock_ticker: Any) -> None:
        super().__init__("yfinance")
        self._mock_ticker = mock_ticker

    def Ticker(self, _symbol: str) -> Any:  # noqa: N802
        return self._mock_ticker


def _install_fake_yfinance(mock_ticker: Any) -> _FakeYFinance:
    fake = _FakeYFinance(mock_ticker)
    sys.modules["yfinance"] = fake
    return fake


def _uninstall_fake_yfinance() -> None:
    sys.modules.pop("yfinance", None)


def test_earnings_calendar_fetcher_returns_same_day_for_premarket_announcement() -> None:
    # Hour 8 = pre-market → gap date is announcement date itself (Monday)
    announcement = datetime(2026, 1, 5, 8, 0, tzinfo=UTC)
    mock_ticker = MagicMock()
    mock_ticker.earnings_dates = _fake_earnings_df(announcement)
    _install_fake_yfinance(mock_ticker)
    try:
        gap_dates = EarningsCalendarFetcher().fetch_gap_dates(
            "AAPL", start=date(2026, 1, 1), end=date(2026, 1, 31)
        )
    finally:
        _uninstall_fake_yfinance()

    assert date(2026, 1, 5) in gap_dates


def test_earnings_calendar_fetcher_returns_next_weekday_for_postmarket_announcement() -> None:
    # Hour 16 = post-market Monday → gap shifts to Tuesday
    announcement = datetime(2026, 1, 5, 16, 0, tzinfo=UTC)
    mock_ticker = MagicMock()
    mock_ticker.earnings_dates = _fake_earnings_df(announcement)
    _install_fake_yfinance(mock_ticker)
    try:
        gap_dates = EarningsCalendarFetcher().fetch_gap_dates(
            "AAPL", start=date(2026, 1, 1), end=date(2026, 1, 31)
        )
    finally:
        _uninstall_fake_yfinance()

    assert date(2026, 1, 6) in gap_dates


def test_earnings_calendar_fetcher_skips_weekend_when_postmarket_falls_on_friday() -> None:
    # Post-market Friday → next weekday is Monday
    announcement = datetime(2026, 1, 2, 17, 0, tzinfo=UTC)
    mock_ticker = MagicMock()
    mock_ticker.earnings_dates = _fake_earnings_df(announcement)
    _install_fake_yfinance(mock_ticker)
    try:
        gap_dates = EarningsCalendarFetcher().fetch_gap_dates(
            "AAPL", start=date(2026, 1, 1), end=date(2026, 1, 31)
        )
    finally:
        _uninstall_fake_yfinance()

    assert date(2026, 1, 5) in gap_dates
    assert date(2026, 1, 3) not in gap_dates  # Saturday excluded


def test_earnings_calendar_fetcher_excludes_dates_outside_range() -> None:
    announcement = datetime(2026, 2, 5, 8, 0, tzinfo=UTC)
    mock_ticker = MagicMock()
    mock_ticker.earnings_dates = _fake_earnings_df(announcement)
    _install_fake_yfinance(mock_ticker)
    try:
        gap_dates = EarningsCalendarFetcher().fetch_gap_dates(
            "AAPL", start=date(2026, 1, 1), end=date(2026, 1, 31)
        )
    finally:
        _uninstall_fake_yfinance()

    assert gap_dates == set()


def test_earnings_calendar_fetcher_returns_empty_set_when_no_earnings_data() -> None:
    mock_ticker = MagicMock()
    mock_ticker.earnings_dates = None
    _install_fake_yfinance(mock_ticker)
    try:
        gap_dates = EarningsCalendarFetcher().fetch_gap_dates(
            "AAPL", start=date(2026, 1, 1), end=date(2026, 1, 31)
        )
    finally:
        _uninstall_fake_yfinance()

    assert gap_dates == set()
