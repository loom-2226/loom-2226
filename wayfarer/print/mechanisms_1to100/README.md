# Wayfarer 1:100 plug-in hot fins and strakes

ALL bodies. ALL sponsors. 2026-2226.

Status: **APPROVED by kT 2026-11-13: no hinges; swappable plug-in sets** (decision
`fin_strake_plugin_1to100_2026_11_13`). The diagram is `fin_mechanism_1to100.png`, made by
`fin_mechanism_diagram.py`. The print files are in `parts/`, made by `fin_parts.py` and listed in `parts_manifest.json`, with a preview in `parts_preview.png`. This is print-scale only, with no
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

## Print files (PLACEHOLDER profile, untested)

| File | Qty | Size (mm) |
|---|---|---|
| `parts/hotfin_deployed.stl` | 4 | 190 x 283 x 4 |
| `parts/hotfin_folded.stl` | 4 | 190 x 23 x 6 |
| `parts/strake_loom.stl` | 4 | 183 x 8 x 4 |
| `parts/strake_metric.stl` | 4 | 183 x 28 x 4 |
| `parts/strake_torch.stl` | 4 | 183 x 48 x 4 |
| `parts/peg_test.stl` | 1 | 60 x 26 x 6. **Print this first.** |

- **Checks:** every part passes the volume check and is watertight (0 unmatched edges). The meshes are exact rectilinear solids.
- **Printing:** flat, with no supports.
- **Peg sockets:** square holes, 1.85 mm by default, for 1.75 mm filament pegs cut to 5 mm. The peg test has sockets from 1.70 to 1.95 mm (1 to 6 notches). Set `HOLE` in `fin_parts.py` to the size that grips, then rerun.
- **Dropped at 1:100:** the pleat edges on the folded stacks (a 0.43 mm pitch, below the 0.5 mm minimum). The stacks carry the approved heat-pipe channels instead.
- **Ship-side sockets:** pegs sit at 40 and 150 mm along each fin and at 40 and 143 mm along each strake. The holes in the ship are cut last, because the model stays whole until the design is finished.

## Bay doors: pivoting (kT 2026-11-14, 'Go pivot')

- **Part:** `parts/bay_door_leaf.stl`. Print 2: the port leaf is the same solid turned end for end. Each leaf is 138 mm long and 1.6 mm thick.
- **Pivot:** one 1.75 mm filament pin, 144 mm long, runs through each leaf's hinge boss and 3 mm into the slot end walls (x 18.25 and 32.05 m). The pin sits at r 45.0 mm, 3 deg inside each slot edge (60.77 and 119.23 deg).
- **Swing:** each leaf swings 75 deg from closed to vertical and clears the hull to 80 deg (`bay_door_swing_1to100.png`). Friction on the pin holds it open.
- **Printing:** standing on end with a brim, so the pin hole prints round. The pin hole is 1.85 mm; tune it with the peg test.
- **Checks:** volume PASS, watertight (0 unmatched edges).
- **Declared exaggerations:** the leaf is 1.6 mm (true 1.0 mm). The hinge boss is 3.5 mm across along the door edge, half proud of the skin.
