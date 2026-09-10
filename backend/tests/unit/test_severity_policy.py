from near_misses.ingestion.severity_policy import meets_minimum_severity
from near_misses.schemas.incident import Category, Severity


def test_rail_and_seismic_require_medium_or_higher():
    assert not meets_minimum_severity(Category.rail, Severity.low)
    assert meets_minimum_severity(Category.rail, Severity.medium)
    assert meets_minimum_severity(Category.rail, Severity.high)
    assert meets_minimum_severity(Category.rail, Severity.critical)

    assert not meets_minimum_severity(Category.seismic, Severity.low)
    assert meets_minimum_severity(Category.seismic, Severity.medium)


def test_categories_without_a_policy_allow_every_severity():
    assert meets_minimum_severity(Category.aviation, Severity.low)
    assert meets_minimum_severity(Category.tsunami, Severity.low)
    assert meets_minimum_severity(Category.hurricane, Severity.low)
