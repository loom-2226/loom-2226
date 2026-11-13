# Wayfarer 1:100 plug-in hot fins and strakes

ALL bodies. ALL sponsors. 2026-2226.

Status: **APPROVED by kT 2026-11-13: no hinges; swappable plug-in sets** (decision
`fin_strake_plugin_1to100_2026_11_13`). The diagram is `fin_mechanism_1to100.png`, made by
`fin_mechanism_diagram.py`. Print files come next. This is print-scale only, with no
canon, geometry or mass change.

## Why no hinges

At 1:100 a deployed hot fin reaches 280 mm and the span is 655 mm, against a 540 mm
ship. Pin hinges would make the folded stack 3x too thick. They would also be fragile
and need tuning. Swapping whole parts keeps both states true to look at and strong.

## Design

- **Hot fins.** Two sets of four on the same sockets:
  - Folded: solid stack, 190 x 20 x 6 mm (true scale), with the 14 pleat edges engraved.
  - Deployed: flat panel, 190 x 280 x 1.6 mm. Pleat lines every 20 mm, plus the approved heat-pipe channels every 5 mm.
- **Socket.** Each fin has a 4 x 3 mm root bar with two pegs. The pegs are cut 1.75 mm filament offcuts, a friction fit in 1.9 mm holes. The fin root on the ship is thickened from 3 to 4 mm to hold them.
- **Strakes.** Three sets of four on the same socket: Loom 0 m (flush bay cover), Metric 2 m (a 20 mm block with the pleat lines engraved) and torch 4 m (a 40 mm panel). Each is 183 mm long.
- **Parts.** 20 plug-in parts and 40 pegs. Each deployed fin prints flat on the 330 x 320 mm bed.
- **Holding the fins in.** Friction pegs are the default. Switch to 3 x 1 mm magnets only if a fin works loose on the test print.
- **Declared print exaggerations.** The deployed panel is 1.6 mm (a true pleat is 0.43 mm). The root bar is 4 mm (the true root edge is 3 mm).
- **Finish.** Colours, glow and channels follow finish-table rows 14-17 and `exterior_remaining_surfaces_2026_11_13`.
