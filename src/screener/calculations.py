"""Screener metric calculations — gap %, relative volume, close return."""

from __future__ import annotations

from statistics import StatisticsError, mean

from src.domain import MarketBar


class GapCalculator:
    def calculate(self, earnings_open: float, prior_close: float) -> float:
        """(earnings_open - prior_close) / prior_close * 100"""
        return (earnings_open - prior_close) / prior_close * 100


class RelativeVolumeCalculator:
    def __init__(self, lookback_days: int = 20) -> None:
        self.lookback_days = lookback_days

    def calculate(self, earnings_volume: float, historical_bars: list[MarketBar]) -> float:
        """earnings_volume / mean(volume over prior lookback_days)"""
        try:
            average_volume = mean(bar.volume for bar in historical_bars)
        except StatisticsError as exc:
            raise ValueError("historical_bars must not be empty") from exc

        return earnings_volume / average_volume


class CloseReturnCalculator:
    def calculate(self, earnings_open: float, earnings_close: float) -> float:
        """(earnings_close - earnings_open) / earnings_open * 100"""
        return (earnings_close - earnings_open) / earnings_open * 100
