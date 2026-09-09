"""Reject incidents outside the US per SPEC.md's "US incidents only" constraint.

Simple bounding boxes rather than a full reverse-geocode/shapefile lookup —
good enough to filter obviously non-US coordinates at ingestion time.
"""

_BOXES = [
    # (min_lat, max_lat, min_lng, max_lng)
    (24.4, 49.4, -125.0, -66.9),  # continental US
    (51.2, 71.5, -179.2, -129.8),  # Alaska
    (18.9, 22.3, -160.3, -154.7),  # Hawaii
    (17.6, 18.6, -67.3, -65.2),  # Puerto Rico
]


def is_us_location(lat: float, lng: float) -> bool:
    return any(
        min_lat <= lat <= max_lat and min_lng <= lng <= max_lng
        for min_lat, max_lat, min_lng, max_lng in _BOXES
    )
