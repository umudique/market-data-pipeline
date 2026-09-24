"""End-to-end ingestion sequence orchestration."""

from __future__ import annotations

from src.domain import IngestionBatch, IngestionRequest


class IngestionCoordinator:
    def run(self, request: IngestionRequest) -> IngestionBatch:
        raise NotImplementedError
