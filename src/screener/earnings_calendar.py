"""Fetch earnings announcement dates and derive expected gap days."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


class EarningsCalendarFetcher:
    def fetch_gap_dates(self, ticker: str, start: date, end: date) -> set[date]:
        """Return dates where an earnings gap may appear for *ticker*.

        Earnings announced after noon (post-market) → gap shows next calendar
        day. Earnings announced before noon (pre-market) → gap shows same day.
        """
        import yfinance as yf

        earnings_dates: Any = yf.Ticker(ticker).earnings_dates  # let network errors propagate
        if earnings_dates is None or earnings_dates.empty:
            return set()

        gap_dates: set[date] = set()
        for ts in earnings_dates.index:
            try:
                dt = ts.to_pydatetime()
            except Exception:
                continue
            d = dt.date()
            if dt.hour >= 12:
                d += timedelta(days=1)
                while d.weekday() >= 5:
                    d += timedelta(days=1)
            if start <= d <= end:
                gap_dates.add(d)
        return gap_dates
