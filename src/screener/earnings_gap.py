"""Earnings gap screener use case — reads normalized trusted bars only."""

from __future__ import annotations

from typing import Any, cast

from src.domain import EarningsGapResult, EarningsGapScreenerRequest
from src.screener.request import ScreenerRequestValidator


class EarningsGapQueryService:
    def __init__(self, repository: Any) -> None:
        self._repository = repository

    def run(self, request: EarningsGapScreenerRequest) -> list[EarningsGapResult]:
        ScreenerRequestValidator().validate(request)
        return cast(
            list[EarningsGapResult],
            self._repository.earnings_gap_candidates(
                tickers=request.ticker_universe,
                start=request.start_date,
                end=request.end_date,
                lookback_days=20,
            ),
        )
