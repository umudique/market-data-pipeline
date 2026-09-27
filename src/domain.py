"""Core domain contracts — shared across all layers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class IssueType(StrEnum):
    DUPLICATE_CANDLE = "DUPLICATE_CANDLE"
    MISSING_INTERVAL = "MISSING_INTERVAL"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    INVALID_PRICE = "INVALID_PRICE"
    OHLC_INCONSISTENCY = "OHLC_INCONSISTENCY"
    MISSING_OBSERVATION = "MISSING_OBSERVATION"
    TIMEZONE_NORMALIZATION_REQUIRED = "TIMEZONE_NORMALIZATION_REQUIRED"
    STALE_RESPONSE = "STALE_RESPONSE"


class IssueSeverity(StrEnum):
    WARNING = "WARNING"
    ERROR = "ERROR"


class BatchStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ValidationStatus(StrEnum):
    VALID = "VALID"
    INVALID = "INVALID"
    FLAGGED = "FLAGGED"


@dataclass
class IngestionRequest:
    ticker_universe: list[str]
    interval: str
    start_time: datetime
    end_time: datetime
    source: str
    exchange: str | None = None
    custom_url: str | None = None
    api_key: str | None = None


@dataclass
class IngestionBatch:
    batch_id: uuid.UUID = field(default_factory=uuid.uuid4)
    source: str = ""
    requested_range: str = ""
    ticker_universe: str = ""
    interval: str = ""
    exchange: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: BatchStatus = BatchStatus.PENDING
    records_received: int = 0
    records_valid: int = 0
    records_invalid: int = 0
    duplicate_count: int = 0
    missing_interval_count: int = 0
    stale_response_count: int = 0
    idempotent_conflict_count: int = 0


@dataclass
class ValidationIssue:
    issue_type: IssueType
    severity: IssueSeverity
    ticker: str
    timestamp: datetime | None
    batch_id: uuid.UUID
    source: str
    details: str = ""


@dataclass
class MarketBar:
    ticker: str
    timestamp: datetime
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    ingestion_batch_id: uuid.UUID
    validated: bool = False
    validation_status: ValidationStatus = ValidationStatus.VALID


@dataclass
class EarningsGapScreenerRequest:
    start_date: datetime
    end_date: datetime
    minimum_gap: float
    minimum_volume: float
    ticker_universe: list[str]


@dataclass
class EarningsGapResult:
    ticker: str
    date: datetime
    gap_percent: float
    relative_volume: float
    close_return: float
    validated: bool
