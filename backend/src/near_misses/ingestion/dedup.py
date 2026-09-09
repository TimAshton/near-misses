from sqlalchemy import select
from sqlalchemy.orm import Session

from near_misses.models.incident import Incident
from near_misses.schemas.incident import NormalizedIncident


def is_duplicate(db: Session, incident: NormalizedIncident) -> bool:
    if incident.source_id:
        existing = db.execute(
            select(Incident.id).where(
                Incident.source == incident.source,
                Incident.source_id == incident.source_id,
            )
        ).first()
        if existing:
            return True

    existing = db.execute(
        select(Incident.id).where(
            Incident.source == incident.source,
            Incident.occurred_at == incident.occurred_at,
            Incident.lat == incident.location.lat,
            Incident.lng == incident.location.lng,
        )
    ).first()
    return existing is not None
