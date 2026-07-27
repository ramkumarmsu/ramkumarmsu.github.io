"""Proof package dataclasses (MVP contract §§5–8)."""

from __future__ import annotations

from dataclasses import dataclass

from .coords import Point
from .merkle import MerkleProof


@dataclass(frozen=True)
class SplitTrianglePackage:
    old_root: bytes
    new_root: bytes
    old_leaf_index: int
    old_leaf_bytes: bytes
    merkle_proof: MerkleProof
    corner: Point
    split_point: Point
    child0_leaf_bytes: bytes
    child1_leaf_bytes: bytes
    old_leaf_hashes: tuple[bytes, ...]


@dataclass(frozen=True)
class SetTriangleDataPackage:
    old_root: bytes
    new_root: bytes
    leaf_index: int
    old_leaf_bytes: bytes
    new_leaf_bytes: bytes
    merkle_proof: MerkleProof
    authority_id: str
    auth_tag: bytes


@dataclass(frozen=True)
class QueryInclusionPackage:
    root: bytes
    leaf_index: int
    leaf_bytes: bytes
    merkle_proof: MerkleProof
