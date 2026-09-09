import csv
import io
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from near_misses.api.deps import get_db
from near_misses.models.incident import Incident
from near_misses.schemas.incident import (
    Category,
    IncidentListResponse,
    IncidentOut,
    IncidentSummaryOut,
    Severity,
)

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

# Allow-list of columns the frontend may sort by — never interpolate the raw
# `sort` query param into a column lookup.
_SORTABLE_COLUMNS = {
    "occurred_at": Incident.occurred_at,
    "category": Incident.category,
    "severity": Incident.severity,
    "title": Incident.title,
    "location.state": Incident.state,
    "state": Incident.state,
}


def _filtered_query(
    category: Category | None,
    severity: Severity | None,
    state: str | None,
    date_from: datetime | None,
    date_to: datetime | None,
):
    stmt = select(Incident)
    if category:
        stmt = stmt.where(Incident.category == category)
    if severity:
        stmt = stmt.where(Incident.severity == severity)
    if state:
        stmt = stmt.where(Incident.state == state.upper())
    if date_from:
        stmt = stmt.where(Incident.occurred_at >= date_from)
    if date_to:
        stmt = stmt.where(Incident.occurred_at <= date_to)
    return stmt


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    category: Category | None = None,
    severity: Severity | None = None,
    state: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort: str = Query(default="occurred_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    filtered = _filtered_query(category, severity, state, date_from, date_to)

    total = db.execute(select(func.count()).select_from(filtered.subquery())).scalar_one()

    sort_column = _SORTABLE_COLUMNS.get(sort, Incident.occurred_at)
    sort_column = sort_column.asc() if order == "asc" else sort_column.desc()
    stmt = filtered.order_by(sort_column).limit(limit).offset(offset)
    incidents = db.execute(stmt).scalars().all()

    return IncidentListResponse(
        items=[IncidentSummaryOut.from_orm_model(i) for i in incidents],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/export.csv")
def export_incidents_csv(
    category: Category | None = None,
    severity: Severity | None = None,
    state: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    stmt = _filtered_query(category, severity, state, date_from, date_to).order_by(
        Incident.occurred_at.desc()
    )
    incidents = db.execute(stmt).scalars().all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["id", "source", "category", "event_type", "severity", "title", "occurred_at",
         "city", "state", "lat", "lng", "source_url"]
    )
    for i in incidents:
        writer.writerow(
            [i.id, i.source, i.category, i.event_type, i.severity, i.title, i.occurred_at,
             i.city, i.state, i.lat, i.lng, i.source_url]
        )
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=incidents.csv"},
    )


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: uuid.UUID, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentOut.from_orm_model(incident)
