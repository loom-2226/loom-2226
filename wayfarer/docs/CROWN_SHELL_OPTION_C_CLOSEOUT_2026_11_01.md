# Wayfarer Option C — kT deeper domes, committed-mass G6, protected-water redistribution

ALL bodies. ALL sponsors. 2026–2226.
**ENGINEERING DRAFT / PR #439 / NOT MERGED.** Metric arrival HOLD; Navigator EXCLUDED; independent ship electrical/thermal power budget OPEN.

## Current geometry and authority

- Current geometry SHA256: `7f620c53ca58fb3bc7b421baf15ce3979e4347bef675f2e5be3b57699b633fa7`.
- kT ADOPTED: original Option C outer surface (+1.2m bow extension, flat r≤2m, 50° faceted annulus r2–3.5m), 37 replaceable 10mm ceramic bumper panes, 16 Strata gore closures, and two independent ~7m 28mm transparent-ceramic pressure domes with the primary apex **X −0.30m**, backup apex **X −0.42m**.
- kT also DECIDED: hatches normally open/passively L1-outflow seated, and water redistributed from the existing protected inventory. Unqualified design choices are not physical proof.
- Dome meridian preserving the original r=3.5m joining circle: `X(r) = 3.043118226826 − 3.343118226826 sqrt(1−(r/4.3)^2)`, primary; backup translated −0.12m axially. New area 45.037m² each vs 41.383m² prior.
- Idealised apex pressure membrane stress, 101.3kPa and 28mm ceramic: **15.56 → 10.00MPa**. This is a thin-shell apex comparison only; edge stresses, differential pressure testing, monolith fabrication and gel-mediated failure remain unqualified.
- Axial central stand-off from exterior protective surface to primary dome becomes **0.90m** (prior 1.40m); to backup dome **0.78m** (prior 1.28m). Near the glazed rim r=3.5m, exterior-to-backup stand-off remains about 0.39m. The Pilot/Captain optimistically unoccluded 60° field remains unchanged in the source sightline screen.
- Charged additional physical ceramic across both domes: **0.767304t** (0.383652t per shell) deducted from the engineering reserve. AOI remains a separately charged 3.000t optical interlayer with **zero** shielding/impact/thermal attenuation credit; cavity fill and fast-fracture mechanics remain physical holds.

## Why the old G6 pass was not valid

`build_v05.py` distributed all unused growth reserve across existing dry components as virtual mass for CG/inertia. The G6 shelter and berth ray routines then treated those augmented part masses as shielding material. Consuming reserve for forward Option C hardware thus lowered computed L3 shielding without changing the real L3 hull. This defect also applies to the prior main geometry `5d73cdd1`; **this branch fixes the common G6 code path but does not mutate main**.

G6 now uses a single `committed_shield_fraction` / `committed_shield_mass` rule shared with the supplemental 36×600 berth-ray screen: ordinary dry part mass is stripped of the distributed, uncommitted growth allowance; physically charged reserve-funded equipment and actual protected water keep full mass; AOI gel gets zero credit. The ship's mass/CG ledger continues carrying the uncommitted reserve separately. No threshold waiver or a physically invented shielding material.

The 0.600t non-physical L3 liner provision was removed. A full corrected baseline rerun, **36 sample points ×600 directions = 21,600 S5 rays at 0.02m step**, without newly redistributed water, returned **38.59g/cm² minimum / 13 sample points below 40g/cm²**. Weak paths included:
- L3-CAPT@15, x6.45/r3.85: 38.59, direction (−0.145,+0.985,+0.089).
- L3-CAPT@15, x6.45/r2.25: 38.86, direction (−0.268,+0.580,+0.769), crossing forward of the old berth ring.
- L3-CB@311, x7.55/r2.25: 39.30, direction (+0.785,−0.584,+0.207), leaving through the service section.

## Real water closes those paths

Only **3.058770t of already protected water** moves from the service reservoir; no extra water and no dry liner:

| Tank | Physical volume = water t | Source geometry |
|---|---:|---|
| Berth-wall extended, continuous utility gap | 2.829695 | X 5.5–8.2m; r4.15–4.19m, full 360° |
| Small aft service-wall return | 0.229074 | X 14.5–16.5m; r4.36–4.39m, θ150°–200° |

The forward extension intercepts the captain's bow-oblique ray, while the narrow service-wall return intercepts the aft-oblique crew-cabin ray. The latter would not be protected merely by thickening the L3 circumferential wall. Source-geometry envelopes and quantitative ray intersections were checked; full plumbing, tank retention, puncture and equipment clearances remain mechanical design assumptions.

The final source-integrated S5 screen, on hash `7f620c53…`, returns **42.59g/cm² minimum, 0 of 36 points below 40**, at 21,600 actual computed rays; the worst is L3-CAPT@15 x6.45/r3.85, direction (−0.145,+0.985,+0.089). The node-faces-open hostile sensitivity returns **19.96g/cm², 27 of 36 points below 40**: metric node faces must remain armour equivalent, not open bores.

The protected water remains **50t total**, allocated approximately: 16.483t storm-shelter jacket, 8.534t L3 berth-wall/ring/collar, 0.229t service return, 24.750t service protected tank, and 0.004t protected C-tank. These are still protected drinking/storm-reserve water by model intent; piping and emergency draw accessibility are not independently hardware-qualified.

