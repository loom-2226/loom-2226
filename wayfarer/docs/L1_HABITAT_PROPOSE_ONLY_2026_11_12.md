# Wayfarer L1 Command Commons: F4 proposal only (12 Nov 2026)
**ALL bodies. ALL sponsors. 2026–2226.**

**kT APPROVED L1 layout 2026-11-12.** This remains the source sketch, with separate GLB / D9 / containment evidence required. Exterior release remains `canon-v2.5.14`.

## Authority and bounds
- `wayfarer/config/kt_decisions.json`: `standing_exterior_rules_F1_F4_2026_11_10.rules.F4`; `design_decisions_2026_10_31.L1`; `design_decisions_2026_10_31.L1_human_factors_step1c`; `decisions.i4_human_factors`, `decisions.l1_l2_pressure_hatches`, `decisions.shelter_life_support`, `decisions.habitat_changes_v057`.
- Source geometry: `wayfarer/results/out/wayfarer_v05_geometry.json`, SHA-256 `88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1`. Source I4 lock says `CANDIDATE_LOCK_STEP1_NON_GOVERNING`, not a new hardware qualification. Current bounded screen: `wayfarer/lab/command/l1_i4_results.json`.
- L1 room window/crown geometry already booked; do not reopen accepted 37 outer panes / twin dome / 16 Strata gores.
- Mass bookkeeping unchanged: dry `868.1922552640087 t`, ECON `707.845 km/s`.
- Source coordinate frame: −X is bow, Y/Z are transverse. The old I4 viewer H=4−X is not a substitute for ship X.

## 1. Existing drawn items vs booking/proxies
| L1 source ID | Booked t | What is actually represented now | Physical furnishing status |
|---|---:|---|---|
| `room_L1-command` | 2.149778 | Source room volume / semantic region, 118.256 m³ (53.215 m³ nominal free) | **EMPTY-SPACE proxy**, not a fitted room or furniture |
| `outfit_L1` | 0.818963 | Thin distributed inner annulus (conformed beneath domed pressure vessel in current renderer) | **Mass envelope**, not drawn individual equipment |
| `floor_L1` | 1.535556 | 0.30 m axial slab, annulus r=0.90..4.15 m | Booked geometric floor; ladder openings are source footprints; individual Boolean cuts not reverified by this sketch |
| `command_terrace` | 0.307111 | 3.40×2.10 m platform X=2.41..2.51 | Built proxy/platform, not detailed crew fixtures |
| `navigator_platform` | 0.102370 | 2.65×2.20 m platform X=2.76..2.86 | Built proxy/platform, mount qualification HOLD |
| `i4_terrace_column_0..3` | 0.016839 combined | Four existing support tubes | Real source-shape tubes; joints/loading HOLD |
| `hatch_L1L2_0/1` | 0.15 each | Parked-open leaves, source box extents; originally `no_render`, included in later mass-neutral true-solid draw pass | kT's normally-open pressure-assisted intent; sealing/torque unqualified |
| `i4_seat_PILOT/NAV/S1..S4` | 0.051185 each | Source `no_render` mass-proxy 0.20×0.70×0.70 m boxes, subsequently visualised in source-booked draw pass | **NOT** 1.58 m contoured couch CAD |
| `i4_mission_table/workbench/cabinetry` | 0.081896 / 0.081896 / 0.040948 | Small proxy booking boxes | **NOT** final table, bench or cabinet shapes |
| `i4_engineering_cabinet/sensors_cabinet/shared_map_table/equipment_workbench/workbench_display` | 0.08/0.08/0.095/0.09/0.03 | Source carryover simple boxes | Not physically qualified furnished detail; not new objects |
| `i4_rails_0..3/lights_0..1/transfer_0..1/observation_rail_0..17/low_g_command_point/map_console` | Source-booked individual proxy amounts | Simple source tubes / boxes, some from previously approved reserve | Fit and attachment unqualified; do not embellish |
| Four `window_L1-command_*` and 37-pane crown | Separately source booked | Glazing/crown physical representation in existing exterior GLBs | Already settled; new internal detail not approved |
| `core_trunk` | 2.047407 | Central passage tube r=0.90 m from X=3.30 aft | Shared access, not L1 furniture |

