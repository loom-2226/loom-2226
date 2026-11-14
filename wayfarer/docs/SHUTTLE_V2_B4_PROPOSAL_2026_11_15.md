# Shuttle v2 proposal: B4 angular lifting body with side-door rover (2026-11-15)

ALL bodies. ALL sponsors. 2026-2226.

**NON-CANON proposal.** kT selected B4 on 2026-11-15 ("Yes b4"). Shuttle v1 stays the booked shuttle
(30.732 t). Nothing here changes canon, Wayfarer mass or any gate. G8 is OPEN.
Lab work: `wayfarer/lab/shuttle/v2_lifting_body/` (PR #550).

## Why

kT wanted a Ranger-style lifting body that still meets the Venus surface requirement
(92 bar outside, 1 bar inside, 18 h). The pressure vessel stays, but it moves inside a
non-pressure aeroshell instead of setting the shuttle's shape.

## What B4 is

| Item | Value |
|---|---|
| Body | angular faceted lifting body, 12.8 m long, 4.25 m span, 2.45 m tall |
| Bay fit | 2.139 m max radius vs 2.15 m (4.3 m envelope) - PASS, wings and fins folded |
| Internal volume | 82.5 m3 (v1 119 m3) |
| Crew vessels | two 1.9 m Ti spheres + tunnel, 92 bar rated, 3 crew; >= 0.10 m to the skin |
| Wings | upper flank skin, hinged on the shoulder, double fold; 8.3 m span, +13 m2 |
| Rover | the twin spheres on a two-rail chassis, 4 x 0.9 m crab-steer wheels |
| Egress | starboard side door 4.2 m long: lower flank folds down as a 30 deg ramp, wing swings up as an awning |
| Ground stance | four short legs, belly 0.6 m up |

## Performance (ROM, `aero_test.py`)

| | v1 | B4 |
|---|---|---|
| Best hypersonic L/D | 0.76 | 1.55 |
| Entry cross-range, Venus | 650 km | ~1,060 km |
| Peak entry g, Venus | 2.3 | 2.0 |
| Glide L/D, wings out | 2.0 | 3.7 |
| Unpowered touchdown, Venus / Titan | 37 / 50 m/s | 19 / 26 m/s |
| Torch dv (exhaust 25 km/s) | 11.3 km/s | ~10.9 km/s |

Mars, Pluto and Triton landings stay torch-only for every shape.

## Mass and gate screen (`b4_mass_gate.py`, 200,000 samples)

| | Core dry p5 / mid / p95 | G8 34.2 t passes | Margin at mid |
|---|---|---|---|
| v1 (baseline A) | 26.01 / 30.02 / 34.01 t | 96% | 4.2 t |
| v2 B4 | 27.99 / 32.09 / 36.22 t | 79% | 2.1 t |

B4 is about **+2.1 t** at the midpoint. Where it comes from:
- wings +1.6 t
- tunnel, second hatch and fittings +0.4 t
- hull +0.5 t: 17% less skin, but flat panels and the big side opening cost more than that saves
- rover chassis +0.2 t
- smaller spheres -0.5 t, smaller belly heat shield -0.1 t

All v2 factors are assumptions, listed in `b4_mass_gate.json`.

## Open before adoption

1. G8 on real solids, and Wayfarer rebooking (B4 midpoint is +1.36 t over the booked 30.732 t).
2. Longerons above and below the 4.2 m side opening.
3. Door seals through the entry heat shield on the lower flank.
4. Shoulder hinge as both wing and door hinge.
5. Dorsal hatch trunk must retract before the rover slides out.
6. Rounded nose and chine edges (10-20 cm) for entry heating.
7. Venus-hot wheels, and Venus kit attachment to the new body.
