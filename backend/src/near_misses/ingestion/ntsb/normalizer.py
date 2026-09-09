from datetime import datetime
from typing import Any

from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity

# NTSB records don't carry a direct "severity" field — map from the highest
# reported injury level (its closest proxy) to our normalized scale.
_INJURY_TO_SEVERITY = {
    "Fatal": Severity.critical,
    "Serious": Severity.high,
    "Minor": Severity.medium,
    "None": Severity.low,
}


class NtsbNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident:
        injury_level = raw.get("HighestInjuryLevel", "None")
        severity = _INJURY_TO_SEVERITY.get(injury_level, Severity.low)

        city = raw.get("City")
        state = raw.get("State")
        airport = raw.get("AirportName") or raw.get("AirportId")
        title_bits = [b for b in [raw.get("AircraftMake"), raw.get("AircraftModel")] if b]
        title = " ".join(title_bits) or "Aviation incident"
        if city and state:
            title = f"{title} — {city}, {state}"

        return NormalizedIncident(
            source="ntsb",
            source_id=raw["NtsbNumber"],
            category=Category.aviation,
            event_type=raw.get("EventType", "Accident"),
            severity=severity,
            title=title,
            description=raw.get("NarrativeBrief", ""),
            occurred_at=datetime.fromisoformat(raw["EventDate"].replace("Z", "+00:00")),
            source_url=raw.get("ReportUrl"),
            location=Location(
                lat=float(raw["Latitude"]),
                lng=float(raw["Longitude"]),
                city=city,
                state=state,
                display_name=airport or (f"{city}, {state}" if city and state else None),
            ),
            raw=raw,
        )
