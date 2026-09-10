from typing import Any

import httpx

from near_misses.config import settings


class UsgsClient:
    """Client for the USGS Earthquake Hazards Program's real-time GeoJSON feed.

    Unlike NTSB (see ../ntsb/README.md), this is a fully public, documented,
    unauthenticated API — no fixture-mode fallback needed.
    """

    source_name = "usgs"

    def fetch(self) -> list[dict[str, Any]]:
        response = httpx.get(settings.usgs_api_base, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("features", [])
