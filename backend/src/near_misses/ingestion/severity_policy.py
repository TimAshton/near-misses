"""Per-category minimum severity to track.

Some sources (USGS earthquakes, FRA rail) return far more low-severity noise
than is useful on a map meant to highlight incidents worth noticing. Where a
source can cheaply filter before normalizing (USGS's magnitude is known from
the raw feed), it does so itself. Where severity can only be determined after
normalizing (FRA rail's severity depends on casualties/damage, not a single
raw field), the pipeline enforces this policy post-normalization instead.
"""

from near_misses.schemas.incident import Category, Severity

_SEVERITY_ORDER = [Severity.low, Severity.medium, Severity.high, Severity.critical]

MIN_SEVERITY_BY_CATEGORY: dict[Category, Severity] = {
    Category.seismic: Severity.medium,
    Category.rail: Severity.medium,
}


def meets_minimum_severity(category: Category, severity: Severity) -> bool:
    minimum = MIN_SEVERITY_BY_CATEGORY.get(category)
    if minimum is None:
        return True
    return _SEVERITY_ORDER.index(severity) >= _SEVERITY_ORDER.index(minimum)
