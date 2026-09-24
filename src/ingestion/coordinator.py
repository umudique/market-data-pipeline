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

from typing import Any

from src.domain import IngestionBatch, IngestionRequest


class IngestionCoordinator:
    """Orchestrate one ingestion request without crossing layer boundaries."""

    def __init__(
        self,
        batch_manager: Any,
        rate_limit: Any,
        retry_policy: Any,
        client: Any,
        staleness_detector: Any,
        raw_writer: Any,
        validation_handoff: Any,
    ) -> None:
        raise NotImplementedError

    def run(self, request: IngestionRequest) -> IngestionBatch:
        """Run the ingestion sequence and return the final batch state."""
        raise NotImplementedError
