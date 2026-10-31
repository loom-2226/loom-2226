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
