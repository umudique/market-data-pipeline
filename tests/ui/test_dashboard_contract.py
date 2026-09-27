from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from app.main import (
    API_BASE_URL,
    format_price_for_display,
    ingestion_kpi_fields,
    parse_ticker_universe,
    quality_batch_summary_fields,
    quality_issue_display_fields,
    render_ingestion_dashboard,
    screener_result_display_columns,
    validate_screener_inputs,
    validate_screener_parameters,
)
from src.api.schemas import BatchSummarySchema, IngestionBatchResponseSchema

pytestmark = pytest.mark.unit


@dataclass
class StreamlitCall:
    name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


@dataclass
class FakeExpander:
    streamlit: FakeStreamlit
    label: str

    def __enter__(self) -> FakeStreamlit:
        self.streamlit.calls.append(StreamlitCall("enter_expander", (self.label,), {}))
        return self.streamlit

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.streamlit.calls.append(StreamlitCall("exit_expander", (self.label,), {}))


@dataclass
class FakeStreamlit:
    calls: list[StreamlitCall] = field(default_factory=list)
    session_state: dict[str, object] = field(default_factory=dict)
    button_value: bool = False

    def __enter__(self) -> FakeStreamlit:
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def __getattr__(self, name: str) -> Any:
        def recorder(*args: Any, **kwargs: Any) -> object:
            self.calls.append(StreamlitCall(name, args, kwargs))
            if name == "expander":
                return FakeExpander(self, str(args[0]))
            if name == "button":
                return self.button_value
            if name == "columns":
                spec = args[0] if args else 1
                count = spec if isinstance(spec, int) else len(spec)
                return [self] * count
            return None

        return recorder


def _rendered_text(fake_streamlit: FakeStreamlit) -> str:
    values: list[str] = []
    for call in fake_streamlit.calls:
        values.extend(str(argument) for argument in call.args)
        values.extend(str(value) for value in call.kwargs.values())
    return "\n".join(value for value in values if isinstance(value, str))


def _ingestion_response(verdict: str = "PASSED WITH ISSUES") -> IngestionBatchResponseSchema:
    return IngestionBatchResponseSchema(
        batch_id="00000000-0000-0000-0000-000000000001",
        status="COMPLETED",
        ingestion_verdict=verdict,
        records_received=10,
        records_valid=8,
        records_invalid=2,
        duplicate_count=1,
        missing_interval_count=1,
        stale_response_count=0,
        idempotent_conflict_count=0,
    )


def _quality_issues() -> list[dict[str, object]]:
    return [
        {
            "issue_type": "MISSING_INTERVAL",
            "severity": "WARNING",
            "ticker": "AAPL",
            "timestamp": "2026-01-02T00:00:00",
            "details": "Expected bar not present",
        }
    ]


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
        ticker_universe="AAPL,MSFT",
        interval="1d",
        requested_range="2024-01-01T00:00:00/2024-09-30T23:59:59",
        records_received=10,
        records_valid=9,
        records_invalid=1,
        duplicate_count=0,
        missing_interval_count=1,
        stale_response_count=0,
    )

    fields = quality_batch_summary_fields([batch])

    assert fields == [
        "tickers",
        "interval",
        "date_range",
        "status",
        "bars_received",
        "bars_valid",
        "issues",
        "run_at",
    ]


def test_ingestion_verdict_banner_renders_schema_verdict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.main as dashboard

    fake_streamlit = FakeStreamlit()
    monkeypatch.setattr(dashboard, "st", fake_streamlit)

    dashboard._render_ingestion_summary_strip(
        response=_ingestion_response("PASSED WITH ISSUES"),
        request={"ticker_universe": ["AAPL"]},
    )

    rendered_text = _rendered_text(fake_streamlit)
    assert "PASSED WITH ISSUES" in rendered_text


def test_ingestion_kpi_strip_contains_five_required_fields() -> None:
    assert ingestion_kpi_fields() == [
        "Rows received",
        "Valid rows",
        "Issues detected",
        "Rows persisted",
        "Duplicates blocked",
    ]


def test_issue_breakdown_table_renders_quality_issues_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.main as dashboard

    fake_streamlit = FakeStreamlit()
    monkeypatch.setattr(dashboard, "st", fake_streamlit)

    render_ingestion_dashboard(
        response=_ingestion_response(),
        quality_issues=_quality_issues(),
        market_data={},
        request_config={},
    )

    rendered_text = _rendered_text(fake_streamlit)
    assert "Data Quality Breakdown" in rendered_text
    assert "Data Gap" in rendered_text
    assert "Expected bar not present" in rendered_text


def test_idempotency_panel_requires_two_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.main as dashboard

    first_run_streamlit = FakeStreamlit(
        session_state={"ingestion_first_response": _ingestion_response()}
    )
    monkeypatch.setattr(dashboard, "st", first_run_streamlit)

    dashboard._render_idempotency_proof()

    first_run_text = _rendered_text(first_run_streamlit)
    assert "First run" in first_run_text
    assert "Second run" not in first_run_text
    assert "Re-run to verify idempotency" in first_run_text

    second_run_streamlit = FakeStreamlit(
        session_state={
            "ingestion_first_response": _ingestion_response(),
            "ingestion_second_response": _ingestion_response(),
        }
    )
    monkeypatch.setattr(dashboard, "st", second_run_streamlit)

    dashboard._render_idempotency_proof()

    second_run_text = _rendered_text(second_run_streamlit)
    assert "First run" in second_run_text
    assert "Second run" in second_run_text


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


def test_dashboard_default_api_port_matches_docker_compose() -> None:
    assert API_BASE_URL == "http://localhost:8001"


def test_format_price_truncates_float_noise_to_two_decimals() -> None:
    assert format_price_for_display(187.14999389648438) == "187.15"
    assert format_price_for_display(169.02999877929688) == "169.03"


def test_format_price_preserves_clean_values() -> None:
    assert format_price_for_display(100.0) == "100.00"
    assert format_price_for_display(99.5) == "99.50"


def test_format_price_returns_none_for_missing_values() -> None:
    assert format_price_for_display(None) is None


def test_format_price_returns_value_unchanged_when_not_numeric() -> None:
    assert format_price_for_display("n/a") == "n/a"


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
