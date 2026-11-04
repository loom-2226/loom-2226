# Wayfarer shuttle v1 integration: kT R1–R5 supersede widening preflight

ALL bodies. ALL sponsors. 2026–2226.

**DRAFT / NON-CANON / UNMERGED / RECERTIFICATION PENDING.**
**2026-11-03:** This record **supersedes the prior slot-widening STOP** in this PR. R1 keeps all certified Wayfarer structure, slot, tank, longerons, strakes and hot fins unchanged. R2 restores the shuttle to 3.8m diameter; R3 resizes the pod to 2.5m OD and 3 crew; R4 conserves total 3–6t entry TPS via assumed 1–2t core Mars shield plus derived extra Venus kit TPS; R5 uses the exact resized core midpoint.

## Exact new source and arithmetic

- Sizer draft: `research/shuttle-v1-resize-20261103` (separate unmerged PR). New input JSON Git blob `a1a8db40fb53ab889fa9bafbe52c299b7a5e529d`. Resized core **30.020646738t** = midpoint of each independent bound, not median of 6561 scenarios. Base TPS **1.5t** included in core; extra Venus TPS **3t** midpoint included in kit, total **4.5t** conserved.
- Current Wayfarer core **27.900000000t** → new **30.020646738t**; **+2.120646738t**.
- Reserve ledger: **11.284117000t** initial → **9.163470262t** after single core debit. Margin over **5t floor = 4.163470262t**. No new tank/slot/structure debit. The existing 19.662t of released longeron allocation is already distributed; not a second pool.
- Existing `ledger.venus_kit_t=1.7` is an obsolete non-booked annotation: builder and G1 do not use this field. **No 1.7t reserve credit** is taken. Kit actual midpoint **10.268750t** is PAYLOAD, not dry.
- Removable electrolysis+H₂/O₂ liquefaction plant **1–4t ASSUMPTION** booked to PAYLOAD, not dry. Combined kit+plant midpoint **11.26875–14.26875t**, leaving **35.73125–38.73125t** of rated 50t free payload, before any other cargo.
- `certify.py` G1 Option C historical reconciliation excludes the separately declared **2.120646738t** new shuttle debit; the frozen Option C amount and the >=5t floor are **not relaxed**. No other certification criterion is changed.
- Existing Wayfarer `shuttle.water_cap_t=23.1`, `max_trip_t=51.1`, `torch_gw=7.7` retained as pre-existing assumptions, **not proven consistent** with the resized sizer's water/propulsion envelopes. A successful full G1–G12 execution must catch any incompatible invariants.

## G8() static clearance, unchanged geometry and criteria

Source `wayfarer/lab/certify.py:g8`; shuttle radius **1.9m**; slot half-width **2.4m**, bore radius **2.4m**, shuttle length **12.8m**, bay x=18.25–32.05m, shuttle x=18.75–31.55m.

| Check | Actual m | Criterion m | Static outcome |
|---|---:|---:|---|
| Bore radial | 0.500000 | >=0.250 | PASS |
| Forward axial | 0.500000 | >=0.500 | PASS |
| Aft axial | 0.500000 | >=0.500 | PASS |
| Slot edge and opened doors | 0.500000 | >=0.500 | PASS |
| Upper sill longerons | 0.650000 | >=0.500 | PASS |
| Upper radiator strakes (40/140 deg) | 0.521390 | >=0.500 | PASS |
| Folded hot fins relative to slot edge | 1.045875 | >=1.000 | PASS |

**All listed nominal G8 static clearance equations PASS on paper.** This is NOT an executed `g8()` certification run or a fully qualified stowed envelope: the strake margin is only **0.02139m**, and the unchanged slot's exact 0.5m exit clearance leaves no allowance for rotor/hub, wheels, pod ramp, belly nozzles, door seals, or any hull protrusion. B stays OPEN until actual stowed geometry is known. KF stays OPEN until actual individual hold apertures, 3m hot-blade joints, and packed assemblies are demonstrated. G8 itself also includes hold free volume and transfer tunnel checks.

## Resized sizer deterministic gate fractions (6561 samples, min/mid/max; NOT probabilities)

