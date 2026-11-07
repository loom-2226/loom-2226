# Phase 1b #471: G1 canon / RCS / G6 / D9 final kT STOP

ALL bodies. ALL sponsors. 2026–2226.

**STATUS: STOPPED on genuine D9 design failure. NO MERGE. NO TUNING. ZERO QUALIFICATION CREDIT.**

## Decision and source

The complete 2026-11-08 kT decisions and authorised work order are recorded **verbatim in draft upstream PR #471**.
Base main: ea50354e222e77d145a6bbbf49227506d2b560fd. Current source geometry SHA256: 88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1.

**Canon water was changed (kT-approved):** prior 300.000t water/250.000t normal remass to **295.3904317110822t** water / **245.39043171108221t** remass; protected water stays 50.000t. The former reference wet mass 1158.5t becomes 1153.8904317110823t. The precise original/new values and reason are in wayfarer/config/wayfarer_v05_inputs.json under canon.canon_change_2026_11_08. Physical reason: in-core 3.8t D–He3 and dry caps displace liquid, and G1 ullage = 5% of the water LIQUID volume, not 5% of tank. No propulsion tuning.

New normal S1 loaded mass = **1167.532687t**; ideal ECON = **707.845455km/s**, >700 and >G2 692.55. These are source mass screens only.

## Item 1: RCS replays, SAME design

The 40s and 60s trace scripts now take S1 remass from the current source inputs rather than hard-coded 250,000kg. No thruster, nozzle, controller, geometry or integrator modifications.
- 40s pitch reversal: 1458.634532kg water, 253.617502MW ideal peak power, attitude error 0.00161451°. Current geometry-hash MATCH.
- 60s degraded pitch reversal: 972.420432kg water, 112.720436MW ideal peak power, attitude error 0.000494564°. Current geometry-hash MATCH.
- Internal mass/reconstruction assertions passed. G4 power/heat PASS-DECLARED. Physical pulse conditioning remains OPEN.

## Item 2: G6 node-face/berth shielding

Fresh 36 berth points × 600 directions × 2cm S5 screen on current source geometry:
- Armour-equivalent node-face design: **41.67g/cm²** minimum, **0/36** below 40. G6 **PASS-DECLARED**.
- Node faces treated as actual open bores (worst sensitivity): **18.89g/cm²**, **29/36** below 40. Not the design configuration; requires genuinely armour-equivalent covers, seal and mounting, OPEN. These mass-column figures do not qualify dose/secondary transport.

## Item 3: D9 current-source exact B-rep, BLOCKED

Source-coded D9 uses the #156 pinned OpenCascade/build123d 0.13 shape conversion and collision triage, but converts **current branch** geometry rather than importing the #157 STEP. No automatic collision resolution.
- 296 dry source parts + 20 S1 fluid records. 122 explicit no_render/unlocated allocation proxies were excluded from installed fit credit and reported separately (~43.239t); their physical placement remains OPEN.
- **194** represented installed B-rep solids, **18,721** unique possible pairs scanned, **0** conversion/Boolean errors.
- **73 independent category-(d) volumetric collisions >0.01m³; limit ZERO. D9 FAIL.**
- Real examples: service_arm ↔ tunnel_0 2.940531m³; frame_34 ↔ manifold 1.536427m³; service_arm ↔ docking_collar 1.369856m³; each of floor_L2/L3/L4 ↔ core_racks 0.618360m³; service_arm ↔ strake_220/320 0.539177m³ each; jacket_outer ↔ jacket_ceiling/floor 0.424115m³ each.
- Complete conflict list: wayfarer/results/out/D9_BREP_CLASH_REPORT.json. Reproducible strict failure GitHub Actions run: https://github.com/loom-2226/loom-2226/actions/runs/42427209439.

**Root cause:** The first upstream packing integration transferred source envelope positions but not all research candidate's D8 secondary-notched/trimmed installed solid geometries. The frozen #157 B-rep candidate was zero-clash, but its result is NOT source #471's D9. A primary frame cannot be notched to fix a manifold overlap without a new kT decision. This is an actual design/integration failure, not stale evidence. STOP without editing geometry or auto-cutting equipment.

## Items 4–5: full certify.py on this branch

The existing script ran to completion with the new G1 canon, updated RCS traces, fresh G6, real D9 evidence. Note: this legacy CLI returns exit code 0 even when gates fail; the machine report explicitly says **certified=false**.

| Gate | Verdict | Evidence / limitation |
|---|---|---|
| G1 | **PASS** | 49/49 ledger checks; physical 295.390t water canon updated. |
| G2 | **PASS** | ECON 707.845km/s; no performance tuning. |
| G3 | **PASS** | All 19 analytic balance/attitude checks, seven-state numeric screen. Real control qualification OPEN. |
| G4 | **PASS-DECLARED** | 48/48 power/heat checks, both new RCS current-hash traces. |
| G5 | **PASS-DECLARED** | 37/37 numerical/declared structure checks; actual D8 doubler fitting still OPEN. |
| G6 | **PASS-DECLARED** | 31/31 checks; fresh node-face 41.67g/cm² minimum. |
| G7 | **FAIL** | 17 downstream I4 human-factors checks tied to stale geometry hash 274e94fb... vs current 88ce19fc..., requires new evidence. |
| G8 | **PASS** | 13/13 source checks; zero geometric margins/dynamic launch sweep OPEN. |
| G9 | **PASS-DECLARED** | 13/13 source failures/reserves checks. |
| G10 | **PASS-DECLARED** | Once checkout included src/ (test dependency), full G10 tests ran. Original incomplete sparse-checkout result was not authoritative. |
| G11 | **PASS** | Current updated canon fit. |
| G12 | **OPEN** | Old image/render manifests and cutaways not regenerated to new hash. |
| **D9** | **FAIL** | 73 category-(d) clashes where zero permitted, no CAD tool errors. |

Evidence: wayfarer/results/out/certification_report.json and CERTIFICATION_REPORT_v0.5.md. Geometry/input SHA stored in report and checked against D9. This is numerical and declared conventional screening, not hardware flightworthiness.

## Resolved source changes vs remaining work

**Source changes/replays complete:** approved D–He3 3.8t and 0.1t house allocation; four conformal lobes; forward courier sector; protected water redistribution; G1 canon water reference with reason; fresh 40s and 60s RCS traces; full G6 node-face screen; real D9 acceptance rule; full certify report.

**OPEN:** 73 D9 real collisions; actual D8 cutouts and fitted doublers; primary protected G5 load paths; source 5.870m³ unlocated tank webs/baffles; cryogenic walls/insulation/lines; 19.45t courier exterior mount/MMOD/1300K strake exposure; seven-state physical RCS validation; true G8 dynamic zero-margin sweep; G7 I4 source-hash human-factors re-evidence; G12 images/viewer rehash; secondary radiation/dose. No qualification credit.

**Stop condition reached. PR #471 DRAFT, UNMERGED, and cannot be approved for merge. kT decides the next geometry correction scope.**
