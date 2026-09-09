import json
from pathlib import Path
from typing import Any, Literal

import httpx

from near_misses.config import settings

_FIXTURE_PATH = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "ntsb_sample.json"


class NtsbClient:
    """Client for NTSB's CAROL accident/incident data.

    See ./README.md — the live query schema is not yet fully solved, so this
    defaults to fixture mode. `_query()` is the single isolated HTTP call to
    fix once the real schema is confirmed (e.g. by capturing a real request
    from https://www.ntsb.gov/Pages/AviationQueryV2.aspx).
    """

    source_name = "ntsb"

    def __init__(self, mode: Literal["live", "fixture"] = "fixture") -> None:
        self.mode = mode

    def fetch(self) -> list[dict[str, Any]]:
        if self.mode == "fixture":
            return json.loads(_FIXTURE_PATH.read_text())
        return self._query()

    def _query(self) -> list[dict[str, Any]]:
        payload = {
            "ResultSetSize": 25,
            "ResultSetOffset": 0,
            "QueryGroups": [
                {
                    "QueryRules": [
                        {
                            "RuleType": "Simple",
                            "Values": ["Aviation"],
                            "Columns": ["Mode"],
                            "Operator": "is",
                        }
                    ],
                }
            ],
            "SortColumn": "EventDate",
            "SortOrder": "desc",
        }
        response = httpx.post(settings.ntsb_api_base, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("Results", data if isinstance(data, list) else [])
