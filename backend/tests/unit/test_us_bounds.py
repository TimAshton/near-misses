from near_misses.ingestion.us_bounds import is_us_location


def test_accepts_continental_us():
    assert is_us_location(30.6333, -97.6772) is True  # Georgetown, TX


def test_accepts_alaska():
    assert is_us_location(61.2181, -149.9003) is True  # Anchorage, AK


def test_accepts_hawaii():
    assert is_us_location(21.3069, -157.8583) is True  # Honolulu, HI


def test_rejects_outside_us():
    assert is_us_location(51.5074, -0.1278) is False  # London, UK
    assert is_us_location(35.6762, 139.6503) is False  # Tokyo, JP
