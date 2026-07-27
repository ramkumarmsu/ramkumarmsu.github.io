# Kickoff Brief — Dual Merkle Geographic Ledger

Hand this to a future agent as prior context.
**Primary agent entry point:** repo-root `README.md` (this file is the longer twin).

User prefers plain language. Do not restart architecture debates already settled below unless asked.

**Canonical project repo:** `GISBC` (not the faculty `ramkumarmsu.github.io` site).
Cloud-agent code may temporarily live on a github.io branch for transfer into GISBC.

Optional deeper references (may live in GISBC after import):
- Planning memo: `docs/spatial-merkle-mesh-planning-summary.md`
- MVP triangle-tree contract (partial): `docs/mvp-contract.md`
- Chat export: `docs/cursor_chat_county_weather_and_spatial_mesh.txt`

---

## Project goal (authoritative)

Digitize geographic regions so that **geographic algorithms can run on a blockchain
as transactions**, and a verifier can check each transaction with:

- **O(1)** logical / geometric predicate checks
- **O(log N)** hash operations (Merkle proofs)

not a full GIS recompute.

Typical algorithms / transaction classes (non-exhaustive):
- point location
- region delegation
- merging regions into larger regions
- boundary updates / splits
- attribution / data updates on tiles or boundary segments

Maps here allocate rights, money, liability, or access. The chain commitment makes
spatial facts attributable, auditable, non-conflicting, and independently checkable.

---

## Core representation: two Merkle trees per geographic region

Each geographic region (state, county, parcel set, …) is committed by **two** roots:

### 1. Triangle-tile tree
- Region interior is partitioned into triangles (“tiles”)
- **Each triangle is a Merkle leaf**
- Leaf commits to: canonical triangle geometry + associated data
- Used for area coverage, point-in-region via tile proofs, paint/attribute updates, etc.

### 2. Boundary-line tree
- Region border is a sequence of boundary segments (edges / polylines broken into segments)
- **Each boundary segment is a Merkle leaf**
- Leaf commits to: canonical segment endpoints (+ optional segment data)
- Used for border identity, shared borders between adjacent regions, merge/split of
  regions along boundaries, delegation of border responsibility, etc.

A published region state is therefore at least:

```
RegionState = { triangle_root, boundary_root, …metadata/auth }
```

Fixed coordinate precision is required so hashes and predicates are deterministic.

---

## Roles

**Provers** (agencies, utilities, surveyors, licensed digitizers, region authorities)
- Maintain mesh + boundary structure
- Run the heavy geographic work
- Emit compact proof packages for transactions

**Verifiers** (chain nodes / TEE / auditors / end users)
- Check O(1) predicates + O(log N) Merkle paths
- Accept/reject and advance roots
- Must **not** run general GIS, shapefile IO, or global remeshing

Design rule: put complexity in the prover library; keep the verifier tiny.

---

## Verifier complexity budget (non-negotiable)

For every accepted transaction type:

| Work | Bound |
|------|-------|
| Geometric / logical predicates | **O(1)** (fixed number of local checks) |
| Hashing / Merkle | **O(log N)** in the size of the touched tree(s) |

If a proposed op needs a global geometry scan, it is the wrong op — redesign into
local ops that preserve invariants by construction.

---

## Invariants (target)

- Triangle tiles of a region are a non-overlapping cover of that region’s interior
- Boundary segments of a region form its border commitment
- Adjacent regions that share a border can prove agreement on shared boundary leaves
- Only legal local ops are accepted ⇒ global consistency is preserved incrementally
- Lon/lat fixed-point is acceptable for parcel-scale predicates; projection is secondary

---

## What already exists (partial prototype)

Implemented as an early **triangle-tree only** sketch:

- `SplitTriangle`, `SetTriangleData`
- stdlib compact verifier + prover demo
- visual demo (needs geographic state/county shapes, not pie slices)

**Missing relative to this brief:**
- boundary-line Merkle tree
- dual-root region state
- point-location transaction
- region delegation transaction
- region merge transaction
- explicit O(1)/O(log N) checklist per tx type
- realistic state→county demo geometry

EDDI/weather scripts are an unrelated side track.

---

## Settled preferences

- Dual trees per region (tiles + boundary segments)
- Verifier triviality is non-negotiable (O(1) logic, O(log N) hashes)
- Prover UX matters; ship a library
- Restricted local ops beat arbitrary remesh transactions
- Demo geometry should look like geographic regions (e.g. state outline ÷ counties),
  even if simplified to ~30–40 outer sides and 4–5 counties for transaction count

---

## Recommended next work

1. **Rewrite contract for dual trees** — boundary leaf layout + triangle leaf layout +
   `RegionState` roots + complexity budget
2. **Define first transaction set with proof shapes**
   - point location
   - paint/delegate triangle set (or region delegation)
   - merge two regions (boundary + triangle root updates)
   - keep `SplitTriangle` / boundary split as refinement ops
3. **Geographic visual demo** — schematic state (~30–40 sides) divided into 4–5
   county polygons; animate boundary cuts + inside/outside (delegation) txs
4. Only later: real county shapefile ingestion on the prover side

---

## Paste template for a new agent
```text
Read README.md in the GISBC repo (agent handoff).

This project commits each geographic region with TWO Merkle trees:
(1) triangular tiles as leaves, (2) boundary segments as leaves.
Blockchain txs must verify in O(1) predicates + O(log N) hashes.

My next goal:
<fill in>
```
