# Triangle Merkle MVP

Continues the spatial Merkle mesh project from
`docs/agent-kickoff-brief.md`.

## What this adds

1. **MVP contract** — `docs/mvp-contract.md`
2. **Prover library** — `spatial_merkle/prover.py` (mesh + proofs)
3. **Compact verifier** — `spatial_merkle/verifier.py` (stdlib only)
4. **End-to-end demo** — genesis → set data → split → query proofs
5. **Visual demo** — 36-gon → 5 regions with animated cut / inside-outside txs

Ops implemented: `SetTriangleData`, `SplitTriangle`.

## Run

```bash
# from repo root
python3 -m spatial_merkle.demo
python3 -m spatial_merkle.build_visual_demo
python3 -m unittest discover -s tests -v
```

Open `docs/spatial-merkle-visual-demo.html` in a browser (Play / Next through transactions).

No third-party packages required.
