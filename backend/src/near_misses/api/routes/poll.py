from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from near_misses.api.deps import get_db
from near_misses.ingestion.pipeline import run_all_sources
from near_misses.ingestion.sources import all_sources
from near_misses.schemas.incident import PollResult

router = APIRouter(prefix="/api/poll", tags=["poll"])


@router.post("/trigger", response_model=PollResult)
async def trigger_poll(db: Session = Depends(get_db)):
    """Manual refresh: runs the exact same pipeline as the scheduled job."""
    return await run_all_sources(db, all_sources())
