from typing import Any

from near_misses.ingestion.nws_alerts import fetch_active_alerts

# Tsunami Warning/Watch/Advisory are already their own category via
# nws_tsunami — excluded here so the same underlying CAP alert never shows
# up twice under two different categories/icons.
_EXCLUDED_EVENTS = {"Tsunami Warning", "Tsunami Watch", "Tsunami Advisory"}


class NwsSevereWeatherClient:
    """Client for NOAA/NWS's public alerts feed, Extreme severity only (see ./README.md)."""

    source_name = "nws_severe_weather"

    def fetch(self) -> list[dict[str, Any]]:
        features = fetch_active_alerts({"severity": "Extreme"})
        return [f for f in features if f.get("properties", {}).get("event") not in _EXCLUDED_EVENTS]
