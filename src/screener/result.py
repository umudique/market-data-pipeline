"""Map calculated screener values to final result shape."""

from __future__ import annotations

from src.domain import EarningsGapResult, MarketBar


class ScreenerResultMapper:
    def map(
        self,
        bar: MarketBar,
        gap_percent: float,
        relative_volume: float,
        close_return: float,
    ) -> EarningsGapResult:
        return EarningsGapResult(
            ticker=bar.ticker,
            date=bar.timestamp,
            gap_percent=gap_percent,
            relative_volume=relative_volume,
            close_return=close_return,
            validated=bar.validated,
        )
