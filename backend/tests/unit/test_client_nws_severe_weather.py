from unittest.mock import MagicMock, patch

from near_misses.ingestion.nws_severe_weather.client import NwsSevereWeatherClient

ALERTS_RESPONSE = {
    "features": [
        {
            "geometry": {"type": "Point", "coordinates": [-97.5, 35.2]},
            "properties": {"id": "a1", "event": "Tornado Emergency", "geocode": {"UGC": []}},
        },
        {
            # Should be dropped — already tracked by nws_tsunami.
            "geometry": {"type": "Point", "coordinates": [-157.86, 21.31]},
            "properties": {"id": "a2", "event": "Tsunami Warning", "geocode": {"UGC": []}},
        },
    ]
}


def _mock_response(payload):
    mock = MagicMock()
    mock.json.return_value = payload
    mock.raise_for_status.return_value = None
    return mock


def test_requests_extreme_severity_only():
    with patch("near_misses.ingestion.nws_alerts.httpx.get") as mock_get:
        mock_get.return_value = _mock_response(ALERTS_RESPONSE)
        NwsSevereWeatherClient().fetch()

    assert mock_get.call_args.kwargs["params"] == {"severity": "Extreme"}


def test_excludes_events_already_tracked_by_nws_tsunami():
    with patch("near_misses.ingestion.nws_alerts.httpx.get") as mock_get:
        mock_get.return_value = _mock_response(ALERTS_RESPONSE)
        features = NwsSevereWeatherClient().fetch()

    ids = {f["properties"]["id"] for f in features}
    assert ids == {"a1"}
