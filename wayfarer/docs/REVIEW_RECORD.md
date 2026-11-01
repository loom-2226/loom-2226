# Wayfarer v0.5.7 review record

ALL bodies. ALL sponsors. 2026-2226.

An append-only log of reviews and decisions; it is the audit trail for Sol and loom-gate. Newest entry last.

## Rev 5 (2026-10-26)

NON-GOVERNING. Not canon, not runtime, not certified. G10 Navigator remains OPEN and deliberately held. PR #430 unchanged.

kT approved the existing rendered views on 2026-10-26. Visual acceptance does not waive the G12 requirement for images to be generated from and stamped with the rev 5 geometry.

Rev 5 corrections: (1) 84.2 mm nominal longeron wall and 0.237 t end fittings, (2) G5 real structural area plus axial/bending check, (3) compliant Ti ring-to-shell flexure fingers and 50 K thermal fatigue assumption. Ledger split longerons 11.862 t + joints 3.476 t + released reserve 19.662 t = 35.000 t, preserving the dry mass.

Local build geometry SHA-256 `1cb0a96412b721c1bf75d6d094182c02091cb6b2716260c6590d2d986f8db21f`, differs from reference `ed692f90d49a2d8aa9f25a4dfc48b4a4410680e4accc77f7938a027952f8e1bf`. Exact source parity is not asserted. Local checks G1-G9 and G11 PASS/PASS-DECLARED, G10 OPEN, G12 stale-image FAIL before rerender. Do not claim certification.

## Update 2026-10-26: source parity reached, G12 closed

kT chose route 2: adopt Claude's rev 5 reference build byte for byte. This directory now holds that build. Its inputs and code reproduce geometry SHA-256 `ed692f90d49a2d8aa9f25a4dfc48b4a4410680e4accc77f7938a027952f8e1bf`. All 29 images and the viewer in `render/out/manifest.json` are stamped with that geometry, so the fingerprint discrepancy above is closed.

Re-run inside this directory (build, L1 study, habitat overlay, certify): G1-G9, G11 and G12 PASS (G4 and G6 PASS-DECLARED, every declared item ACCEPTED by kT); G10 OPEN and held; `certified` false.

Key values: dry 867.68 t; longerons axial + bending 248.3 MPa (limit 250); ring flexure fingers 116.3 MPa (fatigue limit 200); berth screen 40.63 g/cm2; worst trim 0.348 deg; reserve 51.6 t.

Still NON-GOVERNING: no canon promotion, no runtime integration, PR #430 unchanged, nothing merged.

## Update 2026-10-26: G10 v0.2 basis agreed by Sol; G10 FAIL 19/24

G10 v0.1 (Navigator missions) was replaced by G10 v0.2, a set of flight-dynamics tests: `../g10/g10_flight_dynamics.py` and `../g10/CERTIFICATION_BASIS_v0.2_G10.md`. They reuse main's `src/` modules (main 19377b85).

Sol's first review of 318ac4b raised four places where the tests claimed more than they checked. All four were fixed at b1d50de. Sol then re-ran `certify.py` from the repository root in an isolated checkout at b1d50de, reproduced the result (G10 19/24, FAIL; the 11 other gates PASS or PASS-DECLARED; geometry `ed692f90…f8e1bf`), and recorded his disposition: **AGREE, as a proposed engineering certification basis**. The basis stays NON-GOVERNING and is not promoted to canon.

Five G10 failures remain open:
1. Torch thrust: the ship card and `MODE_CARDS` disagree by 122%. Which one governs is HOLD for kT.
2. Torch thrust-vector authority is not declared. 0.847° is needed if the assumed 0.5° error holds. HOLD for kT.
3. RCS cannot hold attitude against the torch error (18.74 vs 3.08 MN·m). This follows decision 2.
4. There are no axial RCS thrusters (x translation 0 kN). HOLD for kT (rev 6).
5. Loom configuration is not declared in the card (2 of 5 items: the strake Loom span, crown Loom state and collar state are missing).

`certified` is false. PR #430 is unchanged; nothing merged; loom-gate neither bypassed nor modified.

## Rev 6 (2026-10-26): kT's four propulsion decisions, one folder

kT: "agree 1-4", and keep only current files. Old revisions live in git history; rev 5 is commit `ef1b871`.

