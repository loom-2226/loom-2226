> **HISTORICAL SHA ea1fcb59. SUPERSEDED for current render/G7/RCS evidence** by [2026-11-01 render review repair](RENDER_REVIEW_REPAIR_2026_11_01.md) on geometry SHA 5d73cdd1. Original 2026-10-31 results remain audit history.

# Wayfarer render track and G12 acceptance / declared assumptions

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING · PR #435 DRAFT/HOLD · kT visual review PENDING**

## Exact source and scope

- Geometry SHA256: `ea1fcb59f1e0a127cd48dc4e0321e7d42247e3f2e445cf89893bdefadb793266` (unchanged from kT accepted S4/I4 configuration).
- All **current-manifest** exterior stills, command/crown images, L1-L5 plans and interactive 3D viewer were built from the hashed geometry. The render-only I4 scene is generated from `inputs/wayfarer_v05_inputs.json` at the same SHA.
- Metric still is a **visual configuration only**, not a Metric simulation; no Navigator or Metric model development was performed.
- One GLB in `render/out/wayfarer_I4_in_out_ea1fcb59.glb` with two scenes (exterior crown closed, interior I4 crown open) derived from the same procedural source. This is visual evidence, not physical fit certification.
- No hull/ship geometry rebuild, no mass/CG/inertia changes, no repo migration or main merge. Existing geometry file hash reverified.

## RCS peak power provenance (existing evidence only)

- **Observed peak simultaneous nozzle count in current-hash FQ traces: UNKNOWN**, because preserved current-hash FQ results do not include time-indexed per-nozzle samples. The older Rev7 archived `.rcs_trace.json` series cannot be assigned to the new source geometry.
- **Observed peak plant heating MW: UNKNOWN**, not extrapolated or invented.
- Declared installed ceiling: **32 × 57.663265 MW = 1845.224 MW**, if all installed 25 kN thrusters fired simultaneously. This is **NOT a measured FQ peak** or evidence the plant can deliver it.
- On-demand plant heating architecture A is accepted *as a declaration*, not power-availability closure. The 2.6 MJ/kg water conditioning plus 0.5 ve² kinetic energy estimate excludes efficiency, pipe/valve transient, concurrency, thermal rejection and fault response.
- No new FQ runs were performed to fill the missing measurement. `RCS_POLICY_DECLARATION.json` records explicit missing-data status and theoretical ceiling.

## G1–G12 rerun on this geometry

| Gate | Verdict |
|---|---|
| G1 Mass and fluids ledger | **PASS** |
| G2 Torch and reach | **PASS** |
| G3 Balance and attitude | **PASS** |
| G4 Power and heat | **PASS-DECLARED** |
| G5 Structure and loads | **PASS-DECLARED** |
| G6 Radiation | **PASS-DECLARED** |
| G7 Compartments and crew space | **PASS-DECLARED** |
| G8 Shuttle, drones and bay exit | **PASS** |
| G9 Failures and reserves | **PASS-DECLARED** |
| G10 Flight dynamics: RCS, torch, Metric, Loom | **PASS-DECLARED** |
| G11 Canon fit | **PASS** |
| G12 Images | **PASS-DECLARED** |

**G12 is PASS-DECLARED**, not unconditional visual approval: current manifest, image counts, viewer and 2-scene GLB all pass provenance checks. kT aesthetic and geometric representation signoff is an explicit declared assumption. `certified=false` remains true until declarations and other gates are appropriately governed.

## Rendered current-hash deliverables

| Class | Count | Examples |
|---|---:|---|
| exterior | 4 | `ext_burn.png`, `ext_closed.png`, `ext_docking.png`, `ext_metric.png` |
| cutaway | 2 | `cut_hab.png`, `cut_long.png` |
| deckplan | 6 | `deck_L1.png`, `deck_L2.png`, `deck_L3.png`, `deck_L4.png`, `deck_L5.png`, `deck_overview.png` |
| command | 4 | `cmd_cutaway.png`, `cmd_pov.png`, `crown_closed.png`, `crown_open.png` |
| viewer | 1 | `wayfarer_v05_viewer.html` |

