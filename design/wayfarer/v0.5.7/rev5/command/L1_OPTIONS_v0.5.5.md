# Wayfarer v0.5.5 candidate: L1 command level, options against real standards

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING.** Follows kT's request of 2026-10-25 to iterate the L1 options and optimise against real spacecraft design standards. Limited to L1 and its direct sensor, structure and mass consequences. Geometry sha256 `8002b4df904d354b9590f768cd5162008292f0bb13c7085cb10a2d323e2f8e56`.

## 1. Claude's view of the v0.5.4 candidate

It got the physics right: crew on their backs facing the bow, so 5 g loads them chest-to-back. Measured against real standards, though, it fails 5 of 11 checks:
- The couches are 10 cm short for a 99th-percentile man after spinal growth.
- The pilots see only 47% of a 60 deg cone, because they sit 1.1 m from small windows.
- There is no standing walkway on the deck at all: the sensor ring leaves 2.0 m of headroom everywhere.
- The pedestal sits 0.2 m from the ladders.
- The ship has 8 windows, below canon's 10-16.

## 2. Criteria, and where they come from

NASA-STD-3001 Vol 2 is mostly performance-based ("the system shall..."), so each requirement is turned into a number, with its source.

| Criterion | Number | Source |
|---|---|---|
| Couch fits the whole crew range | couch >= 2.10 m | [V2 4102]: 1st-percentile female to 99th-percentile male. Male stature mean 178.6 cm, SD 6.8 cm gives a 99th percentile of ~194 cm (NASA NTRS 20080010652); Appendix E adds 3% spinal elongation, ~200 cm |
| Load direction | eyeballs-in (+Gx) at every station | OCHMO acceleration brief: "+Gx is the most advantageous direction"; 4 g tolerable for at least 60 min, 2 g for at least 24 h |
| Window view | >= 90% clear across a 60 deg cone for the two forward stations | [V2 8043] "unobstructed fields of view for expected crew operations" (no number given, so 60 deg is authored, A) |
| Eye to window, eye to display | >= 0.33 m | FAA Human Factors Design Standard 5.1.2.13 (minimum display viewing distance) |
| Windows | <= 0.8 m each; debris pane, two pressure panes, scratch pane, external shutter | ISS Cupola: 7 windows, 80 cm top window (largest flown), four layers, Kevlar/Nextel shutters |
| Window count | 10-16 for the ship | Canon candidate specification |
| Walkways | 0.8 m clear, reaching both ladders and every couch | [V2 8013], [V2 8014] (no number; 0.8 m equals the ladder openings, A) |
| Walkway headroom | >= 2.1 m | Basis v0.1 G7 clear height (A) |
| Sensor packing | <= 0.85 t/m3 | A (dense avionics) |
| Ship length and mass | unchanged | kT's brief: minimal disturbance |

## 3. Options

Each option is a scene built on the real dome, floor and ladders. Rays from every eye measure what each station actually sees, with sensors, decks, the other occupants and placed displays all treated as obstacles. A 10 cm floor grid checks the walkways.

| Option | Layout | Checks | Pilot: 60 deg cone clear | Pilot: share of forward sky visible | Windows |
|---|---|---|---|---|---|
| A (v0.5.4) | 1.2 m pedestal, 2 nose windows, sensor ring around a bore, radial support couches | 6/11 | 47% | 9% | 8 |
| B | Pilots on the floor, sensors moved to the dome shoulder, rim support couches | 7/11 | 20% | 3% | 8 |
| C | **Flight deck** 1.67 m up (eyes 0.65 m from windows), shoulder sensor ring, rim support couches, 2 nose windows | 10/11 | 100% | 20% | 8 |
| D0 | As D, but support couches radial | 9/11 (walkways blocked) | 100% | 29% | 14 |
| **D** | **As C plus a Cupola-style cluster of 8 nose windows** | **11/11** | **100%** | **29%** | **14** |
| E | D with the +1.5 m nose | 10/11 (+17 t, length) | 100% | 29% | 14 |

What decides it:
- **Raising the pilots is essential.** It is what brings the window close to the eye.
- **Moving the sensors to the dome shoulder** frees the nose and gives over 2.1 m of headroom on the walkways.
- **Laying the support couches along the rim** is what makes the walkways work.
- **The window cluster** is what reaches canon's window count.
- **The +1.5 m nose adds nothing** the shorter ship lacks. It does give the support crew a worse view (their windows move further away).

## 4. Tuning D

Swept the pilots' eye-to-window distance and the rim couch radius (`command/l1_sweep_results.json`):
- **Eye-to-window distance:**
  - 0.50 m: 35% of the sky visible;
  - 0.65 m: 29%;
  - 0.80 m: the view falls below 90% clear across 60 deg.
- **Chosen: 0.55 m.** That leaves about 0.45 m in front of a helmet visor.
- **Rim couches at r 3.45 m** bring the support crew closest to their windows while keeping the walkways.

