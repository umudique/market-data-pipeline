"""Streamlit dashboard — presentation only, delegates to API."""

from __future__ import annotations

import os
from datetime import date, datetime, time

import requests
import streamlit as st

from src.api.schemas import BatchSummarySchema, IngestionBatchResponseSchema

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8001")
PAGES = ["Data Ingestion", "Earnings Gap Screener", "Pipeline Quality"]
_EXCHANGE_OPTIONS = [
    "—",
    "24/5",
    "24/7",
    "AIXK",
    "ARCX",
    "ASEX",
    "ASX",
    "BATS",
    "BMF",
    "BSE",
    "BVB",
    "BVMF",
    "CBOT",
    "CFE",
    "CME",
    "CMES",
    "COMEX",
    "FWB",
    "HKEX",
    "ICE",
    "ICEUS",
    "IEPA",
    "JKT",
    "JPX",
    "LSE",
    "LUXSE",
    "NASDAQ",
    "NYFE",
    "NYMEX",
    "NYSE",
    "OOTC",
    "OSE",
    "SIX",
    "SSE",
    "TASE",
    "TSX",
    "XAMS",
    "XASE",
    "XASX",
    "XBDA",
    "XBEL",
    "XBKK",
    "XBOG",
    "XBOM",
    "XBRA",
    "XBRU",
    "XBSE",
    "XBUD",
    "XBUE",
    "XCBF",
    "XCSE",
    "XCYS",
    "XDUB",
    "XDUS",
    "XEEE",
    "XETR",
    "XEUR",
    "XFRA",
    "XHAM",
    "XHEL",
    "XHKG",
    "XICE",
    "XIDX",
    "XIST",
    "XJSE",
    "XKAR",
    "XKLS",
    "XKRX",
    "XLIM",
    "XLIS",
    "XLIT",
    "XLJU",
    "XLON",
    "XLUX",
    "XMAD",
    "XMEX",
    "XMIL",
    "XMOS",
    "XNAS",
    "XNYS",
    "XNZE",
    "XOSL",
    "XPAR",
    "XPHS",
    "XPRA",
    "XRIS",
    "XSAU",
    "XSES",
    "XSGO",
    "XSHG",
    "XSTO",
    "XSTU",
    "XSWX",
    "XTAE",
    "XTAI",
    "XTAL",
    "XTKS",
    "XTSE",
    "XTSX",
    "XWAR",
    "XWBO",
    "XZAG",
    "us_futures",
]

_CSS = """
<style>
@font-face {
    font-family: 'IBM Plex Sans';
    font-weight: 400;
    src: url('/app/static/fonts/IBMPlexSans-Regular.woff2') format('woff2');
}
@font-face {
    font-family: 'IBM Plex Sans';
    font-weight: 500;
    src: url('/app/static/fonts/IBMPlexSans-Medium.woff2') format('woff2');
}
@font-face {
    font-family: 'IBM Plex Sans';
    font-weight: 600;
    src: url('/app/static/fonts/IBMPlexSans-SemiBold.woff2') format('woff2');
}
@font-face {
    font-family: 'IBM Plex Sans';
    font-weight: 700;
    src: url('/app/static/fonts/IBMPlexSans-Bold.woff2') format('woff2');
}
@font-face {
    font-family: 'IBM Plex Mono';
    font-weight: 400;
    src: url('/app/static/fonts/IBMPlexMono-Regular.woff2') format('woff2');
}
@font-face {
    font-family: 'IBM Plex Mono';
    font-weight: 600;
    src: url('/app/static/fonts/IBMPlexMono-SemiBold.woff2') format('woff2');
}
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 400;
}
h1, .stTitle {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 700 !important;
}
h2, h3, h4,
[data-testid="stHeading"],
.stSubheader {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"],
[data-testid="stCaption"],
code, pre, .stCodeBlock {
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricValue"],
.metric-value {
    font-size: 1.55rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"],
.metric-label {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}
.metric-value.bold { font-weight: 700 !important; }
table td, table th {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}
table th {
    font-weight: 600 !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] strong { margin-bottom: 0 !important; }
[data-testid="stCaptionContainer"],
[data-testid="stCaption"] {
    margin-top: 0.1rem !important;
    margin-bottom: 0.35rem !important;
}
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
.block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}
[data-testid="column"]:nth-child(2) {
    overflow-y: auto;
    max-height: 82vh;
    padding-right: 0.5rem;
}
button[kind="secondary"] {
    padding: 0.1rem 0.5rem !important;
    font-size: 0.72rem !important;
    min-height: unset !important;
    line-height: 1.4 !important;
}
</style>
"""

_VERDICT_COLORS = {
    "PASSED": "#1e7a48",
    "PASSED WITH ISSUES": "#c4890a",
    "REJECTED": "#b03535",
}

_ISSUE_TYPE_LABELS: dict[str, str] = {
    "DUPLICATE_CANDLE": "Duplicate Bar",
    "MISSING_INTERVAL": "Data Gap",
    "STALE_RESPONSE": "Stale Feed",
    "INVALID_PRICE": "Invalid Price",
    "OHLC_INCONSISTENCY": "OHLC Inconsistency",
    "TIMEZONE_NORMALIZATION_REQUIRED": "Timezone normalization",
}

