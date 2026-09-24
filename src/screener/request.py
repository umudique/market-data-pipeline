"""Validate screener request parameters before execution."""

from __future__ import annotations

from src.domain import EarningsGapScreenerRequest


class ScreenerRequestValidator:
    def validate(self, request: EarningsGapScreenerRequest) -> None:
        """Raise ValueError on invalid parameters."""
        if request.end_date < request.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
