from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import pytest

from src.domain import BatchStatus, IngestionBatch, IngestionRequest, ValidationIssue
from src.ingestion.coordinator import IngestionCoordinator

pytestmark = pytest.mark.unit


@dataclass
class FakeBatchManager:
    batches: list[IngestionBatch] = field(default_factory=list)

    def create(self, request: IngestionRequest) -> IngestionBatch:
        batch = IngestionBatch(
            source=request.source,
            requested_range=f"{request.start_time.isoformat()}/{request.end_time.isoformat()}",
            started_at=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
            status=BatchStatus.PENDING,
        )
        self.batches.append(batch)
        return batch

    def record_counts(self, batch_id: object, **counts: int) -> None:
        batch = self._batch(batch_id)
        batch.records_received = counts["received"]
        batch.records_valid = counts["valid"]
        batch.records_invalid = counts["invalid"]
        batch.duplicate_count = counts["duplicates"]
        batch.missing_interval_count = counts["missing_intervals"]
        batch.stale_response_count = counts["stale_responses"]
        batch.idempotent_conflict_count = counts["idempotent_conflicts"]

    def mark_completed(self, batch_id: object, status: BatchStatus) -> None:
        batch = self._batch(batch_id)
        batch.status = status
        batch.completed_at = datetime(2026, 1, 2, 14, 33, tzinfo=UTC)

    def _batch(self, batch_id: object) -> IngestionBatch:
        return next(batch for batch in self.batches if batch.batch_id == batch_id)


class FakeRateLimit:
    def __init__(self) -> None:
        self.acquire_count = 0

    def acquire(self) -> None:
        self.acquire_count += 1


class FakeRetry:
    def __init__(self) -> None:
        self.execute_count = 0

    def execute(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        self.execute_count += 1
        return fn(*args, **kwargs)


class FakeClient:
    def __init__(self) -> None:
        self.fetch_count = 0

    def fetch(
        self,
        ticker: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, object]]:
        self.fetch_count += 1
        return [
            {
                "ticker": ticker,
                "timestamp": start,
                "interval": interval,
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.5,
                "volume": 1200,
                "source": "yfinance",
                "raw_payload": {"Close": 100.5},
            }
        ]


class FakeStalenessDetector:
    def is_stale(self, response_bars: list[dict[str, object]], requested_end: datetime) -> bool:
        return False


class FakeRawWriter:
    def __init__(self) -> None:
        self.write_count = 0

    def write_batch(self, batch: IngestionBatch, records: list[dict[str, object]]) -> int:
        self.write_count += 1
        return len(records)


class FakeIssueStore:
    def __init__(self) -> None:
        self.saved: list[ValidationIssue] = []

    def save_all(self, issues: list[ValidationIssue]) -> None:
        self.saved.extend(issues)


class FakeValidationHandoff:
    def __init__(self) -> None:
        self.calls = 0

    def validate(
        self,
        batch: IngestionBatch,
        records: list[dict[str, object]],
    ) -> tuple[dict[str, int], list[ValidationIssue]]:
        self.calls += 1
        counts = {
            "valid": len(records),
            "invalid": 0,
            "duplicates": 0,
            "missing_intervals": 0,
            "idempotent_conflicts": 0 if self.calls == 1 else len(records),
        }
        return counts, []


def _request() -> IngestionRequest:
    return IngestionRequest(
        ticker_universe=["AAPL"],
        interval="1m",
        start_time=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        end_time=datetime(2026, 1, 2, 14, 31, tzinfo=UTC),
        source="yfinance",
    )


def test_coordinator_sequence_records_idempotent_conflicts_on_reingestion() -> None:
    batch_manager = FakeBatchManager()
    rate_limit = FakeRateLimit()
    retry = FakeRetry()
    client = FakeClient()
    raw_writer = FakeRawWriter()
    validation = FakeValidationHandoff()
    coordinator = IngestionCoordinator(
        batch_manager=batch_manager,
        rate_limit=rate_limit,
        retry_policy=retry,
        client=client,
        staleness_detector=FakeStalenessDetector(),
        raw_writer=raw_writer,
        validation_handoff=validation,
        issue_store=FakeIssueStore(),
    )

    first_batch = coordinator.run(_request())
    second_batch = coordinator.run(_request())

    assert first_batch.status is BatchStatus.COMPLETED
    assert first_batch.idempotent_conflict_count == 0
    assert second_batch.status is BatchStatus.COMPLETED
    assert second_batch.idempotent_conflict_count == 1
    assert rate_limit.acquire_count == 2
    assert retry.execute_count == 2
    assert client.fetch_count == 2
    assert raw_writer.write_count == 2
