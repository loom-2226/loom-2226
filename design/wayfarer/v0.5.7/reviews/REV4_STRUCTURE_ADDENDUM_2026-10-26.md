# Wayfarer rev 4: kT decisions and independent structure review

ALL bodies. ALL sponsors. 2026-2226.

NON-GOVERNING. Baseline rev 4 geometry SHA-256 `646ac1bad6852d1c7b25e92e3dd79e46e2d6b719d2edd20270af86203d6ab359`. This record preserves the 2026-10-26 addendum; rev 4 geometry is unchanged. The complete supplied source is `WAYFARER_v0.5.7_rev4_ADDENDUM.md` (conversation attachment).

kT accepted `crown_dome` and `berth_viewports`, and approved `habitat_changes_v057`; those decisions are recorded in candidate `inputs/kt_decisions.json`. All declared assumptions are now accepted. G10 Navigator remains OPEN; no signatures or canon promotion are implied.

## Review findings

A. Four CFRP longerons: G5 inferred area from part mass including distributed engineering reserve. Correct material area is 0.0739 m2/member, not 0.0868 m2. Combined axial and bending stress under stated 5g x 1.5 and 0.5-degree misalignment is 278.8 MPa, exceeding the 250 MPa design target but below the 400 MPa floor. Recommended wall ~83 mm, plus 12% end fitting mass, and correct G5 to use material area and axial+bending.

B. Band ring-to-shell shear: two rows of M10 Ti bolts at 50 mm, shear margin 3.97; CFRP bearing 36.3 MPa. Vierendeel mullion stress 74.4 MPa against 600 MPa. These pass the review's assumed loads.

C. Ti edge rings on CFRP shell: assumed 50 K thermal swing yields ~10.9 mm circumference mismatch, and ~46.2 MPa locked-ring stress. Existing G5 does not check joint thermal cycling. Rev 5 should specify compliant connections or CFRP rings and add a check.

## Scope and disposition

Preserve rev 4 unchanged as the archived baseline. Rev 5 is restricted to (1) longeron sizing and end fittings, (2) G5 area and combined bending method, and (3) thermal accommodation at band-ring attachments. Re-run gates. Hold G10. No loom-gate bypass, no canon or runtime changes. The 50 K swing and 0.5-degree error are review assumptions, not measured operating facts.
