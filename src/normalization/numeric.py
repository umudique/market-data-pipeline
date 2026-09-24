"""Convert numeric fields to expected database-safe types."""

from __future__ import annotations

import math
from typing import Any


class NumericNormalizer:
    _numeric_fields = ("open", "high", "low", "close", "volume")

    def normalize(self, record: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(record)
        for field in self._numeric_fields:
            value = float(normalized[field])
            if math.isnan(value):
                raise ValueError(f"{field} cannot be NaN")
            normalized[field] = value
        return normalized
