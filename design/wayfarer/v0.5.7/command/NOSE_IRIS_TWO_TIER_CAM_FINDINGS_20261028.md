# Wayfarer iris: integrated two-tier cam and 4 cm smaller aperture | 28 October 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT PHYSICALLY QUALIFIED**

Live GitHub source checked: `loom-2226/loom-2226` PR #432 at `3485830a56dfead79b2ef8bba031a595b536fbb5`, still open. All work is isolated in `research/wayfarer-nose-l1-search-20261028`, not canon, original Rev 7, or runtime.

## Narrow hypothesis and result

The previous single-blade cam path cleared the unchanged Rev 7 pressure head and the assumed +1.2 m / 50° faceted exterior, but an **entire two-tier** iris at radius **1.80 m** missed its necessary room by **23.4 mm**. We tested **only** whether a slightly smaller central aperture would allow both existing full-thickness blade tiers to follow the same cam without changing the material, hull, crew or node/sensor locations.

**Yes, in the point-cloud model.** A radius **1.76 m** (3.52 m diameter, only 8 cm smaller in diameter than R1.80) passes the 16-leaf two-level, full-stroke collision/pressure screen under the existing assumptions.

## Geometry actually executed

- Nose +1.2 m / 50° facets, original *unchanged* Rev 7 pressure ellipsoid (tip x=0.20 m; pressure radius 4.30 m).
- Assumed new fixed angular exterior 0.20 m **normal** armour, translated to 0.311 m axial thickness on the 50° cone. **This is a test assumption, not currently manufactured facet CAD.**
- 27 g/cm² areal protection; source-accounting density ~1.376 t/m³; each complete leaf **0.1963 m** thick.
- Two **alternate eight-leaf levels**, offset along x by leaf thickness plus **0.020 m**. Fully closed is *still stepped*, not a flush surface.
- The fixed **0.12 m central armour boss** prevents a mathematical central puncture. Its round impact seam is not mechanically certified.
- Each of the 16 leaf footprints is a radial wedge with source-inspired 1° angular overlap; the rigid 2D leaf profiles rotate at a shared angle from **0 to 62°**, with alternately staggered x positions.
- At the beginning, the 16 leaves translate aft while still within the central iris opening. Then they rotate in 1° steps and a common cam travels aft to keep both tiers behind the surrounding fixed armour.
- Each 2D leaf is sampled over **56 radial × 33 angular points**, thickness tested as front/back slab. Same-tier overlapping sectors are checked via separating-axis tests against all even-index neighbours. Different-tier leaves may overlap in projection, but the model preserves at least **20 mm clear axial separation** of their material slabs.
- Model requires at least **25 mm axial clearance** ahead of the pressure head and behind the assumed stationary armour surface, before additional bearings, tracks, sleeve bushings or seal supports.

| Necessary screen | R1.80 original | **R1.76 selected** | R1.75 conservative |
|---|---:|---:|---:|
| Whole sampled 16-leaf path clear? | **No** | **Yes** | **Yes** |
| Signed remaining common x interval at open | −0.0234 m | **+0.0383 m** | +0.0537 m |
| Smallest pressure gap along path | 0.0006 m | **0.0623 m** | 0.0777 m |
| Smallest fixed-armour axial gap in rotation | +0.026 m | **+0.026 m** | +0.026 m |
| Inter-tier air gap | 0.020 m | 0.020 m | 0.020 m |
| Same-tier polygon collision in all sampled poses | none | none | none |
| Fixed-shoulder sampled slab contact | none | none | none |
| Fully-open unblocked disk radius at 62° | 1.7953 m | **1.7569 m** | 1.7473 m |
| Furthest radial extent when open | 2.7099 m | **2.6509 m** | 2.6361 m |

The open armoured leaves remain below the original bow sensor ring's inner radius r=2.90 m, and the far outer Metric-node ring r≈4.46 m. Their actual mounts and operating fields have not been cleared.

### Visibility consequence

Reserving the opaque annulus to the leaves' parked radius + 0.04 m and keeping the previously studied **four 40° side windows** yields (the same source eye locations, pressure intersections, sensor ring and room furniture):

| Iris layout | Pilot/NAV 60° cone without boss | With fixed 0.12 m boss | Pilot/NAV forward hemisphere, with boss | Worst support forward |
|---|---:|---:|---:|---:|
| R1.80 | 100% sampled | 98.66% | 31.64% | 4.30% |
| **R1.76** | **100% sampled** | **98.66%** | **32.81%** | 4.30% |
| R1.75 | 99.55% | 98.21% | 32.42% | 4.69% |

The corrected Rev 7 original full-crown reference is **69.14% Pilot/NAV forward hemisphere** and **5.47% worst support**, with 100% of sampled cone directions through the specified original glazing. Thus the iris design still *loses substantial broad visibility* relative to Rev 7. No claim of superior panoramic L1 experience is supported.

## What passed and what did not

**Passed in the limited mathematical screen:** the 1.76 m rigid 16-leaf *stepped* two-tier cam does not hit the sampled stationary-armour or pressure envelopes along the explicitly sampled withdrawal and opening path; no same-tier sector overlap and no positive-thickness cross-tier contact is predicted.

**NOT physically closed:** the model permits an idealized global axial cam with only 38 mm of remaining positioning allowance at full open. There is **no actual annular entry throat**, bearing, pivot volume, reinforcement, actuator, cable routing, finite closed leaf-to-hub load path, three-dimensional panel-edge relief, or impact/erosion calculation. The 0.20 m normal conical armour is a hypothetical adaptation of original Rev 7 shielding and would have to be engineered.

**Critically, the closed face remains 216.3 mm stepped.** The user requested a fully closed, *flush* iris. This experiment does **not** achieve that requirement. Earlier raised-face/fairing alternatives hit neighbours around 43° of rotation. Shrinking the iris has not fixed this.

## Decision and stopping condition

**Do not adopt the 16-leaf iris or revise Wayfarer yet.** This targeted experiment resolves the *specific two-tier geometric shortfall* with a 4 cm radius reduction. Nothing in the user requirements forces a larger spacecraft to make room for it.

The only remaining near-term design question worth a tight test is a **recessed flush close-up of one alternating blade seam** that retains this cam path. If a flush 27 g/cm² exterior cannot be achieved without a whole extra armour layer, this concept should be parked rather than turning the nose into another engineering rabbit hole.

## Artifacts

- `command/l1_iris_two_tier_cam.py`, output `command/l1_iris_two_tier_cam_results.json`.
- `render/make_two_tier_cam_viewer.py`, self-contained touchscreen-orbit viewer `render/out/nose_two_tier_cam_viewer.html`. Four candidates (R1.80, 1.76, 1.75, 1.74), 16 rigid moving leaves, two levels, 93 sampled motion frames, selectable pressure hull/exterior/central boss. Viewer depicts sheet faces; slab thickness and clearance are checked in the executable calculation, not actually rendered as mechanical parts.

No source branches, canon, runtime or Rev 7 PR #432 files were modified.
