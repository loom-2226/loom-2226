# Wayfarer Step 1b stale-evidence clearance — 2026-10-31

ALL bodies. ALL sponsors. 2026-2226.

**Reference:** Step 1 locked geometry SHA256 `92905754eec2cae2ea50083803b419c830de7849ef69194e3a863c8a8efa03f1`, on draft PR #435. **Geometry is byte-identical.** No new build, renders, Navigator or Metric work. Non-governing engineering checks, not hardware certification.

| Gate | Step1 verdict | Step1b verdict | Basis |
|---|---|---|---|
| G5 | FAIL | PASS-DECLARED | Four lowered-terrace 7075-T6 76mm OD × 3mm members, 0.49m length; 7.5g ultimate + 0.5g lateral |
| G6 | FAIL | PASS-DECLARED | Full 600-direction, 2cm radiation overlay on this geometry; armour-equivalent face rule |
| G7 | FAIL (stale) | FAIL (current substantive design findings) | New I4 checks with geometry hash, no reuse of layout D |
| G12 | FAIL | FAIL | Old image provenance; rendering explicitly prohibited |

## G5 nominal members
Two 100kg suited occupants, two 50kg seats, 300kg terrace and 20kg displays: 0.62t carried by four columns. Axial load 11.40kN/column, 16.57MPa axial stress, 39.69MPa combined under 0.5g transverse side load; 503MPa nominal yield, 1,353.04kN Euler buckling, buckling factor 118.68 vs required 1.5. Four tubes weigh 0.004926t versus original reserved 0.016839t. **Only column members pass**. Ends, base-plate/bearing, local floor, redundancy, 4g dynamic occupancy, and whole terrace access remain HOLD.

## G6 radiation
The fully rerun `habitat/hab_overlay_checks.py` tested 36 berth sample positions, 600 directional rays, 0.02m step, state S5. Minimum armour-equivalent node-face case **40.38g/cm²**, zero below 40; open-bore sensitivity minimum **14.78g/cm²**, 30/36 below 40. Face coverage must restore equal-or-greater areal density; exact node placement remains HOLD PR #184. Radiation is model evidence, not a full transport/dose qualification.

## G7 I4 source-frame findings
Fresh `command/l1_i4_checks.py` is explicitly bounded: sampled crown **upper bounds** omit Osteon ribs/obstacles, floor corridor samples use 0.1m grid and 0.4m half-width; ladders are plan-reference checks, no certified transfer mechanism.

- Six roles, two preserved ladder landings and Pilot/Captain *unobstructed* 60-degree crown upper bounds: pass at this screen's limited fidelity.
- All six presented seat envelopes 1.58m, short of source 2.10m 99th-percentile elongated-body requirement: **FAIL**.
- S4 radial outer foot and half-width exceeds r=4.15m annular floor limit: **FAIL**.
- Conservative 0.8m floor corridor to S4 inaccessible: **FAIL**.
- Raw dome axial headroom at worst terrace corner **1.339m**, not 2.10m standing: **FAIL**.
- Optional symmetric 0.5m chamfer of the two outboard forward terrace corners raises modeled worst shell clearance to **1.473m** (+0.135m), still below 2.10m; **NOT incorporated** in hashed geometry, mass, CG or inertia.

Couches, pressure shell/seat accommodation, real sightlines, raised platform transfers, handholds/egress and corner swept geometry remain open. G7 is now a current substantive failure, not a stale result.

## Status
G1 PASS; G2 PASS; G3 PASS; G4 PASS-DECLARED; G5 PASS-DECLARED; G6 PASS-DECLARED; G7 FAIL; G8 PASS; G9 PASS-DECLARED; G10 PASS-DECLARED (legacy certification routine only; no new Navigator/Metric work); G11 PASS; G12 FAIL.

`certified=false`. Draft/HOLD PR remains draft. No gate fabricated.
