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
