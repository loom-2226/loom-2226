# Structure review: v0.5.7 rev 4 (four longerons and the L2 viewport band)

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING REVIEW, 2026-10-26** (kT: "let's evaluate 4"). Baseline: rev 4, geometry `646ac1ba...`. **The build is unchanged.** Source: `structure/structure_review_v057.py` (results in `structure_review_v057_results.json`). The review deliberately looks for load cases and methods the design checks did not cover.

**Same day:** kT accepted `crown_dome` and `berth_viewports`, and approved the v0.5.7 habitat changes as design owner (`inputs/kt_decisions.json`). Every declared item is now ACCEPTED. `certified` stays false until G10 is flown and both reviewers sign.

## Verdict

The structure is sound in concept. Every member closes a load path, and nothing fails against the 400 MPa material floor that G5 uses. The review found **one sizing shortfall, one gap in the G5 method, and one unchecked joint problem**. All three are fixable in a rev 5, at about 1.5 t from the 53 t reserve.

## A. Longerons: bending was not checked, and G5 overstates their area

- **Bending.** G5 checks axial load only. The thrust line sits 0.40 m from the centre of the mass ahead, which gives 13.5 MN·m. A 0.5° thrust error adds 9.1 MN·m.
- **Method.** G5 takes the member area from part mass, and part mass includes the spread engineering reserve. That reserve is a mass margin, not material. In v0.5.6 this didn't matter, because the members were six times oversized; with members sized tight, it does.

| | Axial | Axial + bending | Design (sized to) | Floor (G5) |
|---|---|---|---|---|
| G5 method (area 0.0868 m²) | 212 MPa | 237 MPa | 250 | 400 |
| Real material (area 0.0739 m²) | 249 MPa | **279 MPa** | 250 | 400 |

**Fix:**
- **Tubes:** wall from 72 mm to about 83 mm at the same 0.40 m diameter (+11.5% area, +1.2 t of tube; end fittings +12%, about +0.2 t).
- **G5:** compute longeron area from the structure-line share, and add the combined axial + bending check.

## B. Viewport band: two connections the study did not show (both pass)

- **Ring to shell.** 436 kN/m of shear flow on 2 rows of M10 titanium bolts at 50 mm pitch: 10.9 kN per bolt against 43 kN capacity (margin 4.0). Bearing on the CFRP is 36 MPa against 400.
- **Shear across the band.** There are no diagonals across the band, so sideways load is carried by the mullions bending (a Vierendeel frame). 89 kN of lateral load gives 74 MPa in the mullions against 600.

## C. Thermal mismatch between the titanium rings and the CFRP shell (not covered)

- **The problem.** Titanium expands about 17 times more than the CFRP laminate. Over a 50 K swing (shutters opening to deep space and closing), a 27 m ring differs from the shell by **about 11 mm**. Bolted rigidly, the ring would carry about 46 MPa and the joint would work back and forth every cycle, so fatigue matters.
- **Fix:** compliant attachments (slotted holes or titanium flexure fingers, an Osteon-friendly detail). Or make the rings CFRP and keep titanium only at the mullion roots.

## Recommended rev 5 (small)

1. Longeron walls to 83 mm, and end fittings +12% (about 1.4 t in all).
2. G5: area from the structure line, plus a combined axial + bending check.
3. Band rings: compliant attachments, or CFRP rings; add a thermal check.
4. Re-run all gates.