**Important distinction:** In later v2.5.x draw passes, selected source `no_render` IDs were rendered as their booked *proxy* shapes. That does not turn tiny cuboids into approved ergonomic couches. `room_*` nodes indicate empty room volumes; `outfit_*` is distributed booked outfitting. The new interior-only export rules do not retroactively alter released six-state exterior GLBs.

## 2. Plan and section dimensions

See [companion sketch](L1_HABITAT_PROPOSE_ONLY_2026_11_12.svg).

| Element | Source dimensions |
|---|---|
| Pressure vessel | radius 4.30 m (8.60 m diameter), apex X = −0.30 m, transition X ≈ 3.0431 m |
| L1 floor | r=0.90 to 4.15 m, X=3.00–3.30 m; annulus plan area ≈51.561 m² before ladder footprints; 50.556 m² nominal after two Ø0.80 m circles |
| Command terrace | Y ±1.70, Z −3.01..−0.91 m; X=2.41..2.51 m (lowered 0.50 m from earlier candidate) |
| NAV platform | Y ±1.325, Z +1.45..+3.65 m; X=2.76..2.86 m |
| L1/L2 ladders | centre Y=±1.40 m, Z=0, bore Ø0.80 m |
| Hatches | parked-open leaf span 0.92 m, 0.15 t each; no validated automatic closure dynamics |
| Crown | clear projected radius 3.50 m; expected rays from seats to crown schematic only |

### Six settled source station locations
| Station | Centre Y, Z (m) | Station base X (m) | Couch | Upper-bound crown visibility |
|---|---|---:|---|---:|
| Pilot | -0.98, -2.00 | 2.41 | 1.58×0.70 m contoured | 100% |
| Captain | 0.98, -2.00 | 2.41 | 1.58×0.70 m contoured | 100% |
| Navigator | 0.00, 2.50 | 2.76 | 1.58×0.70 m contoured | 85.3% |
| Engineering | -2.85, -0.70 | 2.95 | 1.58×0.70 m contoured | 100% |
| Sensors/EW | 2.85, -0.70 | 2.95 | 1.58×0.70 m contoured | 100% |
| Mission ops | 2.40, -1.70 | 2.95 | 1.58×0.70 m contoured | 100% |

**S4 FINAL kT-APPROVED SOURCE POSITION:** Y=+2.40m, Z=−1.70m, including render-review adjustment +0.20m Y. Earlier shift-only interim point is RETIRED and not drawn. Current source 3D AABB screen gives 0.0541m separation to terrace. No station move.

## 3. Station-by-station shell-only headroom

Using the exact current source pressure vessel dome profile:
`X_shell(r) = 3.0431182268 − (3.0431182268 + 0.3000000000)·√(1−(r/4.30)²)`.
For each station, `base clearance = X_base − X_shell(r)` in metres along ship X; `eye clearance` uses the source human-factors surrogate eye plane `X_base−0.45`. Conservative outer-footprint column samples four nominal 1.58×0.70 m plan corners at station base X. This is **not** measured vertical standing height, hard-point clearance, occupant swept volume or suit/crawl proof.

| Station | Base axial clearance at centre (m) | Eye-plane shell clearance (m) | Minimum shell clearance at couch plan corners (m) |
|---|---:|---:|---:|
| Pilot | 2.227 | 1.991 | 1.691 |
| Captain | 2.227 | 1.991 | 1.691 |
| Navigator | 2.437 | 1.592 | 1.852 |
| Engineering | 2.350 | 2.132 | 1.558 |
| Sensors/EW | 2.350 | 2.132 | 1.558 |
| Mission ops | 2.346 | 2.196 | 1.475 |

Terrace shell-only clearance: **2.343 m at centre and 1.355 m worst corner**. The settled requirement is **≥1.20 m crawl clearance**. A theoretical source `0.5 m chamfer` option is **not adopted**, NOT drawn, and not necessary to reach 1.20 m. Pilot/Captain crown upper-bound sightline 100%, Navigator 85.3%; remaining stations 100% under optimistic no-obstruction screen. Actual Osteon ribs/sensor hardware, shutters, crew and physical line-of-sight may reduce these.

