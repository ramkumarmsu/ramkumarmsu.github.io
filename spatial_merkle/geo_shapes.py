"""Schematic state / county polygons for the visual demo.

Not real Census geometry — an irregular map-like partition so the demo reads
as a state divided into counties (not pie slices from a hub).
"""

from __future__ import annotations

from dataclasses import dataclass

from .coords import Point, quantize
from .leaf import cross


LATTICE_GRID = 1000


def _q(lon: float, lat: float) -> Point:
    p = quantize(lon, lat)
    return Point(
        int(round(p.x / LATTICE_GRID) * LATTICE_GRID),
        int(round(p.y / LATTICE_GRID) * LATTICE_GRID),
    )


@dataclass(frozen=True)
class CountyPoly:
    name: str
    label: str
    ring: tuple[Point, ...]  # CCW, open (first != last)


def _orient_ring_ccw(ring: list[Point]) -> list[Point]:
    area2 = 0
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        area2 += a.x * b.y - b.x * a.y
    if area2 < 0:
        return list(reversed(ring))
    return ring


def ear_clip_triangulate(ring: list[Point]) -> list[tuple[Point, Point, Point]]:
    """Ear-clip a simple polygon (CCW). Returns triangle vertex triples."""
    poly = _orient_ring_ccw(list(ring))
    if len({p.to_tuple() for p in poly}) != len(poly):
        raise ValueError("polygon has duplicate vertices")
    if len(poly) < 3:
        raise ValueError("polygon needs >= 3 vertices")

    idx = list(range(len(poly)))
    tris: list[tuple[Point, Point, Point]] = []

    def is_ear(i0: int, i1: int, i2: int) -> bool:
        a, b, c = poly[i0], poly[i1], poly[i2]
        if cross(a, b, c) <= 0:
            return False
        for j in idx:
            if j in (i0, i1, i2):
                continue
            p = poly[j]
            c1 = cross(a, b, p)
            c2 = cross(b, c, p)
            c3 = cross(c, a, p)
            if c1 >= 0 and c2 >= 0 and c3 >= 0:
                return False
            if c1 <= 0 and c2 <= 0 and c3 <= 0:
                return False
        return True

    guard = 0
    while len(idx) > 3:
        guard += 1
        if guard > 10000:
            raise RuntimeError("ear clipping failed to converge")
        n = len(idx)
        clipped = False
        for k in range(n):
            i0, i1, i2 = idx[(k - 1) % n], idx[k], idx[(k + 1) % n]
            if is_ear(i0, i1, i2):
                tris.append((poly[i0], poly[i1], poly[i2]))
                del idx[k]
                clipped = True
                break
        if not clipped:
            raise RuntimeError("no ear found; polygon may be non-simple")
    tris.append((poly[idx[0]], poly[idx[1]], poly[idx[2]]))
    return tris


