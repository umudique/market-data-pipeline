from __future__ import annotations

import pytest

from src.screener.calculations import CloseReturnCalculator

pytestmark = pytest.mark.unit


def test_close_return_calculator_returns_positive_intraday_return() -> None:
    result = CloseReturnCalculator().calculate(
        earnings_open=100.0,
        earnings_close=105.0,
    )

    assert result == 5.0


def test_close_return_calculator_returns_negative_intraday_return() -> None:
    result = CloseReturnCalculator().calculate(
        earnings_open=100.0,
        earnings_close=95.0,
    )

    assert result == -5.0
