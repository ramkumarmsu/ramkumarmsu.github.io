"""Prover library — mesh state, splits, data updates, query proofs."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field

from .coords import Point
from .geometry import children_from_split
from .leaf import Leaf, hash_data, leaf_hash
from .merkle import MerkleTree
from .packages import QueryInclusionPackage, SetTriangleDataPackage, SplitTrianglePackage
from .verifier import auth_message


@dataclass
class Prover:
    """In-memory triangle mesh + Merkle tree for the MVP demo."""

    leaves: list[Leaf] = field(default_factory=list)
    authority_id: str = "demo-authority"
    authority_key: bytes = field(default_factory=lambda: b"demo-secret-key-change-me")
    _tree: MerkleTree | None = field(default=None, init=False, repr=False)

    def _rebuild(self) -> None:
        if not self.leaves:
            self._tree = None
            return
        self._tree = MerkleTree([leaf_hash(lf) for lf in self.leaves])

    @property
    def root(self) -> bytes:
        if self._tree is None:
            raise RuntimeError("empty mesh has no root")
        return self._tree.root

    @property
    def leaf_hashes(self) -> list[bytes]:
        return list(self._tree.leaf_hashes) if self._tree else []

    def add_genesis_triangle(self, a: Point, b: Point, c: Point, data: bytes = b"") -> int:
        leaf = Leaf.from_vertices(a, b, c, data)
        self.leaves.append(leaf)
        self._rebuild()
        return len(self.leaves) - 1

    def query(self, leaf_index: int) -> QueryInclusionPackage:
        assert self._tree is not None
        leaf = self.leaves[leaf_index]
        return QueryInclusionPackage(
            root=self.root,
            leaf_index=leaf_index,
            leaf_bytes=leaf.to_bytes(),
            merkle_proof=self._tree.proof(leaf_index),
        )

    def split_triangle(
        self, leaf_index: int, corner: Point, split_point: Point
    ) -> SplitTrianglePackage:
        assert self._tree is not None
        old_leaf = self.leaves[leaf_index]
        old_root = self.root
        old_hashes = tuple(self.leaf_hashes)
        proof = self._tree.proof(leaf_index)

        raw0, raw1 = children_from_split(old_leaf.vertices, corner, split_point)
        child0 = Leaf.from_vertices_with_data_hash(*raw0, old_leaf.data_hash)
        child1 = Leaf.from_vertices_with_data_hash(*raw1, old_leaf.data_hash)

        # Apply locally
        self.leaves[leaf_index : leaf_index + 1] = [child0, child1]
        self._rebuild()
        new_root = self.root

        return SplitTrianglePackage(
            old_root=old_root,
            new_root=new_root,
            old_leaf_index=leaf_index,
            old_leaf_bytes=old_leaf.to_bytes(),
            merkle_proof=proof,
            corner=corner,
            split_point=split_point,
            child0_leaf_bytes=child0.to_bytes(),
            child1_leaf_bytes=child1.to_bytes(),
            old_leaf_hashes=old_hashes,
        )

    def set_triangle_data(
        self, leaf_index: int, data: bytes
    ) -> SetTriangleDataPackage:
        assert self._tree is not None
        old_leaf = self.leaves[leaf_index]
        old_root = self.root
        proof = self._tree.proof(leaf_index)
        new_dh = hash_data(data)
        if new_dh == old_leaf.data_hash:
            raise ValueError("data unchanged")
        new_leaf = Leaf(
            old_leaf.v0, old_leaf.v1, old_leaf.v2, new_dh, old_leaf.protocol_version
        )
        tag = hmac.new(
            self.authority_key,
            auth_message(old_root, leaf_index, old_leaf.data_hash, new_dh),
            hashlib.sha256,
        ).digest()

        self.leaves[leaf_index] = new_leaf
        self._rebuild()

        return SetTriangleDataPackage(
            old_root=old_root,
            new_root=self.root,
            leaf_index=leaf_index,
            old_leaf_bytes=old_leaf.to_bytes(),
            new_leaf_bytes=new_leaf.to_bytes(),
            merkle_proof=proof,
            authority_id=self.authority_id,
            auth_tag=tag,
        )
