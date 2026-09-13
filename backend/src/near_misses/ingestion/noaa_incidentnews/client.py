import csv
import io
from typing import Any

import httpx

from near_misses.config import settings

# Tags observed only alongside a land-infrastructure cause (a pipeline
# rupture, a railcar derailment, a wellhead leak) — kept out because those
# aren't maritime accidents even though the resulting spill reaches a US
# waterway. A row with no tags, or with any other tag (Grounding, Collision,
# Derelict, Adrift, Search + Rescue, ...), is kept: most rows carry no tags
# at all and this dataset is inherently coastal/marine-incident-focused, so
# untagged is treated as in-scope rather than excluded.
_LAND_CAUSE_ONLY_TAGS = {"Pipeline", "Railcar", "Wellhead"}


def _is_maritime(raw_tags: str) -> bool:
    tags = [t.strip() for t in raw_tags.split("|") if t.strip()]
    if not tags:
        return True
    return not all(t in _LAND_CAUSE_ONLY_TAGS for t in tags)


class NoaaIncidentNewsClient:
    """Client for NOAA Office of Response and Restoration's IncidentNews feed (see ./README.md)."""

    source_name = "noaa_incidentnews"

    def fetch(self) -> list[dict[str, Any]]:
        response = httpx.get(settings.noaa_incidentnews_api_base, timeout=30)
        response.raise_for_status()
        rows = csv.DictReader(io.StringIO(response.text))
        return [row for row in rows if _is_maritime(row.get("tags") or "")]