# Issue types that represent successful pipeline processing, not data defects.
_PROCESSING_TYPES = {"TIMEZONE_NORMALIZATION_REQUIRED"}

_SEVERITY_LABELS: dict[str, str] = {
    "WARNING": "Warning",
    "ERROR": "Error",
    "INFO": "Info",
}

_YEARS = list(range(2000, 2036))
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def format_price_for_display(val: object) -> str | object:
    """Round a raw float price to 2 decimal places for human display."""
    if val is None:
        return val
    try:
        return f"{float(val):.2f}"
    except (TypeError, ValueError):
        return val


_PREVIEW_COLUMNS = [
    "ticker",
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "interval",
    "validated",
]


def _scrollable_table(data: list[dict], height: int = 300) -> None:
    """Render a list of dicts as a scrollable table matching Streamlit st.table appearance."""
    if not data:
        return
    cols = list(data[0].keys())
    header = "".join(
        f'<th style="padding:6px 13px;text-align:left;background:#ffffff;color:#262730;'
        f"position:sticky;top:0;font-size:0.8rem;font-weight:600;"
        f"font-family:'IBM Plex Mono',monospace;"
        f'border-bottom:1px solid #e6e6e6;white-space:nowrap">{c}</th>'
        for c in cols
    )
    rows_html = ""
    for i, row in enumerate(data):
        cells = "".join(
            f'<td style="padding:5px 13px;font-size:0.8rem;border-bottom:1px solid #e6e6e6;'
            f"font-family:'IBM Plex Mono',monospace;white-space:nowrap;color:#262730\">"
            f"{row.get(c, '')}</td>"
            for c in cols
        )
        rows_html += f"<tr>{cells}</tr>"
    st.markdown(
        f'<div style="max-height:{height}px;overflow-y:auto;overflow-x:auto;'
        f'border:1px solid #e6e6e6;">'
        f'<table style="width:100%;border-collapse:collapse;background:#ffffff">'
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        f"</table></div>",
        unsafe_allow_html=True,
    )


def _date_picker(label: str, default: date, key: str) -> date:
    """Year / month / day inline selectors — replaces st.date_input."""
    import calendar as _cal

    st.markdown(
        f"<p style='margin:0 0 4px;font-size:0.875rem;color:#444'>{label}</p>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([3, 3, 2])
    year = c1.selectbox(
        "Y",
        _YEARS,
        index=_YEARS.index(default.year),
        key=f"{key}_y",
        label_visibility="collapsed",
    )
    month_name = c2.selectbox(
        "M",
        _MONTHS,
        index=default.month - 1,
        key=f"{key}_m",
        label_visibility="collapsed",
    )
    month_num = _MONTHS.index(month_name) + 1
    max_day = _cal.monthrange(year, month_num)[1]
    day = c3.number_input(
        "D",
        min_value=1,
        max_value=max_day,
        value=min(default.day, max_day),
        key=f"{key}_d",
        label_visibility="collapsed",
    )
    return date(year, month_num, int(day))


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
        "tickers",
        "interval",
        "date_range",
        "status",
        "bars_received",
        "bars_valid",
        "issues",
        "run_at",
    ]


