# Wayfarer v0.5.4 candidate: L1 command level

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING.** Answers kT's "L1 Command Level Design Exploration" (2026-10-25) with the existing builder. Limited to L1 and its direct sensor, structure and mass consequences; L2-L5 and the L3/L4 habitat decisions are untouched. Built on v0.5.3. Geometry sha256 `a185c6973ed8712bb53043e06f66a28366c289259b09c91bfc0961a0f7936444`.

## 1. Corrections to the brief's baseline

| Brief | Model | Effect |
|---|---|---|
| Sensor envelope extends aft to ~1.8 m | It ends at **x 1.0 m** (a lens from the nose at x 0.2 to x 1.0, 3.23 m radius at its aft face). L1 is nominally x 0.2-3.0 | The baseline has **2.0 m** of axial space on the axis behind the sensors, not 1.2 m |
| (implicit) | Claude's builder computed that lens as 4.5 m3; it is **14.1 m3**. `DomeCyl.volume` assumed the shape reached its cylinder. Fixed in v0.5.4 | The block was smeared at 1.9 t/m3 instead of 0.6 t/m3 in the radiation ray-marching. Re-run: storm shelter 55.2 g/cm2 and berth screen 40.09 g/cm2 are unchanged (their worst rays do not pass through the bow) |

## 2. The key physical point

Under thrust, aft is down. The only couch orientation that suits 5 g is supine with the back on the floor, so the load is eyeballs-in (Gx). A person lying that way faces the bow. So the restraint requirement and the forward view are compatible: the forward crew look "up" through the nose.

What limits the view is the **distance from eye to window**, not the length of the ship. The field of view through a window is about 2 x atan(window radius / distance).

## 3. Candidate (dimensioned)

| Item | Dimension |
|---|---|
| Couch | 2.0 x 0.7 m, supine facing the bow; back 0.25 m above the couch base; eye 0.20 m above the back and 0.20 m from the head end; occupants up to about 1.9 m |
| Command platform | x 1.8-3.0 (1.2 m high), y -0.8 to +0.8, z -1.4 to +0.7 m; 0.3 t, taken from the L1 room outfitting (3.0 to 2.7 t) |
| PILOT, NAV | On the platform, side by side at y = +/-0.45 m, head toward +Z. **Eyes at (x 1.35, y +/-0.45, z +0.45)** |
| Support S1-S4 | On the floor at 45, 135, 225 and 315 deg, radial, head at r 1.95 m, feet at r 3.95 m. **Eyes at x 2.55, r 2.15** |
| Nose windows | Two 0.8 m pressure windows on the forward lines of PILOT and NAV, centres 0.9 m apart (10 cm mullion), at x 0.23 m on the pressure head. One armour aperture about 1.9 x 1.0 m over both, shuttered. 0.8 m is the ISS Cupola's top window, the largest flown |
| Shoulder windows | The four existing 0.5 m windows at 45/135/225/315 deg, x 1.25 m |
| Bow sensors and electronics | Same mass (8.47 t), repacked into a ring x 0.2-1.0 m around a **2.5 m bore** on the axis: 10.4 m3, 0.81 t/m3 |
| Windows aboard | 8 (was 6 after the L3 decision; canon candidate suggests 10-16) |

## 4. Sightlines (`command/l1_study.py`)

Rays are cast from each eye to 49 points over its window, testing every solid part and the other five occupants (couch plus 0.40 m of body).

| Station | Window | Eye to window | View across | Rays clear |
|---|---|---|---|---|
| PILOT, NAV | nose, 0.8 m | 1.12 m | **39 deg**, straight ahead | 100% |
| S1-S4 | shoulder, 0.5 m | 2.24 m | 13 deg, 55 deg off the bow axis | 100% |

- **Negative control:** with the v0.5 solid sensor block put back, 100% of the pilot's rays are blocked by it.
- **Bore margin:** the view cones reach at most r 1.04 m inside the 1.25 m bore.

## 5. Do the forward stations need raising? Yes, by about 1.2 m

The table gives the view across through the 0.8 m nose window.

| Platform height | Same length | +1.0 m nose | +1.5 m nose |
|---|---|---|---|
| 0 (floor) | 20 deg | 14 deg | 12 deg |
| 0.15 m | 21 deg | 14 deg | 12 deg |
| 0.4 m | 23 deg | 16 deg | 13 deg |
| 0.8 m | 29 deg | 18 deg | 15 deg |
| **1.2 m** | **39 deg** | 21 deg | 17 deg |

A 10-40 cm lift barely changes the view (20 to 23 deg). The 1.2 m platform doubles it. A longer nose moves the windows further away and makes the view narrower.

## 6. The nose extension is not needed

| | Same length | +1.0 m | +1.5 m |
|---|---|---|---|
| Length | 53.3 m | 54.3 m | 54.8 m |
| Dry mass added | 0 | 11.5 t | 17.3 t |
| Cruise acceleration (S1) | 0.992 g | 0.982 g | 0.978 g |
| ECON reach | 722.8 km/s | 714.8 km/s | 710.9 km/s |

The extension costs about 11.4 t per metre: armour 7.6, pressure vessel 1.1, structure 2.8. It buys room behind a sensor block that can instead be repacked, and it makes the forward view worse unless the couches move forward with the dome.

## 7. Clearances

| Clearance | Value |
|---|---|
| Pilot's shins to the sensor ring's aft face | 0.40 m (the feet reach r 1.77 m, under the ring) |
| Platform edge to the ladder openings | 0.20 m |
| Support couches' feet to the wall | 0.20 m |
| Height under the platform | 1.2 m |
| Mass and trim | Dry mass unchanged; worst trim 0.348 deg |

## 8. Remaining physical issues

1. **Standing headroom on the L1 floor is 2.0 m** under the sensor ring and 1.8 m at r 3.5 m, against the basis's 2.1 m deck clear height. G7 checks a nominal 2.3 m per deck, so it does not catch this. The same was true in v0.5.
2. **Forward windows need protection at speed.** At torch cruise speeds dust strikes the bow, so the nose windows need an armoured shutter, closed except for approach and observation. Neither the shutter nor the reinforcement of the pressure head and armour around the two 0.8 m holes (10 cm mullion) is sized.
3. **Docking is not visible from L1.** The collar is at x 16 m on -Z; the nose windows serve planets, moons and approach, not docking.
4. **Unqualified:** the 5 g couch and platform load paths. Climbing onto the 1.2 m platform and getting out under thrust is not demonstrated. Displays are not placed; they must sit outside the 39 deg view cones.
5. **The sensor ring's 0.81 t/m3** is credible for dense equipment, but there is no equipment list behind it.
6. **The two nose windows thin L1's forward shielding.** The storm shelter is unaffected.

## Files

- `command/l1_study.py` and `command/l1_study_results.json`
- `render/out/deck_L1.png` (plan)
- `render/out/deck_L1_section.png` (section through the pilot)
