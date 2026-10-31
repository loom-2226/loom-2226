# Wayfarer — kT declared conventional laboratory acceptance

ALL bodies. ALL sponsors. 2026-2226.

**kT accepted declared G1–G12 conventional laboratory qualification on 2026-11-01; PR #435 remains DRAFT/HOLD.**

## Immutable geometry and scope

- Source geometry SHA256: 5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256. This acceptance changes neither its source geometry, dry/wet mass, CG nor inertia.
- Machine certification predicate is unchanged: every G1–G12 check must be PASS or PASS-DECLARED and every declared item kT ACCEPTED.
- **Machine result certified=true**, strictly for kT-accepted declared conventional laboratory basis. NOT a hardware air/spaceworthiness approval; independently required reviewer signatures and loom-gate are separate.
- **Metric arrival HOLD:** arrival time, endpoint state, trajectory and remass ledger NOT qualified. A G10 title mentioning Metric does not mean arrival is qualified.
- **Navigator EXCLUDED:** no runtime, mission, card deployment, testing or acceptance.
- **RCS supply OPEN:** idle torch reactor or dedicated power source proposed, neither selected or budgeted. No ship-wide electricity/thermal budget. The older nominal on-demand concept is not a verified generator.
- PR #435 remains DRAFT/HOLD. No merge to protected main. No repo move.

## All gate outcomes after rerun

| Gate | Verdict |
|---|---|
| G1 Mass and fluids ledger | PASS |
| G2 Torch and reach | PASS |
| G3 Balance and attitude | PASS |
| G4 Power and heat | PASS-DECLARED |
| G5 Structure and loads | PASS-DECLARED |
| G6 Radiation | PASS-DECLARED |
| G7 Compartments and crew space | PASS-DECLARED |
| G8 Shuttle, drones and bay exit | PASS |
| G9 Failures and reserves | PASS-DECLARED |
| G10 Flight dynamics: RCS, torch, Metric, Loom | PASS-DECLARED |
| G11 Canon fit | PASS |
| G12 Images | PASS-DECLARED |

## kT new acceptance (2026-11-01)

G5 terrace mounts/load paths and G7 3D suited-body fit/egress are **accepted as declared design assumptions**, not falsely reported as newly measured physical tests. G10 axial plumes and segmented burn doctrine likewise; G12 visual review by kT is accepted.

## RCS water and power doctrine

- RCS working fluid is remass water at v_e=1.96 km/s in these lab cases. Five tonnes ring-fenced from torch, protected 50t remains excluded.
- Existing 40s pitch flip, dt 0.1s: **9 simultaneously firing nozzles** (realised thrust greater than 1N) at t=20.0s.
- Thrust-weighted **ideal minimum peak 244.4557MW**; nameplate 9 × 57.6633MW **conservative allowance 518.9694MW**. These do NOT constitute measured generator electrical power or demonstrated heater heat rejection.
- Installed 32-nozzle all-on ceiling is 1,845.2245MW and is NOT an observed firing count.
- **Routine RCS flips: 120s. Fast 40s flips: emergencies only.**
- **B (charged hot-water store) is an OPTION only**; source remains OPEN (idle torch reactor versus dedicated supply). No plant-wide budget has been supplied or accepted.
- Conventional FQ10 remains **conditional on 0.2s stuck-TVC detection and throttle/cut**, plus physically unqualified sensor and valve timing. No new FQ test is implied by accepting declarations.

## Complete declared register (verbatim machine evidence)

All declared conditions remain visible in the machine report and generated Markdown. ACCEPTED means kT accepts the stated assumption as declaration, not that the model computed the missing physics.


### G4 Power and heat

- **torch_heat**: ACCEPTED (decision 2026-10-25).
  - Basis: Torch heat package (kT, 2026-10-25): each pellet is wrapped in a shell of remass that soaks up the burn and leaves as exhaust. The shell must let no more than ~358 ppm of the burn's energy escape as light, counting its own glow (the reactor face's 10 MW/m2 limit); the design value is 180 ppm. With the model's other assumptions (torch/torch_heat_inputs.json: light 40% of fusion energy; He3-rich, spin-polarised fuel with 0.76% neutrons, 85% absorbed by the shell; plume contact 1e-4 of charged energy; coil shield transmission 1e-3), 1.40 GW reaches hot structure and 0.48 MW the magnet coils at 12.6 TW of fusion. These are assumptions, not results. Replaces v0.5.1's 387 MW (34 ppm) torch-leak gap.
  - Accepted as: v0.5.2 torch heat package (kT chose the package and 1,750 K fins on 2026-10-25 and accepted this wording the same day): the remass shell lets no more than ~360 ppm of the burn's energy escape as light, counting its own glow; design value 180 ppm; with the heat model's other assumptions 1.40 GW reaches hot structure and 0.48 MW the magnet coils.
