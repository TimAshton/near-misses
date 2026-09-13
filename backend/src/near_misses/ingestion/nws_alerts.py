"""Shared plumbing for every source built on NOAA/NWS's CAP alerts feed
(`GET api.weather.gov/alerts/active`) — currently nws_tsunami and
nws_severe_weather. Both need the same "most alerts carry no geometry,
resolve one from the alert's forecast zone" dance and the same
geometry-or-zone-centroid fallback when normalizing, so it's factored out
here instead of duplicated per-source.
"""

from typing import Any

import httpx

from near_misses.config import settings


def polygon_centroid(ring: list[list[float]]) -> tuple[float, float]:
    """Vertex-average centroid of a polygon ring: (lng, lat).

    Not area-weighted (a poor approximation for very unevenly-vertexed
    shapes), but adequate for placing a map marker at the approximate
    center of a warned zone — same spirit as SPEC.md's guidance to place
    large-area incidents (hurricanes, seismic zones) at their center.
    """
    lngs = [point[0] for point in ring]
    lats = [point[1] for point in ring]
    return (sum(lngs) / len(lngs), sum(lats) / len(lats))


def fetch_active_alerts(params: dict[str, str]) -> list[dict[str, Any]]:
    """Fetches active CAP alerts matching `params` and enriches every
    geometry-less feature with a `_resolved_centroid` (cached per zone
    within this call, so alerts sharing a zone don't refetch it).
    """
    headers = {"User-Agent": settings.nws_user_agent, "Accept": "application/geo+json"}
    response = httpx.get(
        f"{settings.nws_api_base}/alerts/active", params=params, headers=headers, timeout=15
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
            zone_ring_cache[zone_id] = _fetch_zone_ring(zone_id, headers)
        ring = zone_ring_cache[zone_id]
        if ring:
            feature["_resolved_centroid"] = list(polygon_centroid(ring))

    return features


def _fetch_zone_ring(zone_id: str, headers: dict[str, str]) -> list[list[float]] | None:
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


def resolve_alert_coordinates(raw: dict[str, Any]) -> tuple[float, float]:
    """Returns (lng, lat) for one CAP alert feature: its own geometry when
    present, else the `_resolved_centroid` fetch_active_alerts stashed on it.
    """
    geometry = raw.get("geometry")
    if geometry and geometry.get("coordinates"):
        gtype = geometry.get("type")
        coords = geometry["coordinates"]
        if gtype == "Point":
            return coords[0], coords[1]
        if gtype == "Polygon":
            return polygon_centroid(coords[0])
        if gtype == "MultiPolygon":
            return polygon_centroid(coords[0][0])

    centroid = raw.get("_resolved_centroid")
    if centroid:
        return centroid[0], centroid[1]

    raise ValueError("No resolvable location for NWS alert")
