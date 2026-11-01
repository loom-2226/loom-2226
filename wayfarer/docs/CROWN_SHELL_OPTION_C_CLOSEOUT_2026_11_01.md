# Wayfarer Option C close-out, 2026-11-01

ALL bodies. ALL sponsors. 2026–2226.

Status: ENGINEERING / draft PR #439 / NOT MERGED. Selected Option C outer shell, pressure dome and AOI independent-failure physical proof still OPEN.

## Geometry and source

New geometry SHA256 447c05ccb7a3031823e0713ee6010eaa200dbb4c1635b8a5c747b7cd98dae6a6. External tip 1.2m forward of Rev7, flat r<=2m, 50 degree slope r2–3.5m, fairing into shoulder at 4.5m; ship overall ~54.5m. Existing two independent 7m ceramic pressure domes and 3.023m3 AOI unchanged.
37 independent outer 10mm sacrificial ceramic panes, 37.5kg/m2 (3.75g/cm2), original rings [0,.75,2,2.75,3.5], outer band pi/12 stagger. Four types, 7 reserve-funded hold spares [1,2,2,2]; outward removable retainers from external side while L1 stays pressurised, mechanics unqualified.
16 Strata gores cover 52.887838m2 true faceted face with 27g/cm2 closed; gross 14.279716t, previous projected armour allocation 10.390818t; incremental +3.888898t from reserve. Hinged/tambour transition over r2 and 50-degree seam unqualified. Crown-open quantitative speed and angle thresholds not specified; the older low-speed / bow-away-from-flow doctrine governs.

## Exact G1 reserve reconciliation

| Reserve item | Tonnes | Ledger bucket |
|---|---:|---|
| Extra Strata gore faceted area | 3.888898 | crown_option_c_additions_t |
| Outward removable retainers | 0.120000 | crown_option_c_additions_t |
| Seven spare 1cm outer panes | 0.385772 | crown_option_c_additions_t |
| Two pressure hatches at 0.15t each | 0.300000 | crown_option_c_additions_t |
| Recorded Option C explicit | 4.694670 | crown_option_c_additions_t |
| True-slope extra outer ceramic | 0.540125 | i4_carryover_t delta |
| L3 dry radiation liner (observed G6 correction) | 0.600000 | l3_berth_shield_liner_t |
| TOTAL reserve consumed | 5.834795 | three ledger buckets |

Previous reserve 17.786216t; remaining reserve 11.951421t. No mass discrepancy: 1.140125t gap is panes 0.540125t + liner 0.600000t, both elsewhere in ledger. G1 tests actual mass, three-bucket sum and previous reserve separately.
Total dry ship mass 867.681453t; S1 departure 1167.681453t. CG and inertia recomputed with hatch and all other source components.

## L1/L2 real pressure hatches and bounded egress

Two distinct 0.15t pressure hatch parts include nominal hinges, seals, frame and latch. Each has a 0.92m full square leaf, and its CLOSED state covers a 0.8m ladder opening for L1/L2 pressure isolation. OPEN leaves swing upright next to shafts to avoid seated crew and ladder obstruction; no extra dry mass or phantom equipment.
G7 checks both accessible shafts, connected floor region and the existing 2.0m x 0.60m x 0.35m litter end-first down an open 0.8m x 0.6m shaft at zero g only (0.05m margin). Two-way seal proof, actuator fault behaviour and physical casualty retrieval NOT qualified. Under thrust, treat in couch; transfer only after commanded coast.
G7 14/14 PASS source-layout screening.

## Qualification and images

G6 complete 36×600-ray S5 screen min 40.45g/cm2 with 0 rays below 40.0; open-node-face sensitivity 15.79 unsafe. AOI impact and shielding credit remains zero.
G12 31 source-hash-stamped exterior/interior/deck/section/viewer entries; to-scale crown PNG and SVG, plus source-hash-stamped exterior/interior GLB. Render claims do not establish transparent ceramic optics.
FQ1–FQ4 78/78 fresh conventional numerical manoeuvres PASS at dt=0.2s on revised CG and inertia; full and half propellant. FQ5–FQ10 not rerun on this geometry, Metric arrival HOLD, Navigator EXCLUDED.

