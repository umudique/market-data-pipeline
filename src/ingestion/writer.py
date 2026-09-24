"""Raw source-payload persistence at the raw/staging boundary."""

from __future__ import annotations

from src.domain import IngestionBatch


class RawRecordWriter:
    """Persist source payloads to the raw/staging boundary.

    Preconditions:
        Records are provider/source dictionaries associated with an ingestion
        batch. They may contain defects and are not trusted.

    Postconditions:
        Source payloads are persisted to `raw_market_data` or equivalent staging
        storage. This component never writes to trusted `market_bars`.
    """

    def write_batch(
        self,
        batch: IngestionBatch,
        records: list[dict[str, object]],
    ) -> int:
        """Persist raw records for `batch` and return the staged count."""
        raise NotImplementedError
