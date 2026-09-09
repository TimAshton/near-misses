from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from near_misses.api.deps import get_db
from near_misses.models.incident import Incident
from near_misses.schemas.incident import StateCount, Stats, TimelinePoint

router = APIRouter(prefix="/api/stats", tags=["stats"])

_WINDOWS = {
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
    "all": None,
}


@router.get("", response_model=Stats)
def get_stats(window: str = Query(default="7d"), db: Session = Depends(get_db)):
    delta = _WINDOWS.get(window, _WINDOWS["7d"])
    base = select(Incident)
    if delta is not None:
        base = base.where(Incident.occurred_at >= datetime.now(UTC) - delta)

    incidents = db.execute(base).scalars().all()

    by_category: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    by_state: dict[str, int] = {}
    timeline_buckets: dict[str, int] = {}

    for i in incidents:
        by_category[i.category] = by_category.get(i.category, 0) + 1
        by_severity[i.severity] = by_severity.get(i.severity, 0) + 1
        if i.state:
            by_state[i.state] = by_state.get(i.state, 0) + 1
        day_key = i.occurred_at.strftime("%Y-%m-%d")
        timeline_buckets[day_key] = timeline_buckets.get(day_key, 0) + 1

    timeline = [TimelinePoint(bucket=d, count=c) for d, c in sorted(timeline_buckets.items())]
    top_states = [
        StateCount(state=s, count=c)
        for s, c in sorted(by_state.items(), key=lambda kv: kv[1], reverse=True)[:10]
    ]
    last_updated = db.execute(select(func.max(Incident.ingested_at))).scalar()

    return Stats(
        window=window,
        total_incidents=len(incidents),
        by_category=by_category,
        by_severity=by_severity,
        top_states=top_states,
        timeline=timeline,
        last_updated=last_updated,
    )
