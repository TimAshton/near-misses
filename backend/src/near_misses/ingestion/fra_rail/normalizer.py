from datetime import UTC, datetime
from typing import Any

from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity

_DAMAGE_COST_MEDIUM_THRESHOLD = 200_000


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _severity_for(raw: dict[str, Any]) -> Severity:
    if _to_float(raw.get("totalpersonskilled")) > 0:
        return Severity.critical
    if _to_float(raw.get("totalpersonsinjured")) > 0:
        return Severity.high
    if _to_float(raw.get("totaldamagecost")) >= _DAMAGE_COST_MEDIUM_THRESHOLD:
        return Severity.medium
    return Severity.low


def _occurred_at(raw: dict[str, Any]) -> datetime:
    date_str = raw["date"][:10]  # "2026-06-30T00:00:00.000" -> "2026-06-30"
    hour, minute = 0, 0
    time_str = raw.get("time")
    if time_str:
        try:
            parsed = datetime.strptime(time_str.strip(), "%I:%M %p")
            hour, minute = parsed.hour, parsed.minute
        except ValueError:
            pass
    return datetime.fromisoformat(date_str).replace(hour=hour, minute=minute, tzinfo=UTC)


class FraRailNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident:
        event_type = raw.get("accidenttype") or "Rail accident/incident"
        station = raw.get("station")
        state = raw.get("stateabbr")
        title = event_type
        if station and state:
            title = f"{event_type} — {station.title()}, {state}"

        url = (raw.get("url") or {}).get("url")

        return NormalizedIncident(
            source="fra_rail",
            source_id=raw.get("incidentkey"),
            category=Category.rail,
            event_type=event_type,
            severity=_severity_for(raw),
            title=title,
            description=(raw.get("narrative") or "").strip(),
            occurred_at=_occurred_at(raw),
            source_url=url,
            location=Location(
                lat=float(raw["latitude"]),
                lng=float(raw["longitude"]),
                city=station.title() if station else None,
                state=state,
                display_name=station.title() if station else None,
            ),
            raw=raw,
        )
