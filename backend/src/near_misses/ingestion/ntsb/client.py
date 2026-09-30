import json
import random
from pathlib import Path
from typing import Any, Literal

import httpx

from near_misses.config import settings

_FIXTURE_PATH = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "ntsb_sample.json"


def _flatten(result: dict[str, Any]) -> dict[str, Any]:
    """Query/Main's result shape is a grid row: a list of {FieldName, Values}
    entries rather than a flat object. Collapse each field to its first value
    (these columns are all single-valued) so the rest of the pipeline can
    treat NTSB records like every other source's plain dicts.
    """
    flat: dict[str, Any] = {}
    for field in result.get("Fields", []):
        values = field.get("Values") or []
        flat[field["FieldName"]] = values[0] if values else None
    return flat


class NtsbClient:
    """Client for NTSB's CAROL accident/incident data (see ./README.md)."""

    source_name = "ntsb"

    def __init__(self, mode: Literal["live", "fixture"] = "live") -> None:
        self.mode = mode

    def fetch(self) -> list[dict[str, Any]]:
        if self.mode == "fixture":
            return json.loads(_FIXTURE_PATH.read_text())
        return self._query()

    def _query(self) -> list[dict[str, Any]]:
        payload = {
            "QueryGroups": [
                {
                    "QueryRules": [
                        {
                            "RuleType": "Simple",
                            "Values": ["Aviation"],
                            "Columns": ["Event.Mode"],
                            "Operator": "is",
                        }
                    ],
                    "AndOr": "and",
                }
            ],
            "AndOr": "and",
            "TargetCollection": "cases",
            "ResultSetSize": 50,
            "ResultSetOffset": 0,
            "SortDescending": True,
            # Both required, even for a plain JSON query with no export in
            # mind — omitting either gets back a generic 500 "An unknown
            # exception occured" with no further detail. Found by testing
            # directly against the live endpoint; see README.md. SessionId
            # additionally 500s if it's 0 or 1 specifically (looks like it's
            # used as an array index or divisor server-side) — any other
            # int works, so a random one sidesteps that edge case entirely.
            "ExportFormat": "data",
            "SessionId": random.randint(1000, 999999),
        }
        response = httpx.post(
            settings.ntsb_api_base,
            json=payload,
            headers={"Origin": "https://data.ntsb.gov", "User-Agent": settings.nws_user_agent},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return [_flatten(result) for result in data.get("Results", [])]
