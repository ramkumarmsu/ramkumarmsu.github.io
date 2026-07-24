# Kickoff Brief for Future Agent

Use this document as prior context. Prefer this brief over re-deriving decisions from scratch.
Full chat export (optional detail):
`docs/cursor_chat_county_weather_and_spatial_mesh.txt`
Longer planning notes:
`docs/spatial-merkle-mesh-planning-summary.md`

Repo: `ramkumarmsu/ramkumarmsu.github.io`
Branch with these docs/scripts: `cursor/county-weather-monthly-2b78`
User is a beginner with tooling; prefer plain language and concrete next steps.

---

## Track A — Monthly county weather script (mostly done)

### Goal
Local Python script to compute monthly averages of weather features for all counties in `county_list.csv`.

### Delivered
- Script: `scripts/get_monthly_weather.py`
- Features: `t2m,t850,t250,q250,tmax,r500,u850,u250,v500,r850,r250,v250,q850,v850,u10,v10,d2m,sp,SRO,tp`
- Source: Open-Meteo Historical Forecast API (`ecmwf_ifs025`)
- EDDI intentionally deferred / low priority
- Output: `~/Downloads/county_weather_monthly.csv`
- Supports `--latest`, `--month YYYY-MM`, `--start/--end`
- Resume-friendly; rate-limit pauses; default slower pacing

### How user runs it
```bash
cd ~/Downloads
pip install numpy
# put county_list.csv and get_monthly_weather.py in Downloads
python get_monthly_weather.py --start 2026-04-01 --end 2026-06-30 --pause 15 --batch-size 5
# later months:
python get_monthly_weather.py --latest
```

### Notes
- User hit HTTP 429 with older script versions; ensure they use the latest script
- Aggregation: most vars = mean of hourly; `tmax` = mean of daily maxima; `tp`/`SRO` = mean of daily totals (mm/day)

Only revisit Track A if user asks.

---

## Track B — Main ambitious project (active interest)

### Vision
A verifiable spatial system where land/features are represented as triangles, each triangle is a Merkle leaf, and a blockchain network maintains a committed root. Digitization of parcels, zones, utilities becomes incremental, attributable, and publicly checkable.

### Why it is useful
Not “GIS on chain for novelty.” Useful when maps allocate rights, money, liability, or access:
- shared multi-agency truth
- auditable history of boundary/attribute changes
- verifiable query answers without trusting the responder
- non-overlapping exclusive claims on a layer
- composability with permits/contracts/payments

### Geometry approach
- Start from county polygon shapefile
- Triangulate county interior
- Enclose in bounding box
- Triangulate exterior = box minus county
- Projection not required for parcel-scale point-in-triangle queries; lon/lat is acceptable
- Eventually constrain/refine triangles for parcels, zones, utility lines

### Cryptographic / chain model
**Leaf hash** = canonical ordering of 3 triangle points + associated triangle data  
(Fixed coordinate precision required.)

**Roles**
- Provers: agencies/utilities/surveyors/etc. who need to publish reliable data and produce proofs
- Verifiers:
  - blockchain nodes that validate updates and advance the root
  - end users who verify query answers against the root

**Design principle**
- Verification must be trivial
- Proving may be harder in theory, but should be made easy in practice via a prover library
- Prefer local incremental ops that preserve non-overlap by construction

**Initial ops**
1. `SplitTriangle(corner, point_on_opposite_edge)` → replace one leaf with two
2. `SetTriangleData(...)` → same geometry, update payload/authorship

Avoid arbitrary remeshing in the verifier path.

### Temporal boundaries (important practical issue)
Boundaries change over time (Louisiana coastal/river/thin geometries are a motivating hard case).
System must be a versioned spatial ledger:
- roots over time
- as-of-date queries
- later ops such as reassign / retire (land→water) / introduce (accretion), with authority rules

### Two software components to build together
1. **Prover library** (larger): mesh maintenance, splits, canonicalization, incremental Merkle tree, proof package generation, query proofs
2. **Compact verifier** (tiny): Merkle checks + tiny predicates + auth; small enough for trustworthy boundaries (chain runtime / TEE / auditor)

Do **not** put full GIS tooling inside the verifier.

---

## Current decisions / preferences
- No concrete implementation requested yet for Track B unless user asks to start building
- User wants collaboration on prover library + compact verifier eventually
- Keep explanations accessible; user is learning Cloud Agent workflow
- Saved artifacts matter; user had trouble finding past chats in UI

---

## Suggested next steps when user resumes Track B
Ask which they want first, unless already specified:

1. One-page MVP contract:
   - leaf byte layout
   - hash function
   - coordinate precision
   - exact split predicate
   - proof package format
   - “compact verifier” size/complexity criteria
2. Then implement verifier stub + prover library stub against that contract
3. Round-trip demo: genesis tiny mesh → split → data update → verify → query proof

If user asks to code, start with the MVP contract and the smallest end-to-end split/verify demo before county-scale meshing.

---

## Kickoff prompt template (user can paste)
```text
Read docs/agent-kickoff-brief.md in this repo (branch cursor/county-weather-monthly-2b78)
and continue from there.

My next goal:
<fill in>
```

Or with raw URL:
```text
Read this kickoff brief and continue from it:
https://raw.githubusercontent.com/ramkumarmsu/ramkumarmsu.github.io/cursor/county-weather-monthly-2b78/docs/agent-kickoff-brief.md

My next goal:
<fill in>
```
