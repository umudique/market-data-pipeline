"""End-to-end ingestion sequence orchestration.

Contract:
    `IngestionCoordinator` coordinates ingestion only: create batch, enforce
    rate limit, execute bounded provider fetch, use optional cache, detect stale
    responses, persist raw source payloads, and hand records to validation.

Invariants:
    The coordinator never calls `yfinance` directly. It never normalizes data,
    never writes trusted `market_bars`, and never invokes screener or API code.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Protocol

from src.domain import BatchStatus, IngestionBatch, IngestionRequest, ValidationIssue


class BatchManagerProtocol(Protocol):
    def create(self, request: IngestionRequest) -> IngestionBatch: ...

    def record_counts(
        self,
        batch_id: uuid.UUID,
        *,
        received: int,
        valid: int,
        invalid: int,
        duplicates: int,
        missing_intervals: int,
        stale_responses: int,
        idempotent_conflicts: int,
    ) -> None: ...

    def mark_completed(self, batch_id: uuid.UUID, status: BatchStatus) -> None: ...


class RateLimitProtocol(Protocol):
    def acquire(self) -> None: ...


class RetryPolicyProtocol(Protocol):
    def execute(
        self,
        fn: object,
        *args: object,
        **kwargs: object,
    ) -> list[dict[str, object]]: ...


class MarketDataClientProtocol(Protocol):
    def fetch(
        self,
        ticker: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, object]]: ...


class StalenessDetectorProtocol(Protocol):
    def is_stale(
        self,
        response_bars: list[dict[str, object]],
        requested_end: datetime,
    ) -> bool: ...


class RawWriterProtocol(Protocol):
    def write_batch(
        self,
        batch: IngestionBatch,
        records: list[dict[str, object]],
    ) -> int: ...


class IssueStoreProtocol(Protocol):
    def save_all(self, issues: list[ValidationIssue]) -> None: ...


class ValidationHandoffProtocol(Protocol):
    def validate(
        self,
        batch: IngestionBatch,
        records: list[dict[str, object]],
    ) -> tuple[dict[str, int], list[ValidationIssue]]: ...


class IngestionCoordinator:
    """Orchestrate one ingestion request without crossing layer boundaries."""

    def __init__(
        self,
        batch_manager: BatchManagerProtocol,
        rate_limit: RateLimitProtocol,
        retry_policy: RetryPolicyProtocol,
        client: MarketDataClientProtocol,
        staleness_detector: StalenessDetectorProtocol,
        raw_writer: RawWriterProtocol,
        validation_handoff: ValidationHandoffProtocol,
        issue_store: IssueStoreProtocol,
    ) -> None:
        self._batch_manager = batch_manager
        self._rate_limit = rate_limit
        self._retry_policy = retry_policy
        self._client = client
        self._staleness_detector = staleness_detector
        self._raw_writer = raw_writer
        self._validation_handoff = validation_handoff
        self._issue_store = issue_store

    def run(self, request: IngestionRequest) -> IngestionBatch:
        """Run the ingestion sequence and return the final batch state."""
        batch = self._batch_manager.create(request)
        totals = {
            "received": 0,
            "valid": 0,
            "invalid": 0,
            "duplicates": 0,
            "missing_intervals": 0,
            "stale_responses": 0,
            "idempotent_conflicts": 0,
        }

        try:
            for ticker in request.ticker_universe:
                self._rate_limit.acquire()
                records = self._retry_policy.execute(
                    self._client.fetch,
                    ticker,
                    request.interval,
                    request.start_time,
                    request.end_time,
                )
                is_stale = self._staleness_detector.is_stale(records, request.end_time)
                self._raw_writer.write_batch(batch, records)
                counts, issues = self._validation_handoff.validate(batch, records)
                self._issue_store.save_all(issues)

                totals["received"] += len(records)
                totals["valid"] += counts["valid"]
                totals["invalid"] += counts["invalid"]
                totals["duplicates"] += counts["duplicates"]
                totals["missing_intervals"] += counts["missing_intervals"]
                totals["stale_responses"] += int(is_stale)
                totals["idempotent_conflicts"] += counts["idempotent_conflicts"]

            self._batch_manager.record_counts(batch.batch_id, **totals)
            self._batch_manager.mark_completed(batch.batch_id, BatchStatus.COMPLETED)
        except Exception:
            self._batch_manager.mark_completed(batch.batch_id, BatchStatus.FAILED)
            raise

        return batch
