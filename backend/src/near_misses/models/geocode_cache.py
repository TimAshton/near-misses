from sqlalchemy import Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from near_misses.db import Base


class GeocodeCache(Base):
    """Caches city+state -> lat/lng lookups so sources with no coordinates of
    their own (e.g. NTSB's live search results) don't re-hit the geocoder on
    every poll — see ingestion/geocode.py. A row with lat/lng set to NULL
    records a lookup that failed, so a persistently bad city/state pair
    isn't retried every 5 minutes either.
    """

    __tablename__ = "geocode_cache"
    __table_args__ = (UniqueConstraint("city", "state", name="uq_geocode_cache_city_state"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(64), nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
