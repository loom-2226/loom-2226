# Fair shutter comparison: Rev 7 vs two angular noses | 28 October 2026

**EXPERIMENTAL RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT CERTIFIED**

Live source checked: `loom-2226/loom-2226`, open PR #432, head `3485830a56dfead79b2ef8bba031a595b536fbb5`. The source geometry and governing design are unchanged.

## What Rev 7 actually declares

The source input defines a 2.8 m crown containing 25 m² glazing, 16 armour-equivalent Strata tambour gores, a **0.22 m high × 1.0 m wide** brow ring that "houses 16 retracted gores and their drives", and 27 g/cm² closed protection. The crown dome part is **4.93 t** comprising 2.13 t panes, 1.8 t frame, 0.5 t brow and 0.5 t tracks/drives. The displaced crown shielding is counted in the existing fixed armour mass, not these 4.93 t.

Crucially, neither the source geometry nor the crown inputs specify any manufactured gore strip shapes, physically located brow cavity or three-dimensional retracting swept volumes. The build part is a **placeholder box** (x=0..0.6, y/z=±2.8 m) tagged `no_render`, not 16 geometrically stowed shutters.

## The matched test

For all three designs, compute exterior transparent-area shielding at the declared 27 g/cm², using the armour part's effective accounting density 111.179 t / 80.823 m³ = **1.376 t/m³**, or **0.1963 m equivalent solid-layer thickness**. Integrate curved exterior area and meridian path length, calculate ideal shoulder annulus surface area and minimum lengthwise nested layers, and sample the three-dimensional pressure-head cross-section to test whether their normal-displaced armour-equivalent stack intrudes. Tracks, drives, structural spacing and impact response remain unmodelled.

**The brow ring has not been manufactured in the source.** For this necessary-geometry thought experiment only, interpret its 1.0 m width as a radial span r=2.8..3.8 m and its 0.22 m height as an axial storage depth. That yields only **4.56 m³ gross annular box volume**, *before* mechanism volume. This orientation is a test hypothesis, **not** a claimed physical interpretation of missing CAD.

| Measure | Rev 7 brow | Compact angular | Panoramic angular |
|---|---:|---:|---:|
| Geometry | Original ellipsoid | +0.8 m, 35°, 3.2 m crown | +1.2 m, 50°, 3.5 m crown |
| Exterior crown coverage | 25.50 m² | 38.27 m² | 52.89 m² |
| Protection-equivalent mass | 6.88 t | 10.33 t | 14.28 t |
| Protection-equivalent volume | 5.00 m³ | 7.51 m³ | 10.38 m³ |
| Available exterior stow surface | 24.17 m² (conditional 1 m brow) | 38.39 m² | 39.10 m² |
| Surface margin | −1.33 m² | +0.12 m² | −13.79 m² |
| Cover path / stow path | 2.864 / 1.161 m | 3.642 / 1.587 m | 4.333 / 1.556 m |
| Minimum nested lengthwise layers | **3** | **3** | **3** |
| Minimum signed axial pressure clearance at required stack | **−0.495 m** | **−0.428 m** | **−0.540 m** |
| Full shutter stowage, tracks and actuation | **NOT DEMONSTRATED** | **NOT DEMONSTRATED** | **NOT DEMONSTRATED** |

Negative pressure clearance means a simple inward-normal three-layer nesting **overlaps the unchanged pressure-head envelope**. These are axial overlap figures, not armour structural thickness or impact penetration.

The Rev 7 quoted 25 m² glazing is consistent with integrating the actual ellipsoidal exterior to r=2.8 m: 25.50 m². Its gross conditional brow volume (4.56 m³) is **less** than the equivalent shutter material (5.00 m³), even before drives. This is independent reason **not** to regard brow stowage as demonstrated under this interpretation. A different fold, material packing factor, brow orientation or relocated storage could alter the conclusion.

The first Metric-node face ring sits at x=2.05 m, radial distance 4.463 m. It is an additional clearance constraint for the angular shoulder, not a proven collision with a physical slat path. Rev 7 also retains the separate bow sensor ring at radial values 2.9..4.15 m, overlapping the radial *band* of our hypothetical brow; detailed three-dimensional sensor displacement was not resolved.

## Result and stopping condition

**No winner. Both original Rev 7 gores and the angular shutters lack a demonstrated physical stowage solution.** This comparison rejects the tested **radial nested-slats mechanism**, not the intended panoramic experience or every conceivable shutter mechanism. Relative numbers are not a specification for a manufactured mechanism.

Do not reclassify the existing Rev 7 gores as physically closed simply because `certify.py` lists the declared 2226 materials milestone and operating doctrine. The source is honest about its extrapolation, but the model does not demonstrate mechanical clearance.

**One narrow next experiment, if the visual concept is worth pursuing:** draw *one* actual protective sector with explicit hinge/track and open/closed swept mesh, then check interference against the unchanged pressure head, bow sensors and ring-0 Metric nodes. Prefer a single sector and its 16-fold repeated placement to another parameter sweep. Compare against *both* crowns. Stop if it cannot be placed; no pressure-hull or L1 wholesale redesign.

Executable reproduction: `command/l1_fair_shutter_comparison.py`, machine output `command/l1_fair_shutter_comparison.json`. The original `command/l1_shutter_stowage.py` tests an illustrative inside-the-shoulder nested mechanism for angular geometry alone.
