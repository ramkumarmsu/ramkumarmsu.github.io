"""Compact verifier — stdlib only (MVP contract §9)."""

from __future__ import annotations

import hashlib
import hmac
import struct
from dataclasses import dataclass

from .coords import Point
from .geometry import children_from_split, opposite_edge, point_on_open_segment
from .leaf import LEAF_SIZE, Leaf, leaf_hash
from .merkle import MerkleTree
from .packages import QueryInclusionPackage, SetTriangleDataPackage, SplitTrianglePackage


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    error: str = ""
    new_root: bytes | None = None


def auth_message(
    old_root: bytes,
    leaf_index: int,
    old_data_hash: bytes,
    new_data_hash: bytes,
) -> bytes:
    return (
        b"SetTriangleData|v1|"
        + old_root
        + struct.pack("<I", leaf_index)
        + old_data_hash
        + new_data_hash
    )


class CompactVerifier:
    """Tiny verifier: Merkle + integer predicates + HMAC auth. No GIS."""

    def __init__(self, authorities: dict[str, bytes] | None = None):
        self.authorities = dict(authorities or {})

    def verify_query(self, pkg: QueryInclusionPackage) -> VerifyResult:
        try:
            if len(pkg.leaf_bytes) != LEAF_SIZE:
                return VerifyResult(False, "bad leaf size")
            Leaf.from_bytes(pkg.leaf_bytes)  # validates canonical form
            lh = leaf_hash(pkg.leaf_bytes)
            if pkg.merkle_proof.leaf_index != pkg.leaf_index:
                return VerifyResult(False, "proof index mismatch")
            root = MerkleTree.root_from_proof(lh, pkg.merkle_proof)
            if root != pkg.root:
                return VerifyResult(False, "merkle root mismatch")
            return VerifyResult(True, new_root=pkg.root)
        except Exception as exc:  # noqa: BLE001 — surface as reject
            return VerifyResult(False, str(exc))

    def verify_split(self, pkg: SplitTrianglePackage) -> VerifyResult:
        try:
            old_leaf = Leaf.from_bytes(pkg.old_leaf_bytes)
            lh = leaf_hash(old_leaf)
            if pkg.merkle_proof.leaf_index != pkg.old_leaf_index:
                return VerifyResult(False, "proof index mismatch")
            proved = MerkleTree.root_from_proof(lh, pkg.merkle_proof)
            if proved != pkg.old_root:
                return VerifyResult(False, "old leaf not under old_root")

            # Cross-check provided leaf-hash vector
            if not pkg.old_leaf_hashes:
                return VerifyResult(False, "old_leaf_hashes required for MVP verifier")
            if pkg.old_leaf_hashes[pkg.old_leaf_index] != lh:
                return VerifyResult(False, "old_leaf_hashes entry mismatch")
            tree = MerkleTree(list(pkg.old_leaf_hashes))
            if tree.root != pkg.old_root:
                return VerifyResult(False, "old_leaf_hashes do not hash to old_root")

            vertices = old_leaf.vertices
            try:
                opposite_edge(vertices, pkg.corner)
            except ValueError as exc:
                return VerifyResult(False, str(exc))

            a, b = opposite_edge(vertices, pkg.corner)
            if not point_on_open_segment(a, b, pkg.split_point):
                return VerifyResult(False, "split_point not on open opposite edge")

            raw0, raw1 = children_from_split(vertices, pkg.corner, pkg.split_point)
            expect0 = Leaf.from_vertices_with_data_hash(*raw0, old_leaf.data_hash)
            expect1 = Leaf.from_vertices_with_data_hash(*raw1, old_leaf.data_hash)
            if expect0.to_bytes() != pkg.child0_leaf_bytes:
                return VerifyResult(False, "child0 leaf bytes mismatch")
            if expect1.to_bytes() != pkg.child1_leaf_bytes:
                return VerifyResult(False, "child1 leaf bytes mismatch")

            new_tree = tree.splice_split(
                pkg.old_leaf_index, leaf_hash(expect0), leaf_hash(expect1)
            )
            if new_tree.root != pkg.new_root:
                return VerifyResult(False, "new_root mismatch after split")
            return VerifyResult(True, new_root=pkg.new_root)
        except Exception as exc:  # noqa: BLE001
            return VerifyResult(False, str(exc))

    def verify_set_data(self, pkg: SetTriangleDataPackage) -> VerifyResult:
        try:
            old_leaf = Leaf.from_bytes(pkg.old_leaf_bytes)
            new_leaf = Leaf.from_bytes(pkg.new_leaf_bytes)
            lh = leaf_hash(old_leaf)
            if pkg.merkle_proof.leaf_index != pkg.leaf_index:
                return VerifyResult(False, "proof index mismatch")
            proved = MerkleTree.root_from_proof(lh, pkg.merkle_proof)
            if proved != pkg.old_root:
                return VerifyResult(False, "old leaf not under old_root")

            # Geometry unchanged
            if (old_leaf.v0, old_leaf.v1, old_leaf.v2) != (
                new_leaf.v0,
                new_leaf.v1,
                new_leaf.v2,
            ):
                return VerifyResult(False, "geometry changed in SetTriangleData")
            if new_leaf.data_hash == old_leaf.data_hash:
                return VerifyResult(False, "new_data_hash must differ")

            key = self.authorities.get(pkg.authority_id)
            if key is None:
                return VerifyResult(False, f"unknown authority_id {pkg.authority_id!r}")
            msg = auth_message(
                pkg.old_root, pkg.leaf_index, old_leaf.data_hash, new_leaf.data_hash
            )
            expected = hmac.new(key, msg, hashlib.sha256).digest()
            if not hmac.compare_digest(expected, pkg.auth_tag):
                return VerifyResult(False, "auth tag invalid")

            # Update root at index
            # Rebuild from proof: replace leaf hash then walk — use sibling path
            # For correctness with odd trees, recompute via local splice of known proof:
            # Verifier recomputes by replacing hash and re-hashing up using siblings.
            new_root = self._root_after_leaf_replace(
                leaf_hash(new_leaf), pkg.merkle_proof
            )
            if new_root != pkg.new_root:
                return VerifyResult(False, "new_root mismatch after SetTriangleData")
            return VerifyResult(True, new_root=pkg.new_root)
        except Exception as exc:  # noqa: BLE001
            return VerifyResult(False, str(exc))

    @staticmethod
    def _root_after_leaf_replace(new_leaf_hash: bytes, proof) -> bytes:
        return MerkleTree.root_from_proof(new_leaf_hash, proof)
