"""Triangle Merkle mesh MVP — prover library + compact verifier."""

from .coords import Point, quantize, dequantize
from .leaf import Leaf, leaf_hash, hash_data
from .merkle import MerkleTree, MerkleProof
from .verifier import CompactVerifier, VerifyResult
from .prover import Prover

__all__ = [
    "Point",
    "quantize",
    "dequantize",
    "Leaf",
    "leaf_hash",
    "hash_data",
    "MerkleTree",
    "MerkleProof",
    "CompactVerifier",
    "VerifyResult",
    "Prover",
]

PROTOCOL_VERSION = 1
COORD_SCALE = 10_000_000
