"""Validate screener request parameters before execution."""

from __future__ import annotations

from src.domain import EarningsGapScreenerRequest


class ScreenerRequestValidator:
    def validate(self, request: EarningsGapScreenerRequest) -> None:
        """Raise ValueError on invalid parameters."""
        raise NotImplementedError
