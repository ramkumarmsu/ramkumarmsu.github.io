"""Integer geometry predicates for SplitTriangle (MVP contract §5)."""

from __future__ import annotations

from .coords import Point
from .leaf import cross


def point_on_open_segment(a: Point, b: Point, p: Point) -> bool:
    """True iff P is strictly between A and B and collinear (integer math)."""
    if p == a or p == b:
        return False
    # Collinear
    if (b.x - a.x) * (p.y - a.y) - (p.x - a.x) * (b.y - a.y) != 0:
        return False
    # Bounding box (handles horizontal, vertical, diagonal)
    if not (min(a.x, b.x) <= p.x <= max(a.x, b.x)):
        return False
    if not (min(a.y, b.y) <= p.y <= max(a.y, b.y)):
        return False
    # For diagonal edges, bbox alone is enough with collinearity + not endpoints.
    # Extra: ensure P is a convex combination — dot product of (P-A)·(B-A) in (0, |B-A|^2)
    dx, dy = b.x - a.x, b.y - a.y
    dot = (p.x - a.x) * dx + (p.y - a.y) * dy
    denom = dx * dx + dy * dy
    if denom == 0:
        return False
    return 0 < dot < denom


def opposite_edge(vertices: tuple[Point, Point, Point], corner: Point) -> tuple[Point, Point]:
    """Return opposite edge endpoints (A, B) in the order they appear among vertices."""
    matches = [i for i, v in enumerate(vertices) if v == corner]
    if len(matches) != 1:
        raise ValueError("corner must equal exactly one triangle vertex")
    others = [v for v in vertices if v != corner]
    # Preserve relative order as they appear in canonical vertex list
    return others[0], others[1]


def children_from_split(
    vertices: tuple[Point, Point, Point], corner: Point, split: Point
) -> tuple[tuple[Point, Point, Point], tuple[Point, Point, Point]]:
    """Return raw (unordered) child vertex triples per contract §5."""
    a, b = opposite_edge(vertices, corner)
    if not point_on_open_segment(a, b, split):
        raise ValueError("split_point is not strictly on the opposite edge")
    # Ensure both children non-degenerate
    if cross(corner, a, split) == 0 or cross(corner, split, b) == 0:
        raise ValueError("split produces a degenerate child")
    child0 = (corner, a, split)
    child1 = (corner, split, b)
    return child0, child1
