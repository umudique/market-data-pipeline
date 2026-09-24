"""Validation orchestration entry point for ingestion handoff."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.domain import IngestionBatch, IssueSeverity, IssueType, ValidationIssue
from src.validation.duplicates import DuplicateDetector
from src.validation.gaps import IntervalGapDetector
from src.validation.observations import ObservationValidator
from src.validation.prices import PriceValidator
from src.validation.stale import StaleDataValidator
from src.validation.timestamps import TimestampValidator
from src.validation.timezone import TimezoneValidator


class ValidationOrchestrator:
    """Run stateless validation checks for one ingestion batch.

    Contract:
        Satisfies the ingestion layer validation handoff:
        `validate(batch, records) -> dict[str, int]`.

    Invariants:
        Validation is pure and stateless: no provider calls, no DB writes, no
        normalization, no storage. Idempotent conflicts are always reported as
        `0` here because DB-level conflict detection belongs to storage.
    """

    def validate(
        self,
        batch: IngestionBatch,
        records: list[dict[str, Any]],
    ) -> tuple[dict[str, int], list[ValidationIssue]]:
        """Return validation counts and all detected issues for the batch."""
        if not records:
            return self._counts(valid=0, invalid=0, duplicates=0, missing_intervals=0), []

        source = batch.source
        ticker = str(records[0].get("ticker", ""))
        interval = str(records[0].get("interval", "1m"))
        expected_start, expected_end = self._parse_requested_range(batch.requested_range)

        issues = []
        issues.extend(DuplicateDetector().detect(records, batch.batch_id, source))
        issues.extend(
            IntervalGapDetector().detect(
                records,
                interval=interval,
                expected_start=expected_start,
                expected_end=expected_end,
                ticker=ticker,
                batch_id=batch.batch_id,
                source=source,
            )
        )
        issues.extend(TimestampValidator().validate(records, batch.batch_id, source))
        issues.extend(PriceValidator().validate(records, batch.batch_id, source))
        issues.extend(ObservationValidator().validate(records, batch.batch_id, source))
        issues.extend(
            TimezoneValidator(canonical_timezone="UTC").validate(records, batch.batch_id, source)
        )
        issues.extend(StaleDataValidator().validate(records, expected_end, batch.batch_id, source))

        invalid = sum(1 for issue in issues if issue.severity is IssueSeverity.ERROR)
        duplicates = sum(1 for issue in issues if issue.issue_type is IssueType.DUPLICATE_CANDLE)
        missing_intervals = sum(
            1 for issue in issues if issue.issue_type is IssueType.MISSING_INTERVAL
        )
        valid = max(0, len(records) - invalid)

        return self._counts(
            valid=valid,
            invalid=invalid,
            duplicates=duplicates,
            missing_intervals=missing_intervals,
        ), issues

    @staticmethod
    def _parse_requested_range(requested_range: str) -> tuple[datetime, datetime]:
        start, end = requested_range.split("/", maxsplit=1)
        return datetime.fromisoformat(start), datetime.fromisoformat(end)

    @staticmethod
    def _counts(
        *,
        valid: int,
        invalid: int,
        duplicates: int,
        missing_intervals: int,
    ) -> dict[str, int]:
        return {
            "valid": valid,
            "invalid": invalid,
            "duplicates": duplicates,
            "missing_intervals": missing_intervals,
            "idempotent_conflicts": 0,
        }
