from unittest.mock import patch

FIXTURE_RECORDS = [
    {
        "NtsbNumber": "CEN24LA123",
        "EventType": "Accident",
        "EventDate": "2024-03-14T18:42:00Z",
        "Mode": "Aviation",
        "City": "Georgetown",
        "State": "TX",
        "Latitude": 30.6333,
        "Longitude": -97.6772,
        "AirportId": "KGTU",
        "AirportName": "Georgetown Municipal Airport",
        "AircraftMake": "Cessna",
        "AircraftModel": "172S",
        "HighestInjuryLevel": "Minor",
        "NarrativeBrief": "Test narrative.",
        "ReportUrl": "https://www.ntsb.gov/investigations/AccidentReports/Pages/CEN24LA123.aspx",
    },
    {
        # Non-US coordinate — should be rejected, not persisted.
        "NtsbNumber": "FOREIGN-1",
        "EventType": "Accident",
        "EventDate": "2024-03-15T10:00:00Z",
        "Mode": "Aviation",
        "City": "London",
        "State": None,
        "Latitude": 51.5074,
        "Longitude": -0.1278,
        "HighestInjuryLevel": "None",
        "NarrativeBrief": "",
        "ReportUrl": None,
    },
]


def test_trigger_poll_persists_new_incidents_and_skips_non_us(client, db_session):
    with (
        patch("near_misses.ingestion.ntsb.client.NtsbClient.fetch", return_value=FIXTURE_RECORDS),
        patch("near_misses.ingestion.usgs.client.UsgsClient.fetch", return_value=[]),
        patch("near_misses.ingestion.nws_tsunami.client.NwsTsunamiClient.fetch", return_value=[]),
        patch(
            "near_misses.ingestion.pipeline.archive_raw_response",
            return_value="raw/ntsb/x.json",
        ),
    ):
        response = client.post("/api/poll/trigger")

    assert response.status_code == 200
    body = response.json()
    assert body["fetched"] == 2
    assert body["new_incidents"] == 1
    assert body["rejected_non_us"] == 1
    assert body["duplicates"] == 0

    incidents = client.get("/api/incidents").json()
    assert incidents["total"] == 1
    assert incidents["items"][0]["location"]["state"] == "TX"


def test_trigger_poll_dedupes_on_second_run(client, db_session):
    with (
        patch(
            "near_misses.ingestion.ntsb.client.NtsbClient.fetch",
            return_value=FIXTURE_RECORDS[:1],
        ),
        patch("near_misses.ingestion.usgs.client.UsgsClient.fetch", return_value=[]),
        patch("near_misses.ingestion.nws_tsunami.client.NwsTsunamiClient.fetch", return_value=[]),
        patch(
            "near_misses.ingestion.pipeline.archive_raw_response",
            return_value="raw/ntsb/x.json",
        ),
    ):
        client.post("/api/poll/trigger")
        second = client.post("/api/poll/trigger")

    assert second.json()["new_incidents"] == 0
    assert second.json()["duplicates"] == 1


USGS_FIXTURE_FEATURES = [
    {
        "type": "Feature",
        "id": "ci12345",
        "properties": {
            "mag": 4.8,
            "place": "10km NW of Ridgecrest, CA",
            "title": "M 4.8 - 10km NW of Ridgecrest, CA",
            "time": 1710439320000,
            "type": "earthquake",
            "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ci12345",
        },
        "geometry": {"type": "Point", "coordinates": [-117.6709, 35.7695, 8.0]},
    },
    {
        # Non-US coordinate — should be rejected, not persisted.
        "type": "Feature",
        "id": "us9999",
        "properties": {
            "mag": 5.5,
            "place": "100km SE of Tokyo, Japan",
            "title": "M 5.5 - 100km SE of Tokyo, Japan",
            "time": 1710439320000,
            "type": "earthquake",
            "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us9999",
        },
        "geometry": {"type": "Point", "coordinates": [140.0, 34.0, 35.0]},
    },
]


NWS_TSUNAMI_FIXTURE_FEATURES = [
    {
        # No geometry, but resolvable via zone lookup client-side; the poll
        # test patches the client's fetch() directly, so simulate the
        # enrichment it would have already done.
        "geometry": None,
        "_resolved_centroid": [-151.7, 57.8],
        "properties": {
            "id": "urn:oid:2.49.0.1.840.0.tsunami-warning-poll-test",
            "areaDesc": "Coastal Kodiak Island Borough",
            "geocode": {"UGC": ["AKZ185"]},
            "sent": "2024-03-14T18:42:00-08:00",
            "effective": "2024-03-14T18:42:00-08:00",
            "onset": "2024-03-14T18:42:00-08:00",
            "severity": "Extreme",
            "event": "Tsunami Warning",
            "headline": "Tsunami Warning issued",
            "description": "Move to high ground immediately.",
            "web": "https://tsunami.gov",
        },
    },
]


def test_trigger_poll_runs_all_sources_together(client, db_session):
    with (
        patch("near_misses.ingestion.ntsb.client.NtsbClient.fetch", return_value=FIXTURE_RECORDS),
        patch(
            "near_misses.ingestion.usgs.client.UsgsClient.fetch",
            return_value=USGS_FIXTURE_FEATURES,
        ),
        patch(
            "near_misses.ingestion.nws_tsunami.client.NwsTsunamiClient.fetch",
            return_value=NWS_TSUNAMI_FIXTURE_FEATURES,
        ),
        patch("near_misses.ingestion.pipeline.archive_raw_response", return_value="raw/x.json"),
    ):
        response = client.post("/api/poll/trigger")

    body = response.json()
    assert body["fetched"] == 5
    assert body["new_incidents"] == 3
    assert body["rejected_non_us"] == 2

    incidents = client.get("/api/incidents").json()
    categories = {i["category"] for i in incidents["items"]}
    assert categories == {"aviation", "seismic", "tsunami"}
