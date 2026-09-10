import json
from pathlib import Path

from near_misses.ingestion.usgs.normalizer import UsgsNormalizer
from near_misses.schemas.incident import Category, Severity

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "usgs_sample.json").read_text()
)["features"]


def test_normalizes_moderate_quake_to_high_severity():
    raw = next(f for f in FIXTURE if f["id"] == "ci40624840")
    incident = UsgsNormalizer().normalize(raw)

    assert incident.source == "usgs"
    assert incident.source_id == "ci40624840"
    assert incident.category == Category.seismic
    assert incident.severity == Severity.high
    assert incident.event_type == "Earthquake"
    assert incident.location.lat == 35.7695
    assert incident.location.lng == -117.6709
    assert incident.location.state == "CA"
    assert incident.title == "M 4.8 - 10km NW of Ridgecrest, CA"
    assert incident.source_url.endswith("ci40624840")


def test_normalizes_major_quake_to_critical_severity():
    raw = next(f for f in FIXTURE if f["id"] == "ak02451234")
    incident = UsgsNormalizer().normalize(raw)

    assert incident.severity == Severity.critical
    assert incident.location.state is None  # "Alaska" isn't the 2-letter code we match


def test_normalizes_micro_event_to_low_severity_and_titlecases_event_type():
    raw = next(f for f in FIXTURE if f["id"] == "nc73999999")
    incident = UsgsNormalizer().normalize(raw)

    assert incident.severity == Severity.low
    assert incident.event_type == "Quarry Blast"


def test_missing_magnitude_defaults_to_low_severity():
    raw = {**FIXTURE[0], "properties": {**FIXTURE[0]["properties"], "mag": None}}
    incident = UsgsNormalizer().normalize(raw)
    assert incident.severity == Severity.low
