from __future__ import annotations

import pytest

from src.normalization.ticker import TickerNormalizer

pytestmark = pytest.mark.unit


def test_ticker_normalizer_uppercases_lowercase_input() -> None:
    assert TickerNormalizer().normalize("aapl") == "AAPL"


def test_ticker_normalizer_strips_whitespace_and_provider_prefix() -> None:
    assert TickerNormalizer().normalize("  yfinance:msft  ") == "MSFT"


def test_ticker_normalizer_leaves_canonical_ticker_unchanged() -> None:
    assert TickerNormalizer().normalize("NVDA") == "NVDA"