| Gate | Old 4.3m | New 3.8m | Status |
|---|---:|---:|---|
| A full dry | 243/6561 = 3.704% | 486/6561 = 7.407% | Screen |
| A2 core dry | 4374/6561 = 66.667% | 5103/6561 = 77.778% | Screen |
| KV kit aggregate volume | 4860/6561 = 74.074% | 5103/6561 = 77.778% | Screen |
| KF physical kit fit | 0 PASS, 4860 OPEN | 0 PASS, 5103 OPEN | **OPEN/FAIL** |
| B physical bay/stow | 6561 OPEN | 6561 OPEN | **OPEN** |
| R rotor screen | 6561 PASS | 6561 PASS | Conditional |
| C ideal torch ascent water | 5589/6561 = 85.185% | 5670/6561 = 86.420% | Conditional |
| DS3 three-crew Venus surface | Not run | 2835/6561 = 43.210% | Conditional screen; **not qualified** |

**New kit** independent-component envelope min/mid/max: 4.925 / 10.26875 / 15.6125t (the sampled design observed 5.925–14.2625t); 3–6t old TOTAL entry TPS conserved through 1–2t CORE base and correlated 1–5t EXTRA. Pod shell, fittings, hull, chassis, door and gear mass rescaled with documented simple geometric ASSUMPTIONS, not certified designs. WHOI Alvin supports *three humans in 2.1m internal-diameter sphere* as precedent, not proof this 2.5m OD LOOM pressure sphere meets 92bar Venus external pressure, hot knockdown or required hatch/windows.

## Stage 3 worlds

All worlds share new A2 **5103/6561 PASS** (77.778%). Titan KIT_VOLUME **5103/6561**, ROTOR_MODEL_TOP **3645/6561** (55.556%); its FLIGHT_TOTAL remains OPEN/FAIL. Moon/Mars/Mercury A2_CHEM **5103/6561** each, but FLIGHT_TOTAL remains OPEN/FAIL due to electrolysis, cryo, physical and flight holds. Do not promote screens to certification.

## New Wayfarer G1–G12 certification status

**NOT EXECUTED.** GitHub content API can edit and verify branch source but does not execute the Python builder or produce the mandatory new deterministic geometry hash, `results/out` artifacts, renders and G1–G12 reports. Old main report/hash cannot be reused for changed shuttle mass and CG.

| Gate | Status | Required proof |
|---|---|---|
| G1 mass/fluid | PENDING RUN | Dry sum constant with reserve transfer; wet inventory; G1 historical Option C debit separation |
| G2 torch/performance | PENDING RUN | No reduction in full/empty mission delta-v, remass or 50t gross payload |
| G3 balance | PENDING RUN | Recompute seven state CG, inertia, torch thrust offset |
| G4 thermal/electrical | PENDING RUN | Unchanged ship heat; electrolysis draws house power only when scheduled |
| G5 structure | PENDING RUN | Unchanged geometry; resized shuttle restraint loads |
| G6 radiation | PENDING RUN | Unchanged protected water/shield |
| G7 habitat | PENDING RUN | Zero habitat volume loss |
| G8 shuttle exit | **NOMINAL STATIC PASS; FULL G8 PENDING RUN** | Unchanged criteria, tunnel/holds; full stowed B/KF remain OPEN |
| G9 failures/reserve | PENDING RUN | Reserve **9.163470262 >=5t**; all failure cases |
| G10 flight dynamics | PENDING RUN | New mass distribution/CG/inertia, one-cluster failure |
| G11 canon fit | PENDING RUN | Proposal-only amendment |
| G12 renders | PENDING RUN | New geometry hash and render checks |

**No new geometry hash or certificate claimed.** No habitat, slot, tank, longeron, strake, fin or performance criterion has been modified. Physical invariants are unqualified until executed and reviewed.

## Remaining blockers and explicit holds

1. Execute existing Wayfarer builder and `certify.py` on this branch, regenerate and inspect all artifacts, record actual G1–G12, CG/inertia, new hash, 50t payload and performance. **Do not merge until this exists.**
2. Produce physical 3.8m stowed-envelope/rover geometry: 2.5m sphere, chassis+wheels, mast/hub, folded blades, nozzle/gear, ramp, actual CG. G8's narrow strake clearance and 0.5m slot leave no protrusion margin.
3. Physically qualify KF apertures and blade joints; actual Venus kit mass/volume and cryogenic 1–4t electrolysis plant placement in payload.
4. BASE TPS 1–2t is an **ASSUMPTION** informed by NASA reference aeroshell fractions, **not** a NASA-specified shuttle design. Determine entry trajectories, aerothermal load, shell mass and whether 1–2t is credible.
5. KEEP OPEN: dense CO₂ torch, ascent trajectories, pressure-sphere buckling, world-specific surface thermal, Titan, electric belly alternative.

**No merge, no canon promotion.**