**Not current:** older render files (including the obsolete L1 section) may remain in repository history or working tree, but they are excluded from the current manifest and G12 count. Source layouts no longer use legacy layout D.

## Full declared certification assumptions awaiting explicit kT disposition

The following is the **complete, unabridged `declared` list** emitted by the current `certify.py` machine report. These are not silently treated as resolved by the render track.

### G4 — Power and heat
**torch_heat** · kT: ACCEPTED

Torch heat package (kT, 2026-10-25): each pellet is wrapped in a shell of remass that soaks up the burn and leaves as exhaust. The shell must let no more than ~358 ppm of the burn's energy escape as light, counting its own glow (the reactor face's 10 MW/m2 limit); the design value is 180 ppm. With the model's other assumptions (torch/torch_heat_inputs.json: light 40% of fusion energy; He3-rich, spin-polarised fuel with 0.76% neutrons, 85% absorbed by the shell; plume contact 1e-4 of charged energy; coil shield transmission 1e-3), 1.40 GW reaches hot structure and 0.48 MW the magnet coils at 12.6 TW of fusion. These are assumptions, not results. Replaces v0.5.1's 387 MW (34 ppm) torch-leak gap.

**torch_fin_temperature** · kT: ACCEPTED

Hot fins run for life at 1750 K. Lithium heat pipes have run in lab tests to ~1,500 K and briefly ~1,800 K; years at 1750 K with burn cycling and neutron exposure is an engineering extrapolation (a technology milestone), not new physics. Fallback: 1,500 K fins, ~49 m span, ~30 t, still inside the reserve.

**plant_power** · kT: ACCEPTED

Plant electrical: Metric HARD at a 1300 K reject temperature needs 34.8 MW of cryo-chain electrical power, against canon's 23.9 MW at 900 K. The relational plant must supply this (canon amendment), or the cryo chain must reject through a 900 K loop.

**cold_running** · kT: ACCEPTED

Cold running (rev 7, F5 provisional item F5-TE-01): the tunable flanks drop from emissivity 0.85 to 0.1, so at the same skin temperature they radiate 12% as much. Heat is held, not removed: habitat heat 58.1 kW (x1.25), plus plant standby 10.0 kW and cryo standby 10.0 kW, less 7.1 kW still leaking through 177 m2 of low-e skin at 290 K warms the 50 t of protected water by 15 K in about 12.3 h (ideal no-standby ceiling 17.1 h). ENGINEERING_ASSUMPTION (screening placeholders 10+10 kW, NOT sourced or qualified); editable, replace with measured/engineering budget. Then the ship must open the strakes or switch the flanks back to normal. Detailed load-cycle variation, cryo plant duty, tank thermal coupling, and reserve storage remain open. The metallic look in the viewer is a proposed optical property.

### G5 — Structure and loads
**i4_terrace_mounts** · kT: AWAITING

I4 terrace 4 columns sized as 7075-T6 76mm OD x 3mm at 0.49m. 5g x1.5 ultimate +0.5g lateral member screen, no joint, deck bearing, vibration, fatigue, swept-body or 3D egress qualification. HOLLOW: closed only for column members, not system.

### G6 — Radiation
**berth_viewports** · kT: ACCEPTED

Berth viewports (v0.5.7): 10 x 0.5 m viewports keep the berth screen because acrylic plugs carry at least the g/cm2 they replace (armour 27.14 vs 27.0, ring 8.26 vs 8.0), so the ray screen, which treats the hull as continuous, is unchanged. Rev 3: the same plug kit is in every opening below the crown, including the L2 viewport band, and continues through the storm-shelter jacket (17 cm more acrylic for the 20 cm of water). Not yet shown: the dose. Acrylic is ~8% hydrogen by mass against water's 11%, so per g/cm2 it may stop cosmic-ray secondaries slightly less well; a transport check may ask for a thicker plug. Encapsulated for fire.

