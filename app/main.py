"""Streamlit dashboard — presentation only, delegates to API."""

from __future__ import annotations

from datetime import date

import streamlit as st

from src.api.schemas import BatchSummarySchema

PAGES = ["Earnings Gap Screener", "Pipeline Quality"]


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


def render_earnings_gap_screener() -> None:
    """Render the earnings-gap screener form and result placeholders."""
    st.info("Screener UI — not yet implemented.")


def render_pipeline_quality() -> None:
    """Render ingestion batch and validation issue summaries."""
    st.info("Quality dashboard — not yet implemented.")


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


if __name__ == "__main__":
    main()
