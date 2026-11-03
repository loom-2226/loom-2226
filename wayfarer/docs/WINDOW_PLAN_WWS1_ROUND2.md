# WWS-1 round 2: Window plan, numerical certification, occupant views

ALL bodies. ALL sponsors. 2026–2226.

**DRAFT / NON-CANON / NOT FOR MERGE.** kT approved 2026-11-03; same branch/PR #465 based on PR #460.
Round-one baseline source SHA: 8b43d87dcb5fd8fe9e06e427e957db26dcc8671cbcb2aa28791e77c728384145
Round-two source SHA: 818f83de02e282aaad92dd9a326226eb3185ae69ab623ad8cb9d865fcf46c85a

## Corrected budget authority

The **12.0 t cap is the TOTAL NEW DRAW from structure_split.released_to_reserve**, not a cap on nominal installed window material. kT retired the erroneous 13.7 t installed-mass ceiling. Do not use it as a criterion.
The 1.7t historic Venus-kit annotation was never physically in the dry ledger and never creates reserve credit. The shuttle kit stays payload.

| Allocation (tonnes) | Round 1 | Round 2 additional | Round 2 final |
|---|---:|---:|---:|
| **New structural allocation committed** | 5.492216 | 4.631084 | **10.123300 / 12.0** |
| Remaining NEW draw headroom | 6.507784 | −4.631084 | **1.876700** |
| Released-to-reserve still uncommitted | 14.164784 | −4.631084 | **9.533700** |
| Engineering reserve (unchanged) | 9.163470 | 0 | **9.163470 >= 5.0** |
| **Combined uncommitted** | 23.328254 | −4.631084 | **18.697170 >= 16.8** |

Round-two increment: round ports **1.915491 t** + L2 band **2.715592 t** = **4.631084 t**. Round-one includes **0.060 t** G5 longeron material; no new second-stage longeron appropriation is counted until a demonstrated G5 overrun.
Full nominal installed WWS window assemblies: **13.322831 t → 17.953914 t** (booked WWS material-plus-frames and older physically retained frame allocations), but there is explicitly **NO installed-mass cap**.

## Every round port: room, old/new size, area, mass and local axial frame clearance

| Room / tier | x m | θ ° | Old Ø m | New Ø m | Old total t | New total t | Delta t | Area m² | Frame edge m |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L1-command | 1.25 | 45.0 | 0.50 | 0.50 | 0.1260 | 0.1260 | +0.0000 | 0.1963 | 0.500 |
| L1-command | 1.25 | 135.0 | 0.50 | 0.50 | 0.1260 | 0.1260 | +0.0000 | 0.1963 | 0.500 |
| L1-command | 1.25 | 225.0 | 0.50 | 0.50 | 0.1260 | 0.1260 | +0.0000 | 0.1963 | 0.500 |
| L1-command | 1.25 | 315.0 | 0.50 | 0.50 | 0.1260 | 0.1260 | +0.0000 | 0.1963 | 0.500 |
| L4-medical | 9.10 | 180.0 | 0.75 | 1.55 | 0.1834 | 0.5217 | +0.3383 | 1.8869 | 0.125 |
| L4-medical | 9.10 | 210.0 | 0.75 | 1.55 | 0.1834 | 0.5217 | +0.3383 | 1.8869 | 0.125 |
| L4-medical [NEW] | 9.10 | 240.0 | 0.00 | 1.55 | 0.0000 | 0.5217 | +0.5217 | 1.8869 | 0.125 |
| L5-suits | 12.45 | 50.0 | 0.45 | 0.45 | 0.1172 | 0.1172 | +0.0000 | 0.1590 | 0.225 |
| L5-workshop | 12.45 | 102.5 | 0.45 | 0.45 | 0.1172 | 0.1172 | +0.0000 | 0.1590 | 0.225 |
| L5-workshop | 12.45 | 147.5 | 0.45 | 0.45 | 0.1172 | 0.1172 | +0.0000 | 0.1590 | 0.225 |
| L5-vestibule | 12.45 | 270.0 | 0.40 | 0.40 | 0.1094 | 0.1094 | +0.0000 | 0.1257 | 0.250 |
| L3-CAPT / lower | 7.54 | 15.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.060 |
| L3-CA / lower | 7.54 | 75.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.060 |
| L3-CA / upper | 6.65 | 79.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.250 |
| L3-GUEST / lower | 7.54 | 169.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.060 |
| L3-GUEST / upper | 6.65 | 173.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.250 |
| L3-GUEST / lower | 7.54 | 221.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.060 |
| L3-GUEST / upper | 6.65 | 217.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.250 |
| L3-CB / lower | 7.54 | 259.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.060 |
| L3-CB / upper | 6.65 | 263.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.250 |
| L3-CB / lower | 7.54 | 311.0 | 0.50 | 0.80 | 0.1260 | 0.1977 | +0.0717 | 0.5027 | 0.060 |

