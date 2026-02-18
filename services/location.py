from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Optional

from django.conf import settings

BAYAWAN_CENTER_LAT = 9.366667
BAYAWAN_CENTER_LON = 122.800000
SERVICE_BOUNDS_LAT = 0.05
SERVICE_BOUNDS_LON = 0.05


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
    """
    Ray casting algorithm.
    ring: list of [lon, lat] coordinates.
    """
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
    """
    polygon_coords: GeoJSON Polygon coordinates: [outer_ring, hole1, hole2, ...]
    """
    if not polygon_coords:
        return False
    outer = polygon_coords[0]
    if not _point_in_ring(x, y, outer):
        return False
    # Holes: if point is inside any hole, treat as outside
    for hole in polygon_coords[1:]:
        if _point_in_ring(x, y, hole):
            return False
    return True


@lru_cache(maxsize=1)
def _load_barangay_geojson() -> dict[str, Any]:
    geojson_path = Path(settings.BASE_DIR) / "static" / "data" / "barangay-boundaries.geojson"
    with geojson_path.open("r", encoding="utf-8") as f:
        return json.load(f)


@dataclass(frozen=True)
class _Offset:
    dlat: float
    dlon: float


@lru_cache(maxsize=1)
def _geojson_offset() -> _Offset:
    """
    Auto-align shifted GeoJSON datasets to the Bayawan map center used by the picker.
    This makes point-in-polygon work even if the stored polygons are uniformly translated.
    """
    data = _load_barangay_geojson()
    features = data.get("features") or []

    def _centroid_from_feature(feat: dict[str, Any]) -> tuple[float, float] | None:
        geom = feat.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates")
        ring: list[list[float]] | None = None
        if gtype == "Polygon" and coords:
            ring = coords[0]
        elif gtype == "MultiPolygon" and coords:
            try:
                ring = coords[0][0]
            except Exception:
                ring = None
        if not ring:
            return None
        xs = [float(pt[0]) for pt in ring]
        ys = [float(pt[1]) for pt in ring]
        if not xs or not ys:
            return None
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    center_lon = None
    center_lat = None

    for feat in features:
        props = feat.get("properties") or {}
        name = str(props.get("name") or "").strip().lower()
        if name == "poblacion":
            centroid = _centroid_from_feature(feat)
            if centroid:
                center_lon, center_lat = centroid
                break

    if center_lon is None or center_lat is None:
        minx = float("inf")
        miny = float("inf")
        maxx = float("-inf")
        maxy = float("-inf")

        def bump(x: float, y: float):
            nonlocal minx, miny, maxx, maxy
            minx = min(minx, x)
            maxx = max(maxx, x)
            miny = min(miny, y)
            maxy = max(maxy, y)

        def walk(gtype: str | None, coords: Any):
            if not gtype or not coords:
                return
            if gtype == "Polygon":
                for ring in coords:
                    for pt in ring:
                        bump(float(pt[0]), float(pt[1]))
            elif gtype == "MultiPolygon":
                for poly in coords:
                    for ring in poly:
                        for pt in ring:
                            bump(float(pt[0]), float(pt[1]))

        for feat in features:
            geom = (feat.get("geometry") or {})
            try:
                walk(geom.get("type"), geom.get("coordinates"))
            except Exception:
                continue

        if minx == float("inf") or miny == float("inf"):
            return _Offset(dlat=0.0, dlon=0.0)

        center_lon = (minx + maxx) / 2.0
        center_lat = (miny + maxy) / 2.0

    # Keep consistent with BAYAWAN_CENTER in the template.
    bayawan_center_lat = BAYAWAN_CENTER_LAT
    bayawan_center_lon = BAYAWAN_CENTER_LON

    return _Offset(
        dlat=bayawan_center_lat - center_lat,
        dlon=bayawan_center_lon - center_lon,
    )


@lru_cache(maxsize=256)
def detect_barangay_for_point(lat: float, lon: float) -> Optional[str]:
    """
    Returns barangay name if point is inside any Bayawan City barangay polygon.
    """
    data = _load_barangay_geojson()
    features = data.get("features") or []

    off = _geojson_offset()
    # Translate point into dataset coordinate space (inverse of polygon translation).
    x = float(lon) - off.dlon
    y = float(lat) - off.dlat

    for feat in features:
        props = feat.get("properties") or {}
        name = props.get("name")
        geom = (feat.get("geometry") or {})
        gtype = geom.get("type")
        coords = geom.get("coordinates")
        if not name or not coords:
            continue

        try:
            if gtype == "Polygon":
                # coords: [ring1, ring2, ...]
                outer_ring = coords[0] if coords else []
                bbox = _polygon_bbox(outer_ring)
                if not bbox.contains(x, y):
                    continue
                if _point_in_polygon(x, y, coords):
                    return str(name)
            elif gtype == "MultiPolygon":
                # coords: [polygon1, polygon2, ...] where polygon is [rings...]
                for poly in coords:
                    if not poly:
                        continue
                    outer_ring = poly[0]
                    bbox = _polygon_bbox(outer_ring)
                    if not bbox.contains(x, y):
                        continue
                    if _point_in_polygon(x, y, poly):
                        return str(name)
        except Exception:
            # Malformed geometry should not break request creation
            continue

    return None


def within_service_bounds(lat: float, lon: float) -> bool:
    return (
        abs(float(lat) - BAYAWAN_CENTER_LAT) <= SERVICE_BOUNDS_LAT
        and abs(float(lon) - BAYAWAN_CENTER_LON) <= SERVICE_BOUNDS_LON
    )


@lru_cache(maxsize=1)
def _barangay_centroids() -> list[tuple[str, float, float]]:
    data = _load_barangay_geojson()
    features = data.get("features") or []
    off = _geojson_offset()
    centers: list[tuple[str, float, float]] = []

    for feat in features:
        props = feat.get("properties") or {}
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
        # Convert dataset space -> real coordinates with offset.
        lon_c = (sum(xs) / len(xs)) + off.dlon
        lat_c = (sum(ys) / len(ys)) + off.dlat
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

