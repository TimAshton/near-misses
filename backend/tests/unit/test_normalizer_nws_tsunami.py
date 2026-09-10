import json
from pathlib import Path

import pytest

from near_misses.ingestion.nws_tsunami.normalizer import NwsTsunamiNormalizer
from near_misses.schemas.incident import Category, Severity

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "nws_tsunami_sample.json").read_text()
)["features"]


def _by_id(suffix: str) -> dict:
    return next(f for f in FIXTURE if f["properties"]["id"].endswith(suffix))


def test_normalizes_warning_using_resolved_centroid_fallback():
    raw = {**_by_id("tsunami-warning-001"), "_resolved_centroid": [-151.7, 57.8]}
    incident = NwsTsunamiNormalizer().normalize(raw)

    assert incident.source == "nws_tsunami"
    assert incident.category == Category.tsunami
    assert incident.severity == Severity.critical
    assert incident.event_type == "Tsunami Warning"
    assert incident.location.lng == -151.7
    assert incident.location.lat == 57.8
    assert "Kodiak" in incident.title
    assert "magnitude 7.8 earthquake" in incident.description
    assert "Move to high ground immediately" in incident.description


def test_normalizes_advisory_using_point_geometry():
    raw = _by_id("tsunami-advisory-002")
    incident = NwsTsunamiNormalizer().normalize(raw)

    assert incident.severity == Severity.medium
    assert incident.location.lng == -157.86
    assert incident.location.lat == 21.31
    assert incident.location.display_name == "Coastal Honolulu County"


def test_raises_when_no_location_is_resolvable():
    raw = _by_id("tsunami-warning-001")  # geometry: null, no _resolved_centroid
    with pytest.raises(ValueError):
        NwsTsunamiNormalizer().normalize(raw)


def test_unknown_severity_defaults_to_low():
    raw = {
        **_by_id("tsunami-advisory-002"),
        "properties": {**_by_id("tsunami-advisory-002")["properties"], "severity": "Unknown"},
    }
    incident = NwsTsunamiNormalizer().normalize(raw)
    assert incident.severity == Severity.low


def test_description_falls_back_to_headline_when_no_description_or_instruction():
    props = {**_by_id("tsunami-advisory-002")["properties"], "description": None}
    raw = {**_by_id("tsunami-advisory-002"), "properties": props}
    incident = NwsTsunamiNormalizer().normalize(raw)
    assert incident.description == props["headline"]
