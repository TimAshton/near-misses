def polygon_centroid(ring: list[list[float]]) -> tuple[float, float]:
    """Vertex-average centroid of a polygon ring: (lng, lat).

    Not area-weighted (a poor approximation for very unevenly-vertexed
    shapes), but adequate for placing a map marker at the approximate
    center of a warned zone — same spirit as SPEC.md's guidance to place
    large-area incidents (hurricanes, seismic zones) at their center.
    """
    lngs = [point[0] for point in ring]
    lats = [point[1] for point in ring]
    return (sum(lngs) / len(lngs), sum(lats) / len(lats))
