import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from near_misses.config import settings
from near_misses.db import SessionLocal
from near_misses.ingestion.pipeline import run_all_sources
from near_misses.ingestion.sources import all_sources

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def poll_all_sources() -> None:
    db = SessionLocal()
    try:
        result = await run_all_sources(db, all_sources())
        logger.info("Scheduled poll complete: %s", result)
    finally:
        db.close()


def start_scheduler() -> None:
    if not settings.scheduler_enabled:
        return
    scheduler.add_job(
        poll_all_sources,
        "interval",
        minutes=settings.poll_interval_minutes,
        id="poll_all_sources",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
