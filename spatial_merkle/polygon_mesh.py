"""Convex polygon hub triangulation helpers for demos."""

from __future__ import annotations

import math

from .coords import Point, dequantize, quantize
from .geometry import point_on_open_segment
from .leaf import Leaf
from .prover import Prover


def _snap(v: int, grid: int) -> int:
    return int(round(v / grid) * grid)


def regular_polygon_ring(
    n: int,
    *,
    center_lon: float = -90.0,
    center_lat: float = 32.0,
    radius_deg: float = 0.08,
    start_angle_rad: float = 0.0,
    lattice_grid: int = 1000,
) -> tuple[Point, list[Point]]:
    """Return hub center + n ring vertices for a regular convex polygon.

    Vertices are snapped to ``lattice_grid`` in quantized units so every edge
    difference is a multiple of the grid and therefore admits interior lattice
    split points (needed by SplitTriangle).
    """
    if n < 3:
        raise ValueError("polygon needs at least 3 sides")
    if lattice_grid < 2:
        raise ValueError("lattice_grid must be >= 2")

    raw_c = quantize(center_lon, center_lat)
    center = Point(_snap(raw_c.x, lattice_grid), _snap(raw_c.y, lattice_grid))
    ring: list[Point] = []
    for i in range(n):
        ang = start_angle_rad + (2.0 * math.pi * i) / n
        raw = quantize(
            center_lon + radius_deg * math.cos(ang),
            center_lat + radius_deg * math.sin(ang),
        )
        ring.append(Point(_snap(raw.x, lattice_grid), _snap(raw.y, lattice_grid)))
    # Quantization/snapping can collapse rare near-duplicates; require distinct.
    if len({p.to_tuple() for p in ring}) != n:
        raise ValueError("quantized ring vertices are not distinct; increase radius")
    if center.to_tuple() in {p.to_tuple() for p in ring}:
        raise ValueError("center coincides with a ring vertex after quantization")
    return center, ring


def edge_interior_point(a: Point, b: Point) -> Point:
    """
    Lattice point strictly between a and b on segment ab.

    Component-wise integer midpoints are NOT always collinear. Use the gcd
    lattice walk instead (MVP integer geometry).
    """
    dx, dy = b.x - a.x, b.y - a.y
    g = math.gcd(dx, dy)
    if g < 2:
        raise ValueError("no strict lattice point on segment")
    k = g // 2
    p = Point(a.x + (dx // g) * k, a.y + (dy // g) * k)
    if not point_on_open_segment(a, b, p):
        raise ValueError("failed to construct interior lattice point")
    return p


# Back-compat alias used by the visual demo
def edge_midpoint(a: Point, b: Point) -> Point:
    return edge_interior_point(a, b)


def build_hub_mesh(
    prover: Prover,
    n: int = 36,
    *,
    data: bytes = b"outside",
    **poly_kwargs,
) -> tuple[Point, list[Point], list[int]]:
    """
    Triangulate a regular n-gon by connecting the hub to each boundary edge.

    Returns (center, ring, leaf_indices) where leaf_indices[i] is the leaf for
    triangle (center, ring[i], ring[(i+1) % n]) at genesis (equal to i).
    """
    center, ring = regular_polygon_ring(n, **poly_kwargs)
    indices: list[int] = []
    for i in range(n):
        a = ring[i]
        b = ring[(i + 1) % n]
        idx = prover.add_genesis_triangle(center, a, b, data=data)
        indices.append(idx)
    return center, ring, indices


def triangle_centroid_deg(leaf: Leaf) -> tuple[float, float]:
    lons, lats = [], []
    for v in leaf.vertices:
        lon, lat = dequantize(v)
        lons.append(lon)
        lats.append(lat)
    return (sum(lons) / 3.0, sum(lats) / 3.0)


def sector_index(leaf: Leaf, center: Point, n_sectors: int) -> int:
    """Assign a leaf to a sector by angle of its centroid around hub."""
    cx, cy = dequantize(center)
    lon, lat = triangle_centroid_deg(leaf)
    ang = math.atan2(lat - cy, lon - cx)
    if ang < 0:
        ang += 2.0 * math.pi
    return int((ang / (2.0 * math.pi)) * n_sectors) % n_sectors


def find_leaf_with_outer_edge(
    prover: Prover, center: Point, a: Point, b: Point
) -> int:
    """Find leaf index whose vertices are exactly {center, a, b}."""
    want = {center.to_tuple(), a.to_tuple(), b.to_tuple()}
    for i, leaf in enumerate(prover.leaves):
        have = {leaf.v0.to_tuple(), leaf.v1.to_tuple(), leaf.v2.to_tuple()}
        if have == want:
            return i
    raise ValueError("no leaf matches outer edge")
