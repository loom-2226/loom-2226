# Wayfarer render-review fixes: S4 clash, corrected labels, RCS 40 s trace, G7/G12

ALL bodies. ALL sponsors. 2026-2226.

**STATUS: NON-GOVERNING ENGINEERING EVIDENCE. PR #435 DRAFT/HOLD. kT visual acceptance is pending.**

## Source provenance and mutation limits

- Pre-review geometry SHA256 `ea1fcb59f1e0a127cd48dc4e0321e7d42247e3f2e445cf89893bdefadb793266`.
- **New source-built geometry SHA256 `5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256`**. All new media and current FQ diagnostic refer only to this SHA.
- The sole intended geometry edit is I4 floor station S4 **+0.20m transverse +Y**, centre `(2.20,-1.70)m -> (2.40,-1.70)m`. No terrace chamfer, no new slab/structure/crew mass, no RCS nozzle changes.
- Current geometry dry mass `867.681453467t`, full-remass S1 mass `1167.681453467t`, CG `[24.400485908248697, 0.024564931284559256, -0.3571403252830638]`m; S1 tensor is in the checked geometry JSON.

## S4 spatial clash, tested in G7 as actual 3-axis boxes

- S4 contoured couch nominal 1.58m long, 0.7m wide. Conservatively bounded by **x [2.50, 2.95], y [1.7541, 3.0459], z [-2.7825, -0.6175]m**; terrace slab **x [2.41, 2.51], y [-1.70, 1.70], z [-3.01, -0.91]m**.
- X ranges overlap 0.010m and Z ranges overlap 1.8725m, but **Y ranges are separate by 0.0541m**. Solid AABB volume intersection FALSE. S2/S3 also checked. This is intentionally conservative 3D couch-vs-terrace geometry, **not** a suited human-swept/body-frame collision, buckling, attachment or 4g egress qualification.
- **All 8 G7 bounded I4 checks PASS**; 0.8m floor walkway and 1.2m terrace crawl threshold remain met. Terrace corner axial shell clearance is 1.339m. The optional terrace chamfer was **not built**.

## Corrected visual captions, independent limits

- `cmd_cutaway` now distinguishes **Pilot and Captain/S1** on the raised command terrace from a **separate NAV** station.
- Terrace is **0.59m above the L1 floor**, not the earlier obsolete 1.78m caption. Stale flight-deck wording removed from cutaway labels.
- **4g** is the crew manoeuvre limit in burn and command captions and interactive viewer; **5g** remains the structural screening value, not the crew operational limit.

## RCS 40-second diagnostic, exactly one new run

- 40s **180-degree pitch flip**, state S1 at new source mass properties with 1.96km/s water exhaust, dt=0.1s. Per-nozzle realized thrust samples recorded at 400 integration steps. This is a specific diagnostic **not** a repeat of all FQ1-FQ10.
- **Observed maximum simultaneously firing (>1N realized thrust): 9 nozzles, at t=20.00s**.
- Nominal per-thruster minimum combined water conditioning+jet energy: 57.663MW at full 25kN; **conservative active-count × nameplate allowance = 518.969MW**.
- Actual-thrust-proportional ideal peak in this flight trace = **244.456MW**. Real plant electrical output, transient ramp, concurrent heater operation, efficiency and rejection are not demonstrated.
- **Installed ceiling: 32 × 57.663MW = 1845.224MW**, NOT the observed peak.
- Water consumed `1405.608kg`, terminal attitude error `0.001615°`, numerical result `pass`.
- Sources: `flight_qual/fq_20261031/RCS_40S_PEAK_TRACE_2026_11_01.json`, `RCS_40S_PER_NOZZLE_TRACE_2026_11_01.json.gz`, updated `RCS_POLICY_DECLARATION.json`.

## Regenerated visual deliverables

- All **17 current-manifest artifacts** contain SHA256 `5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256`; old-hash images excluded. One new `wayfarer_I4_in_out_5d73cdd1.glb` has exterior and I4 interior scenes in the accepted viewer architecture.
| Type | Current-hash items |
|---|---:|
| exterior | 4 |
| cutaway | 2 |
| command | 4 |
| deckplan | 6 |
| viewer | 1 |

**All current images are visually stamped with the source SHA**. Deck L1-L5 plans use new S4 coordinates. Metric remains a static configuration view only; no Metric physics code changed.

## Final `certify.py` rerun

| Gate | Verdict |
|---|---|
| G1: Mass and fluids ledger | **PASS** |
| G2: Torch and reach | **PASS** |
| G3: Balance and attitude | **PASS** |
| G4: Power and heat | **PASS-DECLARED** |
| G5: Structure and loads | **PASS-DECLARED** |
| G6: Radiation | **PASS-DECLARED** |
| G7: Compartments and crew space | **PASS-DECLARED** |
| G8: Shuttle, drones and bay exit | **PASS** |
| G9: Failures and reserves | **PASS-DECLARED** |
| G10: Flight dynamics: RCS, torch, Metric, Loom | **PASS-DECLARED** |
| G11: Canon fit | **PASS** |
| G12: Images | **PASS-DECLARED** |

