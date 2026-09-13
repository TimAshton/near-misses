"""Per-category minimum severity to track.

Some sources (USGS earthquakes, FRA rail, NIFC wildfires) return far more
low-severity noise than is useful on a map meant to highlight incidents
worth noticing. Where a source can cheaply filter before normalizing
(USGS's magnitude is known from the raw feed), it does so itself. Where
severity can only be determined after normalizing (FRA rail's severity
depends on casualties/damage, not a single raw field; wildfire severity
depends on acreage), the pipeline enforces this policy post-normalization
instead.
"""

from near_misses.schemas.incident import Category, Severity

_SEVERITY_ORDER = [Severity.low, Severity.medium, Severity.high, Severity.critical]

MIN_SEVERITY_BY_CATEGORY: dict[Category, Severity] = {
    Category.seismic: Severity.high,
    Category.rail: Severity.medium,
    Category.wildfire: Severity.critical,
    # NOAA IncidentNews includes a lot of unconfirmed/untraced "mystery
    # sheen" reports with no real damage yet established — medium+ is a
    # starting point (same as rail/seismic originally were), may need
    # tightening to high once real-world noise is visible on the map.
    Category.maritime: Severity.medium,
    # Backstop, not the primary filter — the source itself only fetches
    # severity=Extreme alerts, so almost everything here is critical
    # already (see nws_severe_weather/README.md).
    Category.severe_weather: Severity.critical,
}


def meets_minimum_severity(category: Category, severity: Severity) -> bool:
    minimum = MIN_SEVERITY_BY_CATEGORY.get(category)
    if minimum is None:
        return True
    return _SEVERITY_ORDER.index(severity) >= _SEVERITY_ORDER.index(minimum)
