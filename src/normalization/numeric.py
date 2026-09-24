"""Convert numeric fields to expected database-safe types."""

from __future__ import annotations

from typing import Any


class NumericNormalizer:
    def normalize(self, record: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
