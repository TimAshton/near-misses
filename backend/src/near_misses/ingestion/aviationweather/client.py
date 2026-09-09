"""Optional supplementary weather context — NOT an incident source.

aviationweather.gov serves current METAR/TAF/PIREP data (confirmed live,
returns HTTP 200, no key required). It has no accident/incident records, so
it's not used as a Phase 1 ingestion source (see ../ntsb and ../faa_aids
READMEs). Kept as a stub for a possible future enrichment step: attaching
weather-at-time-of-incident context to an NTSB record via its
`AirportId`/`occurred_at`. Not wired into the pipeline.
"""

from typing import Any

import httpx

from near_misses.config import settings


def fetch_metar(station_id: str) -> dict[str, Any] | None:
    response = httpx.get(
        f"{settings.aviationweather_api_base}/metar",
        params={"ids": station_id, "format": "json"},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json()
    return results[0] if results else None
