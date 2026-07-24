# Spatial Merkle Mesh — Conversation Planning Summary

Saved from a Cursor cloud-agent discussion for later review.
This is a planning memo only (no implementation commitment).

## Original weather task (separate track)
- Local script: `scripts/get_monthly_weather.py`
- Downloads monthly county weather averages via Open-Meteo
- Output: `~/Downloads/county_weather_monthly.csv`
- EDDI deferred
- Rate limits handled with pauses + resume

## Ambitious project vision
Build a triangulated spatial substrate for counties/parcels/utilities, where:

1. Space is partitioned into triangles
2. Each triangle is a Merkle leaf
3. Updates are incremental and locally checkable
4. A blockchain network stores roots / accepts verified updates
5. End users can query and verify answers against the public root

## Why put GIS on chain?
Not to store shapefiles for novelty. Useful when maps allocate rights, money, liability, or access.

Value comes from:
- shared multi-agency source of truth
- auditable boundary/attribute history
- verifiable answers without trusting the responder
- non-overlapping exclusive claims on a layer
- composability with permits, contracts, payments, sensors

Less useful for purely internal single-trust GIS visualization.

## Geometry plan
Given a US county polygon:
1. Triangulate county interior
2. Build bounding box
3. Triangulate exterior region = box minus county

Projection: not required for parcel-scale point-in-triangle queries; lon/lat is acceptable.

Long-term digitization goal:
- parcels/zones as triangle sets
- utility lines as constrained edges / sequences
- snapping + topology for reliable digitization

## Merkle / blockchain design
### Leaf
Hash of:
- canonical ordering of 3 triangle vertices
- associated triangle data

Fixed coordinate precision is essential.

### Roles
- **Provers**: agencies/utilities/surveyors who submit reliable updates + proofs
- **Verifiers**:
  - blockchain nodes that check proofs and update roots
  - end users who verify query answers against the root

### Preferred update ops (verifier-trivial)
1. `SplitTriangle(corner, point_on_opposite_edge)` → replace 1 leaf with 2
2. `SetTriangleData(...)` → same geometry, new payload

Non-overlap can be preserved by construction if genesis mesh is valid and only legal splits (and carefully controlled later ops) are allowed.

### Asymmetry goal
- Verifier work: trivial (Merkle path + tiny predicates + auth)
- Prover work: allowed to be heavier, but practically made easy via library support

## Practical hard issue: boundaries over time
Especially relevant for thin/shifting geographies (e.g. Louisiana coastal/river change).

System must be a **versioned spatial ledger**:
- roots over time: \(R_t\)
- as-of-date queries
- change reasons (resurvey, court order, coastal loss, subdivision, etc.)
- later ops beyond split: reassign, retire (land→water), introduce (accretion), with authority rules

## Two major software components to build together
### 1. Prover library (large, ergonomic)
Helps provers:
- maintain mesh/adjacency
- apply local ops
- canonicalize geometry
- maintain incremental Merkle tree
- emit update/query proof packages

### 2. Compact verifier application (tiny)
Small enough for trustworthy boundaries (chain runtime / TEE / auditor):
- verify Merkle proofs
- check split / data-update predicates
- check authorization
- accept/reject and update root

Design rule: keep verifier dependency-free and deterministic; put GIS complexity in the prover library.

## Suggested next planning step
Write a one-page MVP contract covering:
- leaf byte format
- hash function
- coordinate precision
- exact split predicate
- proof package format
- success criteria for “verifier is compact”

Then implement prover library + compact verifier against that contract.
