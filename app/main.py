"""Streamlit dashboard — presentation only, delegates to API."""

from __future__ import annotations

import os
from datetime import date, datetime, time

import requests
import streamlit as st

from src.api.schemas import BatchSummarySchema

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
PAGES = ["Earnings Gap Screener", "Pipeline Quality", "Data Ingestion"]


def validate_screener_inputs(
    start_date: date,
    end_date: date,
    ticker_universe: str,
) -> str | None:
    """Return a UX validation message for invalid screener inputs."""
    if end_date < start_date:
        return "End date must be on or after start date."
    if not ticker_universe.strip():
        return "Ticker universe is required."
    return None


def quality_batch_summary_fields(batches: list[BatchSummarySchema]) -> list[str]:
    """Return field names the quality page must render for batch summaries."""
    return [
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


def validate_screener_parameters(minimum_gap: float, minimum_volume: float) -> str | None:
    """Validate numeric screener parameters for dashboard UX.

    Args:
        minimum_gap: Minimum earnings gap threshold entered by the dashboard user.
        minimum_volume: Minimum volume threshold entered by the dashboard user.

    Returns:
        A user-facing validation message when either numeric threshold is below
        zero. Returns None when both values are valid for submission.

    Raises:
        No exceptions are raised for numeric input. Non-numeric coercion is
        outside this helper and belongs to the presentation widget layer.

    Invariants:
        This helper is pure. It does not call the API, query storage, perform
        financial calculations, or validate ticker symbols.
    """
    if minimum_gap < 0:
        return "Minimum gap must be zero or greater."
    if minimum_volume < 0:
        return "Minimum volume must be zero or greater."
    return None


def screener_result_display_columns() -> list[str]:
    """Return the ordered dashboard columns for earnings-gap screener results.

    Args:
        None.

    Returns:
        The fixed, ordered list of result column names: ticker, date,
        gap_percent, relative_volume, close_return, and validated.

    Raises:
        No exceptions are raised.

    Invariants:
        The order is stable and not user-configurable. This helper is pure and
        does not call the API, calculate screener metrics, or inspect data rows.
    """
    return [
        "ticker",
        "date",
        "gap_percent",
        "relative_volume",
        "close_return",
        "validated",
    ]


def quality_issue_display_fields() -> list[str]:
    """Return the ordered dashboard fields for validation issue summaries.

    Args:
        None.

    Returns:
        The fixed, ordered list of issue field names: issue_type, severity,
        ticker, timestamp, and details.

    Raises:
        No exceptions are raised.

    Invariants:
        The order is stable and not user-configurable. This helper is pure and
        does not call the API, query storage, or interpret validation rules.
    """
    return ["issue_type", "severity", "ticker", "timestamp", "details"]


def parse_ticker_universe(raw_input: str) -> list[str]:
    """Parse a dashboard ticker-universe text input into display/API tokens.

    Args:
        raw_input: User-entered ticker text separated by commas, whitespace, or
        a combination of both.

    Returns:
        Uppercase ticker tokens in first-seen order. Returns an empty list for
        blank input.

    Raises:
        No exceptions are raised for string input.

    Invariants:
        This helper performs surface-level parsing only. It does not validate
        ticker-symbol existence, call the API, query storage, or apply financial
        business rules.
    """
    tickers: list[str] = []
    seen: set[str] = set()
    for token in raw_input.replace(",", " ").split():
        ticker = token.strip().upper()
        if ticker and ticker not in seen:
            tickers.append(ticker)
            seen.add(ticker)
    return tickers


def render_earnings_gap_screener() -> None:
    """Render the earnings-gap screener form and display API results."""
    with st.form("earnings-gap-screener"):
        start_date = st.date_input("Start date")
        end_date = st.date_input("End date")
        minimum_gap = st.number_input("Minimum gap", value=2.0)
        minimum_volume = st.number_input("Minimum volume", value=100_000.0)
        ticker_universe = st.text_area("Ticker universe")
        submitted = st.form_submit_button("Run screener")

    if not submitted:
        return

    input_error = validate_screener_inputs(start_date, end_date, ticker_universe)
    if input_error is not None:
        st.error(input_error)
        return

    parameter_error = validate_screener_parameters(minimum_gap, minimum_volume)
    if parameter_error is not None:
        st.error(parameter_error)
        return

    payload = {
        "start_date": datetime.combine(start_date, time.min).isoformat(),
        "end_date": datetime.combine(end_date, time.max).isoformat(),
        "minimum_gap": minimum_gap,
        "minimum_volume": minimum_volume,
        "ticker_universe": parse_ticker_universe(ticker_universe),
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/screeners/earnings-gap",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return

    body = response.json()
    results = body.get("results", [])
    if not results:
        st.warning("No results.")
        return

    columns = screener_result_display_columns()
    st.dataframe([{column: row.get(column) for column in columns} for row in results])


def render_pipeline_quality() -> None:
    """Render ingestion batch summaries and validation issue drilldown."""
    try:
        response = requests.get(f"{API_BASE_URL}/quality/batches", timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return

    batches = response.json()
    batch_columns = quality_batch_summary_fields([])
    st.dataframe([{column: row.get(column) for column in batch_columns} for row in batches])

    if not batches:
        st.warning("No batches.")
        return

    batch_ids = [str(batch.get("batch_id", "")) for batch in batches if batch.get("batch_id")]
    selected_batch_id = st.selectbox("Batch", batch_ids)
    if not selected_batch_id:
        return

    try:
        issues_response = requests.get(
            f"{API_BASE_URL}/quality/issues",
            params={"batch_id": selected_batch_id},
            timeout=30,
        )
        issues_response.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return

    issues = issues_response.json()
    if not issues:
        st.info("No issues for this batch.")
        return

    issue_fields = quality_issue_display_fields()
    st.dataframe([{field: issue.get(field) for field in issue_fields} for issue in issues])


def render_data_ingestion() -> None:
    """Render the ingestion trigger form and display the returned batch."""
    with st.form("data-ingestion"):
        ticker_universe = st.text_area("Ticker universe")
        interval = st.selectbox("Interval", ["1d", "1h", "1wk"])
        start_time = st.date_input("Start time")
        end_time = st.date_input("End time")
        submitted = st.form_submit_button("Run ingestion")

    if not submitted:
        return

    tickers = parse_ticker_universe(ticker_universe)
    if not tickers:
        st.error("Ticker universe is required.")
        return

    payload = {
        "ticker_universe": tickers,
        "interval": interval,
        "start_time": datetime.combine(start_time, time.min).isoformat(),
        "end_time": datetime.combine(end_time, time.max).isoformat(),
        "source": "yfinance",
    }

    try:
        response = requests.post(f"{API_BASE_URL}/ingest", json=payload, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return

    st.json(response.json())


def main() -> None:
    st.set_page_config(page_title="Market Data Pipeline", layout="wide")
    st.title("Financial Market Data Pipeline")

    page = st.sidebar.selectbox("Page", PAGES)

    if page == "Earnings Gap Screener":
        st.header("Earnings Gap Screener")
        render_earnings_gap_screener()

    elif page == "Pipeline Quality":
        st.header("Pipeline Quality")
        render_pipeline_quality()

    elif page == "Data Ingestion":
        st.header("Data Ingestion")
        render_data_ingestion()


if __name__ == "__main__":
    main()
