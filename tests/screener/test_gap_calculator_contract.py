from __future__ import annotations

import pytest

from src.screener.calculations import GapCalculator

pytestmark = pytest.mark.unit


def test_gap_calculator_returns_positive_gap_percent() -> None:
    result = GapCalculator().calculate(earnings_open=110.0, prior_close=100.0)

    assert result == 10.0


def test_gap_calculator_returns_negative_gap_percent() -> None:
    result = GapCalculator().calculate(earnings_open=95.0, prior_close=100.0)

    assert result == -5.0
