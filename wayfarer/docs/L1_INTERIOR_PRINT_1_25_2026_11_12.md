# Wayfarer L1 independent interior: 1:25 print interpretation
**kT-approved L1; original ship model remains true scale. This is a derived print guide, not a mass booking.**

| Element | At 1:25 | Print interpretation |
|---|---:|---|
| L1 annulus outside diameter 8.30 m | 332 mm | Actual BRep deck with two Ø0.80m ladder bores cut, source mass saving ZERO |
| Utility trunk 1.80 m outside diameter | 72 mm | Goods lift, 4 rack proxies, central utilities; NOT crew egress |
| Ladderways 0.80 m diameter each | 32 mm | Two and ONLY two crew egress routes |
| Six 1.58 x 0.70 m contoured couches | 63.2 x 28.0 mm each | Single shared contour, six repeated positions; physical geometry |
| Command terrace 3.40 x 2.10 m | 136 x 84 mm | Physical deck/platform |
| NAV platform 2.65 x 2.20 m | 106 x 88 mm | Physical deck/platform |
| Open hatch leaf 0.92 m | 36.8 mm | Source-booked leaf, display open |
| Existing rails 22–25 mm tube | 0.88–1.00 mm | Fine geometry, fragile at print size |
| Display surface, screen panels | varies | Draw existing booked outlines; interior screen graphics are DECALS |
| Station designators, NO STEP, hazard, interface labels, indicators and bolt dots | sub-mm | DECALS and paint guide, not additional geometry |

Render \`interior_L1.glb\` once, separately from the six exterior states. Do not convert semantic \`room_*\` / distributed \`outfit_*\` into furniture. No mass, source BRep or exterior envelope credit. Detailed material and clearance hardware remain unqualified.

## kT-approved B3 halo and #516 refinements
- One 1.58 × 0.70m source couch mesh reused at six unchanged source positions. B3 split halo: centre display lifts backward and two wings swing to the sides. One L1 GLB has both poses as a glTF animation, NOT embedded in exterior states.
- Geometry: broad headrests, contoured ivory cushion, light blue-grey shell, 2 halo posts, hinge arms, restrained seat base, armrest control bodies, shaped table/bench/cabinet cases, 1.10 × 0.63m map table (44 × 25.2mm), 1.38 × 0.54m equipment bench (55.2 × 21.6mm), 0.54 × 0.35 × 0.70m cabinet (21.6 × 14 × 28mm). The screen faces are geometry, not screens that actually work.
- Decal / paint: screen contents, lettering, button markings, buckles, thin harness weave, hairline seams and indicator dots. Nothing under 0.6mm at 1:25 is independently printable; some B3 visual faces are under this threshold and must be flattened to decal in STL derivation.
- Role controls: Pilot attitude/translation; Captain backup flight/command-transfer; NAV trajectory/waypoint; Engineering power/thermal; Sensors/EW track-slew/modality; Mission Operations sequence/asset selection. Hardware from B3 #517, terminology from #516.
- Palette (already encoded in B3): #ACBBBD pale blue-grey shell, #D8D8CD ivory upholstery, #607A84 slate frame, muted teal and pale surround. Optional 10–20% brighter printed paint only.
- Mass: 46.000kg common couch and 5.185186564kg halo/control budget inside each 51.185186564kg existing i4_seat booking, no double-booked screen; conceptual 5.100kg halo/control estimate is NOT certified hardware mass. Ship mass/ECON unchanged.
- 4g: illustrative 100kg body imposes ~3.92kN acceleration load. Actual mount strength, occupant support, harness proof, suited egress, motion/mechanism loads remain OPEN.

## L1 wall fit-out: kT approved PR #520
Seven units under dome: cabinets h0..0.95m at r3.755..4.00m; U7 dome-following lining h0.30..1.30m. Book all estimated 358kg within outfit_L1 818.963kg, leaving ~460.963kg undrawn. The command/navigation room 2.150t booking remains untouched.
At 1:25 cabinets up to 38mm tall and 9mm deep; door seams ~1.3mm and handles 4.8×1mm. 0.015m lining is 0.6mm: separate skin or paint. Screen labels, controls, keypad marks, nozzles and warnings are DECALS.
Use original #520 palette: light blue-grey #ACBBBD, slate #607A84, teal #3FA79A, ivory #D8D8CD, emergency red #B5473F, panel yellow #E3B23C, vault grey.
