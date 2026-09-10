import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Category(StrEnum):
    aviation = "aviation"
    rail = "rail"
    seismic = "seismic"
    tsunami = "tsunami"
    hurricane = "hurricane"


class Severity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Location(BaseModel):
    lat: float
    lng: float
    city: str | None = None
    state: str | None = None
    display_name: str | None = None


class IncidentBase(BaseModel):
    source: str
    category: Category
    event_type: str
    severity: Severity
    title: str
    description: str
    occurred_at: datetime
    source_url: str | None = None


class NormalizedIncident(IncidentBase):
    """What a source normalizer produces before persistence."""

    source_id: str | None = None
    location: Location
    raw: dict = {}


class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ingested_at: datetime
    location: Location
    raw: dict

    @classmethod
    def from_orm_model(cls, incident) -> "IncidentOut":
        return cls(
            id=incident.id,
            source=incident.source,
            category=incident.category,
            event_type=incident.event_type,
            severity=incident.severity,
            title=incident.title,
            description=incident.description,
            occurred_at=incident.occurred_at,
            ingested_at=incident.ingested_at,
            source_url=incident.source_url,
            location=Location(
                lat=incident.lat,
                lng=incident.lng,
                city=incident.city,
                state=incident.state,
                display_name=incident.display_name,
            ),
            raw=incident.raw,
        )


class IncidentSummaryOut(BaseModel):
    """Lighter payload for list views / WS broadcast."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: Category
    event_type: str
    severity: Severity
    title: str
    occurred_at: datetime
    location: Location

    @classmethod
    def from_orm_model(cls, incident) -> "IncidentSummaryOut":
        return cls(
            id=incident.id,
            category=incident.category,
            event_type=incident.event_type,
            severity=incident.severity,
            title=incident.title,
            occurred_at=incident.occurred_at,
            location=Location(
                lat=incident.lat,
                lng=incident.lng,
                city=incident.city,
                state=incident.state,
                display_name=incident.display_name,
            ),
        )


class IncidentListResponse(BaseModel):
    """Envelope for GET /api/incidents — matches frontend's IncidentListResponse."""

    items: list[IncidentSummaryOut]
    total: int
    limit: int
    offset: int


class PollResult(BaseModel):
    fetched: int
    new_incidents: int
    duplicates: int
    rejected_non_us: int
    below_min_severity: int
    triggered_at: datetime


class TimelinePoint(BaseModel):
    bucket: str
    count: int


class StateCount(BaseModel):
    state: str
    count: int


class Stats(BaseModel):
    """Matches frontend's Stats type exactly (see frontend/src/lib/types.ts)."""

    total_incidents: int
    last_updated: datetime | None
    by_category: dict[str, int]
    by_severity: dict[str, int]
    top_states: list[StateCount]
    timeline: list[TimelinePoint]
    window: str
