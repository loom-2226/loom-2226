# Wayfarer v0.5.7 rev 5 review record

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
