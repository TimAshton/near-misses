from typing import Any

from near_misses.ingestion.nws_alerts import fetch_active_alerts

_EVENTS = "Tsunami Warning,Tsunami Watch,Tsunami Advisory"


class NwsTsunamiClient:
    """Client for NOAA/NWS's public tsunami alerts feed (see ./README.md)."""

    source_name = "nws_tsunami"

    def fetch(self) -> list[dict[str, Any]]:
        return fetch_active_alerts({"event": _EVENTS})