## 5. Built design (v0.5.5)

| Item | Dimension |
|---|---|
| Couches | 2.10 x 0.70 m, supine facing the bow; eye 0.45 m above the couch base, 0.20 m from the head end |
| Flight deck | Mezzanine x 1.225-1.325 m (1.78 m above the L1 floor), 1.7 x 2.3 m, 0.4 t; ladder up at its -Z end; 1.68 m clear underneath for stowage |
| PILOT, NAV | On the flight deck at y = +/-0.45 m, head toward +Z; eyes at (x 0.775, y +/-0.45, z +0.45), 0.55 m below their windows |
| S1-S4 | Along the rim at r 3.45 m, head under the 45/135/225/315 deg shoulder windows; eyes 1.27 m from the window |
| Nose windows | 2 x 0.8 m over the pilots, 6 x 0.6 m around them, mullions >= 10 cm; ship total 14 |
| Sensors | 8.47 t in a ring at the dome shoulder, r >= 2.9 m, x <= 2.0 m, with gaps at the four shoulder windows; 13.0 m3, 0.65 t/m3 |
| Displays | Pilots: 0.55 m from the eye, 45 deg toward the feet. Support: 0.5 m, 30 deg inboard. All outside the central 60 deg |
| Mass, length, trim | Unchanged: dry 867.7 t, 53.3 m; worst trim 0.348 deg |

Re-scored as built (`command/l1_study.py`): **11/11**.
- **Pilots:** 99.9% clear across 60 deg, 65% across 90 deg, 32% of the forward sky.
- **Support crew:** a 21 deg view through their windows, 25 deg off the bow axis.
- **Walkways:** reach both ladders and every couch, with at least 2.28 m of headroom.
- **Other gates:** G1-G9, G11 and G12 pass (G4 and G6 with declared items); G10 is open, for Sol.

## 6. Still open

1. **Nose structure and window protection.** Eight openings in the nose need a Cupola-like frame, debris panes and shutters, closed at cruise speed. Not sized.
   - **Found while rendering D (`command/l1_bore_check.py`):** the ray tests treat each window as a hole in a thin sheet, but 0.20 m of armour sits in front of the panes. Straight bores cut the pilots' 60 deg cone from 99.9% to 89.3% clear (below the 90% criterion) and the 90 deg cone from 65% to 42%.
   - Splaying the armour openings outward fixes it: 12 deg gives 99.7% (90 deg: 49%), 20 deg gives 99.9% (54%).
   - The catch: at 12 deg only 1.5 cm of armour is left between the two 0.8 m openings, and from 15 deg they merge. The cluster needs a real frame carrying the panes (as on the Cupola), sized in v0.5.6. The renders show 12 deg.
2. **Getting onto the flight deck.** A 1.78 m ladder climb under 1 g; egress time and getting an injured pilot down are not demonstrated.
3. **Time on the back.** [V2 6113] limits time on the back with feet raised to 3 h 15 min. EXPEDITE burns at about 2 g can last up to about 3.1 h, close to that limit.
4. **Duration at 5 g.** HARD at 5 g lasts up to about 37 min; check it against NASA's +Gx duration curve (Vol 2 Fig. 6.5; not in this record).
5. **Docking** is not visible from L1 (the collar is at x 16 m on -Z).
6. **Support crew views are narrow** (21 deg); they work mainly from displays.
7. **The nose windows thin L1's shielding.** The storm shelter is unaffected.
8. **Couch shape (design note, kT 2026-10-25).** The intended couch is a knees-up contour like the Soyuz Kazbek seat, with a liner moulded to each person: back flat, hips and knees bent, legs raised. It suits [V2 6113], whose 3 h 15 min limit assumes the feet are raised. It is noted only and not modelled: the checks keep the flat 2.10 x 0.70 m couch as the envelope, which is the larger footprint. A knees-up couch is about 1.5 m long, but the knees stand about 0.6 m above the couch back, so the clearance under the nose dome must be checked before the shape is adopted.

## Files

- `command/l1_options.py` and `command/l1_options_results.json`: options A-E.
- `command/l1_sweep_results.json`: the tuning sweep.
- `command/l1_study.py` and `command/l1_study_results.json`: the built design.
- `command/l1_bore_check.py` and `command/l1_bore_check_results.json`: the armour bore check.
- `render/out/deck_L1.png` and `render/out/deck_L1_section.png`.
- `render/out/cmd_cutaway.png`, `cmd_pov.png`, `ext_nose.png`: 3D views of D. Couches, crew, displays and ladders come from `render/out/l1_scene.json`, the scene `command/l1_study.py` scores. Display mounts, ladder rails and the 12 deg window splay are drawn only (not in the geometry).
- `command/L1_COMMAND_REPORT_v0.5.4.md`: option A, kept as history.
