# L2 viewport band: the full load path (rev 3.1 note for PR #432)

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING STUDY, 2026-10-26.** Baseline: v0.5.7 rev 3 (geometry `262b21a3...`). The build was unchanged at rev 3.1. **Rev 4 builds in the corrections, and these checks now run inside G5.** Source: `habitat/viewport_band_study.py` (results in `viewport_band_study_results.json`, figure `viewport_band_study.png`). Method: closed-form.

**Sol's qualification:** the rev 3 check spread the axial load over 23 mullions but did not show the path through the interrupted pressure shell, the end rings and the window joints.

## Design rule

The glass is **not** trusted to pass hoop tension through its edge joints. Each pane is a plate between frame members, and the titanium frame carries all the shell's loads around the band. This is the conservative rule for windows in pressure hulls.

## Results

Pressure loads use a factor of 2.0, and thrust is 5 g x 1.5.

| Load path | Result | Limit | Status |
|---|---|---|---|
| Hoop across the band | Sill and head rings take half each: 261 kN per ring (general, 0.6 m), 697 kN (lounge, 1.6 m) | — | Carried |
| Rings as beams between mullions | Axial flow 436 kN/m gives 46 kN·m. Ti ring 14 x 4 cm: 477 MPa with the lounge hoop | 600 MPa | **Pass** (a 12 cm ring failed at 625) |
| Shell next to a ring | Rigid-ring discontinuity bending 53 + axial 14 = 67 MPa; dies out within 0.88 m | 250 MPa | Pass |
| Mullion roots | 490 kN each. 4 x M16 Ti bolts in double shear: 885 kN | margin ≥ 1.5 | Pass (1.8) |
| Panes, 2226 ceramic (the crown's milestone) | 14.6 mm general; 17.2 mm in the lounge with a mid transom | 16 mm assumed | Lounge +1.2 mm |
| Panes, 2026 ALON | 24.7 mm and 29.0 mm | 16 mm assumed | **Does not fit** |

## Two corrections to rev 3

1. **The frame is heavier.** The rings (1.34 t), mullions (0.80 t) and the lounge transom (0.06 t) need 2.2 t; rev 3 allowed 0.77 t. With the slightly thicker lounge panes, the band grows by **1.5 t**. The reserve (54.6 t) covers it.
2. **The 16 mm panes depend on the crown's 2226 ceramic milestone.** Today's ALON would need 25-29 mm, and about 1.5 t more glass. So the band's panes should be added to the `crown_dome` declared item (kT to accept), or sized for 2026 ALON.

The rev 3 note "curved panes need 12.4 mm as hoop membranes" assumed the glass joints pass hoop tension. Under the rule above, that figure is withdrawn.

## Design changes this implies, for rev 4

- **Two titanium edge rings, 14 x 4 cm, all the way round.** They close over the washroom, where the shell is unbroken.
- **A mid-height transom in the 1.6 m lounge.** It halves the pane span.
- **Mullion roots:** bolted (4 x M16 Ti), or an integral Osteon fork with no bolts.
- **Band mass:** 4.34 t becomes about 5.8 t.

## Still open

- A shell finite-element model of the band: the next level of fidelity, if Sol asks for it.
- Fatigue of the ring-to-shell bond under pressure cycles (one per dock) and thermal cycles with the shutters opening and closing.
- Dose through the acrylic plugs: needs a transport code (OLTARIS). Still declared.
