# Shuttle v1 × Wayfarer — integration preflight / STOP record

ALL bodies. ALL sponsors. 2026–2226.

**Class: engineering-integration research / DRAFT / NON-CANON. kT APPROVED investigation 2026-11-03.**
**Disposition: STOP before modifying governing Wayfarer geometry/config or claiming certification.**
**Why:** the 4.3 m shuttle fails three *existing* G8 exit-path obstacles after merely widening the slot. The base Mars shield mass is not split from the Venus TPS in the merged sizer, and the 5 t reserve floor cannot be demonstrated with the required changes. No criterion may be weakened. No habitat, performance or canon mutation permitted.

## Live authority and fixed decisions

- Base: `loom-2226/loom-2226` current `main` at branch creation. Source `wayfarer/config/wayfarer_v05_inputs.json`, `wayfarer/config/cert_criteria.json`, `wayfarer/lab/{build_v05.py,certify.py}`, merged `wayfarer/lab/shuttle/{shuttle_inputs.json,SHUTTLE_SIZER_REPORT.md,SHUTTLE_STAGE3_WORLDS_REPORT.md,OPEN_ITEMS.md}`. Shuttle baseline was merged through #458 at `7c6b9b42`; v1 *research*, not mission qualification.
- D1 widen the lateral exit slot so `path_clearance_min_m=0.50` for 4.30 m shuttle. Do **not** alter that 0.50 m criterion or the 0.25 m bore radial criterion.
- D2 exact **31.825 t** as the already-merged sizer's pre-reclassification midpoint A2 core, replacing **27.900 t** existing Wayfarer input; delta **+3.925 t**. The new core **cannot** remain 31.825 t after shifting additional TPS from kit unless an equal amount of existing core mass is demonstrably removed.
- D3 assign the base Mars entry-TPS portion to core, only extra Venus protection to detachable Venus/Titan kit. **STOP:** the merged sizer has only *one combined* `entry_tps_t` range **3.0–6.0 t** (mid **4.5 t**) wholly tagged KIT. There is **no accepted base-versus-extra split**. Do not invent one or count a shield twice.
- D4 Wayfarer electrolysis+LH2/LOX plant **1–4 t ASSUMPTION**, removable mission module counted in **PAYLOAD**, not dry; uses declared twin 50 MW net house reactors. Plant hardware, processing duty, storage and transfer remain unqualified. Payload-accounting intent only, no invisible extra 1–4 t of dry mass.

## Step 1: necessary shuttle geometry, no false B/KF closure

The G8 full-envelope gate **B remains OPEN**. Sizer inputs intentionally leave `mast_stowed_extra_diameter_m`, `hub_axial_length_m`, `crew_pod_x_m`, `rotor_mast_x_m`, `rotor_retracted_cg_m` and `pod_door_ramp_external_excursion_m` null. A notional viewer in draft #459 is *not* accepted 3D engineering geometry. Needed: actual mast/hub hinge length/diameter, folded 12 m rotor roots, four blade paths and spine groove, full pod/chassis/nozzle envelope, pod x and all-phase CG, door/ramp collision envelope and nose/pressure-transfer clearances.

The core **4.30 m** nominal cylinder inside the **4.80 m** bay bore yields **0.250 m** radial gap, exactly the certification minimum; not an allowance for any protruding mast, blades, belly nozzles or landing gear. Axial 12.80 m shuttle in 13.80 m bay has exactly 0.500 m per end in the present dock location. The unqualified mass/CG and geometries preclude B PASS.

The **KF physical kit-fit gate remains OPEN/FAIL conditional on volume**. The separately charged Venus/Titan kit ranges **6.925–16.6125 t** in the merged sizer, charged to up-to-50 t mission payload, not docked shuttle dry. The current holds occupy x=14–17 m; outer hatch features are **2.4×1.8 m**; 3 m blade segments and finite-width hot-gas joints are not proven to pass aperture, clearance, bend routing, pack volume or reassembly. Existing numerical KV aggregate-volume PASS is not KF physical PASS.

## Step 2: G8 clearance, tank and reserve feasibility

### D1: static G8 exit-path equations at the proposed 2.65 m slot half-width

Using exact `wayfarer/lab/certify.py:g8` source geometry with shuttle radius 2.15 m:

| Obstacle | Available (m) | G8 required (m) | Result |
|---|---:|---:|---|
| 4.8 m bore radial | 0.250 | 0.250 | PASS, **nominal hull only** |
| +Z slot edge and door at y=2.65 | 0.500 | 0.500 | PASS, **nominal hull only** |
| Sill longerons at |y|=2.75 with 0.4 m tube | 0.400 | 0.500 | **FAIL by 0.100** |
| Two upper strake envelopes, 40°/140° | 0.271390 | 0.500 | **FAIL by 0.228610** |
| Hot-fin fold corridor after widened slot | 0.795875 | 1.000 | **FAIL by 0.204125** |

**STOP**: changing `tanks.slot_half_width_m` and `bay.slot_half_width_m` to 2.65 m alone cannot certify G8. Proposed mitigations would move/reshape upper longerons, strake grooves/roots and fin root/stack, and require structural, heat and G10 performance recertification. No such redesign has been chosen or booked.

### Tank volumetry, reproduced from the active 300×1440 deterministic CSlot polar-midpoint algorithm and plate-sizing equations

| Quantity | Current hw=2.40, L=13.500 | Candidate hw=2.65, L=13.500 | Candidate hw=2.65, L=14.012791 |
|---|---:|---:|---:|
| Cross-section gross m² | 24.258575 | 22.938035 | 22.938035 |
| Gross tank m³ | 327.490764 | 309.663469 | ~321.425 |
| Structural displacement m³ | 5.870097 | 6.172303 | 6.425883 |
| **Net tank m³** | **321.620667** | **303.491167 FAIL** | **315.000000 (calculated boundary)** |
| Tank structural panel mass required t | 18.288662 | 18.426124 | 19.285156 |

Widening alone costs **17.827295 m³ gross / 18.129501 m³ net**. A **+0.512791 m** tank extension restores *exactly* 315 m³ under this analytical geometry and pressure-panel model, before full-build clearance/CG verification. The tank panel requirement increases **0.996494 t**; whether the current 32 t tank-shell/C-tank penalty allocation can absorb this must be verified without double-counting. If the entire ship's midship is lengthened at active **2.632 t/m**, the separate ship structure *line* implies about **1.349665 t**. The rear electrical ring, bulkheads, nozzle, fins, door, radiator and hull stations must be relocated consistently. Do **not** simply extend tanks from x=31.5 into the pre-existing x=31.5–32.3 aft electrical C-ring: it houses existing declared hardware and is not an empty volume.

Exactly 315 m³ is **not** a design margin. The full builder and G1 must show >=315 with geometry actually adopted.

### Reserve ledger: cannot declare a compliant integration without D3 split and structural accounting

