from typing import Any

import httpx

from near_misses.config import settings


class NhcHurricaneClient:
    """Client for NOAA's National Hurricane Center active-storms feed (see ./README.md)."""

    source_name = "nhc_hurricane"

    def fetch(self) -> list[dict[str, Any]]:
        response = httpx.get(settings.nhc_api_base, timeout=15)
        response.raise_for_status()
        return response.json().get("activeStorms", [])
