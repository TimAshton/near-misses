import pytest

from near_misses.ingestion.nws_severe_weather.normalizer import NwsSevereWeatherNormalizer
from near_misses.schemas.incident import Category, Severity

RAW = {
    "geometry": {"type": "Point", "coordinates": [-97.5, 35.2]},
    "properties": {
        "id": "urn:oid:2.49.0.1.840.0.severe-weather-test",
        "event": "Tornado Emergency",
        "areaDesc": "Cleveland County, OK",
        "severity": "Extreme",
        "onset": "2024-03-14T18:42:00-05:00",
        "headline": "Tornado Emergency issued",
        "description": "A confirmed large and extremely dangerous tornado.",
        "instruction": "Take cover now.",
        "web": "https://www.weather.gov",
    },
}


def test_normalizes_core_fields():
    incident = NwsSevereWeatherNormalizer().normalize(RAW)

    assert incident.source == "nws_severe_weather"
    assert incident.category == Category.severe_weather
    assert incident.event_type == "Tornado Emergency"
    assert incident.severity == Severity.critical
    assert incident.location.lng == -97.5
    assert incident.location.lat == 35.2
    assert "Cleveland County" in incident.title
    assert "extremely dangerous tornado" in incident.description
    assert "Take cover now" in incident.description


def test_unknown_severity_defaults_to_low():
    props = {**RAW["properties"], "severity": "Unknown"}
    incident = NwsSevereWeatherNormalizer().normalize({**RAW, "properties": props})
    assert incident.severity == Severity.low


def test_raises_when_no_location_is_resolvable():
    raw = {**RAW, "geometry": None}
    with pytest.raises(ValueError):
        NwsSevereWeatherNormalizer().normalize(raw)


def test_resolves_via_zone_centroid_when_geometry_missing():
    raw = {**RAW, "geometry": None, "_resolved_centroid": [-97.5, 35.2]}
    incident = NwsSevereWeatherNormalizer().normalize(raw)
    assert incident.location.lng == -97.5
    assert incident.location.lat == 35.2