**crown_dome** · kT: ACCEPTED

Crown dome (v0.5.7): 25 m2 of glazing inside r 2.8 m replaces the 8 nose windows. Assumes (1) proof-tested transparent ceramic panes up to 2.3 m across (2026's largest are ~0.76 m), a 2226 materials milestone like the 1,750 K fins (rev 4: the L2 viewport band's 16-18 mm plate panes rely on the same ceramic; 2026 ALON would need 25-29 mm); (2) tambour gores of armour-equivalent Strata laminate (Builder-derived, MHL-22) that restore 27 g/cm2 when closed and stow in the brow ring; (3) the operating rule: open only at low speed or with the bow facing away from the dust flow (braking and tail-first coasting); closed for solar particle events, radiation belts, torch burns and Loom formation and translation. Stuck closed is safe; stuck open: turn the bow out of the dust flow. With the gores open, L1 loses the armour over the crown (glass 2-9 g/cm2); L1 is not a shelter.

**strata_armour** · kT: ACCEPTED

Habitat armour face (rev 7, kT 2026-10-26): Strata laminate (Builder-derived, MHL-22) over the whole habitat armour, x 0-14. KT_ACCEPTED 2026-10-31 as visible armour face; materials constitutive/physical performance remain OPEN; no changed shielding/mass claim. Bow x 0.0-2.6 m: bare Strata: the erosion face meets the dust flow.

**node_faces** · kT: ACCEPTED

Metric node faces (rev 7, kT 2026-10-26; Sol: AGREE, placement HOLD): 208 visible flush or recessed faces, 13 rings x 16 at 22.5 deg (rev 5 longeron-study layout). 76 are clear; the rest are flagged: 16 faces dust flow bow first, 12 on bay door, 80 on torch chain, 1 overlaps camera, 2 overlaps hold door, 1 overlaps window, 20 under stowed strake. The design case assumes every face carries at least the armour's g/cm2 it replaces, like the berth-viewport plugs. Sensitivity, faces as open bores through the armour: berth screen 14.78 g/cm2 (30 of 36 berth points below 40) and storm shelter 36.3 g/cm2. So a face must be armour-equivalent: materials, cover, seal and mount stay OPEN, and no dust check exists in the basis yet (faces flagged 'faces dust flow' meet the flow when coasting bow-first). Node stations are not moved for the look; PR #184 stays OPEN.

**shelter_life_support** · kT: ACCEPTED

Storm shelter life support: 72 h for 10 people from the life-support room on the same deck (design provision, not computed).

**gcr** · kT: ACCEPTED

Galactic cosmic rays: at 2026 free-space rates (1.8 mSv/day, ~657 mSv/yr) a crew member reaches NASA's 600 mSv career limit after ~333 days in deep space. Hull shielding barely changes this. Long careers aboard rely on canon's off-Earth MED-MOD-RADIATION milestone and crew time-in-space rules; this is a canon question, not something the hull can close.

**torch_neutrons** · kT: ACCEPTED

Torch neutrons and gammas: the shadow shield must attenuate the torch's neutron and gamma output so the dose rate inside the habitat during burns stays within crew limits. The v0.5.2 heat model puts neutrons at ~0.76% of the burn's energy with 85% absorbed by the remass shell; the dose itself is not computed here, only the shadow geometry is checked.

### G7 — Compartments and crew space
**i4_human_factors** · kT: AWAITING

I4 source-frame check rerun against current geometry. Scene seat length 1.58m <2.10m source crew envelope; 2D seat/ladder/walkways and bare dome clearances NOT physical 3D access or 4g qualification. Crown sightlines are optimistic upper bounds only. Optional 0.5m terrace-corner chamfer is NOT BUILT.

### G9 — Failures and reserves
**external_equipment** · kT: ACCEPTED

