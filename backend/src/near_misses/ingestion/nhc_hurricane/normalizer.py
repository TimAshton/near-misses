from datetime import datetime
from typing import Any

from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity

_KNOTS_TO_MPH = 1.15078

_CLASSIFICATION_LABELS = {
    "TD": "Tropical Depression",
    "SD": "Subtropical Depression",
    "TS": "Tropical Storm",
    "SS": "Subtropical Storm",
    "HU": "Hurricane",
    "EX": "Extratropical Cyclone",
    "PTC": "Potential Tropical Cyclone",
}


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _severity_for_intensity(intensity_kt: float | None) -> Severity:
    if intensity_kt is None:
        return Severity.low
    mph = intensity_kt * _KNOTS_TO_MPH
    if mph >= 111:  # Category 3+ (major hurricane)
        return Severity.critical
    if mph >= 74:  # Category 1+ hurricane
        return Severity.high
    if mph >= 39:  # Tropical storm
        return Severity.medium
    return Severity.low


class NhcHurricaneNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident:
        classification = raw.get("classification") or ""
        event_type = _CLASSIFICATION_LABELS.get(classification, classification or "Storm")
        name = raw.get("name") or "Unnamed"
        title = f"{event_type} {name}"

        intensity_kt = _to_float(raw.get("intensity"))
        mph = round(intensity_kt * _KNOTS_TO_MPH) if intensity_kt is not None else None
        pressure = raw.get("pressure")

        description_parts = [f"{name} is a {event_type.lower()}"]
        if mph is not None:
            description_parts.append(f"with sustained winds of {mph} mph ({intensity_kt:.0f} kt)")
        if pressure:
            description_parts.append(f"and a central pressure of {pressure} mb")
        description = " ".join(description_parts) + "."

        public_advisory = raw.get("publicAdvisory") or {}

        return NormalizedIncident(
            source="nhc_hurricane",
            source_id=raw.get("id"),
            category=Category.hurricane,
            event_type=event_type,
            severity=_severity_for_intensity(intensity_kt),
            title=title,
            description=description,
            occurred_at=datetime.fromisoformat(raw["lastUpdate"].replace("Z", "+00:00")),
            source_url=public_advisory.get("url"),
            location=Location(
                lat=float(raw["latitudeNumeric"]),
                lng=float(raw["longitudeNumeric"]),
                display_name=name,
            ),
            raw=raw,
        )
