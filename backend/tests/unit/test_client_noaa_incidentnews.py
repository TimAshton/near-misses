from pathlib import Path
from unittest.mock import MagicMock, patch

from near_misses.ingestion.noaa_incidentnews.client import NoaaIncidentNewsClient

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "noaa_incidentnews_sample.csv"


def _fetch() -> list[dict]:
    mock_response = MagicMock()
    mock_response.text = _FIXTURE.read_text()
    mock_response.raise_for_status.return_value = None
    with patch(
        "near_misses.ingestion.noaa_incidentnews.client.httpx.get", return_value=mock_response
    ):
        return NoaaIncidentNewsClient().fetch()


def test_keeps_untagged_and_vessel_tagged_rows():
    ids = {r["id"] for r in _fetch()}
    assert ids == {"1", "3", "5"}


def test_drops_rows_whose_only_tags_are_land_infrastructure_causes():
    ids = {r["id"] for r in _fetch()}
    assert "2" not in ids  # Pipeline only
    assert "4" not in ids  # Railcar|Wellhead only


def test_keeps_row_with_a_mix_of_land_and_vessel_tags():
    ids = {r["id"] for r in _fetch()}
    assert "5" in ids  # Pipeline|Grounding — at least one vessel-cause tag
