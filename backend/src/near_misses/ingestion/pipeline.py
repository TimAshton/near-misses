import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from near_misses.ingestion.base import Normalizer, SourceClient
from near_misses.ingestion.dedup import is_duplicate
from near_misses.ingestion.us_bounds import is_us_location
from near_misses.models.incident import Incident
from near_misses.schemas.incident import IncidentSummaryOut, PollResult
from near_misses.storage.s3_archive import archive_raw_response
from near_misses.ws.manager import manager

logger = logging.getLogger(__name__)


async def run_ingestion(
    db: Session, source_client: SourceClient, normalizer: Normalizer
) -> PollResult:
    """The one ingestion pipeline every source (and every future phase) shares:

    fetch -> validate (schema + US-bounds) -> normalize -> dedup -> persist
        -> archive raw response to S3 -> broadcast new incidents over WebSocket.

    Called identically by the scheduler (every N minutes) and by
    POST /api/poll/trigger, so scheduled and manual runs can't drift.
    """
    raw_records = source_client.fetch()
    new_count = 0
    duplicate_count = 0
    rejected_count = 0

    for raw in raw_records:
        try:
            normalized = normalizer.normalize(raw)
        except Exception:
            logger.exception("Failed to normalize record from %s", source_client.source_name)
            continue

        if not is_us_location(normalized.location.lat, normalized.location.lng):
            rejected_count += 1
            continue

        if is_duplicate(db, normalized):
            duplicate_count += 1
            continue

        incident = Incident(
            source=normalized.source,
            source_id=normalized.source_id,
            category=normalized.category,
            event_type=normalized.event_type,
            severity=normalized.severity,
            title=normalized.title,
            description=normalized.description,
            occurred_at=normalized.occurred_at,
            lat=normalized.location.lat,
            lng=normalized.location.lng,
            city=normalized.location.city,
            state=normalized.location.state,
            display_name=normalized.location.display_name,
            source_url=normalized.source_url,
            raw=normalized.raw,
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        new_count += 1

        archive_raw_response(source_client.source_name, raw)
        await manager.broadcast(
            {
                "type": "incident.created",
                "incident": IncidentSummaryOut.from_orm_model(incident).model_dump(mode="json"),
            }
        )

    return PollResult(
        fetched=len(raw_records),
        new_incidents=new_count,
        duplicates=duplicate_count,
        rejected_non_us=rejected_count,
        triggered_at=datetime.now(UTC),
    )
