from unittest.mock import MagicMock, patch

from near_misses.ingestion.usgs.client import UsgsClient

FEED_RESPONSE = {
    "features": [
        {"id": "high-mag", "properties": {"mag": 4.8}},
        {"id": "just-below-threshold", "properties": {"mag": 2.45}},  # feed boundary is fuzzy
        {"id": "at-threshold", "properties": {"mag": 2.5}},
        {"id": "unknown-mag", "properties": {"mag": None}},
        {"id": "low-mag", "properties": {"mag": 1.2}},
    ]
}


def test_filters_out_events_below_the_medium_severity_threshold():
    mock_response = MagicMock()
    mock_response.json.return_value = FEED_RESPONSE
    mock_response.raise_for_status.return_value = None

    with patch("near_misses.ingestion.usgs.client.httpx.get", return_value=mock_response):
        features = UsgsClient().fetch()

    ids = {f["id"] for f in features}
    assert ids == {"high-mag", "at-threshold"}