**Decisions**
1. Main's torch working card governs. The ship holds jet power to the 11.361 TW its heat rejection is sized for.
   - The rev 5 card's FAST, HARD and LIMIT thrusts were already exactly that ceiling.
   - The real change is ECON: 3.41 MN at 5.11 TW, not 7.57 MN. Burn times change; Δv does not.
2. 1° of torch thrust-vector authority (declared `torch_tvc`, ACCEPTED).
3. One axial RCS thruster per cluster: 8 x 25 kN, canted 10° outward, 4.0 t from the reserve.
4. The Loom configuration is declared in the inputs and card: strakes span 0, crown gores closed, docking collar free.

**Result**
- Geometry `a534c6b6...c2277d8`; dry 867.68 t; reserve 47.6 t; worst trim 0.346°.
- Minimum berth screen 40.45 g/cm². This is lower than rev 5's 40.63 because the smaller reserve spreads less onto the armour; the limit is 40.
- G1-G9, G11 and G12 PASS (G4 and G6 PASS-DECLARED).
- G10 PASS-DECLARED, 25/25 checks.
- New declared items awaiting kT: `rcs_axial_plumes` and `g10_burn_coasts`.
- `certified` stays false until both are accepted, the reviewers sign and loom-gate passes.

**Consolidated into one folder**
- Rev 5 moved up into `design/wayfarer/v0.5.7/`.
- One spec (`SPEC.md`), one basis (`CERTIFICATION_BASIS.md`, v0.2 with G10 merged), one amendment draft (`PROPOSED_CANON_AMENDMENT_v2.4f.md`) and this record.
- Removed:
  - `candidate/` (rev 4) and `reviews/`;
  - superseded documents for v0.5.1-v0.5.6 and rev 4;
  - amendment v2.4d and v2.4e;
  - study write-ups and figures whose results now run inside the gates;
  - the concept images;
  - the v0.5.6 comparison set;
  - the unbuilt nose windows.
- `compare/previous/` now holds rev 5 only, for the viewer's toggle.
- Stale labels fixed: the L1 section and deck plan still said "nose windows"; the viewer said 0.35 m berth viewports.

Still NON-GOVERNING: no canon promotion, no runtime integration. PR #430 is unchanged, nothing is merged, and loom-gate is neither bypassed nor modified.

## Rev 7 (2026-10-26): the skin, node faces and external equipment

NON-GOVERNING engineering candidate. Built by Claude after Sol's design agreement; Sol reviews the build. No canon promotion, no runtime integration, no gate bypass, PR #430 untouched.

**kT's decisions** (recorded in `inputs/kt_decisions.json`, `design_decisions_2026_10_26_skin`)
1. Low signature is a skin criterion.
2. Open an F5 Frontier item for tunable emissivity: `engineering/frontiers/F5_TUNABLE_EMISSIVITY_ITEM_v0.1.md` (F5-TE-01, PROPOSED; not entered in the register).
3. The metric nodes show on the hull: all 208 (option 3).
4. The habitat armour face is Strata.
kT: "I want sol to agree with the design choices. I want you to handle making it."