def ingestion_kpi_fields() -> list[str]:
    """Return the five KPI labels required by the verdict-first UI.

    Args:
        None.

    Returns:
        Stable KPI label order for the Layer 1 ingestion outcome strip.

    Raises:
        No exceptions are raised.

    Invariants:
        This helper is pure and does not calculate financial metrics, call the
        API, or inspect pipeline internals. Labels remain stable so API field
        gaps are visible rather than silently patched in the dashboard.
    """
    return [
        "Rows received",
        "Valid rows",
        "Errors detected",
        "Rows persisted",
        "Duplicates blocked",
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


def render_ingestion_dashboard(
    response: IngestionBatchResponseSchema,
    quality_issues: list[dict[str, object]],
    market_data: dict[str, object],
    request_config: dict[str, object],
) -> bool:
    """Render the ingestion-first dashboard layers from API response data.

    Args:
        response: Typed ``POST /ingest`` response.
        quality_issues: ``GET /quality/issues`` response rows for the batch.
        market_data: ``GET /market-data`` response body for data preview.
        request_config: Request payload submitted to ``POST /ingest``.

    Returns:
        True when the user requests an identical re-run for idempotency
        verification; otherwise False.

    Raises:
        ValueError: If ``ingestion_verdict`` is not one of the UI-supported
            verdict labels.

    Invariants:
        Render order is ingestion verdict, data quality, pipeline flow,
        idempotency proof, data preview, request config.
        The dashboard displays API fields as produced and does not import or
        call ingestion, validation, normalization, storage, or screener modules.
        Session state stores request/response data only.
    """
    if response.ingestion_verdict not in {"PASSED", "PASSED WITH ISSUES", "REJECTED"}:
        raise ValueError("ingestion_verdict must be PASSED, PASSED WITH ISSUES, or REJECTED")

    _render_data_quality(response, quality_issues)

    with st.expander("Request and configuration", expanded=False):
        _render_request_config(response, request_config)

    return False


def _render_ingestion_outcome(response: IngestionBatchResponseSchema) -> None:
    """Render Layer 1: verdict banner and KPI strip."""
    color = _VERDICT_COLORS.get(response.ingestion_verdict, "#555")
    st.markdown(
        f'<div style="background:{color}18; border-left:4px solid {color}; '
        f'padding:0.75rem 1rem; margin-bottom:0.75rem">'
        f'<span style="font-size:0.72rem; font-weight:700; color:#888; '
        f'letter-spacing:0.08em">INGESTION</span><br>'
        f'<span style="font-size:1.4rem; font-weight:700; color:{color}; line-height:1.2">'
        f"INGESTION: {response.ingestion_verdict}</span></div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4, c5 = st.columns(5)
    total_issues = (
        response.records_invalid
        + response.missing_interval_count
        + response.duplicate_count
        + response.stale_response_count
    )
    rows_persisted = response.records_received - response.idempotent_conflict_count
    c1.metric("Rows received", response.records_received)
    c2.metric("Valid rows", response.records_valid)
    c3.metric("Errors detected", total_issues)
    c4.metric("Rows persisted", rows_persisted)
    c5.metric("Duplicates blocked", response.idempotent_conflict_count)


def _render_data_quality(
    response: IngestionBatchResponseSchema,
    quality_issues: list[dict[str, object]],
) -> None:
    """Render Layer 2: issue type breakdown, trusted/rejected split, per-issue detail."""
    st.markdown("**Data Quality Breakdown**")
    st.caption("How many records passed validation, how many were flagged, and why.")

    # Block A — issue type counts
    _scrollable_table(
        [
            {
                "Issue": "Duplicate Bars",
                "Count": response.duplicate_count,
                "Severity": "Warning" if response.duplicate_count else "—",
            },
            {
                "Issue": "Data Gaps",
                "Count": response.missing_interval_count,
                "Severity": "Warning" if response.missing_interval_count else "—",
            },
            {
                "Issue": "Stale Feed",
                "Count": response.stale_response_count,
                "Severity": "Warning" if response.stale_response_count else "—",
            },
        ]
    )

    # Block B — trusted vs rejected split
    if response.records_received > 0:
        trusted_ratio = response.records_valid / response.records_received
        if trusted_ratio >= 0.95:
            bar_color = "#1e7a48"
        elif trusted_ratio >= 0.70:
            bar_color = "#c4890a"
        else:
            bar_color = "#b03535"
        pct = trusted_ratio * 100
        rejected = response.records_received - response.records_valid
        st.markdown(
            f"**Trusted** &nbsp; {response.records_valid:,} / {response.records_received:,}"
        )
        st.markdown(
            f'<div style="background:#e8e8e8;border-radius:4px;height:8px;margin:4px 0 6px">'
            f'<div style="background:{bar_color};width:{pct:.1f}%;'
            f'height:8px;border-radius:4px"></div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            f"Trusted: {response.records_valid:,} &nbsp;·&nbsp; "
            f"Rejected: {rejected:,} &nbsp;·&nbsp; "
            f"Total: {response.records_received:,}"
        )

    # Block C — aggregated findings
    if quality_issues:
        st.markdown("**Validation Findings**")
        st.caption(
            "Issue categories detected during validation, grouped by type. "
            "Individual records are available in Pipeline Quality."
        )
        agg: dict[tuple[str, str, str], int] = {}
        for issue in quality_issues:
            raw_type = str(issue.get("issue_type", ""))
            raw_sev = str(issue.get("severity", ""))
            label = _ISSUE_TYPE_LABELS.get(raw_type, raw_type.replace("_", " ").title())
            sev = _SEVERITY_LABELS.get(raw_sev, raw_sev.title())
            category = "Processing" if raw_type in _PROCESSING_TYPES else "Issue"
            key = (label, sev, category)
            agg[key] = agg.get(key, 0) + 1
        rows = [
            {"Category": cat, "Finding": label, "Severity": sev, "Records": count}
            for (label, sev, cat), count in sorted(
                agg.items(), key=lambda x: (x[0][2] != "Issue", -x[1])
            )
        ]
        _scrollable_table(rows)
        st.markdown("**Issue Details**")
        _scrollable_table(
            [
                {
                    "Ticker": issue.get("ticker", "—"),
                    "Timestamp": issue.get("timestamp", "—"),
                    "Issue Type": issue.get("issue_type", "—"),
                    "Details": issue.get("details", "—"),
                }
                for issue in quality_issues
            ]
        )


def _render_pipeline_flow(response: IngestionBatchResponseSchema) -> None:
    """Render Layer 3: per-batch data lineage as a simple stage table."""
    st.markdown("**Pipeline Flow**")
    flagged = response.records_invalid
    _scrollable_table(
        [
            {
                "Stage": "Source API",
                "Records in": "—",
                "Records out": response.records_received,
                "Dropped": "—",
            },
            {
                "Stage": "Raw ingest",
                "Records in": response.records_received,
                "Records out": response.records_received,
                "Dropped": 0,
            },
            {
                "Stage": "Validation",
                "Records in": response.records_received,
                "Records out": response.records_valid,
                "Dropped": flagged,
            },
            {
                "Stage": "Normalisation",
                "Records in": response.records_valid,
                "Records out": response.records_valid,
                "Dropped": 0,
            },
            {
                "Stage": "Canonical store",
                "Records in": response.records_valid,
                "Records out": response.records_valid,
                "Dropped": response.duplicate_count,
            },
        ]
    )


def _render_idempotency_proof() -> bool:
    """Render Layer 4: first-run or two-run idempotency comparison."""
    st.markdown("**Idempotency Proof**")
    st.caption(
        "Re-running with the same parameters should produce zero new rows. "
        "This confirms the pipeline never double-writes."
    )
    first_response = st.session_state.get("ingestion_first_response")
    second_response = st.session_state.get("ingestion_second_response")

    if first_response is None:
        st.info("Run ingestion once to capture the first-run panel.")
        return False

    if second_response is None:
        rows = [
            {"Metric": m, "First run": v}
            for m, v in zip(_IDEMPOTENCY_ROWS, _idempotency_values(first_response))
        ]
        _scrollable_table(rows)
        rerun = st.button("Re-run to verify idempotency")
        st.caption(
            "Re-run with identical parameters to see the idempotency proof. "
            "On a correct second run, Rows persisted = 0 and "
            "Duplicates blocked = first-run row count."
        )
        return bool(rerun)

    rows = [
        {"Metric": m, "First run": fv, "Second run": sv}
        for m, fv, sv in zip(
            _IDEMPOTENCY_ROWS,
            _idempotency_values(first_response),
            _idempotency_values(second_response),
        )
    ]
    _scrollable_table(rows)
    st.caption(
        "On re-run with identical parameters, zero new rows are inserted. "
        "The canonical row count is unchanged. Idempotency is enforced at the storage layer."
    )
    return False


_IDEMPOTENCY_ROWS = [
    "Rows received",
    "Valid rows",
    "Rows persisted",
    "Duplicates blocked",
]


def _idempotency_values(response: object) -> list[object]:
    """Extract idempotency spec rows from a stored response.

    'Duplicates blocked' is the count of records already present in the DB
    (idempotent_conflict_count), not within-batch candle duplicates.
    """
    if isinstance(response, IngestionBatchResponseSchema):
        conflicts = getattr(response, "idempotent_conflict_count", 0)
        persisted = response.records_received - conflicts
        return [
            response.records_received,
            response.records_valid,
            persisted,
            conflicts,
        ]
    if isinstance(response, dict):
        received = response.get("records_received", 0) or 0
        conflicts = response.get("idempotent_conflict_count", 0) or 0
        return [
            received,
            response.get("records_valid"),
            received - conflicts,
            conflicts,
        ]
    return [None] * 4


def _render_bars_per_day_chart(market_data: dict[str, object]) -> None:
    import pandas as pd

    bars = market_data.get("bars", [])
    if not bars:
        return

    counts: dict[str, int] = {}
    for bar in bars:
        ts = bar.get("timestamp", "")
        day = str(ts)[:10]
        if day:
            counts[day] = counts.get(day, 0) + 1

    df = pd.DataFrame({"bars": counts}).sort_index()
    st.markdown("**Bars ingested per day**")
    st.bar_chart(df, x_label="Date", y_label="Bars", height=220)


def _render_data_preview(market_data: dict[str, object]) -> None:
    """Render Layer 5: canonical records filtered to spec columns."""
    import csv
    import io

    bars = market_data.get("bars", [])
    if not bars:
        st.markdown("**Data Preview**")
        st.caption(
            "Normalized OHLCV records stored in the canonical layer, ready for downstream use."
        )
        st.info("No canonical records returned for preview.")
        return
    _PRICE_COLS = {"open", "high", "low", "close"}
    filtered = []
    for row in bars:
        if not isinstance(row, dict):
            continue
        entry = {}
        for col in _PREVIEW_COLUMNS:
            val = row.get(col)
            if col in _PRICE_COLS:
                val = format_price_for_display(val)
            entry[col] = val
        filtered.append(entry)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_PREVIEW_COLUMNS)
    writer.writeheader()
    writer.writerows(filtered)
    title_col, btn_col = st.columns([5, 1])
    with title_col:
        st.markdown("**Data Preview**")
        st.caption(
            "Normalized OHLCV records stored in the canonical layer, ready for downstream use."
        )
    with btn_col:
        st.download_button(
            "Export CSV",
            data=buf.getvalue(),
            file_name="market_data_preview.csv",
            mime="text/csv",
            use_container_width=True,
        )
    _scrollable_table(filtered)


def _render_request_config(
    response: IngestionBatchResponseSchema,
    request_config: dict[str, object],
) -> None:
    """Render Layer 6: request parameters as a labeled table."""
    rows = [
        ("Ticker universe", ", ".join(str(t) for t in request_config.get("ticker_universe", []))),
        ("Interval", request_config.get("interval", "—")),
        ("Start date", request_config.get("start_time", "—")),
        ("End date", request_config.get("end_time", "—")),
        ("Source", request_config.get("source", "—")),
        ("Batch ID", response.batch_id),
        ("Status", response.status),
    ]
    for label, value in rows:
        st.write(f"**{label}:** {value}")


def render_pipeline_quality() -> None:
    """Render ingestion batch summaries with delete and export actions."""
    import csv
    import io

    st.markdown("**Pipeline Quality**")
    try:
        response = requests.get(f"{API_BASE_URL}/quality/batches", timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return

    batches = response.json()
    if not batches:
        st.info("No ingestion batches yet.")
        return

    rows = []
    for b in batches:
        tickers_raw = b.get("ticker_universe", "")
        tickers = tickers_raw if tickers_raw else "—"
        date_range = _format_requested_range(b.get("requested_range", ""))
        run_at = _format_run_at(b.get("started_at"))
        total_issues = (
            (b.get("records_invalid") or 0)
            + (b.get("missing_interval_count") or 0)
            + (b.get("duplicate_count") or 0)
            + (b.get("stale_response_count") or 0)
        )
        rows.append(
            {
                "tickers": tickers,
                "interval": b.get("interval") or "—",
                "date_range": date_range,
                "status": b.get("status", "—"),
                "bars_received": b.get("records_received", 0),
                "bars_valid": b.get("records_valid", 0),
                "issues": total_issues,
                "run_at": run_at,
                "_batch_id": b.get("batch_id", ""),
            }
        )

    # Export button
    display_cols = [k for k in rows[0] if not k.startswith("_")]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=display_cols)
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r[k] for k in display_cols})
    _, exp_col = st.columns([5, 1])
    with exp_col:
        st.download_button(
            "Export CSV",
            data=buf.getvalue(),
            file_name="pipeline_quality.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Batch rows with × delete button
    header = st.columns([3, 1, 2, 1, 1, 1, 1, 2, 1])
    for col, label in zip(
        header,
        ["Tickers", "Interval", "Date Range", "Status", "Bars", "Valid", "Issues", "Run At", ""],
    ):
        col.caption(label)

    for r in rows:
        c = st.columns([3, 1, 2, 1, 1, 1, 1, 2, 1])
        c[0].caption(r["tickers"])
        c[1].caption(r["interval"])
        c[2].caption(r["date_range"])
        c[3].caption(r["status"])
        c[4].caption(str(r["bars_received"]))
        c[5].caption(str(r["bars_valid"]))
        c[6].caption(str(r["issues"]))
        c[7].caption(r["run_at"])
        if c[8].button("×", key=f"del_{r['_batch_id']}"):
            try:
                requests.delete(
                    f"{API_BASE_URL}/quality/batches/{r['_batch_id']}", timeout=30
                ).raise_for_status()
                st.rerun()
            except requests.RequestException as exc:
                st.error(f"Delete failed: {exc}")

    # Issue drilldown
    st.divider()
    batch_labels = [f"{r['tickers']}  ·  {r['date_range']}  ({r['_batch_id'][:8]}…)" for r in rows]
    selected_label = st.selectbox("Validation findings", batch_labels)
    selected_idx = batch_labels.index(selected_label)
    selected_batch_id = rows[selected_idx]["_batch_id"]

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
        st.info("No findings for this batch.")
        return

    import csv
    import io

    agg: dict[tuple[str, str, str], int] = {}
    for issue in issues:
        raw_type = str(issue.get("issue_type", ""))
        raw_sev = str(issue.get("severity", ""))
        label = _ISSUE_TYPE_LABELS.get(raw_type, raw_type.replace("_", " ").title())
        sev = _SEVERITY_LABELS.get(raw_sev, raw_sev.title())
        category = "Processing" if raw_type in _PROCESSING_TYPES else "Issue"
        key = (label, sev, category)
        agg[key] = agg.get(key, 0) + 1
    issue_rows = [
        {"Category": cat, "Finding": label, "Severity": sev, "Records": count}
        for (label, sev, cat), count in sorted(
            agg.items(), key=lambda x: (x[0][2] != "Issue", -x[1])
        )
    ]
    if issue_rows:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(issue_rows[0].keys()))
        writer.writeheader()
        writer.writerows(issue_rows)
        _, exp_col = st.columns([5, 1])
        with exp_col:
            st.download_button(
                "Export CSV",
                data=buf.getvalue(),
                file_name="validation_findings.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"export_issues_{selected_batch_id}",
            )
    _scrollable_table(issue_rows)


