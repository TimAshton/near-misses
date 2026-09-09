import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from near_misses.db import Base

# JSONB on Postgres (prod/dev-via-docker), plain JSON on SQLite (fast unit tests).
JSONType = JSON().with_variant(JSONB, "postgresql")


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        UniqueConstraint(
            "source", "occurred_at", "lat", "lng", name="uq_incident_source_time_location"
        ),
        Index("ix_incidents_occurred_at", "occurred_at"),
        Index("ix_incidents_category", "category"),
        Index("ix_incidents_state", "state"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)

    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    raw: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
