# FRA Rail Equipment Accident/Incident Data — Phase 2 (rail)

**Endpoint**: `GET https://data.transportation.gov/resource/85tf-25kj.json`
("Rail Equipment Accident/Incident Data (Form 54)", human-decoded variant)

**Why not FRA's own API**: FRA does publish "pilot" APIs directly
(`safetydata.fra.dot.gov/MasterWebService/FRASafetyDataAPIs.aspx`), but they
require emailing `RsisSupport@dot.gov` to register for credentials — the same
kind of gate that ruled out FAA ASIAS for Phase 1 (see `../faa_aids/README.md`)
and violates the "free, no gatekeeping" bar the other sources meet. Instead,
this uses the same underlying FRA Form 54 data republished on DOT's open
Socrata portal (`data.transportation.gov`) — no key, no registration, real
JSON, and (verified live) updated within the last day.

Two Socrata datasets carry this data: `aqxq-n5hy` is the raw source (numeric
FRA codes for everything) and `85tf-25kj` is FRA's own human-decoded version
(`accidenttype: "Derailment"` instead of a bare code, plus a `narrative` and
a link to the official report). This client uses the decoded one — it also
carries `latitude`/`longitude` directly, so no join against the raw dataset
is needed.

**Reporting lag**: same caveat as NTSB (see `../ntsb/README.md`) — railroads
file Form 54 after the fact, and the published dataset trails real-world
events by roughly one to two months in practice (verified live: newest row
was date-stamped ~2 months before the check date). The client just pulls the
most recent N rows each poll (sorted by `date` desc, excluding the handful of
legacy rows with a null date) — dedup handles any overlap between polls, and
there's no reason to bound by a date window given how sparse the update
cadence already is.

No timezone is given for `time`/`date` — treated as-is (naive, stamped UTC)
rather than guessing a railroad's local offset.