- **torch_fin_temperature**: ACCEPTED (decision 2026-10-25).
  - Basis: Hot fins run for life at 1750 K. Lithium heat pipes have run in lab tests to ~1,500 K and briefly ~1,800 K; years at 1750 K with burn cycling and neutron exposure is an engineering extrapolation (a technology milestone), not new physics. Fallback: 1,500 K fins, ~49 m span, ~30 t, still inside the reserve.
  - Accepted as: kT: "Let's go 1750." Hot fins at 1,750 K, recorded as an engineering extrapolation (technology milestone), with 1,500 K fins as the fallback.
- **plant_power**: ACCEPTED (decision date not recorded).
  - Basis: Plant electrical: Metric HARD at a 1300 K reject temperature needs 34.8 MW of cryo-chain electrical power, against canon's 23.9 MW at 900 K. The relational plant must supply this (canon amendment), or the cryo chain must reject through a 900 K loop.
  - Accepted as: canon states the relational plant supplies ~34.8 MW for Metric HARD at a 1,300 K reject temperature. Option not taken: a 900 K loop for the cryo chain.
- **cold_running**: ACCEPTED (decision 2026-10-31).
  - Basis: Cold running (rev 7, F5 provisional item F5-TE-01): the tunable flanks drop from emissivity 0.85 to 0.1, so at the same skin temperature they radiate 12% as much. Heat is held, not removed: habitat heat 58.1 kW (x1.25), plus plant standby 10.0 kW and cryo standby 10.0 kW, less 7.1 kW still leaking through 177 m2 of low-e skin at 290 K warms the 50 t of protected water by 15 K in about 12.3 h (ideal no-standby ceiling 17.1 h). ENGINEERING_ASSUMPTION (screening placeholders 10+10 kW, NOT sourced or qualified); editable, replace with measured/engineering budget. Then the ship must open the strakes or switch the flanks back to normal. Detailed load-cycle variation, cryo plant duty, tank thermal coupling, and reserve storage remain open. The metallic look in the viewer is a proposed optical property.
  - Accepted as: Provisional ~17.09h ideal cap before plant and cryo standby; 10+10 kW editable illustrative loads yield a shorter window; physical heat budget OPEN

### G5 Structure and loads

- **i4_terrace_mounts**: ACCEPTED (decision 2026-11-01).
  - Basis: I4 terrace 4 columns sized as 7075-T6 76mm OD x 3mm at 0.49m. 5g x1.5 ultimate +0.5g lateral member screen, no joint, deck bearing, vibration, fatigue, swept-body or 3D egress qualification. HOLLOW: closed only for column members, not system.
  - Accepted as: kT accepts I4 terrace mounts and structural load paths as DECLARED, not structurally tested to hardware standard. Original 5g×1.5 member / 0.5g lateral assumption remains visible; joints, bearing, vibration and fatigue have not been newly modelled.

### G6 Radiation

- **berth_viewports**: ACCEPTED (decision 2026-10-26).
  - Basis: Berth viewports (v0.5.7): 10 x 0.5 m viewports keep the berth screen because acrylic plugs carry at least the g/cm2 they replace (armour 27.14 vs 27.0, ring 8.26 vs 8.0), so the ray screen, which treats the hull as continuous, is unchanged. Rev 3: the same plug kit is in every opening below the crown, including the L2 viewport band, and continues through the storm-shelter jacket (17 cm more acrylic for the 20 cm of water). Not yet shown: the dose. Acrylic is ~8% hydrogen by mass against water's 11%, so per g/cm2 it may stop cosmic-ray secondaries slightly less well; a transport check may ask for a thicker plug. Encapsulated for fire.
  - Accepted as: Every opening below the crown carries an acrylic shield plug and insert with at least the g/cm2 they replace (armour 27, berth ring 8, shelter jacket 20), so berths and shelter keep their screens with the shutters open; the dose is accepted as a provision until a transport check (OLTARIS) is run; plugs are encapsulated and counted as fire load.