def toy_state_counties() -> tuple[list[Point], list[CountyPoly]]:
    """
    Irregular ~37-vertex state outline partitioned into 5 counties.

    Layout (north up)::

        +------------+----------------+
        |   Adams    |     Benton     |
        +------+-----+------+---------+
        | Claiborne  | DeSoto | Ellis |
        +------------+--------+-------+
    """
    P = {
        # South coast west→east
        "s0": _q(-91.20, 30.05),
        "s0a": _q(-91.14, 30.02),
        "s1": _q(-91.05, 30.00),
        "s2": _q(-90.90, 30.04),
        "s2a": _q(-90.82, 30.00),
        "s3": _q(-90.75, 30.01),
        "s4": _q(-90.60, 30.06),
        "s4a": _q(-90.52, 30.03),
        "s5": _q(-90.45, 30.02),
        "s6": _q(-90.30, 30.05),
        "s6a": _q(-90.24, 30.07),
        "s7": _q(-90.18, 30.10),
        # East edge south→north
        "e0": _q(-90.12, 30.22),
        "e1": _q(-90.08, 30.38),
        "e1a": _q(-90.10, 30.45),
        "e2": _q(-90.15, 30.52),
        "e3": _q(-90.10, 30.66),
        "e3a": _q(-90.12, 30.73),
        "e4": _q(-90.14, 30.80),
        "e5": _q(-90.10, 30.92),
        # North ridge east→west
        "n0": _q(-90.25, 31.00),
        "n1": _q(-90.40, 30.97),
        "n1a": _q(-90.48, 31.00),
        "n2": _q(-90.55, 31.02),
        "n3": _q(-90.70, 30.98),
        "n3a": _q(-90.78, 30.99),
        "n4": _q(-90.85, 31.01),
        "n5": _q(-91.00, 30.96),
        "n5a": _q(-91.06, 30.94),
        "n6": _q(-91.12, 30.92),
        # West river north→south
        "w0": _q(-91.22, 30.80),
        "w1": _q(-91.18, 30.66),
        "w1a": _q(-91.22, 30.59),
        "w2": _q(-91.25, 30.52),
        "w3": _q(-91.20, 30.38),
        "w3a": _q(-91.23, 30.31),
        "w4": _q(-91.24, 30.24),
        # Internal junctions
        "j_n": _q(-90.70, 30.98),   # on north between Adams/Benton (= n3)
        "j_w": _q(-91.18, 30.66),   # on west (= w1)
        "j_e": _q(-90.10, 30.66),   # on east (= e3)
        "j_s": _q(-90.82, 30.00),   # on south (= s2a)
        "j_c": _q(-90.55, 30.55),   # central hub of internal borders
        "j_nw": _q(-90.85, 30.70),
        "j_ne": _q(-90.35, 30.70),
        "j_sw": _q(-90.85, 30.35),
        "j_se": _q(-90.35, 30.35),
    }

    # Alias junctions that sit on the outer ring to the outer points exactly
    P["j_n"] = P["n3"]
    P["j_w"] = P["w1"]
    P["j_e"] = P["e3"]
    P["j_s"] = P["s2a"]

    outer_names = [
        "s0", "s0a", "s1", "s2", "s2a", "s3", "s4", "s4a", "s5", "s6", "s6a", "s7",
        "e0", "e1", "e1a", "e2", "e3", "e3a", "e4", "e5",
        "n0", "n1", "n1a", "n2", "n3", "n3a", "n4", "n5", "n5a", "n6",
        "w0", "w1", "w1a", "w2", "w3", "w3a", "w4",
    ]
    outer = [P[n] for n in outer_names]
    if len({p.to_tuple() for p in outer}) != len(outer):
        # Collapse diagnostics
        seen = {}
        for n in outer_names:
            t = P[n].to_tuple()
            if t in seen:
                raise RuntimeError(f"outer collapse: {seen[t]} and {n} -> {t}")
            seen[t] = n

    def ring(*names: str) -> tuple[Point, ...]:
        pts = [P[n] for n in names]
        # Drop accidental closing duplicate
        if len(pts) >= 2 and pts[0] == pts[-1]:
            pts = pts[:-1]
        keyed = []
        seen = set()
        for n, p in zip(names[: len(pts)], pts):
            if p.to_tuple() in seen:
                raise RuntimeError(f"duplicate vertex {n} in {names}")
            seen.add(p.to_tuple())
            keyed.append(p)
        return tuple(_orient_ring_ccw(keyed))

    counties = [
        CountyPoly(
            name="county-adams",
            label="Adams",
            # NW: north ridge n3..n6 + west w0..w1 + internal to center
            ring=ring(
                "n3", "n3a", "n4", "n5", "n5a", "n6", "w0", "w1",
                "j_nw", "j_c", "j_ne", "n3",
            ),
        ),
        CountyPoly(
            name="county-benton",
            label="Benton",
            ring=ring(
                "n3", "j_ne", "j_c", "j_se", "j_e",
                "e3a", "e4", "e5", "n0", "n1", "n1a", "n2", "n3",
            ),
        ),
        CountyPoly(
            name="county-claiborne",
            label="Claiborne",
            ring=ring(
                "w1", "w1a", "w2", "w3", "w3a", "w4", "s0", "s0a", "s1", "s2", "s2a",
                "j_sw", "j_c", "j_nw", "w1",
            ),
        ),
        CountyPoly(
            name="county-desoto",
            label="DeSoto",
            ring=ring("j_c", "j_sw", "j_s", "s3", "s4", "s4a", "s5", "j_se", "j_c"),
        ),
        CountyPoly(
            name="county-ellis",
            label="Ellis",
            ring=ring(
                "j_c", "j_se", "s5", "s6", "s6a", "s7",
                "e0", "e1", "e1a", "e2", "e3", "j_e", "j_se", "j_c",
            ),
        ),
    ]

    # Fix Adams — removed erroneous closing dup via ring(); but Adams listed n3 twice
    counties[0] = CountyPoly(
        name="county-adams",
        label="Adams",
        ring=ring(
            "n3", "n3a", "n4", "n5", "n5a", "n6", "w0", "w1", "j_nw", "j_c", "j_ne"
        ),
    )
    counties[1] = CountyPoly(
        name="county-benton",
        label="Benton",
        ring=ring(
            "n3", "n2", "n1a", "n1", "n0", "e5", "e4", "e3a", "e3",
            "j_e", "j_se", "j_c", "j_ne",
        ),
    )
    counties[2] = CountyPoly(
        name="county-claiborne",
        label="Claiborne",
        ring=ring(
            "w1", "w1a", "w2", "w3", "w3a", "w4",
            "s0", "s0a", "s1", "s2", "s2a",
            "j_sw", "j_c", "j_nw",
        ),
    )
    counties[3] = CountyPoly(
        name="county-desoto",
        label="DeSoto",
        ring=ring("j_c", "j_sw", "s2a", "s3", "s4", "s4a", "s5", "j_se"),
    )
    counties[4] = CountyPoly(
        name="county-ellis",
        label="Ellis",
        ring=ring(
            "j_c", "j_se", "s5", "s6", "s6a", "s7",
            "e0", "e1", "e1a", "e2", "e3", "j_e",
        ),
    )

    # Benton and Ellis both use j_e-e3 which is fine (same point).
    # DeSoto and Ellis share j_se-s5; Claiborne and DeSoto share j_sw-s2a.
    # Problem: DeSoto ring includes s5 and Ellis also includes s5 — shared vertex OK.
    # Problem: Benton has j_se and Ellis/DeSoto have j_se — Benton shouldn't own
    # southern points. Benton should only go down to j_e via east, and to j_c via j_ne.
    counties[1] = CountyPoly(
        name="county-benton",
        label="Benton",
        ring=ring(
            "n3", "n2", "n1a", "n1", "n0", "e5", "e4", "e3a", "e3",
            "j_e", "j_c", "j_ne",
        ),
    )
    # Ellis claims east south of e3 and south-east coast; connection j_e-j_c-j_se
    counties[4] = CountyPoly(
        name="county-ellis",
        label="Ellis",
        ring=ring(
            "j_e", "e2", "e1a", "e1", "e0", "s7", "s6a", "s6", "s5",
            "j_se", "j_c",
        ),
    )
    # Wait e3 is j_e — Ellis should start from e3 going south: e3, e2, ... 
    # But e3 to e2 is north-to-south on outer? Outer order is e2, e3, e3a (south to north).
    # So south of e3 is e2, e1a, e1, e0. Good.
    counties[4] = CountyPoly(
        name="county-ellis",
        label="Ellis",
        ring=ring(
            "e3", "e2", "e1a", "e1", "e0", "s7", "s6a", "s6", "s5",
            "j_se", "j_c",
        ),
    )

    for c in counties:
        ear_clip_triangulate(list(c.ring))

    return outer, counties


def shared_border_segments(
    a: CountyPoly, b: CountyPoly
) -> list[tuple[Point, Point]]:
    """Undirected shared edges between two county rings."""

    def edges(ring: tuple[Point, ...]) -> set[tuple[tuple[int, int], tuple[int, int]]]:
        out: set[tuple[tuple[int, int], tuple[int, int]]] = set()
        n = len(ring)
        for i in range(n):
            u, v = ring[i].to_tuple(), ring[(i + 1) % n].to_tuple()
            out.add((u, v) if u <= v else (v, u))
        return out

    shared = edges(a.ring) & edges(b.ring)
    return [(Point(*u), Point(*v)) for u, v in shared]


def find_triangle_with_edge(
    triangles: list[tuple[Point, Point, Point]], a: Point, b: Point
) -> int:
    want = {a.to_tuple(), b.to_tuple()}
    for i, (p, q, r) in enumerate(triangles):
        have = {p.to_tuple(), q.to_tuple(), r.to_tuple()}
        if want <= have:
            return i
    raise ValueError("no triangle contains edge")