def _format_requested_range(requested_range: str) -> str:
    """Convert ISO range string to human-readable date span."""
    try:
        start_str, end_str = requested_range.split("/")
        start = datetime.fromisoformat(start_str).date()
        end = datetime.fromisoformat(end_str).date()
        return f"{start.strftime('%b %Y')} → {end.strftime('%b %Y')}"
    except (ValueError, AttributeError):
        return requested_range or "—"


def _format_run_at(started_at: str | None) -> str:
    """Format batch start timestamp as a short local string."""
    if not started_at:
        return "—"
    try:
        dt = datetime.fromisoformat(started_at)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(started_at)


def render_data_ingestion() -> None:
    if st.session_state.get("show_pipeline_quality"):
        _render_pipeline_quality_page()
    else:
        _render_ingestion_tab()


def _render_pipeline_quality_page() -> None:
    if st.button("← Back", use_container_width=False):
        st.session_state["show_pipeline_quality"] = False
        st.rerun()
    render_pipeline_quality()


def _render_ingestion_tab() -> None:
    if isinstance(st.session_state.get("ingestion_first_response"), IngestionBatchResponseSchema):
        _render_ingestion_results_view()
    else:
        _render_ingestion_form_view()


def _render_db_ticker_browser() -> None:
    """Show past ingestion batches; apply a batch's tickers + date range to the form."""
    _, btn_col = st.columns([5, 1])
    with btn_col:
        if st.button("Browse DB", use_container_width=True):
            st.session_state["show_db_ticker_browser"] = not st.session_state.get(
                "show_db_ticker_browser", False
            )

    if not st.session_state.get("show_db_ticker_browser"):
        return

    try:
        resp = requests.get(f"{API_BASE_URL}/quality/batches", params={"limit": 50}, timeout=10)
        resp.raise_for_status()
        batches: list[dict[str, object]] = resp.json()
    except requests.RequestException:
        st.caption("Could not load batches from database.")
        return

    batches = [b for b in batches if b.get("ticker_universe")]
    if not batches:
        st.caption("No ingestion batches in database yet.")
        return

    labels = [
        f"{b['ticker_universe']}  ·  {b.get('interval', '—')}  ·  "
        f"{_format_requested_range(str(b.get('requested_range', '')))}"
        for b in batches
    ]
    selected_label = st.selectbox("Past batches", labels, label_visibility="collapsed")
    selected_batch = batches[labels.index(selected_label)]

    if st.button("Apply batch", use_container_width=True):
        tickers_raw = str(selected_batch.get("ticker_universe", ""))
        rng = str(selected_batch.get("requested_range", ""))
        try:
            start_str, end_str = rng.split("/")
            st.session_state["db_prefill_start"] = date.fromisoformat(start_str[:10])
            st.session_state["db_prefill_end"] = date.fromisoformat(end_str[:10])
        except Exception:
            pass
        st.session_state["ticker_universe_input"] = tickers_raw.replace(",", ", ")
        st.session_state["db_prefill_interval"] = str(selected_batch.get("interval", "1d"))
        st.session_state["show_db_ticker_browser"] = False
        st.rerun()


