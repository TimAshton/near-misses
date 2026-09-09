from typing import Any, Protocol

from near_misses.schemas.incident import NormalizedIncident


class SourceClient(Protocol):
    """Fetches raw records from one upstream data source."""

    source_name: str

    def fetch(self) -> list[dict[str, Any]]:
        """Return a list of raw records (already-parsed JSON dicts)."""
        ...


class Normalizer(Protocol):
    """Maps one raw record from a source into the shared incident schema."""

    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident: ...
