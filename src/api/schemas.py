"""Pydantic request and response contracts — stable API surface."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ScreenerRequestSchema(BaseModel):
    start_date: datetime
    end_date: datetime
    minimum_gap: float
    minimum_volume: float
    ticker_universe: list[str]


class EarningsGapResultSchema(BaseModel):
    ticker: str
    date: datetime
    gap_percent: float
    relative_volume: float
    close_return: float
    validated: bool


class ScreenerResponseSchema(BaseModel):
    results: list[EarningsGapResultSchema]
    total: int


class MarketBarSchema(BaseModel):
    ticker: str
    timestamp: datetime
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    validated: bool


class MarketDataResponseSchema(BaseModel):
    bars: list[MarketBarSchema]
    total: int


class BatchSummarySchema(BaseModel):
    batch_id: str
    source: str
    status: str
    records_received: int
    records_valid: int
    records_invalid: int
    duplicate_count: int
    missing_interval_count: int
    stale_response_count: int


class ValidationIssueSummarySchema(BaseModel):
    issue_type: str
    severity: str
    ticker: str
    timestamp: datetime | None
    details: str
