from datetime import datetime
from typing import Any

from near_misses.ingestion.nws_tsunami.geo import polygon_centroid
from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity

_SEVERITY_MAP = {
    "Extreme": Severity.critical,
    "Severe": Severity.high,
    "Moderate": Severity.medium,
    "Minor": Severity.low,
}

_MAX_TITLE_LEN = 256


class NwsTsunamiNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident:
        props = raw["properties"]
        lng, lat = self._resolve_coordinates(raw)

        area = props.get("areaDesc") or "affected coastal areas"
        event = props.get("event") or "Tsunami Alert"
        title = f"{event} — {area}"
        if len(title) > _MAX_TITLE_LEN:
            title = title[: _MAX_TITLE_LEN - 1] + "…"

        occurred_raw = props.get("onset") or props.get("effective") or props.get("sent")

        # NWS CAP alerts carry both a situation description and a separate
        # "what to do" instruction — both are sentence-length prose worth
        # surfacing, not just whichever one happens to be present.
        description_parts = [p for p in [props.get("description"), props.get("instruction")] if p]
        description = "\n\n".join(description_parts) or props.get("headline") or ""

        return NormalizedIncident(
            source="nws_tsunami",
            source_id=props.get("id"),
            category=Category.tsunami,
            event_type=event,
            severity=_SEVERITY_MAP.get(props.get("severity"), Severity.low),
            title=title,
            description=description,
            occurred_at=datetime.fromisoformat(occurred_raw),
            source_url=props.get("web"),
            location=Location(lat=lat, lng=lng, display_name=area.split(";")[0].strip()),
            raw=raw,
        )

    def _resolve_coordinates(self, raw: dict[str, Any]) -> tuple[float, float]:
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

        raise ValueError("No resolvable location for NWS tsunami alert")
