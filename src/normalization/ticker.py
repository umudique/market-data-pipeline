"""Convert provider-specific ticker forms to canonical representation."""

from __future__ import annotations


class TickerNormalizer:
    def normalize(self, raw_ticker: str) -> str:
        return raw_ticker.strip().split(":")[-1].upper()
