from typing import Any

import httpx

from near_misses.config import settings


class FraRailClient:
    """Client for FRA's Rail Equipment Accident/Incident data (see ./README.md)."""

    source_name = "fra_rail"

    def fetch(self) -> list[dict[str, Any]]:
        response = httpx.get(
            settings.fra_api_base,
            params={
                "$where": "date IS NOT NULL",
                "$order": "date DESC",
                "$limit": 200,
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
