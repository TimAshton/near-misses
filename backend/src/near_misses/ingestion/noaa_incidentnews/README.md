# NOAA IncidentNews — maritime (not in original SPEC.md phases)

**Endpoint**: `GET https://incidentnews.noaa.gov/raw/incidents.csv`

Public, unauthenticated, real-time-ish CSV (no JSON API exists) — no key. This
is NOAA's Office of Response and Restoration's live incident log: every
oil/chemical spill (and other pollution incident) they've provided scientific
support for, most of them vessel casualties (groundings, collisions, sunken
or derelict vessels) in or near US waters. Rows are ordered most-recent-first
and new ones appear within days of the real-world event — not the multi-month
lag of an investigation-driven source like NTSB, but not instant either,
since the file only gains a row once OR&R is notified and the record is
entered.

**Not every row is a maritime accident.** The feed also carries land-based
causes that happen to threaten a waterway — a pipeline rupture, a railcar
derailment, a wellhead leak — tagged accordingly in the `tags` column
(pipe-separated, e.g. `"Coral|Grounding"`). `client.py` drops a row only when
every tag it has is one of those land-infrastructure causes; a row with no
tags at all (most of them) or with any vessel-related tag (`Grounding`,
`Collision`, `Derelict`, `Adrift`, `Search + Rescue`, ...) is kept.

**Severity** comes from `max_ptl_release_gallons` (critical ≥100k, high
≥10k, medium ≥1k, else low) — unknown/blank defaults to low, same reasoning
as an unknown earthquake magnitude or wildfire acreage: this dataset can't
tell a still-being-assessed casualty from a trivial sheen report, so it
doesn't try to. `severity_policy.py` currently requires medium+; watch for
the same "too much noise" pattern seismic hit and tighten to high if needed.

**Location** (`location`, free text like `"Gulf, LA"` or
`"1900 CA-1, Moss Landing, CA 95039, USA"`) isn't structured, so
`normalizer.py` scans each comma-separated part's first word for a US state
code rather than assuming a fixed format.

**Dedup**: the CSV's own `id` is stable per incident and used as `source_id`,
same as every other source here.
