from near_misses.ingestion.severity_policy import meets_minimum_severity
from near_misses.schemas.incident import Category, Severity


def test_rail_requires_medium_or_higher():
    assert not meets_minimum_severity(Category.rail, Severity.low)
    assert meets_minimum_severity(Category.rail, Severity.medium)
    assert meets_minimum_severity(Category.rail, Severity.high)
    assert meets_minimum_severity(Category.rail, Severity.critical)


def test_maritime_requires_medium_or_higher():
    assert not meets_minimum_severity(Category.maritime, Severity.low)
    assert meets_minimum_severity(Category.maritime, Severity.medium)
    assert meets_minimum_severity(Category.maritime, Severity.high)
    assert meets_minimum_severity(Category.maritime, Severity.critical)


def test_seismic_requires_high_or_higher():
    assert not meets_minimum_severity(Category.seismic, Severity.low)
    assert not meets_minimum_severity(Category.seismic, Severity.medium)
    assert meets_minimum_severity(Category.seismic, Severity.high)
    assert meets_minimum_severity(Category.seismic, Severity.critical)


def test_wildfire_requires_critical():
    assert not meets_minimum_severity(Category.wildfire, Severity.low)
    assert not meets_minimum_severity(Category.wildfire, Severity.medium)
    assert not meets_minimum_severity(Category.wildfire, Severity.high)
    assert meets_minimum_severity(Category.wildfire, Severity.critical)


def test_severe_weather_requires_critical():
    assert not meets_minimum_severity(Category.severe_weather, Severity.low)
    assert not meets_minimum_severity(Category.severe_weather, Severity.medium)
    assert not meets_minimum_severity(Category.severe_weather, Severity.high)
    assert meets_minimum_severity(Category.severe_weather, Severity.critical)


def test_categories_without_a_policy_allow_every_severity():
    assert meets_minimum_severity(Category.aviation, Severity.low)
    assert meets_minimum_severity(Category.tsunami, Severity.low)
    assert meets_minimum_severity(Category.hurricane, Severity.low)
