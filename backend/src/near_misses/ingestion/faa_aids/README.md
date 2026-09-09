# FAA AIDS / ASIAS — ruled out for Phase 1

SPEC.md names "FAA Accident & Incident Data System (AIDS) / Aviation Safety
Hotline" as the primary Phase 1 data source. During the Phase 1 data-source
spike:

- The public entry point for FAA accident/incident data is ASIAS
  (Aviation Safety Information Analysis and Sharing,
  `https://www.asias.faa.gov/apex/f?p=100:1`), an Oracle APEX application.
  A direct request returns an HTTP `302` redirect — consistent with the app
  requiring an authenticated session (ASIAS access is granted to approved
  aviation-industry partners, not the general public).
- No standalone, publicly documented, unauthenticated AIDS REST/JSON API was
  found.

**Decision**: FAA AIDS is not usable as an open public API for this project.
NTSB's CAROL data (`data.ntsb.gov`) — the spec's own named "Backup" — is used
as the actual Phase 1 primary source instead. See `../ntsb/README.md` for that
source's own access notes and open items.

This directory is kept as a placeholder in case FAA later publishes an open
AIDS feed (e.g. via data.gov) worth revisiting for Phase 1 or a later phase.