The live ledger field `ledger.engineering_reserve_t` is **11.284117 t** (kT's ~11.3 t). The separately reported builder `ledger_reserve_t=30.946117 t` also includes **19.662 t of old structure reallocation already distributed into dry parts**, NOT a second pool of unassigned reserve. The builder inflates every dry part by the reserve spread factor; e.g., existing input shuttle 27.900 t becomes a **29.00005 t** geometry part. Account for this when rebalancing, do not silently equate the two physical values.

| Debit / milestone | Engineering reserve t | Status |
|---|---:|---|
| Live starting unallocated reserve | **11.284117** | Above 5.0 |
| D2 declare pre-TPS core 31.825 vs 27.900, nominal delta 3.925 | **7.359117** | Provisional accounting, before builder spread |
| Proposed +0.512791 m × 2.632 t/m structure line, if spent from reserve | **~6.009451** | Provisional; cannot certify geometry or performance |
| If 0.996494 t extra tank panel is **also** a separate reserve debit | **~5.012957** | Barely above floor; **do not double-count if absorbed by allocated tank-shell line** |
| D3 move full 4.500 t midpoint TPS allowance to core, **illustration only** | **~1.509451** without extra tank-panel debit, or **~0.512957** with it | **FAIL <5.0** |
| D3 move 3.000 t of existing TPS to core, **illustration only, NOT kT split** | **~3.009451** without extra tank-panel debit, or **~2.012957** with it | **FAIL <5.0** |
| D4 removable electrolysis+liquefaction module 1–4 t to payload | **No direct engineering reserve debit** | Payload volume, attachment, power/cryogenic safety and remaining cargo checks OPEN |

To retain the 5.0 t floor after D2 + midship structural line, *every additional reserve debit* (base heat shield **plus** added door/fins/longerons/tank panel if not already covered) must total **<=1.009451 t**. If tank-panel increment must also be separately paid, only **~0.012957 t** remains. Because the base TPS split and geometry-obstacle redesign masses are undefined, **neither the floor nor unchanged performance can be certified**. No extra mass may be hidden in existing 55 t electrical or 50 t payload line without an identified tradeoff.

Full TPS reclassification in the *current sizer* would make the midpoint docked core **36.325 t**, over G8's 34.2 t nominal sizer limit, and change resolved A2 fraction from 4374/6561 (66.667%) to **1701/6561 (25.926%)**. Moving an illustrative fixed 3 t to core gives **34.825 t midpoint** and **2187/6561 (33.333%)** A2 PASS. Neither split is accepted: these are non-authoritative *sensitivity checks* that prove a need for D3 mass clarity and A2 rerun.

The detachable Venus/Titan kit **6.925–16.613 t** plus a **1–4 t** Wayfarer-owned mission plant would use **7.925–20.613 t** of the 50 t rated payload in missions loading both, leaving **29.387–42.075 t** of other free cargo by mass. Rated total cargo is unchanged; **unrestricted 50 t extra free cargo** is NOT preserved. This does not imply a dry-mass debit for the plant.

## Step 3: required G1–G12, *not* falsely rerun

The old `main` report's G1–G12 PASS/PASS-DECLARED applies to the **old** inputs and frozen geometry hash `4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331`, **not** to proposed integration. No governing config, criteria or geometry artifact was changed after identifying necessary G8 and reserve blockers. Therefore there is **no new geometry hash, no new G1–G12 certificate**.

| Gate | Existing main | Integration status / why cannot claim PASS |
|---|---|---|
| G1 mass/fluid ledger | PASS | NOT RUN; reserve floor and base TPS transfer unresolved, tank must stay >=315 m³ |
| G2 torch/reach | PASS | NOT RUN; no total wet mass or performance change allowed |
| G3 balance/attitude | PASS | NOT RUN; pod, reactor, mission payload and extended midship shift CG |
| G4 power/heat | PASS-DECLARED | NOT RUN; Wayfarer 2×50 MW electrolysis, peak load and source availability; no extra credited power |
| G5 structure/loads | PASS-DECLARED | NOT RUN; sill longerons, tanks, shell/door and fin mounts require relocation/resizing |
| G6 radiation | PASS-DECLARED | NOT RUN; no protected-water/habitat loss or unapproved shield mutation |
| G7 crew/habitat | PASS-DECLARED | NOT RUN; must demonstrate **zero habitat volume or access loss** |
| G8 shuttle/bay/exit/holds | PASS | **STATIC PREFLIGHT FAIL** at longerons, strakes, fins; KF and complete shuttle stowage OPEN |
| G9 failures/reserves | PASS-DECLARED | NOT RUN; unallocated engineering reserve >=5 t unproven after D3 and repairs |
| G10 dynamics | PASS-DECLARED | NOT RUN; new geometry/CG/inertia and lost-strake/fin cases required |
| G11 canon fit | PASS | NOT RUN; existing §3 and §6 proposed canon refer to old rover-drop shuttle |
| G12 renders | PASS-DECLARED | NOT RUN; existing render outputs and SHA belong to old design |

**No acceptance criterion has been relaxed. No full recertification result is implied.**

## Step 4 / STOP decision needed

- **D3 TPS split:** How much of the merged 3.0–6.0 t entry TPS is reusable Mars CORE protection? Exactly how much additional Venus/Titan TPS remains PAYLOAD? Re-run A2 and G8 34.2t after that split, preserving mass once.
- **D1 actual obstruction layout:** Authorize a specific minimal longerson/strake/fin geometry that maintains 0.50 m G8 exit path, 1.00 m fin corridor and original heat/structure/flight performance. A 2.65 m slot is a *candidate*, not an adequate solution on its own.
- **Reserve and structure:** Decide how the 0.996 t extra tank-panel requirement is paid and whether new aft-ship structural length draws 1.350 t from reserve. Demonstrate >=5 t after **all** new hardware, including doors and longeron work, without using the already-distributed 19.662 t twice.
- **D4 plant:** Confirm whether reduced **free mission cargo** when carrying the removable 1–4 t plant is acceptable within the rated 50 t payload, and where its real envelope/power/cryogenic interfaces fit.

**Explicit preserved holds:** Venus dense CO₂ torch ignition/handover, full ascent Δv and trajectories, 2.8 m pressure sphere and buckling, world-specific surface thermal, Titan rotor/atmosphere, and electric-water belly GW tap. All remain OPEN.

**STOPPING CONDITION ACTIVATED (pre-integration feasibility):** existing D1 candidate fails strict G8; an illustrative physically meaningful D3 base-shield transfer breaches the 5 t reserve floor. The missing D3 split forbids picking a compliant mass out of thin air. Stop before implementing a knowingly failing design. Provide this report and draft proposal for kT; do not merge, rebaseline, or promote to canon.
