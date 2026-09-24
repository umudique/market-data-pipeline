"""Streamlit dashboard — presentation only, delegates to API."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Market Data Pipeline", layout="wide")

st.title("Financial Market Data Pipeline")

page = st.sidebar.selectbox("Page", ["Earnings Gap Screener", "Pipeline Quality"])

if page == "Earnings Gap Screener":
    st.header("Earnings Gap Screener")
    st.info("Screener UI — not yet implemented.")

elif page == "Pipeline Quality":
    st.header("Pipeline Quality")
    st.info("Quality dashboard — not yet implemented.")
