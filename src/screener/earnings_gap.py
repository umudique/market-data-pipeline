"""Earnings gap screener use case — reads normalized trusted bars only."""

from __future__ import annotations

from src.domain import EarningsGapResult, EarningsGapScreenerRequest


class EarningsGapQueryService:
    def run(self, request: EarningsGapScreenerRequest) -> list[EarningsGapResult]:
        raise NotImplementedError
