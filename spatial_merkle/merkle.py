"""Binary Merkle tree over leaf hashes (MVP contract §4)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


def _h(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(left + right).digest()


@dataclass(frozen=True)
class Sibling:
    hash: bytes
    is_right: bool  # sibling sits on the right of the current node


@dataclass(frozen=True)
class MerkleProof:
    leaf_index: int
    siblings: tuple[Sibling, ...]


class MerkleTree:
    """In-memory Merkle tree over an ordered list of 32-byte leaf hashes."""

    def __init__(self, leaf_hashes: list[bytes]):
        if not leaf_hashes:
            raise ValueError("Merkle tree requires at least one leaf")
        for h in leaf_hashes:
            if len(h) != 32:
                raise ValueError("leaf hashes must be 32 bytes")
        self.leaf_hashes = list(leaf_hashes)
        self._layers = self._build_layers(self.leaf_hashes)

    @staticmethod
    def _build_layers(leaves: list[bytes]) -> list[list[bytes]]:
        layers = [list(leaves)]
        while len(layers[-1]) > 1:
            prev = layers[-1]
            nxt: list[bytes] = []
            i = 0
            while i < len(prev):
                if i + 1 < len(prev):
                    nxt.append(_h(prev[i], prev[i + 1]))
                    i += 2
                else:
                    nxt.append(prev[i])  # promote odd leftover
                    i += 1
            layers.append(nxt)
        return layers

    @property
    def root(self) -> bytes:
        return self._layers[-1][0]

    def proof(self, leaf_index: int) -> MerkleProof:
        if leaf_index < 0 or leaf_index >= len(self.leaf_hashes):
            raise IndexError("leaf_index out of range")
        siblings: list[Sibling] = []
        idx = leaf_index
        for layer in self._layers[:-1]:
            if idx % 2 == 0:
                if idx + 1 < len(layer):
                    siblings.append(Sibling(layer[idx + 1], is_right=True))
                # else: odd leftover, no sibling at this level
            else:
                siblings.append(Sibling(layer[idx - 1], is_right=False))
            idx //= 2
        return MerkleProof(leaf_index, tuple(siblings))

    @staticmethod
    def root_from_proof(leaf_hash: bytes, proof: MerkleProof) -> bytes:
        current = leaf_hash
        for sib in proof.siblings:
            if sib.is_right:
                current = _h(current, sib.hash)
            else:
                current = _h(sib.hash, current)
        return current

    def replace_leaf(self, index: int, new_hash: bytes) -> "MerkleTree":
        hashes = list(self.leaf_hashes)
        hashes[index] = new_hash
        return MerkleTree(hashes)

    def splice_split(
        self, index: int, child0_hash: bytes, child1_hash: bytes
    ) -> "MerkleTree":
        """Replace leaf at index with two children; shift right by one."""
        hashes = list(self.leaf_hashes)
        hashes[index : index + 1] = [child0_hash, child1_hash]
        return MerkleTree(hashes)
