# NTSB CAROL API — access spike notes

Resolved as the Phase 1 primary data source (see repo root `PLAN.md` and
`ingestion/faa_aids/README.md` for why FAA AIDS/ASIAS was ruled out).

**Endpoint**: `POST https://data.ntsb.gov/carol-main-public/api/Query/Main`
(confirmed reachable — `GET` returns `405`, so it's a real, live, unauthenticated
JSON API backing the public CAROL search UI at ntsb.gov).

**Status: query body schema not fully reverse-engineered.** The endpoint expects
a JSON body shaped roughly like:

```json
{
  "ResultSetSize": 5,
  "ResultSetOffset": 0,
  "QueryGroups": [{"QueryRules": [{"RuleType": "Simple", "Values": ["Aviation"], "Columns": ["Mode"], "Operator": "is"}]}],
  "SortColumn": "EventDate",
  "SortOrder": "desc"
}
```

but every variation tried during the time-boxed spike (adding `AndOr`/`QueryAndOr`
at various nesting levels) returned `{"Error":"The Query AndOr value {0} is null"}}`
— an unrendered template string, suggesting the real schema needs a field this
spike didn't find (undocumented API; no public schema/OpenAPI spec exists). The
CAROL web UI itself (https://www.ntsb.gov/Pages/AviationQueryV2.aspx) presumably
issues a working request — capturing that via browser devtools/network tab would
be the fastest way to get the exact schema, but browser automation wasn't
available in this environment during the spike.

**What this means for the code**: `client.py`'s `_query()` method isolates the
single HTTP call so fixing the payload is a one-method change once the real
schema is confirmed. Until then, `NtsbClient.fetch()` defaults to
`mode="fixture"`, returning the bundled sample record from
`backend/tests/fixtures/ntsb_sample.json` so the rest of the pipeline
(normalize → dedup → persist → archive → broadcast) is fully buildable and
testable today. Set `mode="live"` (or fix `_query` and flip the default) once
the schema is solved.

**TODO before relying on this in production**: solve the query schema, verify
rate limits/auth requirements (none observed so far — no API key needed), and
confirm update cadence (NTSB accident records are investigation-driven and can
lag the real-world event by weeks to months — this must be disclosed on the
`/about` page, not hidden behind the 5-minute poll interval).
