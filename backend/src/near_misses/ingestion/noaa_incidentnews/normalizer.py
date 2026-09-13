from datetime import UTC, datetime
from typing import Any

from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity

# Same spirit as usgs/normalizer.py's state parsing: NOAA's free-text
# "location" field isn't a structured city/state pair ("Gulf, LA",
# "1900 CA-1, Moss Landing, CA 95039, USA", "WG3M+9M Stockton, CA, USA"), but
# scanning each comma-separated part's first word for a state code catches
# every shape seen in the feed.
_US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC", "PR",
}

_GALLONS_HIGH_THRESHOLD = 10_000
_GALLONS_MEDIUM_THRESHOLD = 1_000
_GALLONS_CRITICAL_THRESHOLD = 100_000


def _parse_state(location: str) -> str | None:
    for part in location.split(","):
        words = part.strip().split(" ")
        if words and words[0] in _US_STATE_CODES:
            return words[0]
    return None


def _severity_for_gallons(raw_gallons: str | None) -> Severity:
    try:
        gallons = float(raw_gallons) if raw_gallons else None
    except ValueError:
        gallons = None
    # Unknown/unquantified is common for a casualty still being assessed
    # (e.g. a just-discovered sunken vessel) as well as for a trivial sheen
    # report — this dataset can't distinguish the two, so it defaults low,
    # same as USGS/NIFC default an unknown magnitude/size to low.
    if gallons is None:
        return Severity.low
    if gallons >= _GALLONS_CRITICAL_THRESHOLD:
        return Severity.critical
    if gallons >= _GALLONS_HIGH_THRESHOLD:
        return Severity.high
    if gallons >= _GALLONS_MEDIUM_THRESHOLD:
        return Severity.medium
    return Severity.low


def _event_type(threat: str) -> str:
    return "Marine Incident" if threat in ("", "Other") else f"{threat} Spill"


class NoaaIncidentNewsNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident:
        location_text = raw.get("location") or "Unknown location"
        event_type = _event_type(raw.get("threat") or "")
        title = raw.get("name") or event_type

        return NormalizedIncident(
            source="noaa_incidentnews",
            source_id=raw.get("id"),
            category=Category.maritime,
            event_type=event_type,
            severity=_severity_for_gallons(raw.get("max_ptl_release_gallons")),
            title=title,
            description=(raw.get("description") or "").strip(),
            occurred_at=datetime.fromisoformat(raw["open_date"]).replace(tzinfo=UTC),
            source_url=f"https://incidentnews.noaa.gov/incident/{raw['id']}",
            location=Location(
                lat=float(raw["lat"]),
                lng=float(raw["lon"]),
                state=_parse_state(location_text),
                display_name=location_text,
            ),
            raw=raw,
        )
