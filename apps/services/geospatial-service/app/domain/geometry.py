"""Small GeoJSON point-in-polygon implementation.

This module deliberately has no spatial-library dependency.  A production
deployment can replace this boundary with a database/spatial index without
changing the HTTP contracts.
"""

from typing import Any


def _in_ring(point: tuple[float, float], ring: list[list[float]]) -> bool:
    x, y = point
    inside = False
    for i, current in enumerate(ring):
        previous = ring[i - 1]
        x1, y1 = current[:2]
        x2, y2 = previous[:2]
        if (y1 > y) != (y2 > y):
            cross_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < cross_x:
                inside = not inside
    return inside


def point_in_geometry(point: tuple[float, float], geometry: dict[str, Any]) -> bool:
    """Return whether a GeoJSON (lon, lat) point is in a Polygon/MultiPolygon."""
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if kind == "Polygon":
        if not coordinates:
            return False
        return _in_ring(point, coordinates[0]) and not any(
            _in_ring(point, hole) for hole in coordinates[1:]
        )
    if kind == "MultiPolygon":
        return any(point_in_geometry(point, {"type": "Polygon", "coordinates": polygon})
                   for polygon in coordinates or [])
    raise ValueError("geometry must be a GeoJSON Polygon or MultiPolygon")
