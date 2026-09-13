from near_misses.ingestion.us_bounds import is_us_location
from near_misses.schemas.incident import Category


def test_accepts_continental_us():
    assert is_us_location(Category.seismic, 30.6333, -97.6772) is True  # Georgetown, TX


def test_accepts_alaska():
    assert is_us_location(Category.seismic, 61.2181, -149.9003) is True  # Anchorage, AK


def test_accepts_hawaii():
    assert is_us_location(Category.seismic, 21.3069, -157.8583) is True  # Honolulu, HI


def test_rejects_outside_us():
    assert is_us_location(Category.seismic, 51.5074, -0.1278) is False  # London, UK
    assert is_us_location(Category.seismic, 35.6762, 139.6503) is False  # Tokyo, JP


def test_land_only_categories_reject_open_water():
    # Well out in the Caribbean/western Atlantic — fine for a hurricane, not
    # for an earthquake epicenter (USGS never reports one there anyway, but
    # the policy itself shouldn't accept it).
    open_water = (20.0, -70.0)
    assert is_us_location(Category.seismic, *open_water) is False


def test_water_categories_accept_us_approach_waters():
    western_atlantic = (20.0, -70.0)
    hawaii_approach = (20.0, -150.0)
    for lat, lng in [western_atlantic, hawaii_approach]:
        assert is_us_location(Category.hurricane, lat, lng) is True
        assert is_us_location(Category.tsunami, lat, lng) is True
        assert is_us_location(Category.maritime, lat, lng) is True


def test_water_categories_still_reject_far_offshore():
    mid_atlantic_near_africa = (20.0, -25.0)
    far_eastern_pacific_off_mexico = (16.5, -119.3)
    assert is_us_location(Category.hurricane, *mid_atlantic_near_africa) is False
    assert is_us_location(Category.hurricane, *far_eastern_pacific_off_mexico) is False
