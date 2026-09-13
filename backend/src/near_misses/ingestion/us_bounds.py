"""Reject incidents outside the US per SPEC.md's "US incidents only" constraint.

Simple bounding boxes rather than a full reverse-geocode/shapefile lookup —
good enough to filter obviously non-US coordinates at ingestion time.
"""

from near_misses.schemas.incident import Category

_LAND_BOXES = [
    # (min_lat, max_lat, min_lng, max_lng)
    (24.4, 49.4, -125.0, -66.9),  # continental US
    (51.2, 71.5, -179.2, -129.8),  # Alaska
    (18.9, 22.3, -160.3, -154.7),  # Hawaii
    (17.6, 18.6, -67.3, -65.2),  # Puerto Rico
]

# A storm, tsunami zone, or vessel incident is meaningfully "US" while still
# well offshore — the land boxes above are land-hugging on purpose for
# sources that only ever report a point on land, so they're too tight for
# anything that happens over water. These add a generous buffer covering US
# territorial/EEZ waters and the ocean approach a tracked storm crosses
# before landfall, without stretching all the way to e.g. the open mid-
# Atlantic or the African coast (still not "US waters" by any reading).
_WATER_BOXES = [
    (15.0, 47.0, -100.0, -55.0),  # Gulf of Mexico, Caribbean/PR/USVI, western Atlantic approach
    (15.0, 42.0, -175.0, -140.0),  # Eastern Pacific approach to Hawaii
    (30.0, 42.0, -140.0, -117.0),  # rare Eastern Pacific approach to the CA/OR/WA coast
    (45.0, 75.0, -179.2, -125.0),  # Gulf of Alaska / Bering Sea
]

# Categories that legitimately occur over open water, not just on land.
_WATER_INCLUDED_CATEGORIES = {Category.hurricane, Category.tsunami, Category.maritime}


def _in_any(lat: float, lng: float, boxes: list[tuple[float, float, float, float]]) -> bool:
    return any(
        min_lat <= lat <= max_lat and min_lng <= lng <= max_lng
        for min_lat, max_lat, min_lng, max_lng in boxes
    )


def is_us_location(category: Category, lat: float, lng: float) -> bool:
    if _in_any(lat, lng, _LAND_BOXES):
        return True
    return category in _WATER_INCLUDED_CATEGORIES and _in_any(lat, lng, _WATER_BOXES)