def _render_ingestion_form_view() -> None:
    _, form_col, _ = st.columns([1, 3, 1])
    with form_col:
        st.title("Market Data Pipeline")
        st.caption("Ingest OHLCV data, validate quality, and screen for earnings gaps.")
        _render_db_ticker_browser()
        with st.form("ingestion-form"):
            st.text_area(
                "Ticker universe",
                placeholder="AAPL, MSFT, SPY",
                height=80,
                key="ticker_universe_input",
            )
            _intervals = ["1d", "1h", "1wk"]
            _prefill_interval = st.session_state.get("db_prefill_interval", "1d")
            _interval_index = (
                _intervals.index(_prefill_interval) if _prefill_interval in _intervals else 0
            )
            interval = st.selectbox("Interval", _intervals, index=_interval_index)
            _default_start = st.session_state.get("db_prefill_start", date(2024, 1, 1))
            _default_end = st.session_state.get("db_prefill_end", date(2024, 9, 30))
            start_time = _date_picker("Start date", _default_start, "land_start")
            end_time = _date_picker("End date", _default_end, "land_end")
            col_l, col_r = st.columns(2)
            with col_l:
                source = st.selectbox("Source", ["yfinance", "Custom API"])
            with col_r:
                exchange_sel = st.selectbox("Exchange", _EXCHANGE_OPTIONS)
            custom_url = None
            api_key = None
            if source == "Custom API":
                custom_url = st.text_input(
                    "Endpoint URL",
                    placeholder="https://myapi.com/ohlcv?ticker={ticker}&start={start}&end={end}&interval={interval}",
                )
                api_key = st.text_input("API Key (optional)", type="password")
            submitted = st.form_submit_button(
                "Run ingestion", type="primary", use_container_width=True
            )

        if submitted:
            tickers = parse_ticker_universe(st.session_state.get("ticker_universe_input", ""))
            if not tickers:
                st.error("Ticker universe is required.")
            elif source == "Custom API" and not custom_url:
                st.error("Endpoint URL is required for Custom API.")
            else:
                payload: dict[str, object] = {
                    "ticker_universe": tickers,
                    "interval": interval,
                    "start_time": datetime.combine(start_time, time.min).isoformat(),
                    "end_time": datetime.combine(end_time, time.max).isoformat(),
                    "source": "custom" if source == "Custom API" else source,
                    "exchange": None if exchange_sel == "—" else exchange_sel,
                }
                if source == "Custom API":
                    payload["custom_url"] = custom_url
                    if api_key:
                        payload["api_key"] = api_key
                _run_first_ingestion(payload)


