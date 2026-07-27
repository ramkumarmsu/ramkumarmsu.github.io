#!/usr/bin/env python3
"""End-to-end MVP demo: genesis → SetTriangleData → SplitTriangle → query."""

from __future__ import annotations

import sys

from spatial_merkle import CompactVerifier, Point, Prover, quantize


def main() -> int:
    # Simple axis-aligned right triangle in quantized lon/lat space
    a = quantize(-90.0, 30.0)
    b = quantize(-89.0, 30.0)
    c = quantize(-90.0, 31.0)

    prover = Prover()
    idx = prover.add_genesis_triangle(a, b, c, data=b"county:unassigned")
    print(f"genesis leaf={idx} root={prover.root.hex()}")

    verifier = CompactVerifier({prover.authority_id: prover.authority_key})

    # Query inclusion
    q = prover.query(idx)
    r = verifier.verify_query(q)
    print(f"query verify: ok={r.ok} error={r.error!r}")
    if not r.ok:
        return 1

    # Attach parcel-ish data
    set_pkg = prover.set_triangle_data(idx, b"parcel:demo-001")
    r = verifier.verify_set_data(set_pkg)
    print(f"set_data verify: ok={r.ok} error={r.error!r} new_root={r.new_root.hex() if r.new_root else None}")
    if not r.ok:
        return 1

    # Split from corner C toward a point mid-edge AB
    # vertices after canonicalize: sorted by (x,y)
    leaf = prover.leaves[idx]
    corner = leaf.v0  # use first canonical vertex as corner
    # opposite edge = the other two; pick midpoint
    others = [v for v in leaf.vertices if v != corner]
    mid = Point(
        (others[0].x + others[1].x) // 2,
        (others[0].y + others[1].y) // 2,
    )
    # Ensure midpoint is strictly between (integer midpoint of distinct points works
    # when they differ in at least one coord by >= 2; our degree spacing is huge)
    split_pkg = prover.split_triangle(idx, corner, mid)
    r = verifier.verify_split(split_pkg)
    print(
        f"split verify: ok={r.ok} error={r.error!r} "
        f"leaves={len(prover.leaves)} new_root={r.new_root.hex() if r.new_root else None}"
    )
    if not r.ok:
        return 1

    # Query both children
    for i in range(len(prover.leaves)):
        qi = prover.query(i)
        ri = verifier.verify_query(qi)
        print(f"  child[{i}] query ok={ri.ok} data_hash={prover.leaves[i].data_hash.hex()[:16]}...")

    print("MVP demo passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
