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
        patch("near_misses.ingestion.fra_rail.client.FraRailClient.fetch", return_value=[]),
        patch(
            "near_misses.ingestion.nhc_hurricane.client.NhcHurricaneClient.fetch", return_value=[]
        ),
        patch(
            "near_misses.ingestion.nifc_wildfire.client.NifcWildfireClient.fetch", return_value=[]
        ),
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
        patch("near_misses.ingestion.fra_rail.client.FraRailClient.fetch", return_value=[]),
        patch(
            "near_misses.ingestion.nhc_hurricane.client.NhcHurricaneClient.fetch", return_value=[]
        ),
        patch(
            "near_misses.ingestion.nifc_wildfire.client.NifcWildfireClient.fetch", return_value=[]
        ),
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


FRA_RAIL_FIXTURE_RECORDS = [
    {
        # High damage, no casualties -> medium severity -> persisted.
        "date": "2024-03-14T00:00:00.000",
        "time": "10:56 PM",
        "accidenttype": "Derailment",
        "stateabbr": "PA",
        "station": "CONWAY",
        "totalpersonskilled": "0",
        "totalpersonsinjured": "0",
        "totaldamagecost": "450000",
        "latitude": "40.672362",
        "longitude": "-80.251826",
        "incidentkey": "NS171002202606",
        "narrative": "Test narrative.",
        "url": {"url": "https://safetydata.fra.dot.gov/x"},
    },
    {
        # Low damage, no casualties -> low severity -> filtered out by policy.
        "date": "2024-03-15T00:00:00.000",
        "time": "9:00 AM",
        "accidenttype": "Obstruction",
        "stateabbr": "OH",
        "station": "TOLEDO",
        "totalpersonskilled": "0",
        "totalpersonsinjured": "0",
        "totaldamagecost": "5000",
        "latitude": "41.6528",
        "longitude": "-83.5379",
        "incidentkey": "AA260630002202606",
        "narrative": "Test narrative.",
        "url": {"url": "https://safetydata.fra.dot.gov/y"},
    },
]


NHC_HURRICANE_FIXTURE_STORMS = [
    {
        # Within US bounds -> persisted.
        "id": "al092026",
        "name": "Milton",
        "classification": "HU",
        "intensity": "115",
        "pressure": "935",
        "latitudeNumeric": 27.5,
        "longitudeNumeric": -83.2,
        "lastUpdate": "2024-03-14T18:42:00.000Z",
        "publicAdvisory": {"url": "https://www.nhc.noaa.gov/text/MIATCPAT1.shtml"},
    },
    {
        # Non-US coordinate — should be rejected, not persisted.
        "id": "ep142026",
        "name": "Norbert",
        "classification": "TS",
        "intensity": "35",
        "pressure": "1003",
        "latitudeNumeric": 16.5,
        "longitudeNumeric": -119.3,
        "lastUpdate": "2024-03-14T18:42:00.000Z",
        "publicAdvisory": {"url": "https://www.nhc.noaa.gov/text/MIATCPEP4.shtml"},
    },
]


NIFC_WILDFIRE_FIXTURE_FEATURES = [
    {
        # Within US bounds -> persisted.
        "attributes": {
            "IncidentName": "PALISADES",
            "IncidentSize": 23713.0,
            "PercentContained": 45.0,
            "FireDiscoveryDateTime": 1710439320000,
            "POOState": "US-CA",
            "POOCounty": "Los Angeles",
            "FireCause": "Undetermined",
            "UniqueFireIdentifier": "2026-CALAC-325444",
        },
        "geometry": {"x": -118.07282, "y": 34.03108},
    },
    {
        # Non-US coordinate — should be rejected, not persisted.
        "attributes": {
            "IncidentName": "FOREIGN",
            "IncidentSize": 500.0,
            "PercentContained": 10.0,
            "FireDiscoveryDateTime": 1710439320000,
            "POOState": "US-XX",
            "POOCounty": "Nowhere",
            "FireCause": "Undetermined",
            "UniqueFireIdentifier": "2026-XXNOW-000001",
        },
        "geometry": {"x": 140.0, "y": 34.0},
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
        patch(
            "near_misses.ingestion.fra_rail.client.FraRailClient.fetch",
            return_value=FRA_RAIL_FIXTURE_RECORDS,
        ),
        patch(
            "near_misses.ingestion.nhc_hurricane.client.NhcHurricaneClient.fetch",
            return_value=NHC_HURRICANE_FIXTURE_STORMS,
        ),
        patch(
            "near_misses.ingestion.nifc_wildfire.client.NifcWildfireClient.fetch",
            return_value=NIFC_WILDFIRE_FIXTURE_FEATURES,
        ),
        patch("near_misses.ingestion.pipeline.archive_raw_response", return_value="raw/x.json"),
    ):
        response = client.post("/api/poll/trigger")

    body = response.json()
    assert body["fetched"] == 11
    assert body["new_incidents"] == 6
    assert body["rejected_non_us"] == 4
    assert body["below_min_severity"] == 1

    incidents = client.get("/api/incidents").json()
    categories = {i["category"] for i in incidents["items"]}
    assert categories == {"aviation", "seismic", "tsunami", "rail", "hurricane", "wildfire"}
    rail_incidents = [i for i in incidents["items"] if i["category"] == "rail"]
    assert len(rail_incidents) == 1
    assert rail_incidents[0]["severity"] == "medium"
