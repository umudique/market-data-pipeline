from __future__ import annotations

import ast
from datetime import date
from pathlib import Path

import pytest

from app.main import quality_batch_summary_fields, validate_screener_inputs
from src.api.schemas import BatchSummarySchema

pytestmark = pytest.mark.unit


def test_screener_form_rejects_end_date_before_start_date() -> None:
    error = validate_screener_inputs(
        start_date=date(2026, 1, 3),
        end_date=date(2026, 1, 2),
        ticker_universe="AAPL",
    )

    assert error == "End date must be on or after start date."


def test_screener_form_rejects_empty_ticker_universe() -> None:
    error = validate_screener_inputs(
        start_date=date(2026, 1, 2),
        end_date=date(2026, 1, 3),
        ticker_universe="",
    )

    assert error == "Ticker universe is required."


def test_quality_page_renders_batch_summary_fields() -> None:
    batch = BatchSummarySchema(
        batch_id="00000000-0000-0000-0000-000000000001",
        source="yfinance",
        status="COMPLETED",
        records_received=10,
        records_valid=9,
        records_invalid=1,
        duplicate_count=0,
        missing_interval_count=1,
        stale_response_count=0,
    )

    fields = quality_batch_summary_fields([batch])

    assert fields == [
        "batch_id",
        "source",
        "status",
        "records_received",
        "records_valid",
        "records_invalid",
        "duplicate_count",
        "missing_interval_count",
        "stale_response_count",
    ]


def test_dashboard_does_not_import_pipeline_internals_directly() -> None:
    forbidden_modules = {
        "src.ingestion",
        "src.validation",
        "src.normalization",
        "src.storage",
        "src.screener",
    }
    tree = ast.parse(Path("app/main.py").read_text())
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert not any(
        module == forbidden or module.startswith(f"{forbidden}.")
        for module in imported_modules
        for forbidden in forbidden_modules
    )
