import json
from pathlib import Path

from near_misses.ingestion.nifc_wildfire.normalizer import NifcWildfireNormalizer
from near_misses.schemas.incident import Category, Severity

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "nifc_wildfire_sample.json").read_text()
)["features"]


def _by_id(fire_id: str) -> dict:
    return next(f for f in FIXTURE if f["attributes"]["UniqueFireIdentifier"] == fire_id)


def test_normalizes_large_fire_to_critical_severity():
    raw = _by_id("2026-CALAC-325444")
    incident = NifcWildfireNormalizer().normalize(raw)

    assert incident.source == "nifc_wildfire"
    assert incident.source_id == "2026-CALAC-325444"
    assert incident.category == Category.wildfire
    assert incident.event_type == "Wildfire"
    assert incident.severity == Severity.critical
    assert incident.title == "PALISADES Fire — Los Angeles, CA"
    assert incident.location.lat == 34.03108
    assert incident.location.lng == -118.07282
    assert incident.location.state == "CA"
    assert "23,713 acres" in incident.description
    assert "45% contained" in incident.description
    assert incident.source_url is None


def test_normalizes_medium_fire_to_high_severity():
    raw = _by_id("2026-ORJAC-100123")
    incident = NifcWildfireNormalizer().normalize(raw)
    assert incident.severity == Severity.high


def test_normalizes_tiny_fire_to_low_severity():
    raw = _by_id("2026-CAMEU-010693")
    incident = NifcWildfireNormalizer().normalize(raw)
    assert incident.severity == Severity.low


def test_missing_size_defaults_to_low_severity_and_handles_missing_fields():
    raw = _by_id("2026-TXTRV-000001")
    incident = NifcWildfireNormalizer().normalize(raw)
    assert incident.severity == Severity.low
    assert incident.description == ""
