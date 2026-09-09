from datetime import UTC, datetime

from near_misses.models.incident import Incident


def _seed(db_session, **overrides):
    defaults = dict(
        source="ntsb",
        source_id="A1",
        category="aviation",
        event_type="Accident",
        severity="high",
        title="Test incident",
        description="desc",
        occurred_at=datetime(2024, 5, 1, tzinfo=UTC),
        lat=30.0,
        lng=-97.0,
        city="Austin",
        state="TX",
        raw={"foo": "bar"},
    )
    defaults.update(overrides)
    incident = Incident(**defaults)
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident


def test_list_incidents_returns_seeded_row(client, db_session):
    _seed(db_session)
    response = client.get("/api/incidents")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == "Test incident"
    assert body["items"][0]["location"]["state"] == "TX"


def test_list_incidents_filters_by_state(client, db_session):
    _seed(db_session, source_id="A1", state="TX")
    _seed(db_session, source_id="A2", state="CA", occurred_at=datetime(2024, 5, 2, tzinfo=UTC))

    response = client.get("/api/incidents", params={"state": "ca"})
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["location"]["state"] == "CA"


def test_list_incidents_sorts_by_column(client, db_session):
    _seed(db_session, source_id="A1", title="First", occurred_at=datetime(2024, 5, 1, tzinfo=UTC))
    _seed(db_session, source_id="A2", title="Second", occurred_at=datetime(2024, 5, 2, tzinfo=UTC))

    response = client.get("/api/incidents", params={"sort": "occurred_at", "order": "asc"})
    body = response.json()
    assert [item["title"] for item in body["items"]] == ["First", "Second"]


def test_get_incident_by_id(client, db_session):
    incident = _seed(db_session)
    response = client.get(f"/api/incidents/{incident.id}")
    assert response.status_code == 200
    assert response.json()["raw"] == {"foo": "bar"}


def test_get_incident_404(client):
    response = client.get("/api/incidents/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_export_csv(client, db_session):
    _seed(db_session)
    response = client.get("/api/incidents/export.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Test incident" in response.text
