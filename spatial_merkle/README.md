# Triangle Merkle MVP

Continues the spatial Merkle mesh project from
`docs/agent-kickoff-brief.md`.

## What this adds

1. **MVP contract** — `docs/mvp-contract.md`
2. **Prover library** — `spatial_merkle/prover.py` (mesh + proofs)
3. **Compact verifier** — `spatial_merkle/verifier.py` (stdlib only)
4. **End-to-end demo** — genesis → set data → split → query proofs

Ops implemented: `SetTriangleData`, `SplitTriangle`.

## Run

```bash
# from repo root
python3 -m spatial_merkle.demo
python3 -m unittest discover -s tests -v
```

No third-party packages required.