**certified=false**. G12 is expected PASS-DECLARED for source-complete images, not automatic kT aesthetic acceptance or hardware flight qualification. No 3D occupant test or full FQ1-FQ10 replay on the new hash was authorised.

## Full machine-declared assumptions (unabridged)

### G4 Power and heat
**torch_heat** · kT ACCEPTED

Torch heat package (kT, 2026-10-25): each pellet is wrapped in a shell of remass that soaks up the burn and leaves as exhaust. The shell must let no more than ~358 ppm of the burn's energy escape as light, counting its own glow (the reactor face's 10 MW/m2 limit); the design value is 180 ppm. With the model's other assumptions (torch/torch_heat_inputs.json: light 40% of fusion energy; He3-rich, spin-polarised fuel with 0.76% neutrons, 85% absorbed by the shell; plume contact 1e-4 of charged energy; coil shield transmission 1e-3), 1.40 GW reaches hot structure and 0.48 MW the magnet coils at 12.6 TW of fusion. These are assumptions, not results. Replaces v0.5.1's 387 MW (34 ppm) torch-leak gap.

**torch_fin_temperature** · kT ACCEPTED

Hot fins run for life at 1750 K. Lithium heat pipes have run in lab tests to ~1,500 K and briefly ~1,800 K; years at 1750 K with burn cycling and neutron exposure is an engineering extrapolation (a technology milestone), not new physics. Fallback: 1,500 K fins, ~49 m span, ~30 t, still inside the reserve.

**plant_power** · kT ACCEPTED

Plant electrical: Metric HARD at a 1300 K reject temperature needs 34.8 MW of cryo-chain electrical power, against canon's 23.9 MW at 900 K. The relational plant must supply this (canon amendment), or the cryo chain must reject through a 900 K loop.

**cold_running** · kT ACCEPTED

Cold running (rev 7, F5 provisional item F5-TE-01): the tunable flanks drop from emissivity 0.85 to 0.1, so at the same skin temperature they radiate 12% as much. Heat is held, not removed: habitat heat 58.1 kW (x1.25), plus plant standby 10.0 kW and cryo standby 10.0 kW, less 7.1 kW still leaking through 177 m2 of low-e skin at 290 K warms the 50 t of protected water by 15 K in about 12.3 h (ideal no-standby ceiling 17.1 h). ENGINEERING_ASSUMPTION (screening placeholders 10+10 kW, NOT sourced or qualified); editable, replace with measured/engineering budget. Then the ship must open the strakes or switch the flanks back to normal. Detailed load-cycle variation, cryo plant duty, tank thermal coupling, and reserve storage remain open. The metallic look in the viewer is a proposed optical property.

### G5 Structure and loads
**i4_terrace_mounts** · kT AWAITING

I4 terrace 4 columns sized as 7075-T6 76mm OD x 3mm at 0.49m. 5g x1.5 ultimate +0.5g lateral member screen, no joint, deck bearing, vibration, fatigue, swept-body or 3D egress qualification. HOLLOW: closed only for column members, not system.

### G6 Radiation
**berth_viewports** · kT ACCEPTED

Berth viewports (v0.5.7): 10 x 0.5 m viewports keep the berth screen because acrylic plugs carry at least the g/cm2 they replace (armour 27.14 vs 27.0, ring 8.26 vs 8.0), so the ray screen, which treats the hull as continuous, is unchanged. Rev 3: the same plug kit is in every opening below the crown, including the L2 viewport band, and continues through the storm-shelter jacket (17 cm more acrylic for the 20 cm of water). Not yet shown: the dose. Acrylic is ~8% hydrogen by mass against water's 11%, so per g/cm2 it may stop cosmic-ray secondaries slightly less well; a transport check may ask for a thicker plug. Encapsulated for fire.

**crown_dome** · kT ACCEPTED

Crown dome (v0.5.7): 25 m2 of glazing inside r 2.8 m replaces the 8 nose windows. Assumes (1) proof-tested transparent ceramic panes up to 2.3 m across (2026's largest are ~0.76 m), a 2226 materials milestone like the 1,750 K fins (rev 4: the L2 viewport band's 16-18 mm plate panes rely on the same ceramic; 2026 ALON would need 25-29 mm); (2) tambour gores of armour-equivalent Strata laminate (Builder-derived, MHL-22) that restore 27 g/cm2 when closed and stow in the brow ring; (3) the operating rule: open only at low speed or with the bow facing away from the dust flow (braking and tail-first coasting); closed for solar particle events, radiation belts, torch burns and Loom formation and translation. Stuck closed is safe; stuck open: turn the bow out of the dust flow. With the gores open, L1 loses the armour over the crown (glass 2-9 g/cm2); L1 is not a shelter.

**strata_armour** · kT ACCEPTED

