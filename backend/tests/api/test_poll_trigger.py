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
        patch("near_misses.api.routes.poll.NtsbClient.fetch", return_value=FIXTURE_RECORDS),
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
        patch("near_misses.api.routes.poll.NtsbClient.fetch", return_value=FIXTURE_RECORDS[:1]),
        patch(
            "near_misses.ingestion.pipeline.archive_raw_response",
            return_value="raw/ntsb/x.json",
        ),
    ):
        client.post("/api/poll/trigger")
        second = client.post("/api/poll/trigger")

    assert second.json()["new_incidents"] == 0
    assert second.json()["duplicates"] == 1
