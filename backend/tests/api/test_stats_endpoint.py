from datetime import UTC, datetime, timedelta

from near_misses.models.incident import Incident


def _seed(db_session, **overrides):
    defaults = dict(
        source="ntsb",
        source_id="A1",
        category="aviation",
        event_type="Accident",
        severity="high",
        title="x",
        description="",
        occurred_at=datetime.now(UTC),
        lat=30.0,
        lng=-97.0,
        state="TX",
        raw={},
    )
    defaults.update(overrides)
    db_session.add(Incident(**defaults))
    db_session.commit()


def test_stats_aggregates_by_category_severity_state(client, db_session):
    _seed(db_session, source_id="A1", severity="high", state="TX")
    _seed(db_session, source_id="A2", severity="critical", state="TX")
    _seed(db_session, source_id="A3", severity="low", state="CA")

    response = client.get("/api/stats", params={"window": "all"})
    body = response.json()

    assert body["total_incidents"] == 3
    assert body["by_category"]["aviation"] == 3
    assert body["by_severity"] == {"high": 1, "critical": 1, "low": 1}
    assert {s["state"]: s["count"] for s in body["top_states"]} == {"TX": 2, "CA": 1}
    assert body["last_updated"] is not None


def test_stats_window_excludes_old_incidents(client, db_session):
    _seed(db_session, source_id="OLD", occurred_at=datetime.now(UTC) - timedelta(days=60))
    _seed(db_session, source_id="RECENT", occurred_at=datetime.now(UTC))

    response = client.get("/api/stats", params={"window": "24h"})
    body = response.json()
    assert body["total_incidents"] == 1
