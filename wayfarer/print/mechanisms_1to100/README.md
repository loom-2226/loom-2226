# Wayfarer 1:100 deployable hot fins and strakes (PROPOSAL, F4: sketch + numbers)

ALL bodies. ALL sponsors. 2026-2226.

Status: **proposal, awaiting kT.** This is a diagram only (`fin_mechanism_1to100.png`,
made by `fin_mechanism_diagram.py`). No print files yet, and no canon, geometry or mass
change. kT asked for radiators and fins that deploy mechanically rather than being glued
in place.

## Canon facts used

From SPEC.md, finish-table rows 14-17 and the geometry parts:

- **Hot fins:** four, x 34.3-53.3, at 40/140/220/320 deg, root r 4.75. Each has 14 pleats of 2 m. They unfold to 28 m in torch burns and fold into 0.6 m stacks otherwise.
- **Strakes:** four accordions, x 14-32.3. Span is 0 (Loom), 2 m (Metric) or 4 m (torch).

## The problem at 1:100

- A deployed fin reaches 280 mm from the hull, and the span is 655 mm tip to tip. The ship is 540 mm long.
- A true-scale pleat would be 0.43 mm thick, below what the printer can make.

## Proposed mechanism

- **Construction:** each fin is a separate part, 14 pleats of 20 x 190 x 1.2 mm.
- **Hinges:** a 1.0 mm steel pin runs the full length of each hinge line. Knuckles are 2.4 mm across, with 0.15 mm clearance so friction holds the fin in position. A 180 deg hard stop keeps the deployed fin flat.
- **Folded stack:** 17.5 mm. That is 3x true scale, a declared print exaggeration like the 0.5 mm grooves.
- **Strakes:** the same hinge with 4 pleats of 10 x 183 mm. Friction holds the 0, 20 and 40 mm positions.
- **Printing:** each fin prints flat and fully deployed (190 x 280 mm) on the A2L's 330 x 320 mm bed.

## kT decides

| | Option A | Option B | Claude |
|---|---|---|---|
| Pleat count | 14 (canon); stack 17.5 mm | 7 double pleats; stack 9 mm; pleats 40 mm wide | 14 |
| How fins hold position | Friction pins + 180 deg stop | Plus 2 x 1 mm magnets in the pleat edges | Friction first; magnets only if the test hinge sags |
| Pins | 1.0 mm steel piano wire | 1.75 mm filament offcuts (stack about 25 mm) | Steel |

**Next, after the decision:** a one-hinge test strip (two pleats) to tune the clearance,
then the full fin and strake print files.
