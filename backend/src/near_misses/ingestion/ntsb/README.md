# NTSB CAROL API — live query notes

**Status: live.** `NtsbClient()` defaults to `mode="live"` and hits the real
endpoint on every poll. `mode="fixture"` (returning
`backend/tests/fixtures/ntsb_sample.json`) still exists for offline tests.

**Endpoint**: `POST https://data.ntsb.gov/carol-main-public/api/Query/Main`.

**The schema, solved**: the original spike (see git history) got
`{"Error":"The Query AndOr value {0} is null"}` on every attempt because it
was missing an `AndOr` key at both the query-group level and the top level.
Once those are added, two more requirements surface one at a time as you fix
them — `Columns` must be the dotted form (`"Event.Mode"`, not `"Mode"`), and
the endpoint needs **both** `"ExportFormat": "data"` and a `"SessionId"` —
omit either and it falls through to a generic, undiagnosable
`"An unknown exception occured"` 500. `SessionId` also 500s if it's
literally `0` or `1` (looks like it's used as an array index or divisor
server-side) — any other int is fine, so `client.py` uses a random one each
request rather than a fixed value. None of this is documented anywhere;
found entirely by testing against the live endpoint. `client.py`'s
`_query()` payload has the full working shape. Sorting newest-first uses `"SortDescending": true`;
a `SortColumn`/`SortOrder` pair (what the original spike tried) isn't a
field this endpoint accepts and also 500s.

The response is a results grid, not a flat object — each record is
`{"Fields": [{"FieldName", "Values": [...]}, ...], "EntryId": ...}`.
`client._flatten()` collapses that into a plain dict keyed by `FieldName`
before handing records to the normalizer.

**The bigger catch: no coordinates.** The live search grid's fixed column
set (`NtsbNo`, `EventDate`, `City`, `State`, `VehicleMake`, `VehicleModel`,
`HighestInjuryLevel`, ...) has no `Latitude`/`Longitude`, no airport, and no
narrative — unlike the original hand-authored fixture, which had all of
those because it was never actually shaped like a real response. Passing an
explicit `Columns` list in the request to ask for more fields just 500s, and
the only other NTSB reverse-engineering effort found (a GitHub proxy around
the `FileExport` endpoint) only streams raw case-docket ZIPs, which don't
obviously carry structured coordinates either.

**Resolution**: `normalizer.py` geocodes `City` + `State` via OpenStreetMap
Nominatim (`ingestion/geocode.py`) to get an approximate lat/lng — city-
center precision, not the exact accident site. Results are cached in the
`geocode_cache` table so a poll that re-fetches the same recent records every
5 minutes doesn't re-hit Nominatim for the same city/state pair, keeping
well under its 1 req/sec free-tier usage policy. A record whose city/state
can't be geocoded is dropped (caught and logged by the pipeline) rather than
stored with no location, since `Location.lat`/`lng` are required.

**Reporting lag**: unlike the FRA rail feed (1-2 months), NTSB's preliminary
listing for an event shows up fast — verified live results included records
from 2-3 days before the check date. Full investigation writeups (narrative,
cause, docket) still lag by weeks to months, but that's a completeness gap
in the record, not a delay in the record existing.
