from unittest.mock import MagicMock, patch

from near_misses.ingestion.usgs.client import UsgsClient

FEED_RESPONSE = {
    "features": [
        {"id": "critical-mag", "properties": {"mag": 6.1}},
        {"id": "just-below-threshold", "properties": {"mag": 4.45}},
        {"id": "at-threshold", "properties": {"mag": 4.5}},
        {"id": "unknown-mag", "properties": {"mag": None}},
        {"id": "medium-mag", "properties": {"mag": 3.0}},
        {"id": "low-mag", "properties": {"mag": 1.2}},
    ]
}


def test_filters_out_events_below_the_high_severity_threshold():
    mock_response = MagicMock()
    mock_response.json.return_value = FEED_RESPONSE
    mock_response.raise_for_status.return_value = None

    with patch("near_misses.ingestion.usgs.client.httpx.get", return_value=mock_response):
        features = UsgsClient().fetch()

    ids = {f["id"] for f in features}
    assert ids == {"critical-mag", "at-threshold"}
