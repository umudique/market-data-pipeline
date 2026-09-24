"""Screener metric calculations — gap %, relative volume, close return."""

from __future__ import annotations

from src.domain import MarketBar


class GapCalculator:
    def calculate(self, earnings_open: float, prior_close: float) -> float:
        """(earnings_open - prior_close) / prior_close * 100"""
        raise NotImplementedError


class RelativeVolumeCalculator:
    def __init__(self, lookback_days: int = 20) -> None:
        raise NotImplementedError

    def calculate(self, earnings_volume: float, historical_bars: list[MarketBar]) -> float:
        """earnings_volume / mean(volume over prior lookback_days)"""
        raise NotImplementedError


class CloseReturnCalculator:
    def calculate(self, earnings_open: float, earnings_close: float) -> float:
        """(earnings_close - earnings_open) / earnings_open * 100"""
        raise NotImplementedError
