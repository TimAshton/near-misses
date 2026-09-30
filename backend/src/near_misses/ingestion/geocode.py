"""City+state -> lat/lng lookups for sources that don't carry their own
coordinates (currently just NTSB's live CAROL search results — see
ingestion/ntsb/README.md).

Backed by the geocode_cache table so repeat lookups — the overwhelming
majority in steady state, since a poll re-fetches mostly the same recent
records every 5 minutes and real-world reports cluster into a limited set of
cities/states — never re-hit the geocoder. That keeps this well under
Nominatim's free-tier usage policy (max 1 request/second, no bulk use)
without needing to special-case "is this a duplicate record" logic here.

Uses its own short-lived DB session rather than the caller's, since this
cache is valid independent of whatever incident row is or isn't ultimately
written in the surrounding pipeline run.
"""

import logging
import time

import httpx
from sqlalchemy import select

from near_misses.config import settings
from near_misses.db import SessionLocal
from near_misses.models.geocode_cache import GeocodeCache

logger = logging.getLogger(__name__)

_MIN_REQUEST_INTERVAL_SECONDS = 1.0
_last_request_at: float = 0.0


def geocode_city_state(city: str, state: str) -> tuple[float, float] | None:
    """Returns (lat, lng) for a US city+state, or None if it can't be resolved."""
    db = SessionLocal()
    try:
        cached = db.execute(
            select(GeocodeCache).where(GeocodeCache.city == city, GeocodeCache.state == state)
        ).scalar_one_or_none()
        if cached is not None:
            return (cached.lat, cached.lng) if cached.lat is not None else None

        coords = _query_nominatim(city, state)
        db.add(
            GeocodeCache(
                city=city,
                state=state,
                lat=coords[0] if coords else None,
                lng=coords[1] if coords else None,
            )
        )
        db.commit()
        return coords
    finally:
        db.close()


def _query_nominatim(city: str, state: str) -> tuple[float, float] | None:
    global _last_request_at
    wait = _MIN_REQUEST_INTERVAL_SECONDS - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)

    try:
        response = httpx.get(
            settings.nominatim_api_base,
            params={
                "q": f"{city}, {state}, USA",
                "format": "json",
                "limit": 1,
                "countrycodes": "us",
            },
            headers={"User-Agent": settings.nws_user_agent},
            timeout=10,
        )
        _last_request_at = time.monotonic()
        response.raise_for_status()
        results = response.json()
    except httpx.HTTPError:
        logger.exception("Nominatim geocode request failed for %s, %s", city, state)
        return None

    if not results:
        return None
    return float(results[0]["lat"]), float(results[0]["lon"])