| Gate | Result |
|---|---|
| G1 | PASS |
| G2 | PASS |
| G3 | PASS |
| G4 | PASS-DECLARED |
| G5 | PASS-DECLARED |
| G6 | PASS-DECLARED |
| G7 | PASS-DECLARED |
| G8 | PASS |
| G9 | PASS-DECLARED |
| G10 | PASS-DECLARED |
| G11 | PASS |
| G12 | PASS-DECLARED |

Machine certified=false; 18/29 declared kT ACCEPTED; 11 pending. kT approved Option C exterior choice, not physical pressure/damage qualification.

## Outstanding declarations
- crown_option_c_load_paths: Full faceted nose 1.2m ahead of old bow and gore hinges at 50deg break; actual retaining loads, impact, thermal cycling, 5g attachment paths and shutter transition mechanics UNSHOWN.
- l1_l2_pressure_hatches: Two new 0.15t pressure hatches at existing L1/L2 0.8m ladder wells: mass and parked clearance checked, seal under full differential, latch actuation and 4g crew passage NOT demonstrated.
- crown_option_c_gore_fairing: 16 Strata tambour gores cover the full r<=3.5m faceted external 50deg profile at 27g/cm2 when closed; 2m flat/slope hinge transition and shoulder fairing have no measured shock/seam/drive failure qualification.
- l3_shield_liner_material: Observed G6 two rays at 39.86g/cm2 corrected by reserve-funded 0.6t continuous L3 dry foamed high-hydrogen liner (x5.9-8.2,r4.18-4.25). No water moved and no gel radiation credited. g/cm2 mass/geometry screen only: polymer composition, actual charged-particle transport, structural attachment, fire and dose remain UNSHOWN.
- crown_option_c_tiles: 37 independent ceramic 1cm sacrificial tiles, outward-removable retainers while L1 pressure stays sealed. Four types, seven spares in hold. Cupola precedent establishes separable outer debris panes, NOT service tool loads or 2226 particle impact protection.
- crown_dome: Rev7 16 closing Strata gores and opening doctrine are retained; their original acceptance applied only to the earlier segmented 2.3m pressure panes, not the new 7m seamless dome.
- crown_monolith_7m: kT Option A 2026-11-01: TWO independent full-pressure ~7m transparent ceramic domes, each 28mm/10.5g/cm2, shaped X(r)=2.35-2.15sqrt(1-(r/4.3)^2), backup shifted 0.12m forward. Both must survive loss of the other; 37 outer segmented nonpressure panes +16 closure gores unchanged. 7m monolithic materials fabrication/pressure/impact and optical radiation behaviour UNSHOWN.
- aoi_failure_independence: AOI-2226 ~3.023m3 (~3t) gel between two separately sealed pressure domes, gap min normal 5.973cm with backup axial offset ~12cm. Neither pressure-bearing nor a pressure seal. Each independent dome MUST withstand full 101.3kPa after other's failure while optogel is present, WITHOUT shock, fracture, crack bridging or fast pressure-pulse coupling. The research has NO measured high-rate response or independent-shell survival test; do not credit impact damping. Rim slip/contact interfaces and >=56L illustrative thermal-expansion compliance still require engineering.
- crown_option_c_open_limit: Option C crown-open limit surfaced in 3D viewer as proposed max speed and/or bow-to-flow angle; BOTH numeric thresholds default UNQUALIFIED. Existing doctrine remains governing (low speed OR bow out of dust flow; closed for torch, radiation, Metric). Sensor accuracy, failure-mode logic and numeric dynamic threshold still OPEN.
- crown_option_c_axial_rcs_plumes: External nose shifted 1.2m forward with flat 2m crown and 50deg face. Old accepted G10 axial RCS plume direction/impingement declaration predates the extended nose; no new plume clearance proof performed. The existing RCS nozzle geometry is unchanged, but plume impingement on Option C gores/ceramic/retainers remains HOLD.
- kT_visual_acceptance: Required before treating rendered representation as accepted design evidence; generated images meet source/hash coverage only

## Current images
- render/out/deck_crown_option_c_section.png
- render/out/ext_hero.png
- render/out/crown_open.png

DO NOT MERGE before kT acceptance and GitHub loom-gate pass.
