# Kickoff Brief — Triangle Merkle Prover / Verifier Architecture

Hand this to a future agent as prior context.
User prefers plain language. Do not restart architecture debates already settled below unless asked.

Optional deeper references:
- Planning memo: `docs/spatial-merkle-mesh-planning-summary.md`
- Full chat export: `docs/cursor_chat_county_weather_and_spatial_mesh.txt`
- Repo branch: `cursor/county-weather-monthly-2b78`

---

## Project goal
Build a verifiable spatial records system where:

1. Geographic space is partitioned into triangles
2. Each triangle is a Merkle tree leaf
3. Authoritative actors (“provers”) submit incremental updates with proofs
4. A compact verifier checks those proofs cheaply
5. A blockchain / trust network stores roots and accepts valid updates
6. End users query facts and verify answers against the published root

This is meant for reliable digitization of parcel boundaries, zones, utility lines, etc.

Useful because maps here are not just pictures — they allocate rights, money, liability, or access. The chain commitment makes spatial facts attributable, auditable, non-conflicting, and independently checkable.

---

## Core architecture

### Geometry substrate
- Start from a county polygon
- Triangulate the county interior
- Build a bounding box around it
- Triangulate the exterior region = box minus county
- Lon/lat is acceptable for parcel-scale point-in-triangle queries; projection is not required for the current design intent
- Later: refine/constrain triangles for parcels, zones, utilities

### Merkle leaf
A leaf hash commits to:
- the 3 triangle vertices in **canonical order**
- **data associated with that triangle**

Fixed coordinate precision is required so hashes are deterministic.

### Roles
**Provers**
- Entities who need to provide reliable data
- Includes government agencies, utilities, surveyors, licensed digitizers
- They prepare updates and generate proofs

**Verifiers**
- Blockchain / network nodes that validate update transactions and advance the root
- End users / apps that verify query answers against the root
- Verification must stay trivial

### Design principle
- Verifier work: cheap and obvious
- Prover work: may be heavier in theory, but should be made easy in practice with a library
- Preserve non-overlap by construction via restricted local operations
- Do **not** put full GIS inside the verifier

---

## First-class operations (MVP)

### 1. SplitTriangle
Cut one triangle into two by specifying:
- a corner of the triangle
- a point on the opposite edge

Verifier checks:
- old leaf exists under old root (Merkle proof)
- point lies on the opposite edge (deterministic rule)
- two child triangles are correctly formed and canonicalized
- new root correctly replaces one leaf with two
- payload inheritance rule is followed

### 2. SetTriangleData
Attach/update data on an existing triangle leaf.

Verifier checks:
- Merkle proof of old leaf
- geometry unchanged
- new data hash/payload valid
- authorization / signature for that data class
- Merkle update to new root

These two ops are enough to begin progressive digitization by refinement.

### Later ops (not MVP, but anticipated)
- Reverse merge of a recorded split pair
- Reassign triangle between parcels (boundary move)
- Retire triangle from land domain (e.g. inundation)
- Introduce triangle into domain (e.g. accretion/fill)
- Temporal versioning of roots and as-of-date queries

---

## Non-overlap logic
If:
- genesis mesh is a valid non-overlapping partition, and
- only legal local ops are accepted,

then non-overlap is preserved by construction.
Verifiers should not need a global geometry re-check on every transaction.

---

## Two software components to build

### A. Prover library (larger, ergonomic)
Helps provers:
- maintain triangle mesh + adjacency
- canonicalize points/triangles
- apply splits / data updates
- maintain an incremental Merkle tree
- emit update proof packages (old root → new root)
- answer queries with inclusion/attribution proofs

GIS dependencies are allowed here.

### B. Compact verifier application (tiny)
Intended to run inside trustworthy boundaries such as:
- blockchain runtime / smart contract constraints
- TEE / enclave
- air-gapped auditor

It should only:
- verify Merkle paths
- evaluate tiny predicates for allowed ops
- check authorization
- accept/reject and compute/accept new root

No shapefile IO. No general triangulation. No heavy dependencies.

---

## Temporal / real-world hard case
Boundaries change over time. Thin and shifting geographies (e.g. Louisiana coastal/river boundaries) are a motivating stress case.

Therefore the long-term system is a **versioned spatial ledger**:
- sequence of roots over time
- feature effective dates
- as-of-date queries
- explicit change reasons and authorities

MVP can still begin with split + data update on a static genesis mesh.

---

## Settled preferences from prior discussion
- Put whole GIS on chain is an aspiration, but only valuable if verifiable multi-party spatial truth is the product
- Leaf = canonical triangle + data
- Verifier triviality is non-negotiable
- Prover UX matters in practice
- Start with restricted local ops, not arbitrary remesh transactions
- Projection concerns are secondary for parcel-scale queries
- EDDI/weather work is a separate side track, not this architecture

---

## Requested collaboration
User wants to eventually produce, together:
1. prover software library
2. compact verifier application

---

## Status (MVP landed)
Implemented on branch `cursor/triangle-merkle-mvp-2e31`:

- Contract: `docs/mvp-contract.md`
- Package: `spatial_merkle/` (prover + compact stdlib verifier)
- Demo: `python3 -m spatial_merkle.demo`
- Tests: `python3 -m unittest discover -s tests -v`

Ops working end-to-end: `SetTriangleData`, `SplitTriangle`, query inclusion proofs.

---

## Recommended next work when resuming
Unless user specifies otherwise, proceed in this order:

1. **Multi-triangle genesis helper** — build a tiny hand mesh (or box+diagonal) and exercise several splits
2. **Point-in-triangle query with proof** — return containing leaf + Merkle inclusion
3. **County shapefile → genesis triangulation** (prover-side only; keep verifier untouched)
4. Replace HMAC auth with public-key signatures when packaging for a chain/TEE target

---

## Paste template for a new agent
```text
Read this kickoff brief and continue from it:
docs/agent-kickoff-brief.md
Also read docs/mvp-contract.md and run the spatial_merkle demo/tests.

Focus on the triangle Merkle prover/verifier architecture, not the weather script.

My next goal:
<fill in>
```