- **crown_dome**: ACCEPTED (decision 2026-10-26).
  - Basis: Crown dome (v0.5.7): 25 m2 of glazing inside r 2.8 m replaces the 8 nose windows. Assumes (1) proof-tested transparent ceramic panes up to 2.3 m across (2026's largest are ~0.76 m), a 2226 materials milestone like the 1,750 K fins (rev 4: the L2 viewport band's 16-18 mm plate panes rely on the same ceramic; 2026 ALON would need 25-29 mm); (2) tambour gores of armour-equivalent Strata laminate (Builder-derived, MHL-22) that restore 27 g/cm2 when closed and stow in the brow ring; (3) the operating rule: open only at low speed or with the bow facing away from the dust flow (braking and tail-first coasting); closed for solar particle events, radiation belts, torch burns and Loom formation and translation. Stuck closed is safe; stuck open: turn the bow out of the dust flow. With the gores open, L1 loses the armour over the crown (glass 2-9 g/cm2); L1 is not a shelter.
  - Accepted as: Crown dome over L1 and the L2 viewport band: proof-tested transparent ceramic panes up to 2.3 m (band panes 16-18 mm plates) as a 2226 materials milestone; tambour gores and shutters of armour-equivalent Strata laminate (Builder-derived, MHL-22); the dome and shutters open only at low speed or with the bow out of the dust flow, closed for solar particle events, radiation belts and torch burns.
- **strata_armour**: ACCEPTED (decision 2026-10-31).
  - Basis: Habitat armour face (rev 7, kT 2026-10-26): Strata laminate (Builder-derived, MHL-22) over the whole habitat armour, x 0-14. KT_ACCEPTED 2026-10-31 as visible armour face; materials constitutive/physical performance remain OPEN; no changed shielding/mass claim. Bow x 0.0-2.6 m: bare Strata: the erosion face meets the dust flow.
  - Accepted as: Strata as armour face; constitutive performance OPEN; drone-deployed over-crown armour is OPTION ONLY and drone bay HOLD
- **node_faces**: ACCEPTED (decision 2026-10-31).
  - Basis: Metric node faces (rev 7, kT 2026-10-26; Sol: AGREE, placement HOLD): 208 visible flush or recessed faces, 13 rings x 16 at 22.5 deg (rev 5 longeron-study layout). 76 are clear; the rest are flagged: 16 faces dust flow bow first, 12 on bay door, 80 on torch chain, 1 overlaps camera, 2 overlaps hold door, 1 overlaps window, 20 under stowed strake. The design case assumes every face carries at least the armour's g/cm2 it replaces, like the berth-viewport plugs. Sensitivity, faces as open bores through the armour: berth screen 14.78 g/cm2 (30 of 36 berth points below 40) and storm shelter 36.3 g/cm2. So a face must be armour-equivalent: materials, cover, seal and mount stay OPEN, and no dust check exists in the basis yet (faces flagged 'faces dust flow' meet the flow when coasting bow-first). Node stations are not moved for the look; PR #184 stays OPEN.
  - Accepted as: armour-equivalent g/cm2 per node face; placement HOLD pending PR #184
- **shelter_life_support**: ACCEPTED (decision date not recorded).
  - Basis: Storm shelter life support: 72 h for 10 people from the life-support room on the same deck (design provision, not computed).
  - Accepted as: 72 h of life support for 10 people in the storm shelter, from the life-support room on the same deck, recorded as a design provision to be sized in detail later.
- **gcr**: ACCEPTED (decision date not recorded).
  - Basis: Galactic cosmic rays: at 2026 free-space rates (1.8 mSv/day, ~657 mSv/yr) a crew member reaches NASA's 600 mSv career limit after ~333 days in deep space. Hull shielding barely changes this. Long careers aboard rely on canon's off-Earth MED-MOD-RADIATION milestone and crew time-in-space rules; this is a canon question, not something the hull can close.
  - Accepted as: crew protection from galactic cosmic rays relies on canon's off-Earth MED-MOD-RADIATION milestone plus crew time-in-space limits.
- **torch_neutrons**: ACCEPTED (decision date not recorded).
  - Basis: Torch neutrons and gammas: the shadow shield must attenuate the torch's neutron and gamma output so the dose rate inside the habitat during burns stays within crew limits. The v0.5.2 heat model puts neutrons at ~0.76% of the burn's energy with 85% absorbed by the remass shell; the dose itself is not computed here, only the shadow geometry is checked.
  - Accepted as: covered by the same declared gap: the torch and shadow shield keep neutron and gamma dose in the habitat within crew limits during burns; the shadow geometry is checked (G6).

### G7 Compartments and crew space

- **i4_human_factors**: ACCEPTED (decision 2026-11-01).
  - Basis: I4 source-frame check rerun against current geometry. Scene seat length 1.58m <2.10m source crew envelope; 2D seat/ladder/walkways and bare dome clearances NOT physical 3D access or 4g qualification. Crown sightlines are optimistic upper bounds only. All three annulus-floor couches now clear the rectangular terrace in a conservative 3D axis-aligned box test; S4 is moved +0.20m outboard with 0.0541m clearance. This is not occupant-swept collision testing. Optional terrace chamfer NOT BUILT.
  - Accepted as: kT accepts I4 3D suited-body fit and egress as DECLARED for conventional Wayfarer lab qualification. Bounded plan and 3D couch-versus-terrace AABB tests pass; full physical occupant-swept/4g restraint and evacuation evidence is not represented as newly computed.

