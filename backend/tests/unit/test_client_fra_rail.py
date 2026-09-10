from unittest.mock import MagicMock, patch

from near_misses.ingestion.fra_rail.client import FraRailClient


def test_fetch_requests_recent_dated_rows_sorted_descending():
    mock_response = MagicMock()
    mock_response.json.return_value = [{"incidentkey": "a"}, {"incidentkey": "b"}]
    mock_response.raise_for_status.return_value = None

    with patch(
        "near_misses.ingestion.fra_rail.client.httpx.get", return_value=mock_response
    ) as mock_get:
        result = FraRailClient().fetch()

    assert result == [{"incidentkey": "a"}, {"incidentkey": "b"}]
    _, kwargs = mock_get.call_args
    assert kwargs["params"]["$where"] == "date IS NOT NULL"
    assert kwargs["params"]["$order"] == "date DESC"
