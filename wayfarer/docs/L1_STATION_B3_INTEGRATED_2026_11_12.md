# Wayfarer L1 B3 integration: accepted station, merged details

**ALL bodies. ALL sponsors. 2026–2226.** kT authority: `kt_decisions.json::l1_station_b3_merge_2026_11_12`. The built model is a **separate** L1-only GLB, not one of the six exterior states.

## Design authority and scope

- **PR #517 B3** is the accepted station. The exact source generator `wayfarer/lab/l1_station_b3_generator.py` supplies one shared contoured 1.58m couch mesh (six instances), headrest, five-point restraint, light palette, two arch posts, a curved **centre halo that lifts back**, two **wing screens that swing aside**, and six small role-control sets.
- **PR #516 keepers**: 46.000kg common couch allocation, 5.185186564kg halo/control allocation, brighter blue-grey/ivory/slate/teal finish (already applied in #517), refinements of existing map table, mission cassette, equipment workbench and cassette, engineering and sensor cabinets with their contained source sleeve, display frames/bezels, 4g limitations, and functional names for role controls.
- **PR #516 discarded**: a single hinged foldaway tablet. **No such hardware was imported.** #516 remains unmerged because its keeper content is carried by this PR.
- Fixed I4 station locations, including S4 at **Y=+2.40m, Z=−1.70m**, terrace and NAV platform, two egress-only ladderways, utility-only trunk and pressure-assisted parked-open hatches are unmodified.

## Verified integration

[L1 GLB](../render/out/interior_L1.glb) · [D9 and containment report](../render/out/interior_L1_report.json) · [1:25 print note](L1_INTERIOR_PRINT_1_25_2026_11_12.md).

| Checked item | Halo closed | Centre lifted / wings open |
|---|---:|---:|
| True FCL triangle intersections after positive-volume broadphase | **0** | **0** |
| Pressure-vessel containment, each B3 moving vertex | **PASS** | **PASS** |
| Minimum source pressure-shell clearance | 0.512934m | 0.512934m |
| Station mesh-components examined | 30 | 30 |
| Installed physical fixture nodes screened | 65 | 65 |

**NAV mount contact:** Initial FCL detection was a **face-sharing zero-volume contact** between the NAV couch base ending at axial X=2.76m and the NAV platform beginning at X=2.76m. Category-d requires a positive penetrating volume, not a correctly seated mounting surface. The validator first excludes AABB candidates with ≤1µm extent in any axis, then runs FCL on every remaining candidate. All six station poses and 65 source/derived fixtures remain checked. No stations were moved, and no D9 contacts remain.

The standalone GLB has **one common B3 couch mesh instanced six times**, separate B3 halo elements and six source role-control variants. Its glTF animation has 18 rotation channels for the six raised centre sections and twelve wing panels. No new exterior GLB, source BRep or operating-state mass entries are added.

## Exact existing bookings and proposed internal allocations

Each `i4_seat_<role>` source owner is already booked at **51.185186564kg** (6× = 307.111119385kg). Only an internal representation:
- Common couch **46.000kg**
- B3 halo and role controls **5.185186564kg maximum**

| Proposed halo/control material group | Estimated mass |
|---|---:|
| Hollow composite arch/posts, hinges and actuators | 2.800kg |
| Thin-film screen faces and backing | 0.550kg |
| Two role-control modules | 1.500kg |
| Wiring and connectors | 0.250kg |
| **Estimated subtotal** | **5.100kg** |
| **Estimated remaining margin** | **0.085kg** |

**Material proof remains open.** The #517 35mm arch bars are exterior shape envelopes, *not* declared solid-density blocks. The 5.100kg estimate assumes hollow composite members and film displays; this is a plausibility screen only. If physical materials cannot achieve it, the decision returns to kT; mass may not be silently rebooked. Full ship **dry 868.1922552640087t** and **ECON Δv 707.845km/s** remain unchanged.

## Fixture keepers from #516 under their own ledger owners

| Source item | Already booked mass | New visible representation (inside source box) |
|---|---:|---|
| `i4_shared_map_table` | 95.000kg | Recessed top/rim with corner braces |
| `i4_mission_table` | 81.896kg | Nested under-top cassette (not another table) |
| `i4_equipment_workbench` | 90.000kg | Recessed working surface and edge rim |
| `i4_workbench` | 81.896kg | Nested underside cassette (not another bench) |
| `i4_engineering_cabinet` | 80.000kg | Open case and flush doors |
| `i4_sensors_cabinet` | 80.000kg | Shared-case shape with role-specific decals |
| `i4_cabinetry` | 40.948kg | Interior cassette / sleeve, not new freestanding cabinet |
| `i4_workbench_display` | 30.000kg | Screen bezel and inset |
| `i4_map_console` | 12.000kg | Existing panel bezel and recessed face |

The nested 3 original source mass-only proxies were made visible as **nested parts**, with independent nonadditive provenance. The rest of the previously drawn fixtures, hatch leaves, platforms, ladder cut-outs and utilities are preserved.

## Role controls and 4g limits

| Station | B3 physical controls | #516 semantic naming retained |
|---|---|---|
| Pilot | throttle / sidestick | Attitude + translation flight control |
| Captain | keypad / backup stick | Backup flight and command transfer |
| Navigator | keypad / trackball | Trajectory / waypoint review |
| Engineering | keypad / guarded switches | Thermal/power selection and acknowledgment |
| Sensors/EW | twin trackballs | Track slew / sensor modality |
| Mission Ops | keypad / comms | Task sequencing and asset selection |

The 4g doctrine is **reclined, restrained, armrest-operated**, with low-g standing stations inactive. A representative 100kg occupant experiences ~3.92kN inertia at 4g. **Mount strength, off-axis restraint loading, occupant/suit fit, halo actuator loads, 4g operability, interface semantics and physical printing tolerances are still open.** None are made certification passes by this visual milestone.

At 1:25, couch 63.2×28mm, map top 44×25.2mm, bench 55.2×21.6mm; physical shapes are retained only where print feature ≥0.6mm. Screens/UI, tiny buttons, warning glyphs, small indicators and thin fabric detail are print decals, not claimed printable geometry.

**Checks applied:** L1 D9 category-d and containment in both halo states. **Not G1–G12.** The authorisation ends here.