**Sol (2026-10-26): AGREE 1-6**, with two qualifications carried into the build:
- Cold running must account for retained heat; no heat sink, no radiative multiplier; the mirror look is a proposed optical property.
- Node faces join the dust and radiation checks as discontinuities; they are not qualified penetrations; stations are not moved for the look (PR #184 OPEN).
- The inventory is a draft requirement: allocate new mass against the reserve, reconcile existing equipment, keep the drone-bay and node-placement holds.

**What was built**
- `inputs/`: `skin` (Strata habitat armour, bare Strata bow x 0-2.6, tunable flanks with normal 0.85 / cold running 0.10 emissivity, seams on the frames and node rings), `node_faces` (13 x 16, 0.35 m, HOLD), `external_equipment` (13 item types; drone bays HOLD, navigation lights OPTIONAL, crawler rails not yet), `cold_running` (protected-water buffer, 15 K rise).
- `build_v05.py`: 55 external parts; items with a ledger line are located inside it (mass moved from that line's part), only new hardware draws on the reserve (`ledger.reserve_draws_rev7`, 1.42 t). 208 node faces as geometry features, each flagged for the placement check.
- `certify.py`: G6 berth screen with node faces armour-equivalent, an open-bore sensitivity and declared items `strata_armour` and `node_faces`; G4 declared item `cold_running` with the computed endurance; G9 reserve and equipment-clearance checks and declared item `external_equipment`.
- `habitat/hab_overlay_checks.py`: the berth screen also runs with node faces as open bores (worst case, sensitivity only).
- `render/`: Strata/tunable skin shading, node faces and equipment drawn from the geometry; viewer chips for Strata skin / engineering grey and flanks normal / cold running; stills `ext_skin` and `ext_skin_cold`. `compare/previous/` now holds rev 6.

**Result**
- Geometry `74e22938...dc161271`; dry 867.68 t (unchanged); reserve 46.17 t; worst trim 0.341°.
- Minimum berth screen 40.38 g/cm² (limit 40), down from 40.45 by the 1.42 t of new hardware. The forecast was about 40.4 for that draw.
- Node faces as open bores (sensitivity, not the design case): berth screen 14.78 g/cm², 30 of 36 berth points below 40; storm shelter 36.3 g/cm². So each face must carry at least the armour's g/cm².
- Node faces: 76 of 208 clear; 20 under the stowed strakes, 12 on the bay doors, 80 on the torch chain, 16 facing the dust flow bow-first, 2 on the hold doors, 1 on a window, 1 on a camera. Placement stays HOLD.
- Cold running: 58.1 kW in, 7.1 kW leaking through the low-e skin, about 17 h to warm the 50 t of protected water by 15 K. Plant standby heat is not modelled (OPEN).
- External equipment: 1.88 t located inside existing lines (including their share of growth margin), 1.42 t new; no overlaps with node faces, windows, hatches or doors.
- Every gate PASS or PASS-DECLARED; G10 25/25. Declared items awaiting kT: `rcs_axial_plumes`, `g10_burn_coasts`, `strata_armour`, `node_faces`, `cold_running`, `external_equipment`.
- No dust check exists in the basis yet; the node-face dust flag is reported, not gated.
- `certified` stays false.

## Option C G6 defect closure and kT declared acceptance (2026-11-01)

**Source:** PR #439, expected merged head after protected-water declaration. **Geometry:** `7f620c53ca58fb3bc7b421baf15ce3979e4347bef675f2e5be3b57699b633fa7`.

**Claude review:** reported by kT as verified on PR head `4752913f`; **not** represented here as an independently retrieved GitHub APPROVED review event. **Sol independent numerical review:** corrected G6 excludes virtual growth reserve; full 21,600-ray berth and 1,800-ray shelter source screen passes with 3.058770t of pre-existing protected water shifted to actual shield walls, 0t liner; design-case berth min 42.59g/cm² and shelter min 53.4g/cm², open-node-face sensitivity fails (19.96g/cm²) as intended. Conventional FQ1–FQ4 78/78 fresh/exit-zero; G1–G12 PASS or PASS-DECLARED and G12 31/31 source-stamped assets.

**kT decision:** accepts passive L1/L2 hatches *as declared*, default crown-open policy and Whipple-like standoff with numerical speed/angle variables UNQUALIFIED, visual acceptance on `7f620c53`, and new water reserve doctrine: service tank drawn first, critical L3/shelter shield water last and refilled first. `certify.py` now returns `certified=true` for 29/29 declared items, conventional laboratory basis only.

**Release boundary:** loom-gate exact-head GREEN required before protected-main promotion. No hardware pressure/fragment certification; Metric arrival HOLD, Navigator excluded, independent ship-power closure OPEN.

**Water draw sensitivity qualification:** on unchanged `7f620c53` geometry, 21,600-ray G6 berth min is 42.59g/cm² at service draw 0, 12.375t and 19.750t (5t retained); after all 24.750t service drawn it falls to **39.04g/cm²** with 1/36 berth sample points below the 40g/cm² requirement. **Provisional service hold 5t** pending continuous-fill validation; no claim that service water is radiologically inert or that all intermediate states are qualified.

## House-power budget from protected main (2026-11-01; NEW ENGINEERING CANDIDATE)

**Base:** main `ce9ee0810b7d8e71842a5771dea789e664819a43`, Option C `7f620c53`. kT decisions: dedicated direct-conversion D–He3 house reactor; relational plant only a consumer; Metric bank not energy source; routine 120s RCS from house, emergency ~520MW×40s RCS from charged store; main torch always PULSED, house-mode torch only for emergency; 5t D–He3 wet fuel, dry tank from reserve; declared 2226 batteries.

**Integrated model:** 80MW net house reactor @40kW/kg, 75% direct conversion; 2t reactor and 0.65t 6.5MWh flywheel physically reallocated **inside existing 55t electrical budget**. Flywheel @10kWh/kg, 800kW/kg is speculative, not demonstrated. Fuel tank 0.5t dry debited against reserve; 5t D–He3 wet in S1–S7 physical mass model and segregated from 300t water. Current geometry SHA `49cc20e70f5ad2b39280fa460cec07874a1053ca2a6fed48dda38ca4527d7c6b`. Dry stays 867.681453t; departure S1 1172.681453t; reserve 11.284117t, >5t.

**New results:** G1 PASS (32 checks), G3 PASS (19 checks), G4 PASS-DECLARED (29 checks), all on new source SHA. Actual source-stamped FQ1–FQ4 78/78 from exit-zero full/half test workers, each 39 cases; prior `7f620c53` FQ source artifacts retained untouched under their original folder. The 10-row, per-state electric/thermal budget and source/peak/fuel consumption are in `docs/SHIP_POWER_BUDGET_2026_11_01.md`. Thermal caveats include recharge at ~5.16min energy-only ceiling, Metric-field electrical requirement unquantified, 120s RCS throttling not FQ-traced, cold running down to ~9.41h with house-reactor loss, no steady ship electrical supply if house reactor fails after 24h essential battery.

**Boundaries:** previous accepted full G6 and G12 are only for prior hash `7f620c53`; neither is hereby requalified. This is not a new 12-gate certificate, a hardware reactor/tank/shielding qualification, Navigator, Metric arrival, or a main promotion. Independent review and full source-hash-gated qualification needed before any future integration approval.


## PR #440 redundancy revision, kT decision 2026-11-01 (non-merging)

**Parent:** `42ac3f52eef524fe94c2fba2689f2b313c7be015`. **Revised geometry:** `9544a893d711fb9f9c91b145edeb5137728429315e0c852e1e8beab60da46661`. This version supersedes the preceding 80MW single-house entry in the current engineering branch; historical Git evidence is retained.

kT adopts **two 50MW net D–He3 direct-conversion reactor units**, declared 2226 net specific 40kW/kg and 75% conversion, with 10% **5MW electrical minimum per online unit**. The two units are a single 2.5t grouped equipment/mass envelope in the existing 55t electrical ring; actual independent containment and fault isolation remain physically unqualified. Existing 0.5t dry D–He3 fuel tank remains the sole new dry reserve draw, with 5t wet consumable D–He3 in the ship's mass states. New flywheel 7MWh, 0.7t at declared speculative 10kWh/kg, 800kW/kg, 90% roundtrip. The 3.2t combined electrical hardware is a reallocation of the existing 55t, **not** another reserve debit.

The separate **Metric field/control electrical allowance** is explicitly non-canon, **NORMAL 1MW, FAST 2MW, EXPEDITE 3MW, HARD 5MW** delivered, on top of the canon cryo card and E1 PMAD 0.98×0.96; the governing E1 source leaves environmental correction power OPEN. HARD known load is ~42.655MW upstream including ordinary ship loads, below one 50MW reactor. Pulsed torch magnet/ordinary loads ~47.909MW, below one reactor. Routine 120s flip requires one 50MW unit and ~8.052MW of flywheel output; this is still an unverified 1/t² thrust/duty estimate. Emergency 40s flip draws ~519.358MW from the wheel, energy ~5.771MWh, with about **7.755min** energy-only recharge from one 50MW unit. Do not treat this as a manoeuvre rate; remass and hardware constraints remain.

At zero reactor output, the flywheel supplies **65kW essential quiet/cold load for ~102.17h energy-only**, but the 50t×15K cold-running water buffer takes only ~11.70h before reaching its declared thermal limit. One failed reactor leaves one unit; both failed leave ~17.08h of ordinary power from flywheel; pulsed torch emergency house mode is an **unqualified fallback**, then 0.6kW ×24h shelter battery. Neither Metric bank nor relational plant is a generator, and main torch operation is pulsed.

**Verification:** source-backed 18-state machine/table in `results/out/ship_power_budget.json` and `docs/SHIP_POWER_BUDGET_2026_11_01.md`. Targeted G1/G3/G4 and source-hash-specific FQ1–FQ4 on this new geometry reported separately. Dry mass and centre of gravity did not change; the reallocated grouped electrical-ring components shift source-calculated inertia tensor by ~39.9 kg·m², so earlier FQ results were not copied as current-hash PASS. PR remains DRAFT/UNMERGED; prior G6/G12 physical/radiation/visual acceptance cannot be transferred to the new hash.

## PR #440 battery + lower-density pulse flywheel + C-lite revision (kT 2026-11-01)

**Source:** protected main ce9ee081, parent PR #440 53f0bb59. New geometry `f7dc6b8c69cf56f48a55eeaa1a5daa7779fce3e06474157c960ef2f08cac95f7`; previous geometry hashes and historical signoffs remain evidence only.

kT replaces the 7MWh/0.7t 10kWh/kg sole flywheel with three narrowly scoped 2226 DECLARED resources **inside the 55t loaded electrical allocation**: (1) a 3MWh 1.5t battery at 2kWh/kg, (2) a 1.5MWh 1.5t flywheel at 1kWh/kg and 150kW/kg peak electrical power, with counter-rotating pairs and containment physically DECLARED but UNQUALIFIED in the aft C-ring, and (3) independent C-lite green monoprop 0.25t loaded, of which 0.10t is DRY hardware and 0.15t is WET propellant, up to two idealized 600s/75kg recovery turns. C-lite actual nozzle geometry, thrust/torque and flight response are OPEN, not counted as verified attitude recovery. Reactor design remains two 50MW D-He3 units.

Current-source 40s pitch 180 RCS run: ideal 6.556093GJ total, 252.23438MW actual thrust-weighted peak, 1.450206t water, 9 nozzles concurrent. A 50MW house unit leaves **4.685639GJ = 1.301566MWh flywheel discharge** and 202.623MW electrical peak, within the 1.423025MWh deliverable and 225MW proposed rotor envelope. This uses the sampled trace, NOT 519MW nameplate multiplied by 40s; reactor dispatch, energy transfer, bus/thermal and water heating are not physically qualified.

Battery declared 90% round-trip gives 2.846MWh deliverable; quiet/cold 65kW electrical energy-only duration 43.785h, but existing water thermal screen limits cold to 11.70h. With both reactors gone: one hour 0.389MW ordinary hotel loads then 37.80h 0.065MW essentials, assuming fully charged and physical heat rejection. Pulsed torch emergency house electrical output remains UNQUALIFIED, followed by the separate 0.6kW x 24h shelter battery.

**Half battery + flywheel performance, unchanged installed mass:** battery 1.423MWh deliverable, still one hour ordinary followed by approximately 15.9h essentials; flywheel 0.7115MWh deliverable and 112.5MW maximum. Routine 120s RCS proxy and stationary/Metric/torch-magnet electrical states remain in their arithmetic envelopes, although their independent hardware holds remain. **Fast 40s flip FAILS both supplemental event energy and peak power.** Unqualified torch emergency source also remains UNSERVED regardless of sensitivity. This is a sensitivity failure, not a surprise late hardware pass.

Mass closes without growth-reserve debit: dry 867.531453t; S1 loaded 1172.681453t; electrical dry 54.85t plus wet C-lite propellant 0.15t = 55t provisioned. Growth reserve unchanged **11.284117t**, 6.284117t above 5t floor. Original house D-He3 remains 5t WET and protected water remains distinct.

**Full G1-G12 certification on this new SHA:** G1 40/40 PASS, G2 3/3 PASS, G3 19/19 PASS, G4 46/46 PASS-DECLARED, G5 31/31 PASS-DECLARED, G6 22/22 PASS-DECLARED on refreshed radiation overlay, G7 34/34 PASS-DECLARED on refreshed I4 geometry, G8 13/13 PASS, G9 13/13 PASS-DECLARED, G10 25/25 PASS-DECLARED, G11 1/1 PASS; **G12 FAIL 2/10** because current-hash render/viewer assets have not been regenerated. Thus **certified=false**. No assertion of transferred old render acceptance, physical hardware fitness, Metric arrival or Navigator operation. No merge.

**FQ1–FQ4 current-source result (final):** Full-remass worker 39/39 PASS, half-remass worker 39/39 PASS, both exit code 0, total **78/78 PASS NUMERICAL**, exact matching geometry hash f7dc6b8c69cf56f48a55eeaa1a5daa7779fce3e06474157c960ef2f08cac95f7. Current results in lab/flight_qual/fq_house_power_20261101/FQ1_FQ4_CURRENT_SUMMARY.json. These runs do NOT certify the C-lite chemical nozzle hardware or the 40s RCS power-distribution and heat-transfer hardware. G12 remains FAIL, so certified=false.

## PR #440 storage final-sizing, degraded manoeuvre, separate sources and visual requalification (2026-11-01)

**Source:** protected main ce9ee081; prior PR head d9134f28; revised geometry SHA **4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331**. DRAFT non-canon engineering, DO NOT MERGE. All mass source, traces, state ledger and future FQ/G12 evidence must carry this new SHA; historical passes never transfer.

kT decisions embodied, with no new mechanical or programmatic architecture:
- Pulse flywheel **1.8MWh at 1kWh/kg**, **1.8t**, 150kW/kg maximum, **270MW** peak, 90% roundtrip. Paired counter-rotating assemblies and burst containment are DECLARED inside this mass, hardware OPEN. A single 50MW house reactor feeds the 40s flip; 40s trace gives 1.301889MWh delivered supplemental with 202.653MW pulse peak, versus flywheel usable 1.707630MWh: **31.2% energy margin** at nominal 2226 performance. No misleading nameplate thruster-count×40s electrical budget.
- At HALF flywheel specific energy and specific power, the 40s emergency flip remains OUTSIDE the degraded store envelope. Source-consistent **60s** pitch 180 diagnostic with one surviving 50MW unit takes **0.497488MWh** and **62.508MW** supplemental, versus half flywheel **0.853815MWh / 135MW** limits. **PASS NUMERICAL** with heat/electric bus and control-loop coupling hardware still OPEN. 60s is a distinct actual flightlab trace, not a mathematical time-scaled assertion; it is *not* a two-reactor-dead emergency flip.
- Reactor A **aft C-ring x31.5–32.3m**, reactor B **forward service ring x17.0–18.0m**, independently represented 1.25t nominal mass each. Distinct azimuth sectors avoid overlapping visual equipment proxies, but true shielding, fault containment, converters and wiring separation remain NOT QUALIFIED.
- DOCKED: shore electrical service (declared maximum **2MW**) supplies normal/crown-open loads; both house reactors are OFF. Shore connector and thermal interface are unqualified.
- PULSED MAIN TORCH BURN ONLY: 47.52MW net magnet/cryogenic electric is explicitly tapped from **63.36MW raw torch energy at declared 75% electric conversion**; 15.84MW conversion waste joins rejected heat. Jet/flight model has not yet debited this internal extraction (small relative to TW jet but a genuine scientific closure HOLD). No invented continuous torch house generator.
- FAILURE doctrine: **surviving reactor B → 3MWh rechargeable battery (1h ordinary then 37.8h essentials energy-only) → independent C-lite chemical slow attitude recovery** (not an electrical source). The separate existing 0.6kW×24h shelter refuge battery is not treated as a house generator. No torch emergency-house stage.
- Complete loaded electrical provision remains **55t** (54.85t dry + 0.15t C-lite wet); dry **867.531453t**, loaded S1 **1172.681453t**, reserve **11.284117t** unchanged and above 5t floor by 6.284117t. House D–He3 remains 5t wet separately from 300t water.

Current-source operating ledger (20 states) in `wayfarer/results/out/ship_power_budget.json`, generated by `wayfarer/lab/ship_power_budget.py`. Every modeled electrical row balances. Half-performance energy/power sensitivity closes all electrical screens except the original fast 40s flip; physical qualification remains OPEN and must not be confused with an ideal load match.

**NEW declarations awaiting explicit kT acceptance rather than inheriting prior design verdicts:** (1) 2MW dock shore-power interface rating; (2) burn-only 63.36MW raw to 47.52MW delivered torch magnet-electric conversion at 75%, including 15.84MW heat and OPEN thrust debit; (3) interpretation/visual acceptance of newly stamped reactor/flywheel/battery layout cutaway. These are separate from kT's already given architecture and degraded-doctrine decisions. The locked source geometry hash is distinct from all previous power and crown certification hashes.

**Current geometry FQ1–FQ4 final:** exact SHA 4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331, full-remass worker **39/39 PASS**, half-remass worker **39/39 PASS**, two exit-zero processes, total **78/78 PASS_NUMERICAL** (FQ1 6/6, FQ2 48/48, FQ3 12/12, FQ4 12/12). See the current source-stamped FQ summary, fixture and matrices in `wayfarer/lab/flight_qual/fq_house_power_20261101/`. This does NOT qualify electrical, thermal, chemical backup or power tap hardware.

**Final visual and conventional certification evidence, same exact source SHA:** Regenerated full existing views, one additional power-systems cutaway `wayfarer/render/out/cut_power.png` with colour-coded render-only source parts and labels for reactor A aft, reactor B service, flywheel aft and battery service; rebuilt current I4 interior/exterior GLB and phone viewer. Render manifest **32/32** entries exist and match the final geometry SHA; G12 **11/11 PASS-DECLARED** (including newly added cutaway presence/source evidence). Full `certify.py`: G1 41/41 PASS, G2 3/3 PASS, G3 19/19 PASS, G4 47/47 PASS-DECLARED, G5 31/31 PASS-DECLARED, G6 22/22 PASS-DECLARED, G7 34/34 PASS-DECLARED, G8 13/13 PASS, G9 13/13 PASS-DECLARED, G10 25/25 PASS-DECLARED, G11 1/1 PASS, G12 11/11 PASS-DECLARED. **`certified=false` deliberately:** the three novel declarations remain AWAITING kT acceptance. This is honest source-geometry and conventional lab evidence, not hardware or Metric/Navigator qualification.

**Postscript on legacy inputs:** the three old `ship_power.rcs_40s_ideal_* ` screening fields remain a historic 40-second diagnostic reference in the unchanged source input manifest; the CURRENT authoritative numerical electrical budget is recalculated directly from `RCS_40S_CURRENT_TRACE.json` and `RCS_60S_DEGRADED_TRACE.json` on hash 4d598212. Do not substitute old diagnostic constants for current-geometry trace results. Cleaning the historical input fields would change the source hash and require re-running these exact-source geometry/qualification/render results; no such unrequested source mutation was made.

## PR #440 kT final declarations, tank placement evidence and conventional lab certification (2026-11-01)

**Authoritative kT approval in chat:** 2MW dock shore power (reactors OFF); burn-only 63.36MW torch raw energy at 75% to net 47.52MW magnets (15.84MW conversion waste, flight-thrust debit/real hardware OPEN); and power-bay layout image on exact geometry **4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331**. These three exact-source declarations are now `ACCEPTED` in `config/kt_decisions.json`; acceptance does not certify the power electronics, pressure-vessel containment, propulsion-energy debit, or Metric/Navigator.

**Tank envelopes were ALREADY source-present; no source geometry change:** D–He3 dry containment proxy `house_fuel_tank` has 0.50t dry, `house_fuel` 5.00t wet, both sector [x21–29m,r2–4m,θ220–320°] and **source centroid (25.000,0.000,-2.731)m**. Independent C-lite `c_lite_dry` is 0.10t nominal dry **total ACS/tank hardware**, actual ~0.103943t after existing distributed growth-reserve spread; `c_lite_monoprop` 0.15t wet, both source sector [x17–18m,r2–4.3m,θ-45–225°] and **source centroid (17.500,0.000,+0.987)m**. These are coarse wet/dry mass-and-CG proxies. C-lite's service-ring sector is NOT a demonstrated independently packed/isolated physical tank; bounds overlap other service systems at coarse resolution. No shielding credit for either wet fuel. Cutaway labels and translucent source geometry added for BOTH envelopes. G12 now checks source dry/wet sector equality, wet/dry centroid equality, and both CG label positions; no fabricated tank hardware.

**Final exact-source `certify.py`:** G1–G11 PASS/PASS-DECLARED, G12 **12/12 PASS-DECLARED**, all declared items accepted, **`certified=true`** on source SHA 4d598212. Full and half FQ1–FQ4 remain **78/78 PASS_NUMERICAL** on this same, unchanged geometry SHA. Source-signed 32-asset renderer manifest and two-scene GLB source geometry are unchanged except re-rendered `cut_power.png` and refreshed phone viewer to display current certification. All conventional lab certifications are explicitly NON-CANON and NOT actual hardware flightworthiness; Metric arrival and Navigator unqualified.

**Merge:** kT explicitly authorized merge of PR #440 after certificate and successful LOOM gate. Final GitHub outcome recorded in GitHub PR and protected main commit history, not pre-declared by this review record.
