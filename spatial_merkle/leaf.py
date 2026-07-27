"""Leaf encoding and hashing (MVP contract §§2–3)."""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass

from .coords import Point

PROTOCOL_VERSION = 1
LEAF_STRUCT = struct.Struct("<B6q32s")  # 1 + 48 + 32 = 81
LEAF_SIZE = LEAF_STRUCT.size
assert LEAF_SIZE == 81


def hash_data(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def cross(a: Point, b: Point, c: Point) -> int:
    """2*signed area of triangle (a,b,c) via integer cross product at a."""
    return (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)


def canonicalize(a: Point, b: Point, c: Point) -> tuple[Point, Point, Point]:
    pts = sorted([a, b, c])
    if len({p.to_tuple() for p in pts}) != 3:
        raise ValueError("triangle vertices must be distinct")
    if cross(pts[0], pts[1], pts[2]) == 0:
        raise ValueError("degenerate triangle (collinear vertices)")
    return pts[0], pts[1], pts[2]


@dataclass(frozen=True)
class Leaf:
    v0: Point
    v1: Point
    v2: Point
    data_hash: bytes
    protocol_version: int = PROTOCOL_VERSION

    def __post_init__(self) -> None:
        if len(self.data_hash) != 32:
            raise ValueError("data_hash must be 32 bytes")
        # Ensure canonical order stored
        c0, c1, c2 = canonicalize(self.v0, self.v1, self.v2)
        object.__setattr__(self, "v0", c0)
        object.__setattr__(self, "v1", c1)
        object.__setattr__(self, "v2", c2)

    @classmethod
    def from_vertices(
        cls, a: Point, b: Point, c: Point, data: bytes = b""
    ) -> "Leaf":
        v0, v1, v2 = canonicalize(a, b, c)
        return cls(v0, v1, v2, hash_data(data))

    @classmethod
    def from_vertices_with_data_hash(
        cls, a: Point, b: Point, c: Point, data_hash: bytes
    ) -> "Leaf":
        v0, v1, v2 = canonicalize(a, b, c)
        return cls(v0, v1, v2, data_hash)

    @property
    def vertices(self) -> tuple[Point, Point, Point]:
        return (self.v0, self.v1, self.v2)

    def to_bytes(self) -> bytes:
        return LEAF_STRUCT.pack(
            self.protocol_version,
            self.v0.x,
            self.v0.y,
            self.v1.x,
            self.v1.y,
            self.v2.x,
            self.v2.y,
            self.data_hash,
        )

    @classmethod
    def from_bytes(cls, raw: bytes) -> "Leaf":
        if len(raw) != LEAF_SIZE:
            raise ValueError(f"leaf must be {LEAF_SIZE} bytes, got {len(raw)}")
        ver, x0, y0, x1, y1, x2, y2, dh = LEAF_STRUCT.unpack(raw)
        if ver != PROTOCOL_VERSION:
            raise ValueError(f"unsupported protocol version {ver}")
        leaf = cls(Point(x0, y0), Point(x1, y1), Point(x2, y2), dh, ver)
        # Reject non-canonical encodings
        if leaf.to_bytes() != raw:
            raise ValueError("leaf bytes are not in canonical form")
        return leaf


def leaf_hash(leaf: Leaf | bytes) -> bytes:
    raw = leaf.to_bytes() if isinstance(leaf, Leaf) else leaf
    if len(raw) != LEAF_SIZE:
        raise ValueError("invalid leaf bytes length")
    return hashlib.sha256(raw).digest()
