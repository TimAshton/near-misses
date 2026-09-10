from typing import Any

import httpx

from near_misses.config import settings
from near_misses.ingestion.nws_tsunami.geo import polygon_centroid

_EVENTS = "Tsunami Warning,Tsunami Watch,Tsunami Advisory"


class NwsTsunamiClient:
    """Client for NOAA/NWS's public tsunami alerts feed (see ./README.md)."""

    source_name = "nws_tsunami"

    def fetch(self) -> list[dict[str, Any]]:
        headers = {"User-Agent": settings.nws_user_agent, "Accept": "application/geo+json"}
        response = httpx.get(
            f"{settings.nws_api_base}/alerts/active",
            params={"event": _EVENTS},
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        features = response.json().get("features", [])

        zone_ring_cache: dict[str, list[list[float]] | None] = {}
        for feature in features:
            if feature.get("geometry"):
                continue
            ugc_codes = feature.get("properties", {}).get("geocode", {}).get("UGC", [])
            if not ugc_codes:
                continue
            zone_id = ugc_codes[0]
            if zone_id not in zone_ring_cache:
                zone_ring_cache[zone_id] = self._fetch_zone_ring(zone_id, headers)
            ring = zone_ring_cache[zone_id]
            if ring:
                feature["_resolved_centroid"] = list(polygon_centroid(ring))

        return features

    def _fetch_zone_ring(self, zone_id: str, headers: dict[str, str]) -> list[list[float]] | None:
        try:
            response = httpx.get(
                f"{settings.nws_api_base}/zones/forecast/{zone_id}", headers=headers, timeout=10
            )
            response.raise_for_status()
            geometry = response.json().get("geometry") or {}
        except httpx.HTTPError:
            return None

        if geometry.get("type") == "Polygon":
            return geometry["coordinates"][0]
        if geometry.get("type") == "MultiPolygon":
            return geometry["coordinates"][0][0]
        return None
