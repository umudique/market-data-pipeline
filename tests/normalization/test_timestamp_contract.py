from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest

from src.normalization.timestamp import TimestampNormalizer

pytestmark = pytest.mark.unit


def test_timestamp_normalizer_converts_non_utc_timestamp_to_utc() -> None:
    raw_timestamp = datetime(2026, 1, 2, 9, 30, tzinfo=timezone(timedelta(hours=-5)))

    normalized = TimestampNormalizer(canonical_timezone="UTC").normalize(raw_timestamp)

    assert normalized == datetime(2026, 1, 2, 14, 30, tzinfo=UTC)
    assert normalized.tzinfo is UTC


def test_timestamp_normalizer_leaves_utc_input_unchanged() -> None:
    raw_timestamp = datetime(2026, 1, 2, 14, 30, tzinfo=UTC)

    assert TimestampNormalizer(canonical_timezone="UTC").normalize(raw_timestamp) == raw_timestamp


def test_timestamp_normalizer_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError):
        TimestampNormalizer(canonical_timezone="UTC").normalize(datetime(2026, 1, 2, 14, 30))
