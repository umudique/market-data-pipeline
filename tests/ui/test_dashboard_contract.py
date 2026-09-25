from __future__ import annotations

import ast
from datetime import date
from pathlib import Path

import pytest

from app.main import (
    parse_ticker_universe,
    quality_batch_summary_fields,
    quality_issue_display_fields,
    screener_result_display_columns,
    validate_screener_inputs,
    validate_screener_parameters,
)
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


def test_screener_parameters_rejects_negative_minimum_gap() -> None:
    error = validate_screener_parameters(minimum_gap=-0.1, minimum_volume=0.0)

    assert error is not None
    assert "gap" in error.lower()


def test_screener_parameters_rejects_negative_minimum_volume() -> None:
    error = validate_screener_parameters(minimum_gap=0.0, minimum_volume=-0.1)

    assert error is not None
    assert "volume" in error.lower()


def test_screener_parameters_accepts_zero_values() -> None:
    error = validate_screener_parameters(minimum_gap=0.0, minimum_volume=0.0)

    assert error is None


def test_screener_result_display_columns_contains_required_fields() -> None:
    assert screener_result_display_columns() == [
        "ticker",
        "date",
        "gap_percent",
        "relative_volume",
        "close_return",
        "validated",
    ]


def test_quality_issue_display_fields_contains_required_fields() -> None:
    assert quality_issue_display_fields() == [
        "issue_type",
        "severity",
        "ticker",
        "timestamp",
        "details",
    ]


def test_parse_ticker_universe_splits_comma_separated() -> None:
    assert parse_ticker_universe("AAPL,MSFT") == ["AAPL", "MSFT"]


def test_parse_ticker_universe_splits_whitespace_separated() -> None:
    assert parse_ticker_universe("AAPL MSFT TSLA") == ["AAPL", "MSFT", "TSLA"]


def test_parse_ticker_universe_uppercases_input() -> None:
    assert parse_ticker_universe("aapl") == ["AAPL"]


def test_parse_ticker_universe_deduplicates() -> None:
    assert parse_ticker_universe("AAPL,AAPL") == ["AAPL"]


def test_parse_ticker_universe_returns_empty_for_blank_input() -> None:
    assert parse_ticker_universe("   ") == []


def test_dashboard_does_not_import_api_facade_directly() -> None:
    tree = ast.parse(Path("app/main.py").read_text())
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    forbidden_modules = {"src.api.facade"}
    assert not any(
        module == forbidden or module.startswith(f"{forbidden}.")
        for module in imported_modules
        for forbidden in forbidden_modules
    )
    assert not any(
        module == "src.api.routes" or module.startswith("src.api.routes.")
        for module in imported_modules
    )
    assert all(
        module == "src.api.schemas" for module in imported_modules if module.startswith("src.api.")
    )
