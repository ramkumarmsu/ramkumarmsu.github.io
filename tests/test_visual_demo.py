"""Tests for polygon hub mesh and visual demo scenario."""

from __future__ import annotations

import unittest

from spatial_merkle import CompactVerifier, Prover
from spatial_merkle.build_visual_demo import build_scenario
from spatial_merkle.geometry import point_on_open_segment
from spatial_merkle.leaf import hash_data
from spatial_merkle.polygon_mesh import (
    build_hub_mesh,
    edge_interior_point,
    regular_polygon_ring,
)


class TestPolygonMesh(unittest.TestCase):
    def test_regular_ring_distinct(self):
        center, ring = regular_polygon_ring(36)
        self.assertEqual(len(ring), 36)
        self.assertEqual(len({p.to_tuple() for p in ring}), 36)
        self.assertNotIn(center.to_tuple(), {p.to_tuple() for p in ring})

    def test_outer_edges_have_interior_lattice_points(self):
        _, ring = regular_polygon_ring(36)
        for i in range(len(ring)):
            a, b = ring[i], ring[(i + 1) % len(ring)]
            p = edge_interior_point(a, b)
            self.assertTrue(point_on_open_segment(a, b, p))

    def test_hub_mesh_leaf_count(self):
        prover = Prover()
        center, ring, idxs = build_hub_mesh(prover, 24, data=b"outside")
        self.assertEqual(len(prover.leaves), 24)
        self.assertEqual(idxs, list(range(24)))
        self.assertEqual(len(ring), 24)
        # All genesis triangles include the hub
        for leaf in prover.leaves:
            self.assertIn(center, leaf.vertices)


class TestVisualScenario(unittest.TestCase):
    def test_build_scenario_verifies_and_marks(self):
        scenario = build_scenario(n_sides=24, n_regions=4)
        self.assertGreaterEqual(len(scenario["steps"]), 10)
        self.assertTrue(any(s["op"] == "SplitTriangle" for s in scenario["steps"]))
        self.assertTrue(any(s["op"] == "SetTriangleData" for s in scenario["steps"]))
        last = scenario["steps"][-1]
        labels = {t["label"] for t in last["triangles"]}
        self.assertEqual(labels, {"inside", "outside"})
        self.assertGreater(sum(1 for t in last["triangles"] if t["label"] == "inside"), 0)
        self.assertGreater(sum(1 for t in last["triangles"] if t["label"] == "outside"), 0)
        # Final payloads match hashes
        self.assertEqual(scenario["meta"]["n_regions"], 4)


if __name__ == "__main__":
    unittest.main()
