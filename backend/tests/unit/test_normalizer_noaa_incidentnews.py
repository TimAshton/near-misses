from datetime import UTC, datetime

from near_misses.ingestion.noaa_incidentnews.normalizer import NoaaIncidentNewsNormalizer
from near_misses.schemas.incident import Category, Severity

RAW = {
    "id": "11212",
    "open_date": "2026-08-30",
    "name": "Sunken Vessel at Boat Ramp; Moss Landing, California",
    "location": "1900 CA-1, Moss Landing, CA 95039, USA",
    "lat": "36.811476",
    "lon": "-121.786806",
    "threat": "Oil",
    "tags": "",
    "max_ptl_release_gallons": "",
    "description": "A vessel sank, discharging diesel.",
}


def test_normalizes_core_fields():
    incident = NoaaIncidentNewsNormalizer().normalize(RAW)

    assert incident.source == "noaa_incidentnews"
    assert incident.source_id == "11212"
    assert incident.category == Category.maritime
    assert incident.event_type == "Oil Spill"
    assert incident.title == RAW["name"]
    assert incident.occurred_at == datetime(2026, 8, 30, tzinfo=UTC)
    assert incident.source_url == "https://incidentnews.noaa.gov/incident/11212"
    assert incident.location.lat == 36.811476
    assert incident.location.lng == -121.786806
    assert incident.location.state == "CA"


def test_unknown_gallons_defaults_to_low_severity():
    incident = NoaaIncidentNewsNormalizer().normalize(RAW)
    assert incident.severity == Severity.low


def test_severity_scales_with_gallons():
    normalizer = NoaaIncidentNewsNormalizer()
    assert normalizer.normalize({**RAW, "max_ptl_release_gallons": "500"}).severity == Severity.low
    assert (
        normalizer.normalize({**RAW, "max_ptl_release_gallons": "5000"}).severity
        == Severity.medium
    )
    assert (
        normalizer.normalize({**RAW, "max_ptl_release_gallons": "50000"}).severity
        == Severity.high
    )
    assert (
        normalizer.normalize({**RAW, "max_ptl_release_gallons": "500000"}).severity
        == Severity.critical
    )


def test_other_threat_gets_generic_event_type():
    incident = NoaaIncidentNewsNormalizer().normalize({**RAW, "threat": "Other"})
    assert incident.event_type == "Marine Incident"


def test_parses_state_from_messy_location_strings():
    normalizer = NoaaIncidentNewsNormalizer()
    assert normalizer.normalize({**RAW, "location": "Gulf, LA"}).location.state == "LA"
    assert (
        normalizer.normalize({**RAW, "location": "WG3M+9M Stockton, CA, USA"}).location.state
        == "CA"
    )
    assert normalizer.normalize({**RAW, "location": "Somewhere, ZZ"}).location.state is None
