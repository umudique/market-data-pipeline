"""Earnings gap screener use case — reads normalized trusted bars only."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from src.domain import EarningsGapResult, EarningsGapScreenerRequest, MarketBar
from src.screener.calculations import (
    CloseReturnCalculator,
    GapCalculator,
    RelativeVolumeCalculator,
)
from src.screener.earnings_calendar import EarningsCalendarFetcher
from src.screener.request import ScreenerRequestValidator
from src.screener.result import ScreenerResultMapper


class EarningsGapQueryService:
    def __init__(
        self,
        repository: Any,
        calendar_fetcher: EarningsCalendarFetcher | None = None,
    ) -> None:
        self._repository = repository
        self._calendar_fetcher = calendar_fetcher or EarningsCalendarFetcher()

    def run(self, request: EarningsGapScreenerRequest) -> list[EarningsGapResult]:
        ScreenerRequestValidator().validate(request)
        bars: list[MarketBar] = self._repository.earnings_gap_candidates(
            tickers=request.ticker_universe,
            start=request.start_date,
            end=request.end_date,
            lookback_days=20,
            interval="1d",
        )

        start_date = request.start_date.date()
        end_date = request.end_date.date()

        gap_dates_by_ticker: dict[str, set[date]] = {
            ticker: self._calendar_fetcher.fetch_gap_dates(ticker, start_date, end_date)
            for ticker in request.ticker_universe
        }

        bars_by_ticker: dict[str, list[MarketBar]] = defaultdict(list)
        for bar in bars:
            bars_by_ticker[bar.ticker].append(bar)

        gap_calc = GapCalculator()
        rvol_calc = RelativeVolumeCalculator(lookback_days=20)
        cr_calc = CloseReturnCalculator()
        mapper = ScreenerResultMapper()

        results: list[EarningsGapResult] = []
        for ticker, ticker_bars in bars_by_ticker.items():
            ticker_bars.sort(key=lambda b: b.timestamp)
            gap_dates = gap_dates_by_ticker.get(ticker, set())

            for i, bar in enumerate(ticker_bars):
                if bar.timestamp.date() not in gap_dates:
                    continue

                prior_close = ticker_bars[i - 1].close if i > 0 else bar.open
                historical = ticker_bars[max(0, i - 20) : i]

                gap_pct = gap_calc.calculate(bar.open, prior_close)
                if abs(gap_pct) < request.minimum_gap:
                    continue

                try:
                    rvol = rvol_calc.calculate(bar.volume, historical)
                except ValueError:
                    rvol = 0.0
                if bar.volume < request.minimum_volume:
                    continue

                cr = cr_calc.calculate(bar.open, bar.close)
                results.append(mapper.map(bar, gap_pct, rvol, cr))

        return results