External equipment (rev 7, ENGINEERING_ASSUMPTION): 55 parts from the inventory's 13 item types. Items with a ledger line are located inside it (sensor turrets in mission systems, RF arrays, laser terminals and aft trackers in the avionics racks, forward trackers in the bow sensor ring, service ports in the service arm, vents in life support, the docking target in the collar): 1.88 t, no new mass. New hardware (crawler docks and points, grapple fixtures, EVA rails): 1.42 t from the reserve. Not built: drone_bay HOLD; nav_lights OPTIONAL; crawler_rails NOT YET. Masses are 2026-analogue allowances to be sized.

### G10 — Flight dynamics: RCS, torch, Metric, Loom
**torch_tvc** · kT: ACCEPTED

Torch thrust-vector control: the magnetic nozzle steers the thrust line by up to 1.0 deg (asymmetric coil current). Needed: trim plus an assumed 0.5 deg thrust error (0.843 deg). The error is an engineering assumption, not a measured disturbance history; the authority is not a qualified nozzle capability.

**rcs_axial_plumes** · kT: AWAITING

Axial RCS: one 25 kN thruster per cluster, canted 10 deg outward (bow ones exhaust forward, aft ones aft). Assumes the plumes clear the crown glazing, hull, hot fins and torch chain; plume impingement is not yet modelled.

**g10_burn_coasts** · kT: AWAITING

Long torch burns split into segments of at most 165 min ([V2 6113]) with 15 min coasts (engineering assumption; in free space the coasts change elapsed time, not delta-v).

### G12 — Images
**kT_visual_acceptance** · kT: AWAITING

Required before treating rendered representation as accepted design evidence; generated images meet source/hash coverage only


## Additional kT choices / explicit OPEN and HOLD boundaries

1. **L1 I4:** Six 1.58m contoured couch positions accepted for plan screen, not 2.10m straight berths; 1.2m crawling-terrace clearance accepted; S4 moved onto annulus. 3D occupant accommodation, actual ladders/egress, restraint and mounts are HOLD.
2. **Crown:** Ceramic panes and 16 closing Strata armour-equivalent gores retained; actual pressure, optical material and damage tolerance not qualified. Drone-deployed extra Strata crown armour OPTION, drone bay HOLD.
3. **Node faces:** Armour-equivalent areal density rule accepted; exact location/physical integration HOLD PR #184; full radiation transport/dose remains open.
4. **Cold running:** 17.087h no-standby ideal ceiling vs ~12.276h with assumed 10kW plant and 10kW cryo standby; real standby budget, thermal coupling and operating duty HOLD.
5. **External equipment:** Editable 1.4208t new allowance is a 2026 analogue guess paid from reserve, not fixed installation. At 0t, return allowance to uncommitted reserve; mass-property rerun if a real alternate hardware arrangement is selected.
6. **RCS:** Existing 32 × 25kN nozzles and positions; working fluid remass water, with 5t ring-fenced from torch; 50t protected water excluded. ve variable; 1.96km/s scenario is not verified water-thruster hardware law.
7. **FQ10 TVC safing:** Lab detection assumed 0.20s, torque-authority cap, cut on saturation or rate/attitude threshold. No qualified physical sensor, throttle/cut actuator rate, FDIR or sustained limp-home test. Conditional numerical PASS is not hardware qualification.
8. **RCS plant A:** Architecture accepted on demand, minimum 57.663MW per 25kN firing unit at ve1.96km/s; heater bus availability, pump, feed, concurrent power/thermal rejection HOLD. B hot-water storage OPTION.
9. **Rendering:** Visual modes are schematic and non-governing. Full 3D viewer uses six source I4 couch positions but intentionally excludes crew mannequins until 4g suited-body fitting accepted. GLB is visual media, not an independent geometry certificate. kT visual approval still AWAITING.

## Lock and rollback

- PR #435 remains DRAFT/HOLD and must not be merged by this task.
- PR #436 independent draft card proposals untouched. No Navigator, Metric physics or repository migration.
- Revert this render-only evidence commit to restore earlier failure state; the unchanged current geometry SHA is the independent rollback anchor.
