from datetime import datetime
from typing import Any

from near_misses.ingestion.nws_alerts import resolve_alert_coordinates
from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity

# The client only fetches severity=Extreme, so in practice every record maps
# to critical here — this mirrors nws_tsunami's map anyway (kept the same
# shape rather than a single hardcoded value) so a missing `severity` field
# degrades to low instead of silently mis-mapping to critical.
_SEVERITY_MAP = {
    "Extreme": Severity.critical,
    "Severe": Severity.high,
    "Moderate": Severity.medium,
    "Minor": Severity.low,
}

_MAX_TITLE_LEN = 256


class NwsSevereWeatherNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident:
        props = raw["properties"]
        lng, lat = resolve_alert_coordinates(raw)

        area = props.get("areaDesc") or "affected areas"
        event = props.get("event") or "Severe Weather Alert"
        title = f"{event} — {area}"
        if len(title) > _MAX_TITLE_LEN:
            title = title[: _MAX_TITLE_LEN - 1] + "…"

        occurred_raw = props.get("onset") or props.get("effective") or props.get("sent")

        description_parts = [p for p in [props.get("description"), props.get("instruction")] if p]
        description = "\n\n".join(description_parts) or props.get("headline") or ""

        return NormalizedIncident(
            source="nws_severe_weather",
            source_id=props.get("id"),
            category=Category.severe_weather,
            event_type=event,
            severity=_SEVERITY_MAP.get(props.get("severity"), Severity.low),
            title=title,
            description=description,
            occurred_at=datetime.fromisoformat(occurred_raw),
            source_url=props.get("web"),
            location=Location(lat=lat, lng=lng, display_name=area.split(";")[0].strip()),
            raw=raw,
        )