## 4. Contents and provenance
| Item | Source | Label here |
|---|---|---|
| L1 floor and two ladderways (ONLY crew egress) | `wayfarer/results/out/wayfarer_v05_geometry.json::floor_L1`; `wayfarer/config/wayfarer_v05_inputs.json::habitat.ladderways` | SOURCE / booked |
| Utility core, avionics racks, goods lift, NOT crew passage | `wayfarer/config/wayfarer_v05_inputs.json::habitat.core_note`; `wayfarer/results/out/wayfarer_v05_geometry.json::core_trunk` | SOURCE / booked; radius 0.90m kept |
| Six distinct I4 station roles and source positions | `design_decisions_2026_10_31.L1`; `wayfarer/results/out/wayfarer_v05_geometry.json::l1_i4_lock.stations` | SETTLED roles; geometry remains proxy |
| 1.58 m contoured couches | `design_decisions_2026_10_31.L1_human_factors_step1c` | SETTLED dimension; detailed form **PROPOSED** |
| Command terrace lowered 0.5 m | same decision and `wayfarer/results/out/wayfarer_v05_geometry.json::l1_i4_lock.platforms` | SETTLED |
| S4 final Y=+2.40 m, Z=−1.70 m | `wayfarer_l1_layout_approval_2026_11_12`; source `l1_i4_lock.stations[S4]` | kT APPROVED, interim retired |
| NAV platform | source `navigator_platform`, `l1_i4_lock.platforms` | BOOKED; hardware hold |
| Pressure-assisted normally-open L1/L2 leaves | `decisions.l1_l2_pressure_hatches`, source `hatch_L1L2_0/1` | SETTLED design intent |
| Rails, two lights, hand/foot transfers, two cabinet functions, shared map table, equipment workbench/display, observation rail, low-g command point | `wayfarer/docs/I4_ORIGINAL_SCENE_2026_10_29.json`, `wayfarer/docs/I4_COMPLETENESS_RECOVERY_2026_11_01.md`; source `i4_* ` | BOOKED / source proxy representation; **no newly invented furnishings** |
| Crown viewing geometry | `decisions.crown_dome`, `decisions.crown_option_c_tiles`, current crown geometry | Settled, no new viewport |
| 10 berths one per crew, G7 | `decisions.habitat_changes_v057` | **L3, not an L1 furnishings list** |
| Storm shelter 72 h × 10 and same-deck life support | `decisions.shelter_life_support` | **L4 constraint, not additional L1 fixtures** |

## 5. Print at 1:25 (view/marking proposals, not STL exports)
| Source object | At 1:25 | Read or paint? |
|---|---:|---|
| Floor annulus OD 8.30 m | **332 mm** | Obvious deck ring (printable part only after approval) |
| Crown clear diameter 7.00 m | **280 mm** | Existing crown glazing; assembly seams read |
| Utility core Ø1.80 m | **72 mm** | Goods lift, racks, utilities; NOT crew egress |
| Two ladder shafts Ø0.80 m | **32 mm each** | Physical holes/shafts only if cut in later approved STL derivation |
| Terrace 3.40×2.10 m | **136×84 mm** | Physical platform reads |
| NAV platform 2.65×2.20 m | **106×88 mm** | Physical platform reads |
| 1.58×0.70 m couches | **63.2×28 mm** | Recognisable if detailed couch design later approved; current box proxies do **not** portray couches |
| Hatch 0.92 m leaf | **36.8 mm** | Leaf readable, hinge/actuation details not qualified |
| Rail Ø0.022–0.025 m | **0.88–1.00 mm** | Edge is visible but fragile; don't treat as certified printable hardware |
| Display labels, station IDs, warnings, console text | Variable, sub-mm strokes | **Decals/paint guide only**; no raised print lettering |
| Fine indicator lamps, bolt dots, keys | Sub-mm | **Decal / paint only** |

kT APPROVED L1 layout. This remains the source plan; the separate L1 build must supply D9 and containment evidence. The two ladderways are the only crew egress; central utilities/racks/goods lift are not crew passage.
