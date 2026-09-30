from datetime import datetime
from typing import Any

from near_misses.ingestion.geocode import geocode_city_state
from near_misses.ingestion.us_states import US_STATE_NAME_TO_ABBR
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
        injury_level = raw.get("HighestInjuryLevel") or "None"
        severity = _INJURY_TO_SEVERITY.get(injury_level, Severity.low)

        city = raw.get("City")
        state_name = raw.get("State")
        state_abbr = US_STATE_NAME_TO_ABBR.get(state_name) if state_name else None

        if state_abbr and city:
            coords = geocode_city_state(city, state_name)
        elif city:
            # No resolvable US state — either missing entirely or a
            # placeholder like "Other Foreign". NTSB tracks foreign
            # occurrences of US-registered aircraft too, and both shapes
            # mean the same thing here: no US city/state pair to geocode.
            # Hand back an obviously-non-US point rather than raise (which
            # the pipeline would log as a failure every single poll, for
            # what's actually expected, recurring input) — this way the
            # normal is_us_location rejection path in the pipeline filters
            # it the same way every other source's non-US records are.
            coords = (0.0, 0.0)
        else:
            coords = None

        if coords is None:
            raise ValueError(
                f"Could not geocode {city!r}, {state_name!r} for NTSB record "
                f"{raw.get('NtsbNo')!r}"
            )

        title_bits = [b for b in [raw.get("VehicleMake"), raw.get("VehicleModel")] if b]
        title = " ".join(title_bits) or "Aviation incident"
        if city and state_abbr:
            title = f"{title} — {city}, {state_abbr}"

        description_bits = [f"NTSB-reported {(raw.get('EventType') or 'accident').lower()}"]
        registration = raw.get("N#")
        if registration:
            description_bits.append(f"involving {registration}")
        if city and state_abbr:
            description_bits.append(f"near {city}, {state_abbr}")
        description = " ".join(description_bits) + f". Highest reported injury: {injury_level}."

        ntsb_no = raw["NtsbNo"]
        return NormalizedIncident(
            source="ntsb",
            source_id=ntsb_no,
            category=Category.aviation,
            event_type=raw.get("EventType") or "Accident",
            severity=severity,
            title=title,
            description=description,
            occurred_at=datetime.fromisoformat(raw["EventDate"].replace("Z", "+00:00")),
            source_url=f"https://www.ntsb.gov/investigations/AccidentReports/Pages/{ntsb_no}.aspx",
            location=Location(
                lat=coords[0],
                lng=coords[1],
                city=city,
                state=state_abbr,
                display_name=f"{city}, {state_abbr}" if city and state_abbr else city,
            ),
            raw=raw,
        )
