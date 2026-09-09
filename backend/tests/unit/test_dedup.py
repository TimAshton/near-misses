from datetime import UTC, datetime

from near_misses.ingestion.dedup import is_duplicate
from near_misses.models.incident import Incident
from near_misses.schemas.incident import Category, Location, NormalizedIncident, Severity

OCCURRED_AT = datetime(2024, 3, 14, 18, 42, tzinfo=UTC)


def _normalized(**overrides) -> NormalizedIncident:
    defaults = dict(
        source="ntsb",
        source_id="CEN24LA123",
        category=Category.aviation,
        event_type="Accident",
        severity=Severity.medium,
        title="Cessna 172S",
        description="",
        occurred_at=OCCURRED_AT,
        source_url=None,
        location=Location(lat=30.6333, lng=-97.6772, city="Georgetown", state="TX"),
        raw={},
    )
    defaults.update(overrides)
    return NormalizedIncident(**defaults)


def test_same_source_id_is_duplicate(db_session):
    db_session.add(
        Incident(
            source="ntsb",
            source_id="CEN24LA123",
            category="aviation",
            event_type="Accident",
            severity="medium",
            title="x",
            description="",
            occurred_at=OCCURRED_AT,
            lat=30.6333,
            lng=-97.6772,
            raw={},
        )
    )
    db_session.commit()

    assert is_duplicate(db_session, _normalized()) is True


def test_different_source_id_same_time_and_place_is_duplicate(db_session):
    db_session.add(
        Incident(
            source="ntsb",
            source_id="OTHER-ID",
            category="aviation",
            event_type="Accident",
            severity="medium",
            title="x",
            description="",
            occurred_at=OCCURRED_AT,
            lat=30.6333,
            lng=-97.6772,
            raw={},
        )
    )
    db_session.commit()

    assert is_duplicate(db_session, _normalized(source_id="CEN24LA123-reprocessed")) is True


def test_different_time_and_place_is_not_duplicate(db_session):
    assert is_duplicate(db_session, _normalized()) is False
