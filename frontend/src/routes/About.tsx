import { PageShell } from "../components/layout/PageShell";

export function About() {
  return (
    <PageShell title="About">
      <div className="max-w-2xl space-y-6 text-sm text-gray-300">
        <section>
          <h2 className="mb-1 text-base font-semibold text-gray-100">Project</h2>
          <p>
            US Incident Map overlays publicly available US incident data — aviation, rail,
            seismic, tsunami, hurricane, and wildfire — onto an interactive map. Data is polled
            from free public APIs, normalized to a shared schema, and stored persistently. No
            authentication is required to view the site.
          </p>
        </section>

        <section>
          <h2 className="mb-1 text-base font-semibold text-gray-100">Data sources &amp; attribution</h2>
          <p>
            Aviation incidents are sourced from the NTSB accident/incident database, with FAA data
            incorporated where it is publicly accessible. Earthquakes (magnitude 2.5+) come from
            the USGS Earthquake Hazards Program. Tsunami warnings/watches/advisories come from
            NOAA/NWS's public alerts feed. Rail equipment accidents/incidents come from FRA's Form
            54 data. Hurricanes and tropical storms come from NOAA's National Hurricane Center.
            Wildfires come from NIFC's (National Interagency Fire Center) WFIGS incident feed.
            All raw source records are retained for auditing and can be viewed on each incident's
            detail page.
          </p>
        </section>

        <section>
          <h2 className="mb-1 text-base font-semibold text-gray-100">Refresh cadence &amp; data lag</h2>
          <p>
            The system polls source APIs automatically every 5 minutes, and a manual refresh is
            available from the Dashboard. Aviation (NTSB) and rail (FRA) records are published only
            after an investigation or report concludes, which can lag the real-world event by days
            to months — the 5-minute poll interval reflects how quickly newly published records are
            picked up, not how quickly incidents occurred. Earthquake, tsunami, hurricane, and
            wildfire data is different: those sources reflect live/current conditions with no
            investigation lag, so the 5-minute interval there is close to real-time.
          </p>
        </section>
      </div>
    </PageShell>
  );
}
