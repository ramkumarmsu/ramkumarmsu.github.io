"""Tests for triangle Merkle MVP contract + prover/verifier."""

from __future__ import annotations

import hashlib
import hmac
import unittest

from spatial_merkle import CompactVerifier, Point, Prover, quantize
from spatial_merkle.geometry import point_on_open_segment
from spatial_merkle.leaf import Leaf, leaf_hash
from spatial_merkle.merkle import MerkleTree
from spatial_merkle.verifier import auth_message


class TestLeafCanonical(unittest.TestCase):
    def test_canonical_order_and_hash_stable(self):
        a, b, c = Point(0, 0), Point(10, 0), Point(0, 10)
        l1 = Leaf.from_vertices(a, b, c, b"x")
        l2 = Leaf.from_vertices(c, a, b, b"x")
        self.assertEqual(l1.to_bytes(), l2.to_bytes())
        self.assertEqual(leaf_hash(l1), leaf_hash(l2))
        self.assertEqual(len(l1.to_bytes()), 81)

    def test_rejects_degenerate(self):
        with self.assertRaises(ValueError):
            Leaf.from_vertices(Point(0, 0), Point(1, 1), Point(2, 2), b"")


class TestMerkle(unittest.TestCase):
    def test_proof_roundtrip(self):
        leaves = [hashlib.sha256(bytes([i])).digest() for i in range(5)]
        tree = MerkleTree(leaves)
        for i in range(5):
            proof = tree.proof(i)
            self.assertEqual(MerkleTree.root_from_proof(leaves[i], proof), tree.root)


class TestGeometry(unittest.TestCase):
    def test_on_open_segment(self):
        a, b = Point(0, 0), Point(10, 0)
        self.assertTrue(point_on_open_segment(a, b, Point(5, 0)))
        self.assertFalse(point_on_open_segment(a, b, Point(0, 0)))
        self.assertFalse(point_on_open_segment(a, b, Point(5, 1)))


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.a = quantize(-90.0, 30.0)
        self.b = quantize(-89.0, 30.0)
        self.c = quantize(-90.0, 31.0)
        self.prover = Prover()
        self.idx = self.prover.add_genesis_triangle(
            self.a, self.b, self.c, data=b"empty"
        )
        self.verifier = CompactVerifier(
            {self.prover.authority_id: self.prover.authority_key}
        )

    def test_query(self):
        q = self.prover.query(self.idx)
        r = self.verifier.verify_query(q)
        self.assertTrue(r.ok, r.error)

    def test_set_data_and_split(self):
        set_pkg = self.prover.set_triangle_data(self.idx, b"parcel:1")
        r = self.verifier.verify_set_data(set_pkg)
        self.assertTrue(r.ok, r.error)

        leaf = self.prover.leaves[self.idx]
        corner = leaf.v0
        others = [v for v in leaf.vertices if v != corner]
        mid = Point((others[0].x + others[1].x) // 2, (others[0].y + others[1].y) // 2)
        split_pkg = self.prover.split_triangle(self.idx, corner, mid)
        r = self.verifier.verify_split(split_pkg)
        self.assertTrue(r.ok, r.error)
        self.assertEqual(len(self.prover.leaves), 2)

        # Both children inherit data_hash
        self.assertEqual(
            self.prover.leaves[0].data_hash, self.prover.leaves[1].data_hash
        )

        for i in range(2):
            r = self.verifier.verify_query(self.prover.query(i))
            self.assertTrue(r.ok, r.error)

    def test_rejects_bad_auth(self):
        set_pkg = self.prover.set_triangle_data(self.idx, b"parcel:1")
        # Tamper tag
        bad = set_pkg.__class__(
            **{
                **set_pkg.__dict__,
                "auth_tag": b"\x00" * 32,
            }
        )
        r = self.verifier.verify_set_data(bad)
        self.assertFalse(r.ok)
        self.assertIn("auth", r.error)

    def test_rejects_off_edge_split(self):
        leaf = self.prover.leaves[self.idx]
        corner = leaf.v0
        bad_point = Point(corner.x + 1, corner.y + 1)
        with self.assertRaises(ValueError):
            self.prover.split_triangle(self.idx, corner, bad_point)


if __name__ == "__main__":
    unittest.main()