def _render_ingestion_results_view() -> None:
    stored_response: IngestionBatchResponseSchema = st.session_state["ingestion_first_response"]
    stored_request: dict[str, object] = st.session_state.get("ingestion_request_config", {})

    _render_ingestion_summary_strip(stored_response, stored_request)

    _, nav_l, nav_r = st.columns([4, 1, 1])
    with nav_l:
        if st.button("Pipeline Quality", use_container_width=True):
            st.session_state["show_pipeline_quality"] = True
            st.rerun()
    with nav_r:
        if st.button("← New ingestion", use_container_width=True):
            _clear_ingestion_state()
            st.rerun()

    left, right = st.columns(2)
    with left:
        rerun_requested = _render_idempotency_proof()
        if rerun_requested:
            _run_second_ingestion(stored_request)
            st.rerun()
        stored_market_data = st.session_state.get("ingestion_market_data")
        if stored_market_data:
            _render_data_preview(stored_market_data)
        else:
            st.caption("No canonical records available for preview.")
    with right:
        render_ingestion_dashboard(
            response=stored_response,
            quality_issues=_session_list("ingestion_quality_issues"),
            market_data=_session_dict("ingestion_market_data"),
            request_config=stored_request,
        )

    st.divider()
    _render_inline_screener(stored_request)