G6's separate three-point shelter screen uses 600 directions per point in S5 and reports **53.4g/cm² minimum** (threshold 40). Weakest shelter path starts at (9.0,0.0,3.65), toward (+0.11,+0.18,+0.98). This is a mass-column screen, not particle transport or a biologically validated dose estimate.

## Hatches, views and standoff

- Two existing **0.15t each** L1/L2 hatch leaves remain normally OPEN and upright beside the 0.8m ladder wells. The passive hinge opens aft (+X) but must close toward the L2-side seat at X3.0m under **L2→L1 gas outflow (−X)**. Differential pressure then assists seating; no sensor, electrical motor or controller. The same hardware/mass allocation remains.
- Reverse L1→L2 outflow is **not automatically isolated** by this check-valve-like arrangement. Hinge torque, impact stops, leak tightness, chatter and high-pressure time response remain unqualified; no claim of bidirectional full-differential seal has been earned.
- Source G7 checks the two parked hatch envelopes, 0g rigid-litter end-first shaft access, walkway, couches and optimistic eye rays. Six I4 sightline fractions after dome deepening: PILOT 1.000, NAV 0.853, S1–S4 1.000 (unoccluded upper-bound ray screen). Actual glazing refractive properties and blocked sightlines remain OPEN.
- The shell is **Whipple-like standoff**, NOT a tested Whipple shield: 10mm replaceable outer ceramic bumper tiles; an exterior vacuum stand-off region varying approximately 0.39–1.16m axially to the backup dome (not a uniform gap); two independent ceramic rear pressure shells. No calculated hypervelocity penetration limit or AOI impact credit.
- Crown-open speed and bow-to-flow angle remain *visible variables set to null/UNQUALIFIED*. The governing operating doctrine remains low-speed **OR** bow-away-from-dust-flow, otherwise gores closed; closed for torch, particle event, radiation belts and Metric. Unqualified values do not authorise opening.

## Mass, qualification, stopping condition

- Final dry ship mass approximately **867.681t**; S1 departure approximately **1167.681t**. RCS and torch protected remass inventories unchanged.
- Engineering reserve after dome addition and liner removal: **11.784117t**, with **6.784117t available above a mandatory 5t growth floor**. The house reactor / proposed ~5t D–He3 tank may be examined against this *dry-mass* ceiling, not declared a closed power/propellant/thermal design. Neither helium-3 fuel contents nor launch plumbing have been sized here.
- G1/G6/G7 results are source-backed after the rebuilt geometry. Other declared gates retain their existing scope. **This report does not itself certify the design, accept the held declarations, or authorise a merge.**

Remaining qualification closure items: passive hatch physical closure/sealing, quantitative crown-open environmental limits, kT current-hash visual acceptance, independent reviewer/loom-gate as prescribed by existing workflow. Materials, AOI shock independence and radiation dose remain declared technology/failure requirements, not demonstrated.

## Fresh FQ1–FQ4, same current hash

The initial attempt with system Python lacked `scipy`, exited 1 and revealed the qualification wrapper could read pre-existing output JSON as though it were fresh. The wrapper now *deletes* old run files and insists on (a) worker exit 0, (b) the exact current SHA, (c) correct remass state and dt, and (d) 39 actual rows per worker; no output is accepted from a failed worker.

A genuine rerun using an existing isolated SciPy-capable flight-lab interpreter on `7f620c53…`, `dt=0.2s`, returned **full 39/39 and half 39/39 (78/78 total)**, both worker exits **0**. By gate: FQ1 6/6, FQ2 48/48, FQ3 12/12, FQ4 12/12. Read `lab/flight_qual/fq_current_option_c_20261101/FQ1_FQ4_CURRENT_SUMMARY.json` and the two underlying per-state source-hash-stamped matrices. These tests are conventional numerical only, not FQ5–FQ10, Navigator or Metric arrival.

## Final source-hash certificate and G12 visuals

After the full source render and two-scene GLB export, the certification script was rerun on final geometry `7f620c53ca58fb3bc7b421baf15ce3979e4347bef675f2e5be3b57699b633fa7`. **G1, G2, G3, G8, G11 PASS; G4, G5, G6, G7, G9, G10, G12 PASS-DECLARED**. The renderer's manifest contains **31/31 current-hash files** (no stale/missing entries), including full exterior/cutaway/deck sets, equal-scale crown section PNG/SVG, phone 3D viewer and source-hash-stamped two-scene `wayfarer_I4_in_out_7f620c53.glb`.

The machine correctly remains **`certified=false`**: active declaration keys `l1_l2_pressure_hatches`, `crown_option_c_open_limit`, and `kT_visual_acceptance` remain **AWAITING**. Unproven hinge/seal physics, quantitative environmental limits, and aesthetic/source-interpretation acceptance are not turned into PASS by an image. Do not merge.

The conventional FQ1–FQ4 78/78 and this final G1–G12 certificate both use the same immutable geometry SHA. Main `5d73cdd1` is known to share the reserve-as-shielding defect but is **not modified by this PR**; only this branch's shared shielding logic has been fixed and tested.