### G9 Failures and reserves

- **external_equipment**: ACCEPTED (decision 2026-10-31).
  - Basis: External equipment (rev 7, ENGINEERING_ASSUMPTION): 55 parts from the inventory's 13 item types. Items with a ledger line are located inside it (sensor turrets in mission systems, RF arrays, laser terminals and aft trackers in the avionics racks, forward trackers in the bow sensor ring, service ports in the service arm, vents in life support, the docking target in the collar): 1.88 t, no new mass. New hardware (crawler docks and points, grapple fixtures, EVA rails): 1.42 t from the reserve. Not built: drone_bay HOLD; nav_lights OPTIONAL; crawler_rails NOT YET. Masses are 2026-analogue allowances to be sized.
  - Accepted as: editable 1.4208t new allowance within dry reserve (2026 analogue guess), 0t sensitivity case required; item positions not frozen

### G10 Flight dynamics: RCS, torch, Metric, Loom

- **torch_tvc**: ACCEPTED (decision 2026-10-26).
  - Basis: Torch thrust-vector control: the magnetic nozzle steers the thrust line by up to 1.0 deg (asymmetric coil current). Needed: trim plus an assumed 0.5 deg thrust error (0.843 deg). The error is an engineering assumption, not a measured disturbance history; the authority is not a qualified nozzle capability.
  - Accepted as: Declare 1 deg of torch thrust-vector authority (decision 2), on the assumed 0.5 deg thrust error.
- **rcs_axial_plumes**: ACCEPTED (decision 2026-11-01).
  - Basis: Axial RCS: one 25 kN thruster per cluster, canted 10 deg outward (bow ones exhaust forward, aft ones aft). Assumes the plumes clear the crown glazing, hull, hot fins and torch chain; plume impingement is not yet modelled.
  - Accepted as: kT accepts axial RCS plume clearance as DECLARED, not a new physical plume impingement calculation. Original 10° canted one-nozzle-per-cluster assumption remains.
- **g10_burn_coasts**: ACCEPTED (decision 2026-11-01).
  - Basis: Long torch burns split into segments of at most 165 min ([V2 6113]) with 15 min coasts (engineering assumption; in free space the coasts change elapsed time, not delta-v).
  - Accepted as: kT accepts segmented burn doctrine as DECLARED: ≤165min torch burn segments with ≥15min coasts. Coasts add elapsed time, not free-space delta-v. This is not Metric travel qualification.

### G12 Images

- **kT_visual_acceptance**: ACCEPTED (decision 2026-11-01).
  - Basis: Required before treating rendered representation as accepted design evidence; generated images meet source/hash coverage only
  - Accepted as: kT reviewed and ACCEPTED the viewer and render set stamped with geometry SHA256 5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256. Source/provenance G12 passed; this is visual acceptance, not pressure/material or occupied-body physical validation.

## Proposed main landing — NOT EXECUTED

1. Obtain kT authorisation for **a separate main-based integration PR**. PR #435 currently targets the pinned Rev7 PR #432 commit rather than protected main. Do not retarget or merge blindly.
2. Pin this geometry, the 18 declared acceptances, FQ1–FQ10 conditional lab campaign, FQ10 0.2s safing, power OPEN, source-hash-stamped image/GLB evidence and the kT-rejected/parked Metric/Navigator scopes as release manifest.
3. Create an integration branch from fresh origin/main, which already incorporates I4 from main commit f07354f. Replay and reconcile the qualified conventional source changes, resolving existing I4/main source overlaps deliberately. Preserve main authority and other projects.
4. Rebuild geometry bit-for-bit, rerun G1–G12, verify all 18 declarations, reproduce/check the relevant flight evidence against the intended hash, verify the render manifest, run existing CI and independent reviewer/loom-gate checks. If geometry changes in integration, reopen all hash-sensitive evidence.
5. Only after approvals merge the **conventional lab-qualified baseline** to main. Do not imply physical flightworthiness, Metric arrival or Navigator readiness from that merge. Keep PR #435 as historical review evidence.

## Proposed single wayfarer/ home — NOT EXECUTED

Create a separate, subsequent path-only migration PR after landing. Proposed root: wayfarer/ with config/, geometry/, flight/, habitat/, thermal/, qualification/, render/, docs/, results/, and adapters/. Map current design/wayfarer/v0.5.7 and src/wayfarer_* and related frontiers into an authoritative manifest. Do not duplicate active authority. Preserve stable imports and paths using compatibility shims, migration maps and old→new provenance links. Run byte/hash, import, reproduction, build, CI and external-dependency checks. Navigator adapters remain non-authoritative; Metric arrival work remains HOLD. Do not move any file until migration is separately approved.
