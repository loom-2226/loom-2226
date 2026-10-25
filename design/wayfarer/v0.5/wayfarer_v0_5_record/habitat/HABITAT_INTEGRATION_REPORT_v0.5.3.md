# Wayfarer v0.5.3 candidate: Sol's habitat package, integrated

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING.** Implements `sol_package/HABITAT_DESIGN_DATA.json` (Sol, 2026-10-25) as frozen, on top of v0.5.2 (torch heat package). No redesign. Geometry sha256 `faeb0f45870012c180354f50709283749ed7098110a04dfb36fd355bf0ad70ec`.

## Baseline

Sol's `BASELINE/` is byte-identical to Claude's archived v0.5 record and to PR #430 (geometry `406424a7...`). The habitat and protected-water inputs are unchanged from v0.5 through v0.5.2, so the overlay applies cleanly. Live `main` has no newer Wayfarer design.

## What was applied

- L3: captain (1, 0-60 deg), crew A (2, 60-120), guest washroom (120-150), guests (4, 150-240), crew B (3, 240-330), crew washroom (330-360); rooms r 1.9-4.07 m; six bunk footprints 2.00 x 0.75 m at r 2.01-4.01 (tiers 1, 2, 2, 2, 2, 1); 0.8 m sliding doors; couches = occupancy (10 berths + 6 command stations = 16).
- L3 berth shield: 8 cm water ring, r 4.07-4.15, x 5.9-8.2, 4.752 t.
- L4: 2.4 m clear medical opening centred at 210 deg on the r 1.9 wall (arc 173.8-246.2 deg, inside the medical wall 165-255).
- Room masses: 0.45 t per occupant, as before (4.5 t for the cabins; 1.2 t washrooms). Bunk and restraint structure is not separately sized.

## Reconciliation (Sol's step 4)

| Item | Result |
|---|---|
| Ring water | 4.752 t of **protected water**, present in every state S1-S7, taken from the service tank (32.5 to 28.76 t). Total water 300 t and protected water 50 t unchanged; no double count |
| Displacement | The ring overlapped only the L3 distributed-outfitting layer (r 4.05-4.15). That layer (0.8 t) moved to r 4.15-4.25, the utility gap inside the pressure wall. Sampled overlap of the ring with every part: none |
| Mass and trim | Dry 867.7 t, S1 1,167.7 t (unchanged). Worst trim 0.347 deg (design target 0.35, limit 0.5); thrust-line offset y +0.05, z -0.20 m |
| Gates | G1-G9, G11, G12 pass (G4, G6 with declared items); G10 OPEN. G7 passes after kT's basis change (item 1) |

## Concrete issues

1. **Resolved by kT on 2026-10-25: private cabins removed.** Was: G7 failed under basis v0.1, private quarters. The basis asks for "a private quarter for every person >= 2.1 m3". Four cabins for ten people gives 3 crew + 1 guest cabins against 6 + 4. Per occupant: captain 15.6 m3, crew A 7.8, crew B 7.8, guests 5.9 m3 each. kT chose shared cabins. G7 now asks for a cabin berth with 5 g restraints for every person and at least 2.1 m3 of cabin volume per occupant (same threshold, now per occupant): 6 crew + 4 guest berths, smallest 5.85 m3 per occupant. **Sol to agree the basis change as second reviewer.**
2. **The port ladderway blocks the stretcher turn.** Sol's search fixes the stretcher's centre at 210 deg and models no ladderways. The L4 port ladderway (theta 180, r 1.4 m, 0.8 m square) sits beside the opening. Rerun with the stretcher free to move around the corridor ring (`stretcher_path_3dof.py`, 3 degrees of freedom), plan view, ladderway treated as floor to ceiling:
   - without the ladderway, a path exists through openings of 2.0, 2.4 and 2.8 m;
   - with it, there is no path for any opening of 2.0-2.8 m, with either Sol's 11 cm wall band or thin walls;
   - the result holds on a grid twice as fine (2.5 cm, 1 deg, 2.5 deg).
   With Sol's 11 cm wall band, a 2.0 x 0.6 m rigid stretcher cannot lie anywhere in the 1 m corridor ring except across the opening. How a stretcher reaches L4 (the 0.8 m ladder shafts, carried axially) is an open 3D question.
3. **Evidence scripts do not reproduce as packaged.**
   - `wayfarer_stretcher_turn.py` sets `W,L=.6,1.4` (a 1.4 m stretcher). With 1.4 m a path appears from a 1.6 m opening. With 2.0 m it reproduces Sol's stated result: pass at 2.4 m, fail at 2.2 m.
   - `wayfarer_cabin_layer_test.py` executes `/tmp/wayfarer_cabin_ray_probe.py`, which is not in the package.
   - `wayfarer_cabin_fine.py` samples bunks at 0 and 60 deg (room boundaries) instead of the captain's and crew A bunks at 15 and 75 deg.
4. **Windows drop from 16 to 6.** The continuous ring leaves no L3 cabin windows. The canon candidate suggests 10-16. This is not a gate, but it needs a decision.

## Confirmed

- **Bunk radiation screen, integrated geometry, S5, correct bunk angles, 600 directions, 36 points.** The minimum and the count below 40 g/cm2 at each ray step:

  | Ray step | Minimum | Below 40 |
  |---|---|---|
  | 2 cm | 40.09 g/cm2 | 0 |
  | 1 cm | 41.26 g/cm2 | 0 |
  | 5 cm | 34.65 g/cm2 | 16 |

  The worst point is the captain's bunk (15 deg), which Sol's script did not sample. The margin is about 1 g/cm2 and the 5 cm result shows the method's sensitivity; this is a material-column screen, not dose.
- **Plan clearances.** Bunk outer corners reach r 4.0275 m, 4.25 cm inside the ring. Side-wall clearance is 14.5-27.9 cm. Door edge to the nearest bunk corner is 18.5-29.2 cm.
- **Berth stacking.** Two tiers take 2.16 m of the 2.30 m deck, as Sol states.
- **Medical opening.** The 2.4 m arc fits the medical bay's inner wall.

## Not claimed (as Sol listed)

- the 5 g berth load path;
- the medical opening's pressure closure;
- a continuous swept-volume proof;
- full-body dose;
- effective clear height and access between bunk tiers.

## Files

- `habitat/hab_overlay_checks.py` and `habitat/hab_overlay_results.json`: ring overlap, plan clearances, bunk screen.
- `habitat/stretcher_path_3dof.py` and `habitat/stretcher_path_3dof_results.json`: the stretcher search.
- `habitat/sol_package/`: Sol's design data, start note, manifest and evidence scripts as received.