def _render_ingestion_summary_strip(
    response: IngestionBatchResponseSchema,
    request: dict[str, object],
) -> None:
    tickers = request.get("ticker_universe", [])
    ticker_label = ", ".join(str(t) for t in tickers[:3])
    if len(tickers) > 3:
        ticker_label += f" +{len(tickers) - 3}"
    total_issues = (
        response.records_invalid
        + response.missing_interval_count
        + response.duplicate_count
        + response.stale_response_count
    )
    color = _VERDICT_COLORS.get(response.ingestion_verdict, "#555")
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.markdown(
        f'<div style="margin-top:0.25rem">'
        f'<div class="metric-label" style="color:#888;margin-bottom:0.15rem">'
        f"INGESTION VERDICT</div>"
        f'<div class="metric-value bold" style="color:{color};line-height:1.1">'
        f"{response.ingestion_verdict}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    c2.metric("Rows received", f"{response.records_received:,}")
    c3.metric("Valid rows", f"{response.records_valid:,}")
    c4.metric("Errors detected", f"{total_issues:,}")
    c5.metric(
        "Rows persisted", f"{response.records_received - response.idempotent_conflict_count:,}"
    )
    c6.metric("Duplicates blocked", f"{response.idempotent_conflict_count:,}")
    c7.metric("Tickers", ticker_label)
    st.divider()


def _clear_ingestion_state() -> None:
    for key in [
        "ingestion_first_response",
        "ingestion_second_response",
        "ingestion_request_config",
        "ingestion_quality_issues",
        "ingestion_market_data",
        "ingestion_screener_results",
    ]:
        st.session_state.pop(key, None)


def _render_screener_tab() -> None:
    if st.session_state.get("screener_results") is not None:
        _render_screener_results_view()
    else:
        _render_screener_form_view()


def _render_screener_form_view() -> None:
    _, form_col, _ = st.columns([1, 3, 1])
    with form_col:
        with st.form("screener-form"):
            ticker_universe = st.text_area("Ticker universe", placeholder="AAPL, MSFT", height=80)
            start_date = _date_picker("Start date", date(2024, 1, 1), "scr_start")
            end_date = _date_picker("End date", date(2024, 9, 30), "scr_end")
            minimum_gap = st.number_input("Minimum gap %", value=2.0, step=0.5)
            minimum_volume = st.number_input("Minimum volume", value=100_000.0, step=50_000.0)
            submitted = st.form_submit_button(
                "Run screener", type="primary", use_container_width=True
            )

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
        _submit_screener(payload)


def _render_screener_results_view() -> None:
    results: list = st.session_state.get("screener_results", [])
    payload: dict[str, object] = st.session_state.get("screener_payload", {})

    if st.button("← New screener"):
        st.session_state.pop("screener_results", None)
        st.session_state.pop("screener_payload", None)
        st.rerun()

    _render_screener_summary_strip(results, payload)

    tickers = payload.get("ticker_universe", [])
    st.caption(
        f"{', '.join(str(t) for t in tickers)}  ·  "
        f"gap ≥ {payload.get('minimum_gap')}%  ·  "
        f"vol ≥ {payload.get('minimum_volume', 0):,.0f}"
    )
    columns = screener_result_display_columns()
    rows = []
    for row in results:
        r = {column: row.get(column) for column in columns}
        if isinstance(r.get("date"), str):
            r["date"] = r["date"].replace("T", "  ")
        rows.append(r)
    _scrollable_table(rows)


def _render_screener_summary_strip(results: list, payload: dict[str, object]) -> None:
    tickers = payload.get("ticker_universe", [])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Matches", len(results))
    c2.metric("Tickers scanned", len(tickers))
    c3.metric("Min gap", f"{payload.get('minimum_gap', 0)}%")
    c4.metric("Min volume", f"{payload.get('minimum_volume', 0):,.0f}")
    st.divider()


def _submit_screener(payload: dict[str, object]) -> None:
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
    st.session_state["screener_results"] = body.get("results", [])
    st.session_state["screener_payload"] = payload
    st.rerun()


def _render_inline_screener(ingestion_request: dict[str, object]) -> None:
    """Screener panel anchored to the ingestion date range, rendered below the split."""
    st.markdown("**Screener**")

    try:
        ing_start = datetime.fromisoformat(str(ingestion_request.get("start_time", ""))).date()
    except (ValueError, TypeError):
        ing_start = date(2024, 1, 1)
    try:
        ing_end = datetime.fromisoformat(str(ingestion_request.get("end_time", ""))).date()
    except (ValueError, TypeError):
        ing_end = date(2024, 9, 30)

    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
    with c1:
        scr_start = _date_picker("Start date", ing_start, "iscr_start")
    with c2:
        scr_end = _date_picker("End date", ing_end, "iscr_end")
    with c3:
        min_gap = st.number_input("Min gap %", value=2.0, step=0.5, key="iscr_gap")
    with c4:
        min_volume = st.number_input("Min volume", value=100_000.0, step=50_000.0, key="iscr_vol")

    _, btn_col = st.columns([4, 1])
    with btn_col:
        run = st.button("→ Run in Screener", use_container_width=True)

    if run:
        tickers = ingestion_request.get("ticker_universe", [])
        payload = {
            "start_date": datetime.combine(scr_start, time.min).isoformat(),
            "end_date": datetime.combine(scr_end, time.max).isoformat(),
            "minimum_gap": min_gap,
            "minimum_volume": min_volume,
            "ticker_universe": tickers,
        }
        try:
            response = requests.post(
                f"{API_BASE_URL}/screeners/earnings-gap",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            st.error(f"Screener request failed: {exc}")
            return
        body = response.json()
        results = body.get("results", [])
        st.session_state["ingestion_screener_results"] = results
        st.session_state["screener_results"] = results
        st.session_state["screener_payload"] = payload
        st.rerun()

    results = st.session_state.get("ingestion_screener_results")
    if results is not None:
        import csv
        import io

        columns = screener_result_display_columns()
        rows = []
        for row in results:
            r = {column: row.get(column) for column in columns}
            if isinstance(r.get("date"), str):
                r["date"] = r["date"].replace("T", "  ")
            rows.append(r)
        if rows:
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
            _, exp_col = st.columns([5, 1])
            with exp_col:
                st.download_button(
                    "Export CSV",
                    data=buf.getvalue(),
                    file_name="screener_results.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            _scrollable_table(rows)
        else:
            st.info("No matches found for the given parameters.")


def _run_first_ingestion(payload: dict[str, object]) -> None:
    """Submit the first ingestion request, persist results, then rerender."""
    try:
        response_body = _post_ingestion(payload)
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return

    st.session_state["ingestion_request_config"] = payload
    st.session_state["ingestion_first_response"] = response_body
    st.session_state.pop("ingestion_second_response", None)
    st.session_state["ingestion_quality_issues"] = [
        i.model_dump() for i in response_body.validation_issues
    ]
    st.session_state["ingestion_market_data"] = _fetch_market_data(payload)
    st.rerun()


def _run_second_ingestion(payload: dict[str, object]) -> None:
    """Submit an identical ingestion request for idempotency proof."""
    try:
        st.session_state["ingestion_second_response"] = _post_ingestion(payload)
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")


def _post_ingestion(payload: dict[str, object]) -> IngestionBatchResponseSchema:
    """POST the ingestion request and return the typed API response schema."""
    response = requests.post(f"{API_BASE_URL}/ingest", json=payload, timeout=30)
    response.raise_for_status()
    return IngestionBatchResponseSchema.model_validate(response.json())


def _fetch_quality_issues(batch_id: str) -> list[dict[str, object]]:
    """Fetch validation issues for the batch from the API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/quality/issues",
            params={"batch_id": batch_id},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException:
        return []
    body = response.json()
    if isinstance(body, list):
        return [item for item in body if isinstance(item, dict)]
    return []


def _fetch_market_data(payload: dict[str, object]) -> dict[str, object]:
    """Fetch canonical data preview for all tickers in the universe."""
    ticker_universe = payload.get("ticker_universe")
    if not isinstance(ticker_universe, list) or not ticker_universe:
        return {}

    all_bars: list[object] = []
    for ticker in ticker_universe:
        try:
            response = requests.get(
                f"{API_BASE_URL}/market-data",
                params={
                    "ticker": ticker,
                    "start": "1900-01-01T00:00:00",
                    "end": "2099-12-31T23:59:59",
                    "interval": payload.get("interval", "1d"),
                    "limit": 100,
                },
                timeout=30,
            )
            response.raise_for_status()
            body = response.json()
            if isinstance(body, dict) and isinstance(body.get("bars"), list):
                all_bars.extend(body["bars"])
        except requests.RequestException:
            continue
    return {"bars": all_bars, "total": len(all_bars)}


def _session_list(key: str) -> list[dict[str, object]]:
    """Read list response data from Streamlit session state."""
    value = st.session_state.get(key)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _session_dict(key: str) -> dict[str, object]:
    """Read dictionary response data from Streamlit session state."""
    value = st.session_state.get(key)
    return value if isinstance(value, dict) else {}


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


def main() -> None:
    st.set_page_config(page_title="Market Data Pipeline", layout="wide")
    st.markdown(_CSS, unsafe_allow_html=True)
    render_data_ingestion()


if __name__ == "__main__":
    main()
