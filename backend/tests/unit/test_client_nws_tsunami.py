from unittest.mock import MagicMock, patch

from near_misses.ingestion.nws_tsunami.client import NwsTsunamiClient

ALERTS_RESPONSE = {
    "features": [
        {
            "geometry": None,
            "properties": {"id": "a1", "geocode": {"UGC": ["AKZ185"]}},
        },
        {
            "geometry": None,
            "properties": {"id": "a2", "geocode": {"UGC": ["AKZ185"]}},  # same zone as a1
        },
        {
            "geometry": {"type": "Point", "coordinates": [-157.86, 21.31]},
            "properties": {"id": "a3", "geocode": {"UGC": ["HIZ001"]}},
        },
    ]
}

ZONE_RESPONSE = {
    "geometry": {
        "type": "Polygon",
        "coordinates": [[[-152.0, 57.0], [-151.0, 57.0], [-151.5, 58.0], [-152.0, 57.0]]],
    }
}


def _mock_response(payload):
    mock = MagicMock()
    mock.json.return_value = payload
    mock.raise_for_status.return_value = None
    return mock


def test_enriches_geometry_less_alerts_with_zone_centroid_and_caches_per_zone():
    with patch("near_misses.ingestion.nws_tsunami.client.httpx.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(ALERTS_RESPONSE),
            _mock_response(ZONE_RESPONSE),  # only one zone lookup for AKZ185, shared by a1/a2
        ]
        features = NwsTsunamiClient().fetch()

    assert mock_get.call_count == 2  # alerts + one zone lookup (not two, despite two alerts)
    assert features[0]["_resolved_centroid"] == features[1]["_resolved_centroid"]
    assert "_resolved_centroid" not in features[2]  # already had geometry
