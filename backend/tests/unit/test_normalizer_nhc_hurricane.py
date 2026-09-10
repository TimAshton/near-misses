import json
from pathlib import Path

from near_misses.ingestion.nhc_hurricane.normalizer import NhcHurricaneNormalizer
from near_misses.schemas.incident import Category, Severity

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "nhc_hurricane_sample.json").read_text()
)["activeStorms"]


def _by_id(storm_id: str) -> dict:
    return next(s for s in FIXTURE if s["id"] == storm_id)


def test_normalizes_major_hurricane_to_critical_severity():
    raw = _by_id("al092026")
    incident = NhcHurricaneNormalizer().normalize(raw)

    assert incident.source == "nhc_hurricane"
    assert incident.source_id == "al092026"
    assert incident.category == Category.hurricane
    assert incident.event_type == "Hurricane"
    assert incident.severity == Severity.critical
    assert incident.title == "Hurricane Milton"
    assert incident.location.lat == 27.5
    assert incident.location.lng == -83.2
    assert "132 mph" in incident.description
    assert incident.source_url.endswith("MIATCPAT1.shtml")


def test_normalizes_tropical_storm_to_medium_severity():
    raw = _by_id("ep142026")
    incident = NhcHurricaneNormalizer().normalize(raw)

    assert incident.severity == Severity.medium
    assert incident.event_type == "Tropical Storm"
    assert incident.title == "Tropical Storm Norbert"


def test_normalizes_tropical_depression_to_low_severity():
    raw = _by_id("al102026")
    incident = NhcHurricaneNormalizer().normalize(raw)

    assert incident.severity == Severity.low
    assert incident.event_type == "Tropical Depression"


def test_unknown_classification_falls_back_to_raw_code():
    raw = {**_by_id("al102026"), "classification": "XX"}
    incident = NhcHurricaneNormalizer().normalize(raw)
    assert incident.event_type == "XX"
