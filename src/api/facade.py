"""Application-service facade for API routes."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.domain import EarningsGapScreenerRequest, IngestionBatch, MarketBar, ValidationIssue
from src.screener.earnings_gap import EarningsGapQueryService

from .schemas import (
    BatchSummarySchema,
    EarningsGapResultSchema,
    MarketBarSchema,
    MarketDataResponseSchema,
    ScreenerRequestSchema,
    ScreenerResponseSchema,
    ValidationIssueSummarySchema,
)


class ApplicationServiceFacade:
    def __init__(self, uow: Any) -> None:
        self._uow = uow

    def run_earnings_gap(self, request: ScreenerRequestSchema) -> ScreenerResponseSchema:
        results = EarningsGapQueryService(self._uow.screener).run(
            EarningsGapScreenerRequest(
                start_date=request.start_date,
                end_date=request.end_date,
                minimum_gap=request.minimum_gap,
                minimum_volume=request.minimum_volume,
                ticker_universe=request.ticker_universe,
            )
        )
        mapped = [
            EarningsGapResultSchema(
                ticker=result.ticker,
                date=result.date,
                gap_percent=result.gap_percent,
                relative_volume=result.relative_volume,
                close_return=result.close_return,
                validated=result.validated,
            )
            for result in results
        ]
        return ScreenerResponseSchema(results=mapped, total=len(mapped))

    def list_market_data(
        self,
        ticker: str,
        start: datetime,
        end: datetime,
        interval: str,
        limit: int,
    ) -> MarketDataResponseSchema:
        bars = self._uow.market_bars.list_by_ticker(ticker, start, end)
        filtered_bars = [bar for bar in bars if bar.interval == interval][:limit]
        mapped = [self._market_bar_schema(bar) for bar in filtered_bars]
        return MarketDataResponseSchema(bars=mapped, total=len(mapped))

    def list_batches(self, limit: int) -> list[BatchSummarySchema]:
        return [
            self._batch_schema(batch) for batch in self._uow.ingestion_batches.list_recent(limit)
        ]

    def list_issues(self, batch_id: uuid.UUID) -> list[ValidationIssueSummarySchema]:
        return [
            self._validation_issue_schema(issue)
            for issue in self._uow.validation_issues.list_by_batch(batch_id)
        ]

    @staticmethod
    def _market_bar_schema(bar: MarketBar) -> MarketBarSchema:
        return MarketBarSchema(
            ticker=bar.ticker,
            timestamp=bar.timestamp,
            interval=bar.interval,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            validated=bar.validated,
        )

    @staticmethod
    def _batch_schema(batch: IngestionBatch) -> BatchSummarySchema:
        return BatchSummarySchema(
            batch_id=str(batch.batch_id),
            source=batch.source,
            status=batch.status.value,
            records_received=batch.records_received,
            records_valid=batch.records_valid,
            records_invalid=batch.records_invalid,
            duplicate_count=batch.duplicate_count,
            missing_interval_count=batch.missing_interval_count,
            stale_response_count=batch.stale_response_count,
        )

    @staticmethod
    def _validation_issue_schema(issue: ValidationIssue) -> ValidationIssueSummarySchema:
        return ValidationIssueSummarySchema(
            issue_type=issue.issue_type.value,
            severity=issue.severity.value,
            ticker=issue.ticker,
            timestamp=issue.timestamp,
            details=issue.details,
        )
