"""Earnings gap screener use case — reads normalized trusted bars only."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.domain import EarningsGapResult, EarningsGapScreenerRequest, MarketBar
from src.screener.calculations import (
    CloseReturnCalculator,
    GapCalculator,
    RelativeVolumeCalculator,
)
from src.screener.request import ScreenerRequestValidator
from src.screener.result import ScreenerResultMapper


class EarningsGapQueryService:
    def __init__(self, repository: Any) -> None:
        self._repository = repository

    def run(self, request: EarningsGapScreenerRequest) -> list[EarningsGapResult]:
        ScreenerRequestValidator().validate(request)
        bars: list[MarketBar] = self._repository.earnings_gap_candidates(
            tickers=request.ticker_universe,
            start=request.start_date,
            end=request.end_date,
            lookback_days=20,
        )

        bars_by_ticker: dict[str, list[MarketBar]] = defaultdict(list)
        for bar in bars:
            bars_by_ticker[bar.ticker].append(bar)

        gap_calc = GapCalculator()
        rvol_calc = RelativeVolumeCalculator(lookback_days=20)
        cr_calc = CloseReturnCalculator()
        mapper = ScreenerResultMapper()

        results: list[EarningsGapResult] = []
        for ticker_bars in bars_by_ticker.values():
            ticker_bars.sort(key=lambda b: b.timestamp)
            for i, bar in enumerate(ticker_bars):
                prior_close = ticker_bars[i - 1].close if i > 0 else bar.open
                historical = ticker_bars[:i] if i > 0 else []

                gap_pct = gap_calc.calculate(bar.open, prior_close)
                try:
                    rvol = rvol_calc.calculate(bar.volume, historical)
                except ValueError:
                    rvol = 0.0
                cr = cr_calc.calculate(bar.open, bar.close)

                results.append(mapper.map(bar, gap_pct, rvol, cr))

        return results
