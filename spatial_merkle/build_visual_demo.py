#!/usr/bin/env python3
"""
Build a visual demo scenario: ~36-gon hub mesh, boundary cuts, inside/outside marks.

Writes a self-contained HTML file with step playback.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from spatial_merkle import CompactVerifier, Point, Prover
from spatial_merkle.coords import dequantize
from spatial_merkle.leaf import hash_data
from spatial_merkle.polygon_mesh import (
    build_hub_mesh,
    edge_midpoint,
    find_leaf_with_outer_edge,
    sector_index,
)


REGION_COLORS = {
    "outside": "#9aa7b5",
    "inside": "#2f6f5e",
    "cut": "#c45c26",
    "unassigned": "#c5ced6",
    "region-0": "#5f8f78",
    "region-1": "#4f7f8c",
    "region-2": "#c4a35a",
    "region-3": "#b08968",
    "region-4": "#6d7c91",
}


def _pt(p: Point) -> list[float]:
    lon, lat = dequantize(p)
    return [lon, lat]


def _label_of(data_hash: bytes, table: dict[bytes, str]) -> str:
    return table.get(data_hash, "unknown")


def snapshot(
    prover: Prover,
    *,
    center: Point,
    title: str,
    caption: str,
    op: str,
    label_table: dict[bytes, str],
    highlight: list[int] | None = None,
    cut_segment: list[list[float]] | None = None,
    n_sectors: int = 5,
) -> dict:
    tris = []
    for i, leaf in enumerate(prover.leaves):
        label = _label_of(leaf.data_hash, label_table)
        tris.append(
            {
                "i": i,
                "points": [_pt(leaf.v0), _pt(leaf.v1), _pt(leaf.v2)],
                "label": label,
                "sector": sector_index(leaf, center, n_sectors),
            }
        )
    return {
        "title": title,
        "caption": caption,
        "op": op,
        "root": prover.root.hex(),
        "leaf_count": len(prover.leaves),
        "highlight": highlight or [],
        "cut_segment": cut_segment,
        "triangles": tris,
        "center": _pt(center),
    }


def build_scenario(n_sides: int = 36, n_regions: int = 5) -> dict:
    if n_sides < 12:
        raise ValueError("demo expects a reasonably fine polygon (>= 12)")
    if n_regions < 2:
        raise ValueError("need at least 2 regions")

    prover = Prover()
    verifier = CompactVerifier({prover.authority_id: prover.authority_key})

    label_table = {
        hash_data(b"outside"): "outside",
        hash_data(b"inside"): "inside",
    }

    center, ring, _ = build_hub_mesh(
        prover,
        n_sides,
        data=b"outside",
        center_lon=-90.15,
        center_lat=32.35,
        radius_deg=0.09,
        start_angle_rad=-math.pi / 2,
    )

    steps: list[dict] = []
    steps.append(
        snapshot(
            prover,
            center=center,
            title=f"Genesis · {n_sides}-gon hub mesh",
            caption=(
                f"County-like demo polygon with {n_sides} boundary edges, "
                f"fan-triangulated from the hub. All triangles start as outside."
            ),
            op="genesis",
            label_table=label_table,
            n_sectors=n_regions,
        )
    )

    # Boundary cut vertices: every n_sides/n_regions around the ring
    cut_vertex_indices = [
        (i * n_sides) // n_regions for i in range(n_regions)
    ]

    # Refine mesh at each region boundary by splitting the triangle on the
    # clockwise side of the cut radial (center → ring[v]).
    for cut_i, vidx in enumerate(cut_vertex_indices):
        # Triangle whose outer edge starts at this vertex: (center, ring[vidx], ring[next])
        a = ring[vidx]
        b = ring[(vidx + 1) % n_sides]
        leaf_idx = find_leaf_with_outer_edge(prover, center, a, b)
        mid = edge_midpoint(a, b)
        cut_seg = [_pt(center), _pt(a)]

        steps.append(
            snapshot(
                prover,
                center=center,
                title=f"Cut boundary {cut_i + 1}/{n_regions}",
                caption=(
                    f"Transaction SplitTriangle: cut from the hub toward a new "
                    f"point on the outer edge. This commits radial boundary "
                    f"#{cut_i + 1} between regions."
                ),
                op="SplitTriangle",
                label_table=label_table,
                highlight=[leaf_idx],
                cut_segment=cut_seg,
                n_sectors=n_regions,
            )
        )

        pkg = prover.split_triangle(leaf_idx, center, mid)
        result = verifier.verify_split(pkg)
        if not result.ok:
            raise RuntimeError(f"split verify failed: {result.error}")

        steps.append(
            snapshot(
                prover,
                center=center,
                title=f"Boundary {cut_i + 1} committed",
                caption=(
                    f"Verifier accepted the split. Merkle root advanced to "
                    f"{prover.root.hex()[:16]}…  Mesh now has {len(prover.leaves)} triangles."
                ),
                op="SplitTriangle",
                label_table=label_table,
                highlight=[leaf_idx, leaf_idx + 1],
                cut_segment=cut_seg,
                n_sectors=n_regions,
            )
        )

    # Paint each wedge as its own sub-polygon (region-0 .. region-k)
    for r in range(n_regions):
        payload = f"region-{r}".encode()
        label_table[hash_data(payload)] = f"region-{r}"

    for r in range(n_regions):
        payload = f"region-{r}".encode()
        idxs = [
            i
            for i, leaf in enumerate(prover.leaves)
            if sector_index(leaf, center, n_regions) == r
            and leaf.data_hash != hash_data(payload)
        ]
        for leaf_idx in idxs:
            pkg = prover.set_triangle_data(leaf_idx, payload)
            result = verifier.verify_set_data(pkg)
            if not result.ok:
                raise RuntimeError(f"region mark verify failed: {result.error}")
        steps.append(
            snapshot(
                prover,
                center=center,
                title=f"Form sub-polygon {r + 1}/{n_regions}",
                caption=(
                    f"SetTriangleData assigns sector {r} triangles to region-{r}. "
                    f"The {n_regions} radial cuts now bound distinct smaller polygons."
                ),
                op="SetTriangleData",
                label_table=label_table,
                highlight=idxs,
                n_sectors=n_regions,
            )
        )

    # Convert a claim (two contiguous regions) to inside / outside
    inside_sectors = {0, 1}
    to_inside = [
        i
        for i, leaf in enumerate(prover.leaves)
        if sector_index(leaf, center, n_regions) in inside_sectors
    ]
    to_outside = [
        i
        for i, leaf in enumerate(prover.leaves)
        if sector_index(leaf, center, n_regions) not in inside_sectors
    ]

    steps.append(
        snapshot(
            prover,
            center=center,
            title="Claim: inside vs outside",
            caption=(
                f"Next, mark sectors {sorted(inside_sectors)} as inside and the "
                f"remaining sectors as outside — a verifiable ownership / zoning claim."
            ),
            op="SetTriangleData",
            label_table=label_table,
            highlight=to_inside,
            n_sectors=n_regions,
        )
    )

    for k, leaf_idx in enumerate(to_inside):
        if prover.leaves[leaf_idx].data_hash == hash_data(b"inside"):
            continue
        pkg = prover.set_triangle_data(leaf_idx, b"inside")
        result = verifier.verify_set_data(pkg)
        if not result.ok:
            raise RuntimeError(f"set_data verify failed: {result.error}")
        if k == 0 or k == len(to_inside) - 1 or (k + 1) % 4 == 0:
            steps.append(
                snapshot(
                    prover,
                    center=center,
                    title=f"Mark inside · {k + 1}/{len(to_inside)}",
                    caption=(
                        "Transaction SetTriangleData: geometry unchanged, payload "
                        "becomes inside. Verifier checks Merkle proof + HMAC auth."
                    ),
                    op="SetTriangleData",
                    label_table=label_table,
                    highlight=[leaf_idx],
                    n_sectors=n_regions,
                )
            )

    for k, leaf_idx in enumerate(to_outside):
        if prover.leaves[leaf_idx].data_hash == hash_data(b"outside"):
            continue
        pkg = prover.set_triangle_data(leaf_idx, b"outside")
        result = verifier.verify_set_data(pkg)
        if not result.ok:
            raise RuntimeError(f"outside mark verify failed: {result.error}")
        if k == 0 or k == len(to_outside) - 1 or (k + 1) % 6 == 0:
            steps.append(
                snapshot(
                    prover,
                    center=center,
                    title=f"Mark outside · {k + 1}/{len(to_outside)}",
                    caption=(
                        "Remaining triangles are marked outside the claim. "
                        "Each update advances the Merkle root."
                    ),
                    op="SetTriangleData",
                    label_table=label_table,
                    highlight=[leaf_idx],
                    n_sectors=n_regions,
                )
            )

    inside_count = sum(
        1
        for leaf in prover.leaves
        if leaf.data_hash == hash_data(b"inside")
    )
    steps.append(
        snapshot(
            prover,
            center=center,
            title="Demo complete",
            caption=(
                f"Final mesh: {len(prover.leaves)} triangles · "
                f"{inside_count} inside · {len(prover.leaves) - inside_count} outside · "
                f"root {prover.root.hex()[:20]}…"
            ),
            op="done",
            label_table=label_table,
            n_sectors=n_regions,
        )
    )

    return {
        "meta": {
            "n_sides": n_sides,
            "n_regions": n_regions,
            "final_root": prover.root.hex(),
            "final_leaf_count": len(prover.leaves),
            "colors": REGION_COLORS,
        },
        "steps": steps,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Spatial Merkle · Visual Demo</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,650&family=Sora:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  :root {
    --ink: #1c2a33;
    --muted: #5b6b76;
    --wash0: #d9e3ea;
    --wash1: #eef3f6;
    --panel: rgba(255,255,255,0.72);
    --accent: #c45c26;
    --inside: #2f6f5e;
    --outside: #9aa7b5;
    --line: #24333d;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; min-height: 100%;
    color: var(--ink);
    font-family: "Sora", sans-serif;
    background:
      radial-gradient(1200px 700px at 12% -10%, #f7fbfc 0%, transparent 55%),
      radial-gradient(900px 600px at 100% 0%, #d7e7df 0%, transparent 50%),
      linear-gradient(165deg, var(--wash1), var(--wash0));
  }
  body {
    display: grid;
    grid-template-rows: auto 1fr;
    min-height: 100vh;
  }
  header {
    padding: 1.6rem 1.6rem 0.4rem;
    max-width: 1100px;
    margin: 0 auto;
    width: 100%;
  }
  .brand {
    font-family: "Newsreader", serif;
    font-weight: 650;
    font-size: clamp(1.8rem, 4vw, 2.6rem);
    letter-spacing: -0.02em;
    line-height: 1.05;
    margin: 0;
  }
  .sub {
    margin: 0.55rem 0 0;
    color: var(--muted);
    max-width: 40rem;
    font-size: 0.98rem;
    line-height: 1.45;
  }
  main {
    max-width: 1100px;
    width: 100%;
    margin: 0 auto;
    padding: 1rem 1.6rem 2rem;
    display: grid;
    grid-template-columns: 1.4fr 0.9fr;
    gap: 1.25rem;
    align-items: stretch;
  }
  @media (max-width: 860px) {
    main { grid-template-columns: 1fr; }
  }
  .stage {
    position: relative;
    border-radius: 0;
    min-height: 520px;
    background:
      linear-gradient(180deg, rgba(255,255,255,0.35), rgba(255,255,255,0.08));
    box-shadow: inset 0 0 0 1px rgba(28,42,51,0.08);
    overflow: hidden;
  }
  canvas {
    width: 100%;
    height: 100%;
    display: block;
    min-height: 520px;
  }
  .side {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 0.2rem 0;
  }
  .step-title {
    font-family: "Newsreader", serif;
    font-size: 1.55rem;
    font-weight: 650;
    margin: 0;
    line-height: 1.15;
  }
  .caption {
    margin: 0;
    color: var(--muted);
    line-height: 1.5;
    font-size: 0.95rem;
  }
  .meta {
    display: grid;
    gap: 0.35rem;
    font-size: 0.82rem;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }
  .meta strong { color: var(--ink); font-weight: 600; }
  .root {
    word-break: break-all;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 0.72rem;
    line-height: 1.35;
    color: var(--ink);
    background: rgba(255,255,255,0.55);
    padding: 0.55rem 0.65rem;
    box-shadow: inset 0 0 0 1px rgba(28,42,51,0.06);
  }
  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: auto;
  }
  button {
    appearance: none;
    border: 0;
    background: var(--ink);
    color: #f4f7f8;
    font: inherit;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 0.65rem 0.95rem;
    cursor: pointer;
    transition: transform 160ms ease, background 160ms ease;
  }
  button:hover { transform: translateY(-1px); }
  button.secondary {
    background: transparent;
    color: var(--ink);
    box-shadow: inset 0 0 0 1px rgba(28,42,51,0.35);
  }
  .legend {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    font-size: 0.8rem;
    color: var(--muted);
  }
  .swatch {
    display: inline-block;
    width: 0.75rem; height: 0.75rem;
    margin-right: 0.35rem;
    vertical-align: -1px;
  }
  .progress {
    height: 3px;
    background: rgba(28,42,51,0.1);
    margin-top: 0.4rem;
  }
  .progress > span {
    display: block;
    height: 100%;
    background: var(--accent);
    width: 0%;
    transition: width 280ms ease;
  }
</style>
</head>
<body>
  <header>
    <h1 class="brand">Spatial Merkle</h1>
    <p class="sub">
      Visual walk through of verifiable mesh transactions: cut region boundaries
      with <em>SplitTriangle</em>, then mark triangles <em>inside</em> or
      <em>outside</em> with <em>SetTriangleData</em>.
    </p>
  </header>
  <main>
    <section class="stage" aria-label="Mesh stage">
      <canvas id="c" width="900" height="720"></canvas>
    </section>
    <section class="side">
      <div>
        <h2 class="step-title" id="title">Loading…</h2>
        <div class="progress" aria-hidden="true"><span id="bar"></span></div>
      </div>
      <p class="caption" id="caption"></p>
      <div class="meta">
        <div><strong>Op</strong> · <span id="op"></span></div>
        <div><strong>Triangles</strong> · <span id="leaves"></span></div>
        <div><strong>Step</strong> · <span id="stepn"></span></div>
      </div>
      <div class="root" id="root"></div>
      <div class="legend">
        <span><i class="swatch" style="background:#2f6f5e"></i>inside</span>
        <span><i class="swatch" style="background:#9aa7b5"></i>outside</span>
        <span><i class="swatch" style="background:#5f8f78"></i>regions</span>
        <span><i class="swatch" style="background:#c45c26"></i>active cut</span>
      </div>
      <div class="controls">
        <button type="button" id="prev" class="secondary">Back</button>
        <button type="button" id="play">Play</button>
        <button type="button" id="next" class="secondary">Next</button>
      </div>
    </section>
  </main>
<script>
const DATA = __DATA__;

const colors = Object.assign({
  outside: "#9aa7b5",
  inside: "#2f6f5e",
  unassigned: "#c5ced6",
  unknown: "#b0b8c0",
}, (DATA.meta && DATA.meta.colors) || {});

const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");
let idx = 0;
let playing = false;
let timer = null;
let pulse = 0;

function project(step) {
  const pts = [];
  for (const t of step.triangles) for (const p of t.points) pts.push(p);
  if (step.center) pts.push(step.center);
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const [x,y] of pts) {
    if (x < minX) minX = x; if (x > maxX) maxX = x;
    if (y < minY) minY = y; if (y > maxY) maxY = y;
  }
  const pad = 0.08;
  const w = maxX - minX || 1;
  const h = maxY - minY || 1;
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;
  const scale = (1 - pad * 2) / Math.max(w, h);
  return (x, y) => {
    const nx = 0.5 + (x - cx) * scale;
    const ny = 0.5 - (y - cy) * scale; // y up in data → canvas down
    return [nx * canvas.width, ny * canvas.height];
  };
}

function draw() {
  const step = DATA.steps[idx];
  const to = project(step);
  const hi = new Set(step.highlight || []);
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // soft vignette grid
  ctx.save();
  ctx.globalAlpha = 0.22;
  ctx.strokeStyle = "#7f92a0";
  ctx.lineWidth = 1;
  for (let i = 1; i < 8; i++) {
    const x = (canvas.width / 8) * i;
    const y = (canvas.height / 8) * i;
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
  }
  ctx.restore();

  for (const t of step.triangles) {
    const p0 = to(...t.points[0]);
    const p1 = to(...t.points[1]);
    const p2 = to(...t.points[2]);
    ctx.beginPath();
    ctx.moveTo(p0[0], p0[1]);
    ctx.lineTo(p1[0], p1[1]);
    ctx.lineTo(p2[0], p2[1]);
    ctx.closePath();
    const base = colors[t.label] || colors.unknown;
    ctx.fillStyle = hi.has(t.i) ? shade(base, pulse) : base;
    ctx.globalAlpha = hi.has(t.i) ? 0.92 : 0.72;
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.strokeStyle = "rgba(28,42,51,0.55)";
    ctx.lineWidth = hi.has(t.i) ? 2.2 : 1;
    ctx.stroke();
  }

  if (step.cut_segment && step.cut_segment.length === 2) {
    const a = to(...step.cut_segment[0]);
    const b = to(...step.cut_segment[1]);
    ctx.strokeStyle = "#c45c26";
    ctx.lineWidth = 3.5;
    ctx.setLineDash([10, 7]);
    ctx.beginPath();
    ctx.moveTo(a[0], a[1]);
    ctx.lineTo(b[0], b[1]);
    ctx.stroke();
    ctx.setLineDash([]);
    // endpoints
    for (const p of [a, b]) {
      ctx.fillStyle = "#c45c26";
      ctx.beginPath();
      ctx.arc(p[0], p[1], 4.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  if (step.center) {
    const c = to(...step.center);
    ctx.fillStyle = "#1c2a33";
    ctx.beginPath();
    ctx.arc(c[0], c[1], 3.5, 0, Math.PI * 2);
    ctx.fill();
  }
}

function shade(hex, t) {
  // pulse toward white
  const n = parseInt(hex.slice(1), 16);
  let r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  const a = 0.18 * (0.5 + 0.5 * Math.sin(t));
  r = Math.round(r + (255 - r) * a);
  g = Math.round(g + (255 - g) * a);
  b = Math.round(b + (255 - b) * a);
  return `rgb(${r},${g},${b})`;
}

function sync() {
  const step = DATA.steps[idx];
  document.getElementById("title").textContent = step.title;
  document.getElementById("caption").textContent = step.caption;
  document.getElementById("op").textContent = step.op;
  document.getElementById("leaves").textContent = step.leaf_count;
  document.getElementById("stepn").textContent = `${idx + 1} / ${DATA.steps.length}`;
  document.getElementById("root").textContent = step.root;
  document.getElementById("bar").style.width = `${(idx / (DATA.steps.length - 1)) * 100}%`;
  draw();
}

function setPlaying(on) {
  playing = on;
  document.getElementById("play").textContent = on ? "Pause" : "Play";
  if (timer) { clearInterval(timer); timer = null; }
  if (on) {
    timer = setInterval(() => {
      if (idx >= DATA.steps.length - 1) { setPlaying(false); return; }
      idx += 1; sync();
    }, 1100);
  }
}

document.getElementById("prev").onclick = () => { setPlaying(false); idx = Math.max(0, idx - 1); sync(); };
document.getElementById("next").onclick = () => { setPlaying(false); idx = Math.min(DATA.steps.length - 1, idx + 1); sync(); };
document.getElementById("play").onclick = () => setPlaying(!playing);

function tick() {
  pulse += 0.12;
  draw();
  requestAnimationFrame(tick);
}
sync();
requestAnimationFrame(tick);
</script>
</body>
</html>
"""


def render_html(scenario: dict) -> str:
    payload = json.dumps(scenario, separators=(",", ":"))
    return HTML_TEMPLATE.replace("__DATA__", payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sides", type=int, default=36)
    parser.add_argument("--regions", type=int, default=5)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("docs/spatial-merkle-visual-demo.html"),
    )
    args = parser.parse_args()

    scenario = build_scenario(n_sides=args.sides, n_regions=args.regions)
    html = render_html(scenario)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"wrote {args.output}")
    print(
        f"steps={len(scenario['steps'])} leaves={scenario['meta']['final_leaf_count']} "
        f"root={scenario['meta']['final_root'][:24]}…"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
