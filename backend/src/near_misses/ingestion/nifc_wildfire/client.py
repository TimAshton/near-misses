from typing import Any

import httpx

from near_misses.config import settings

_OUT_FIELDS = (
    "IncidentName,IncidentSize,PercentContained,FireDiscoveryDateTime,"
    "POOState,POOCounty,FireCause,UniqueFireIdentifier"
)


class NifcWildfireClient:
    """Client for NIFC's WFIGS current wildland fire incidents feed (see ./README.md)."""

    source_name = "nifc_wildfire"

    def fetch(self) -> list[dict[str, Any]]:
        response = httpx.get(
            settings.nifc_api_base,
            params={
                "where": "IncidentTypeCategory='WF'",
                "outFields": _OUT_FIELDS,
                "f": "json",
                "resultRecordCount": 500,
                "orderByFields": "FireDiscoveryDateTime DESC",
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json().get("features", [])
