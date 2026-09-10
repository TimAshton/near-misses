from near_misses.ingestion.base import Normalizer, SourceClient
from near_misses.ingestion.ntsb.client import NtsbClient
from near_misses.ingestion.ntsb.normalizer import NtsbNormalizer
from near_misses.ingestion.usgs.client import UsgsClient
from near_misses.ingestion.usgs.normalizer import UsgsNormalizer


def all_sources() -> list[tuple[SourceClient, Normalizer]]:
    """Every source the scheduler and manual /api/poll/trigger poll.

    Returns fresh instances per call — sources are stateless, and this keeps
    tests (and any future concurrent callers) from sharing client state.
    """
    return [
        (NtsbClient(), NtsbNormalizer()),
        (UsgsClient(), UsgsNormalizer()),
    ]
