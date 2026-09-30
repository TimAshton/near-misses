import json
from pathlib import Path
from unittest.mock import patch

import pytest

from near_misses.ingestion.ntsb.normalizer import NtsbNormalizer
from near_misses.schemas.incident import Category, Severity

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "ntsb_sample.json").read_text()
)

# The live endpoint has no coordinates of its own (see ingestion/ntsb/README.md) —
# normalize() geocodes City+State instead. Mocked here so unit tests never hit
# Nominatim or the geocode_cache table.
_GEOCODES = {
    ("Georgetown", "Texas"): (30.6333, -97.6772),
    ("Ocala", "Florida"): (29.1727, -82.2243),
}


def _mock_geocode(city, state):
    return _GEOCODES.get((city, state))


@patch("near_misses.ingestion.ntsb.normalizer.geocode_city_state", side_effect=_mock_geocode)
def test_normalizes_fatal_record_to_critical_severity(_mock):
    raw = next(r for r in FIXTURE if r["NtsbNo"] == "ERA24FA089")
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


@patch("near_misses.ingestion.ntsb.normalizer.geocode_city_state", side_effect=_mock_geocode)
def test_normalizes_minor_record_to_medium_severity(_mock):
    raw = next(r for r in FIXTURE if r["NtsbNo"] == "CEN24LA123")
    incident = NtsbNormalizer().normalize(raw)

    assert incident.severity == Severity.medium
    assert incident.location.display_name == "Georgetown, TX"


@patch("near_misses.ingestion.ntsb.normalizer.geocode_city_state", side_effect=_mock_geocode)
def test_unknown_injury_level_defaults_to_low(_mock):
    raw = {**FIXTURE[0], "HighestInjuryLevel": "SomethingUnexpected"}
    incident = NtsbNormalizer().normalize(raw)
    assert incident.severity == Severity.low


@patch("near_misses.ingestion.ntsb.normalizer.geocode_city_state")
def test_foreign_state_skips_geocoding_and_gets_non_us_sentinel(mock_geocode):
    # NTSB tracks some foreign occurrences too (state is a non-US placeholder
    # like "Other Foreign", or missing entirely) — normalize() should still
    # succeed, routing it to the pipeline's normal non-US rejection instead
    # of raising (which would log a "failure" for expected, recurring input).
    raw = {**FIXTURE[0], "City": "Farnham", "State": "Other Foreign"}
    incident = NtsbNormalizer().normalize(raw)

    assert incident.location.lat == 0.0
    assert incident.location.lng == 0.0
    mock_geocode.assert_not_called()


@patch("near_misses.ingestion.ntsb.normalizer.geocode_city_state", return_value=None)
def test_missing_city_raises(_mock):
    raw = {**FIXTURE[0], "City": None, "State": None}
    with pytest.raises(ValueError):
        NtsbNormalizer().normalize(raw)
