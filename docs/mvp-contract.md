# MVP Contract — Triangle Merkle Prover / Verifier

Protocol version: `1`  
Hash function: `SHA-256`  
Coordinate system: WGS84 lon/lat as fixed-point integers

This is the machine-checkable contract for the first end-to-end demo.
It implements only `SplitTriangle` and `SetTriangleData`.

---

## 1. Coordinate quantization

Each coordinate is stored as a signed 64-bit integer:

```
q = round(degrees * 10_000_000)
```

Scale `1e7` ≈ 1.1 cm at the equator. All geometry predicates and hashes use
quantized integers only. Floating point is allowed only at the prover UI edge
when converting human degrees ↔ quantized values.

A **point** is `(x: i64, y: i64)` = `(lon_q, lat_q)`.

---

## 2. Canonical triangle ordering

Given three distinct quantized points `A, B, C`:

1. Sort lexicographically by `(x, y)` ascending → `P0 ≤ P1 ≤ P2`.
2. That ordered triple is the **canonical vertex order**.
3. Degenerate triangles (collinear / zero area in integer cross-product) are
   illegal leaves and must be rejected by both prover and verifier.

Area proxy (integer):

```
2*area_sign = (P1.x - P0.x)*(P2.y - P0.y) - (P2.x - P0.x)*(P1.y - P0.y)
```

Require `2*area_sign ≠ 0`.

---

## 3. Leaf byte layout

A leaf commits to geometry + data hash.

Encoding (`leaf_bytes`), little-endian, fixed length **81 bytes**:

| Offset | Size | Field |
|--------|------|-------|
| 0 | 1 | `protocol_version` = `1` |
| 1 | 8 | `v0.x` |
| 9 | 8 | `v0.y` |
| 17 | 8 | `v1.x` |
| 25 | 8 | `v1.y` |
| 33 | 8 | `v2.x` |
| 41 | 8 | `v2.y` |
| 49 | 32 | `data_hash` |

`data_hash = SHA-256(data_bytes)` where `data_bytes` is opaque application
payload (may be empty). Empty payload hashes to `SHA-256(b"")`.

```
leaf_hash = SHA-256(leaf_bytes)
```

---

## 4. Merkle tree

Leaves are ordered in a stable array index `0 .. n-1`.

Internal node:

```
H(left || right) = SHA-256(left_hash || right_hash)
```

Odd leftover node is promoted unchanged (Bitcoin-style).

`MerkleProof` for leaf index `i`:

- `leaf_index: u32`
- `siblings: [(hash: [u8;32], is_right: bool)]` walking leaf → root
  - `is_right = true` means sibling is on the right of the current node

Verifier recomputes root from `leaf_hash` + siblings.

---

## 5. Operation: SplitTriangle

### Meaning
Replace one triangle leaf with two children by cutting from a **corner** to a
**point on the opposite edge**.

### Inputs (in the proof package)
- `old_root`
- `old_leaf_index`
- `old_leaf_bytes` (81 bytes)
- `merkle_proof` of old leaf under `old_root`
- `corner`: point that must equal one of the three vertices
- `split_point`: point claimed to lie on the opposite edge

### Geometry predicate (deterministic)
Let vertices be `V0,V1,V2` in canonical order. Identify `corner = C`.
Opposite edge endpoints `A,B` are the other two vertices (in their relative
canonical order as they appear among the three).

`split_point = P` is **on edge AB** iff all hold in integer arithmetic:

1. Collinear: `(B.x - A.x)*(P.y - A.y) - (P.x - A.x)*(B.y - A.y) == 0`
2. Within segment bounds (inclusive endpoints forbidden — P must be strictly
   between A and B so both children have non-zero area):
   - `min(A.x,B.x) ≤ P.x ≤ max(A.x,B.x)`
   - `min(A.y,B.y) ≤ P.y ≤ max(A.y,B.y)`
   - `P ≠ A` and `P ≠ B`
3. Both children non-degenerate after canonicalization

### Children
```
child0_vertices = canonicalize(C, A, P)
child1_vertices = canonicalize(C, P, B)
```

**Payload inheritance (MVP):** both children receive the parent's `data_hash`
unchanged.

Child leaf indices: replace index `i` with `child0` at `i` and `child1` at
`i+1`, shifting subsequent leaves right by one. New root is recomputed over
the updated leaf-hash array.

### Verifier checks
1. Decode `old_leaf_bytes`; version == 1; non-degenerate
2. Recompute `old_leaf_hash`; Merkle proof yields `old_root`
3. `corner` equals exactly one vertex
4. On-edge predicate for `split_point`
5. Children match the formulas above (geometry + inherited data_hash)
6. Applying the leaf-array splice and Merkle rebuild yields `new_root`
   claimed in the package

For the compact verifier demo, the proof package may include the full ordered
`old_leaf_hashes` array so the verifier can splice and rebuild without storing
global state. Production chain verifiers would keep the leaf-hash vector (or an
incremental tree) as state; the predicates stay identical.

---

## 6. Operation: SetTriangleData

### Inputs
- `old_root`
- `leaf_index`
- `old_leaf_bytes`
- `merkle_proof`
- `new_data_hash`
- `auth` (MVP): HMAC-SHA256 over a fixed message using an authority key

### Auth message
```
msg = b"SetTriangleData|v1|" || old_root || leaf_index_u32_le || old_data_hash || new_data_hash
tag = HMAC-SHA256(authority_key, msg)
```

Verifier holds a map `authority_id → key` (demo: one key). Production would
use public-key signatures; HMAC keeps the verifier dependency-free for MVP.

### Verifier checks
1. Old leaf proof under `old_root`
2. Geometry bytes unchanged in new leaf
3. `data_hash` becomes `new_data_hash`
4. Auth tag verifies
5. Merkle update at `leaf_index` yields `new_root`

---

## 7. Proof package fields

### SplitTrianglePackage
```
op = "SplitTriangle"
old_root, new_root
old_leaf_index
old_leaf_bytes
merkle_siblings
corner, split_point
child0_leaf_bytes, child1_leaf_bytes
old_leaf_hashes[]   # optional state aid for stateless demo verifier
```

### SetTriangleDataPackage
```
op = "SetTriangleData"
old_root, new_root
leaf_index
old_leaf_bytes, new_leaf_bytes
merkle_siblings
authority_id
auth_tag
```

---

## 8. Query proof

```
QueryInclusion:
  root
  leaf_index
  leaf_bytes
  merkle_siblings
```

Verifier: `SHA-256(leaf_bytes)` + siblings → `root`.

---

## 9. Success criteria — “verifier is compact”

The verifier module must:

- Use **Python stdlib only** (`hashlib`, `hmac`, `struct`)
- Contain **no** shapefile / GIS / triangulation code
- Implement only: leaf decode, SHA-256 Merkle, on-edge integer predicate,
  split child construction check, HMAC auth, root update
- Accept/reject packages with clear boolean + error string

Prover may be larger and maintain mesh adjacency / convenience APIs.

---

## 10. Out of scope for MVP

- County shapefile triangulation
- Reverse merge, reassign, retire, introduce
- Temporal root versioning / as-of queries
- Blockchain runtime packaging
- Public-key authorization
