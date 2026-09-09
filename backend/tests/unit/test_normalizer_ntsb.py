import json
from pathlib import Path

from near_misses.ingestion.ntsb.normalizer import NtsbNormalizer
from near_misses.schemas.incident import Category, Severity

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "ntsb_sample.json").read_text()
)


def test_normalizes_fatal_record_to_critical_severity():
    raw = next(r for r in FIXTURE if r["NtsbNumber"] == "ERA24FA089")
    incident = NtsbNormalizer().normalize(raw)

    assert incident.source == "ntsb"
    assert incident.source_id == "ERA24FA089"
    assert incident.category == Category.aviation
    assert incident.severity == Severity.critical
    assert incident.location.lat == 29.1727
    assert incident.location.lng == -82.2243
    assert incident.location.state == "FL"
    assert "Piper" in incident.title
    assert incident.source_url.endswith("ERA24FA089.aspx")


def test_normalizes_minor_record_to_medium_severity():
    raw = next(r for r in FIXTURE if r["NtsbNumber"] == "CEN24LA123")
    incident = NtsbNormalizer().normalize(raw)

    assert incident.severity == Severity.medium
    assert incident.location.display_name == "Georgetown Municipal Airport"


def test_unknown_injury_level_defaults_to_low():
    raw = {**FIXTURE[0], "HighestInjuryLevel": "SomethingUnexpected"}
    incident = NtsbNormalizer().normalize(raw)
    assert incident.severity == Severity.low