The 10 berth windows enlarge **0.50 → 0.80m**. Upper-tier ports shift 4° in the direction that clears the fixed Metric faces and retain at least 0.10m between paired pressure cutouts. At 0.80m, the opening nearly fills the declared 0.82m tier height: the pressure-retaining rim must mount outward / within structural shell. **That physical clearance and pressure-seal durability remain OPEN.**
Medical: two existing 0.75m ports replaced with 1.55m ports and a **third 1.55m port added** at θ180/210/240 and x9.10. All round apertures must pass G5 principal frames / 0.10m hull-web separation and G9 crawler clearances.

## L2 galley and exercise glass, no other room intrusions

| Sector | Old x-range m | New x-range m | θ ° | New area m² |
|---|---|---|---|---:|
| Galley | 3.60–5.20 | 3.35–5.55 | 300–360 | 9.906 |
| Galley | 3.60–5.20 | 3.35–5.55 | 0–30 | 4.953 |
| Wardroom | 3.90–4.50 | 3.90–4.50 | 30–150 | 5.404 |
| Observation | 3.60–5.20 | 3.60–5.20 | 150–210 | 7.205 |
| Exercise | 3.60–5.20 | 3.35–5.55 | 210–270 | 9.906 |

Total L2 glazing **30.620056 → 37.374481 m²**; extended galley/exercise segments to x3.35–5.55, maintaining 0.05m room-end allowance. Other sectors and opaque washroom unchanged. Added local partial edge rings **0.558333 t** and two transoms **0.128000 t** to the existing frame model, plus scaled mullions and shutters. This is declared design mass, not local FEA pressure/vibration qualification.
G5 correction: the enlarged 2.2m ceramic plate span requires 19.1mm under the UNCHANGED source load/plate criterion. The old L2 study was still comparing an 18mm legacy plate; WWS-1 already physically books TWO independent 28mm pressure ceramics. The source pane_mm has been synchronised to 28/28mm, with zero added mass and no criterion relaxation. Independent failure and rim pressure qualification remain OPEN.

## Window/node/external-equipment clearances

- 208 existing Metric faces, placement authority **PR #184 HOLD**. New window/node overlaps: **0**. No node-face coordinates moved.
- Storm shelter L4 **ZERO** windows. Camera-only shuttle hull and three separately covered 92-bar-unqualified pod ports are unchanged.
- Source certifier G5 checks every round port against 2m-pitch axial frames, all round-port pair hull-web separation >=0.10m, and enlarged L2 sectors against room limits and node faces. G9 checks all external gear incl. crawler point #6. A geometric pass is not an independently proved pressure seal, FEM load path or particle transport model.

## G1–G12 exact-geometry certification

| Gate | Result | Failed source checks |
|---|---|---|
| G1 | PASS | None |
| G2 | PASS | None |
| G3 | PASS | None |
| G4 | PASS-DECLARED | None |
| G5 | PASS-DECLARED | None |
| G6 | PASS-DECLARED | None |
| G7 | PASS-DECLARED | None |
| G8 | PASS | None |
| G9 | PASS-DECLARED | None |
| G10 | PASS-DECLARED | None |
| G11 | PASS | None |
| G12 | PASS-DECLARED | None |
**G1–G12 PASS/PASS-DECLARED; no criteria relaxed.** PASS-DECLARED is a design screen, not hardware qualification.

**FQ1–FQ4 current-geometry matrix:** PASS_NUMERICAL. Check the source case counts in the linked FQ file.
- RCS_40S_CURRENT_TRACE.json: hash MATCH
- RCS_60S_DEGRADED_TRACE.json: hash MATCH

## Five occupant viewpoints

Each uses the same camera both rounds, source 3D geometry, shutters OPEN, and source-hashed render manifest.

| Occupant view | Round 1 BEFORE | Round 2 AFTER |
|---|---|---|
| berth | [Rendered](../render/wws1_round2/before_pov_berth.png) | [Rendered](../render/wws1_round2/after_pov_berth.png) |
| lounge | [Rendered](../render/wws1_round2/before_pov_lounge.png) | [Rendered](../render/wws1_round2/after_pov_lounge.png) |
| galley | [Rendered](../render/wws1_round2/before_pov_galley.png) | [Rendered](../render/wws1_round2/after_pov_galley.png) |
| exercise | [Rendered](../render/wws1_round2/before_pov_exercise.png) | [Rendered](../render/wws1_round2/after_pov_exercise.png) |
| medical | [Rendered](../render/wws1_round2/before_pov_medical.png) | [Rendered](../render/wws1_round2/after_pov_medical.png) |

### What remains unqualified

Large 2226 ceramic primary/backup pane independent failure, AOI shock coupling and optical/heat attenuation, per-cutout fatigue and pressure-seal FEM, movable Strata shutter/edge radiation transport, and emergency closing actuation. Every shutter CLOSED restores nominal local armour areal mass but no actual dose-transport qualification has been established. PR #184 node placement remains HOLD.
