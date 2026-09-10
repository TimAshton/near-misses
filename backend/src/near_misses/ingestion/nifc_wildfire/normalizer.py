from datetime import UTC, datetime
from typing import Any

from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity


def _severity_for_acres(acres: float | None) -> Severity:
    if acres is None:
        return Severity.low
    if acres >= 10_000:
        return Severity.critical
    if acres >= 1_000:
        return Severity.high
    if acres >= 100:
        return Severity.medium
    return Severity.low


def _state_abbr(poo_state: str | None) -> str | None:
    if not poo_state:
        return None
    return poo_state.removeprefix("US-")


class NifcWildfireNormalizer:
    def normalize(self, raw: dict[str, Any]) -> NormalizedIncident:
        attrs = raw["attributes"]
        geometry = raw["geometry"]

        name = attrs.get("IncidentName") or "Unnamed Fire"
        state = _state_abbr(attrs.get("POOState"))
        county = attrs.get("POOCounty")
        title = f"{name} Fire"
        if county and state:
            title = f"{name} Fire — {county}, {state}"

        acres = attrs.get("IncidentSize")
        contained = attrs.get("PercentContained")
        cause = attrs.get("FireCause")

        description_parts = []
        if acres is not None:
            description_parts.append(f"{acres:,.0f} acres")
        if contained is not None:
            description_parts.append(f"{contained:.0f}% contained")
        if cause:
            description_parts.append(f"Cause: {cause}")
        description = ", ".join(description_parts) + "." if description_parts else ""

        return NormalizedIncident(
            source="nifc_wildfire",
            source_id=attrs.get("UniqueFireIdentifier"),
            category=Category.wildfire,
            event_type="Wildfire",
            severity=_severity_for_acres(acres),
            title=title,
            description=description,
            occurred_at=datetime.fromtimestamp(attrs["FireDiscoveryDateTime"] / 1000, tz=UTC),
            source_url=None,
            location=Location(
                lat=geometry["y"],
                lng=geometry["x"],
                state=state,
                display_name=county,
            ),
            raw=raw,
        )
