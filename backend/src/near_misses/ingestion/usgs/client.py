from typing import Any

import httpx

from near_misses.config import settings

# Keep in sync with normalizer.py's magnitude->severity mapping: this is the
# low/medium boundary, so anything below it is excluded here rather than
# ingested as a "low" severity earthquake. The feed URL (see config.py) is
# already pre-filtered to 2.5+ server-side, but its boundary isn't exact
# (observed magnitudes just under 2.5 slipping through), so this is enforced
# again client-side.
MIN_TRACKED_MAGNITUDE = 2.5


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
        features = data.get("features", [])
        return [
            f
            for f in features
            if (f.get("properties", {}).get("mag") or 0) >= MIN_TRACKED_MAGNITUDE
        ]
