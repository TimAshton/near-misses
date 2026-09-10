import json
from pathlib import Path

import pytest

from near_misses.ingestion.fra_rail.normalizer import FraRailNormalizer
from near_misses.schemas.incident import Category, Severity

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "fra_rail_sample.json").read_text()
)


def _by_key(key: str) -> dict:
    return next(r for r in FIXTURE if r["incidentkey"] == key)


def test_normalizes_low_damage_no_casualty_derailment_to_low_severity():
    raw = _by_key("NS171002202606")
    incident = FraRailNormalizer().normalize(raw)

    assert incident.source == "fra_rail"
    assert incident.source_id == "NS171002202606"
    assert incident.category == Category.rail
    assert incident.event_type == "Derailment"
    assert incident.severity == Severity.low  # damage below $200k threshold
    assert incident.location.lat == 40.672362
    assert incident.location.lng == -80.251826
    assert incident.location.state == "PA"
    assert incident.title == "Derailment — Conway, PA"
    assert incident.occurred_at.hour == 22
    assert incident.occurred_at.minute == 56
    assert incident.description.startswith("Cause: Retarder worn, broken, or malfunctioning.")
    assert "MALFUNCTIONING RETARDER" in incident.description


def test_description_falls_back_to_narrative_only_when_cause_missing():
    raw = {**_by_key("NS171002202606"), "primaryaccidentcause": None}
    incident = FraRailNormalizer().normalize(raw)
    assert not incident.description.startswith("Cause:")
    assert "MALFUNCTIONING RETARDER" in incident.description


def test_normalizes_high_damage_no_casualty_derailment_to_medium_severity():
    raw = _by_key("UP-HIGH-DAMAGE-NO-INJURY")
    incident = FraRailNormalizer().normalize(raw)
    assert incident.severity == Severity.medium


def test_normalizes_injury_accident_to_high_severity():
    raw = _by_key("UP0626TO035202606")
    incident = FraRailNormalizer().normalize(raw)

    assert incident.severity == Severity.high
    assert incident.occurred_at.hour == 18
    assert incident.occurred_at.minute == 1


def test_normalizes_fatal_collision_to_critical_severity():
    raw = _by_key("CSX000232036202605")
    incident = FraRailNormalizer().normalize(raw)

    assert incident.severity == Severity.critical
    assert incident.occurred_at.hour == 3
    assert incident.occurred_at.minute == 15


def test_raises_on_missing_date():
    raw = _by_key("LEGACY-NO-DATE")
    with pytest.raises(TypeError):
        FraRailNormalizer().normalize(raw)