Habitat armour face (rev 7, kT 2026-10-26): Strata laminate (Builder-derived, MHL-22) over the whole habitat armour, x 0-14. KT_ACCEPTED 2026-10-31 as visible armour face; materials constitutive/physical performance remain OPEN; no changed shielding/mass claim. Bow x 0.0-2.6 m: bare Strata: the erosion face meets the dust flow.

**node_faces** · kT ACCEPTED

Metric node faces (rev 7, kT 2026-10-26; Sol: AGREE, placement HOLD): 208 visible flush or recessed faces, 13 rings x 16 at 22.5 deg (rev 5 longeron-study layout). 76 are clear; the rest are flagged: 16 faces dust flow bow first, 12 on bay door, 80 on torch chain, 1 overlaps camera, 2 overlaps hold door, 1 overlaps window, 20 under stowed strake. The design case assumes every face carries at least the armour's g/cm2 it replaces, like the berth-viewport plugs. Sensitivity, faces as open bores through the armour: berth screen 14.78 g/cm2 (30 of 36 berth points below 40) and storm shelter 36.3 g/cm2. So a face must be armour-equivalent: materials, cover, seal and mount stay OPEN, and no dust check exists in the basis yet (faces flagged 'faces dust flow' meet the flow when coasting bow-first). Node stations are not moved for the look; PR #184 stays OPEN.

**shelter_life_support** · kT ACCEPTED

Storm shelter life support: 72 h for 10 people from the life-support room on the same deck (design provision, not computed).

**gcr** · kT ACCEPTED

Galactic cosmic rays: at 2026 free-space rates (1.8 mSv/day, ~657 mSv/yr) a crew member reaches NASA's 600 mSv career limit after ~333 days in deep space. Hull shielding barely changes this. Long careers aboard rely on canon's off-Earth MED-MOD-RADIATION milestone and crew time-in-space rules; this is a canon question, not something the hull can close.

**torch_neutrons** · kT ACCEPTED

Torch neutrons and gammas: the shadow shield must attenuate the torch's neutron and gamma output so the dose rate inside the habitat during burns stays within crew limits. The v0.5.2 heat model puts neutrons at ~0.76% of the burn's energy with 85% absorbed by the remass shell; the dose itself is not computed here, only the shadow geometry is checked.

### G7 Compartments and crew space
**i4_human_factors** · kT AWAITING

I4 source-frame check rerun against current geometry. Scene seat length 1.58m <2.10m source crew envelope; 2D seat/ladder/walkways and bare dome clearances NOT physical 3D access or 4g qualification. Crown sightlines are optimistic upper bounds only. All three annulus-floor couches now clear the rectangular terrace in a conservative 3D axis-aligned box test; S4 is moved +0.20m outboard with 0.0541m clearance. This is not occupant-swept collision testing. Optional terrace chamfer NOT BUILT.

### G9 Failures and reserves
**external_equipment** · kT ACCEPTED

External equipment (rev 7, ENGINEERING_ASSUMPTION): 55 parts from the inventory's 13 item types. Items with a ledger line are located inside it (sensor turrets in mission systems, RF arrays, laser terminals and aft trackers in the avionics racks, forward trackers in the bow sensor ring, service ports in the service arm, vents in life support, the docking target in the collar): 1.88 t, no new mass. New hardware (crawler docks and points, grapple fixtures, EVA rails): 1.42 t from the reserve. Not built: drone_bay HOLD; nav_lights OPTIONAL; crawler_rails NOT YET. Masses are 2026-analogue allowances to be sized.

### G10 Flight dynamics: RCS, torch, Metric, Loom
**torch_tvc** · kT ACCEPTED

Torch thrust-vector control: the magnetic nozzle steers the thrust line by up to 1.0 deg (asymmetric coil current). Needed: trim plus an assumed 0.5 deg thrust error (0.843 deg). The error is an engineering assumption, not a measured disturbance history; the authority is not a qualified nozzle capability.

**rcs_axial_plumes** · kT AWAITING

Axial RCS: one 25 kN thruster per cluster, canted 10 deg outward (bow ones exhaust forward, aft ones aft). Assumes the plumes clear the crown glazing, hull, hot fins and torch chain; plume impingement is not yet modelled.

**g10_burn_coasts** · kT AWAITING

Long torch burns split into segments of at most 165 min ([V2 6113]) with 15 min coasts (engineering assumption; in free space the coasts change elapsed time, not delta-v).

### G12 Images
**kT_visual_acceptance** · kT AWAITING

Required before treating rendered representation as accepted design evidence; generated images meet source/hash coverage only


## Boundaries

- PR #435 remains draft/HOLD, no merge to main. No Navigator, Metric physics, repo migration or downstream card adoption.
- FQ10 remains conditional on detector/torch-cut within 0.20s and plant MW delivery; geometric seat move has not been subjected to another full FQ matrix.
- This report supersedes the earlier render-track acceptance report only as to geometry SHA, views, G7 clash and measured RCS peak; older engineering decisions remain recorded in history.
