from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Optional

from django.conf import settings

BAYAWAN_CENTER_LAT = 9.470
BAYAWAN_CENTER_LON = 122.821

CENRO_OFFICE_LAT = 9.3630
CENRO_OFFICE_LON = 122.8013


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_from_cenro(lat: float, lon: float) -> float:
    """Distance in km from the CENRO Bayawan Office to a given point."""
    return haversine_km(CENRO_OFFICE_LAT, CENRO_OFFICE_LON, lat, lon)


@dataclass(frozen=True)
class _BBox:
    minx: float
    miny: float
    maxx: float
    maxy: float

    def contains(self, x: float, y: float) -> bool:
        return self.minx <= x <= self.maxx and self.miny <= y <= self.maxy


def _polygon_bbox(coords: Iterable[Iterable[float]]) -> _BBox:
    xs: list[float] = []
    ys: list[float] = []
    for x, y in coords:
        xs.append(float(x))
        ys.append(float(y))
    return _BBox(min(xs), min(ys), max(xs), max(ys))


def _point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    inside = False
    n = len(ring)
    if n < 3:
        return False

    j = n - 1
    for i in range(n):
        xi, yi = float(ring[i][0]), float(ring[i][1])
        xj, yj = float(ring[j][0]), float(ring[j][1])
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-16) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def _point_in_polygon(x: float, y: float, polygon_coords: list[list[list[float]]]) -> bool:
    if not polygon_coords:
        return False
    outer = polygon_coords[0]
    if not _point_in_ring(x, y, outer):
        return False
    for hole in polygon_coords[1:]:
        if _point_in_ring(x, y, hole):
            return False
    return True


def _point_in_feature(x: float, y: float, feat: dict[str, Any]) -> bool:
    geom = feat.get("geometry") or {}
    gtype = geom.get("type")
    coords = geom.get("coordinates")
    if not coords:
        return False
    if gtype == "Polygon":
        outer_ring = coords[0] if coords else []
        bbox = _polygon_bbox(outer_ring)
        if not bbox.contains(x, y):
            return False
        return _point_in_polygon(x, y, coords)
    elif gtype == "MultiPolygon":
        for poly in coords:
            if not poly:
                continue
            outer_ring = poly[0]
            bbox = _polygon_bbox(outer_ring)
            if not bbox.contains(x, y):
                continue
            if _point_in_polygon(x, y, poly):
                return True
    return False


@lru_cache(maxsize=1)
def _load_barangay_geojson() -> dict[str, Any]:
    geojson_path = Path(settings.BASE_DIR) / "static" / "data" / "barangay-boundaries.geojson"
    with geojson_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def is_inside_bayawan_city(lat: float, lon: float) -> bool:
    """Check if a point falls inside the Bayawan City boundary polygon."""
    data = _load_barangay_geojson()
    x, y = float(lon), float(lat)
    for feat in (data.get("features") or []):
        props = feat.get("properties") or {}
        if props.get("type") == "city_boundary":
            try:
                return _point_in_feature(x, y, feat)
            except Exception:
                return False
    return False


@lru_cache(maxsize=256)
def detect_barangay_for_point(lat: float, lon: float) -> Optional[str]:
    """
    Returns barangay name if point is inside any Bayawan City barangay polygon.
    Falls back to 'Bayawan City' if inside the city boundary but not a named barangay.
    Returns None if outside.
    """
    data = _load_barangay_geojson()
    features = data.get("features") or []
    x, y = float(lon), float(lat)

    inside_city = False
    for feat in features:
        props = feat.get("properties") or {}
        if props.get("type") == "city_boundary":
            try:
                inside_city = _point_in_feature(x, y, feat)
            except Exception:
                pass
            continue

        name = props.get("name")
        if not name:
            continue
        try:
            if _point_in_feature(x, y, feat):
                return str(name)
        except Exception:
            continue

    if inside_city:
        return "Bayawan City"
    return None


def within_service_bounds(lat: float, lon: float) -> bool:
    return is_inside_bayawan_city(lat, lon)


@lru_cache(maxsize=1)
def _barangay_centroids() -> list[tuple[str, float, float]]:
    data = _load_barangay_geojson()
    features = data.get("features") or []
    centers: list[tuple[str, float, float]] = []

    for feat in features:
        props = feat.get("properties") or {}
        if props.get("type") == "city_boundary":
            continue
        name = props.get("name")
        geom = feat.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates")
        if not name or not coords:
            continue
        ring = None
        if gtype == "Polygon":
            ring = coords[0] if coords else None
        elif gtype == "MultiPolygon":
            try:
                ring = coords[0][0]
            except Exception:
                ring = None
        if not ring:
            continue
        xs = [float(pt[0]) for pt in ring]
        ys = [float(pt[1]) for pt in ring]
        if not xs or not ys:
            continue
        lon_c = sum(xs) / len(xs)
        lat_c = sum(ys) / len(ys)
        centers.append((str(name), lat_c, lon_c))

    return centers


def nearest_barangay(lat: float, lon: float) -> Optional[str]:
    centers = _barangay_centroids()
    if not centers:
        return None
    best_name = None
    best_dist = None
    for name, c_lat, c_lon in centers:
        d = (c_lat - lat) ** 2 + (c_lon - lon) ** 2
        if best_dist is None or d < best_dist:
            best_dist = d
            best_name = name
    return best_name

