from typing import Any

import httpx

from near_misses.config import settings

# Keep in sync with normalizer.py's magnitude->severity mapping: this is the
# medium/high boundary, so anything below it is excluded here rather than
# ingested as a medium (or lower) severity earthquake that severity_policy
# would just filter out post-normalization anyway. The feed URL (see
# config.py) is only pre-filtered to 2.5+ server-side, so this is enforced
# again client-side at the real threshold.
MIN_TRACKED_MAGNITUDE = 4.5


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
