# Agent handoff — GISBC dual Merkle geographic ledger

**This file is for a follow-up agent.** Read it before changing architecture or restarting debates.

User: Mahalingam (researcher). Prefer plain language. Prefer coding and iterating in-repo.
**Canonical repo:** `GISBC` (not `ramkumarmsu.github.io`).

---

## What this project is

Run geographic algorithms on a blockchain as **transactions**. Each transaction must be checkable by a tiny verifier:

- **O(1)** logical / geometric predicates
- **O(log N)** Merkle hash operations

Each geographic region is committed by **two** Merkle trees:

1. **Triangle-tile tree** — interior triangles (“tiles”) as leaves  
2. **Boundary-segment tree** — border segments as leaves  

```
RegionState = { triangle_root, boundary_root, … }
```

Example transaction classes: point location, region delegation, merging regions,
boundary splits/updates, tile/boundary attribute updates.

Do **not** put full GIS inside the verifier. Heavy work stays in the prover library.

---

## Settled (do not re-litigate unless asked)

- Dual trees per region (tiles + boundary)
- Verifier budget: O(1) predicates + O(log N) hashes
- Restricted local ops that preserve invariants by construction
- Demo geometry should look like a **state divided into counties**
  (~30–40 outer sides, 4–5 counties) — **not** pie slices from a hub
- Lon/lat fixed-point is fine for parcel-scale predicates for now

---

## What exists today (partial)

Triangle-tree sketch only:

- `spatial_merkle/` — prover + stdlib compact verifier
- Ops: `SplitTriangle`, `SetTriangleData`
- `docs/mvp-contract.md` — triangle MVP contract
- `docs/spatial-merkle-visual-demo.html` — visual demo (still pie-slice style; needs rewrite)
- `spatial_merkle/geo_shapes.py` — WIP state/county outlines (incomplete)

**Missing:** boundary-segment tree, dual-root `RegionState`, point-location tx,
delegation tx, merge-regions tx, geographic (state/county) visual demo.

More detail: `docs/agent-kickoff-brief.md`  
Prior chat/planning: `docs/spatial-merkle-mesh-planning-summary.md`,
`docs/cursor_chat_county_weather_and_spatial_mesh.txt`

---

## Do this next (unless user specifies otherwise)

1. Dual-tree contract (triangle leaf + boundary leaf + `RegionState` + complexity budget)
2. Implement one end-to-end tx with proofs (prefer **point location**)
3. Geographic visual demo: schematic state → 4–5 counties; show boundary cut +
   inside/outside (delegation) transactions
4. Only later: real shapefile ingestion on the prover side

### Quick checks

```bash
python3 -m unittest discover -s tests -v
python3 -m spatial_merkle.demo
```

---

## User prompt template

```text
Read README.md (this agent handoff) in the GISBC repo.

Each geographic region has TWO Merkle trees: triangular tiles and boundary
segments. Verifier budget: O(1) predicates + O(log N) hashes.

My next goal:
<fill in>
```
