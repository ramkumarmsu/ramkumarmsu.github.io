# GISBC — Geographic Merkle Ledger

Verifiable geographic algorithms on a blockchain-friendly commitment scheme.

Each geographic region is represented by **two Merkle trees**:

1. **Triangle-tile tree** — interior partitioned into triangles; each tile is a leaf  
2. **Boundary-segment tree** — region border broken into segments; each segment is a leaf  

Provers do the heavy GIS work. Verifiers check each transaction with:

- **O(1)** logical / geometric predicates  
- **O(log N)** hash operations (Merkle proofs)

Example transaction classes: point location, region delegation, merging regions,
boundary refinement, tile attribute updates.

## Layout

| Path | What it is |
|------|------------|
| `docs/agent-kickoff-brief.md` | Authoritative architecture brief |
| `docs/mvp-contract.md` | Early triangle-tree MVP contract (partial) |
| `docs/spatial-merkle-visual-demo.html` | Visual walkthrough (open in a browser) |
| `spatial_merkle/` | Prover + compact verifier prototype (triangle tree) |
| `tests/` | Unit tests |

The boundary-segment tree and full algorithm transaction set are **not finished yet**.
Current code is an early triangle-tree sketch.

## Run (from this repo root)

```bash
python3 -m unittest discover -s tests -v
python3 -m spatial_merkle.demo
python3 -m spatial_merkle.build_visual_demo
```

Then open `docs/spatial-merkle-visual-demo.html`.

No third-party Python packages required for the current prototype.

## Note on repos

Prototype files may have been developed on a cloud-agent branch of
`ramkumarmsu.github.io` and copied into this **GISBC** project. Prefer **GISBC**
as the home for ongoing work.
