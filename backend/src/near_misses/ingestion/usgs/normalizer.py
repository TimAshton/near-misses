from datetime import UTC, datetime
from typing import Any

from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity

# USGS "place" strings (e.g. "10km NW of Ridgecrest, CA") aren't a structured
# city/state pair, but the trailing ", XX" is a US state/territory code often
# enough to be worth surfacing in the state filter and top_states stat.
_US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC", "PR",
}


def _parse_state(place: str) -> str | None:
    if "," not in place:
        return None
    candidate = place.rsplit(",", 1)[-1].strip().upper()
    return candidate if candidate in _US_STATE_CODES else None


def _severity_for_magnitude(mag: float | None) -> Severity:
    if mag is None:
        return Severity.low
    if mag >= 6.0:
        return Severity.critical
    if mag >= 4.5:
        return Severity.high
    if mag >= 2.5:
        return Severity.medium
    return Severity.low


class UsgsNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident:
        props = raw["properties"]
        lng, lat, *_ = raw["geometry"]["coordinates"]
        mag = props.get("mag")

        place = props.get("place") or "Unknown location"
        title = props.get("title") or (
            f"M {mag} - {place}" if mag is not None else f"Earthquake - {place}"
        )

        return NormalizedIncident(
            source="usgs",
            source_id=raw["id"],
            category=Category.seismic,
            event_type=(props.get("type") or "earthquake").replace("_", " ").title(),
            severity=_severity_for_magnitude(mag),
            title=title,
            description=(
                f"Magnitude {mag} earthquake near {place}." if mag is not None
                else f"Earthquake near {place}."
            ),
            occurred_at=datetime.fromtimestamp(props["time"] / 1000, tz=UTC),
            source_url=props.get("url"),
            location=Location(
                lat=lat,
                lng=lng,
                state=_parse_state(place),
                display_name=place,
            ),
            raw=raw,
        )
