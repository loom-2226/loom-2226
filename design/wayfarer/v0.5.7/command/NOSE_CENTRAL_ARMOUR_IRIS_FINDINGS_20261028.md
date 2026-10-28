# Wayfarer central armour iris: actual 16-leaf geometry experiment | 28 Oct 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT CERTIFIED.**

Source verified from live `loom-2226/loom-2226`: PR #432 head `3485830a56dfead79b2ef8bba031a595b536fbb5`. This work uses its exact original pressure head, the existing bow sensor and node locations, and the 2 tested angular noses. No source Rev 7, canon, runtime or PR change.

## Design intent

The user supplied an image of a *rotating multi-blade iris* as a **central** viewing-window armour closure. It must close completely, look flush and unobtrusive, avoid giant deployed petals, and preserve useful panoramic command-deck visibility. Unlike the earlier flower and lateral covers, the iris rotates its own leaves around the central aperture in a local annulus.

The working model is **not** a fabricated camera diaphragm. Each rigid leaf is a shallow circular-sector polygon, engineered hypothetically to carry **27 g/cm² of armour-equivalent protection**. The test measures blade motion and the space available, but does not assert that 16 rigid 196-mm-thick leaves can be built with camera-iris edge interweaving and flush seals.

## Matched physical inputs

- Current Rev 7 original pressure head: tip x=0.20 m, ellipsoid radius 4.30 m, shoulder x=2.35 m. Original bow sensor radial occupancy is 2.9–4.15 m and front Metric-node faces are near r=4.463 m.
- Angular compact: +0.8 m bow extension, face radius 1.2 m, 35° facets.
- Angular panorama: +1.2 m bow extension, **flat face radius 2.0 m**, 50° facets.
- Declared closed protection: 27 g/cm² = 270 kg/m². Effective reference armour density from source ledger 111.179 t / 80.823 m³ = 1.376 t/m³, equivalent one-leaf depth **0.1963 m**. This is a volume/accounting approximation, not a proven 2226 armour constitutive law.
- 16 identical radial wedge leaves, each 22.5° wide plus 1° angular overlap on both edges. Adjacent leaves alternate in two axial levels, separated by 20 mm; ideal two-level depth **0.4126 m**, not including bearings, seals, guides or frame.
- Off-axis blade pivot at radial distance R+0.07 m and angle 22° relative to each blade's centreline; rotate about ship x axis. One fully rigid wedge geometry in a given tier is rotated through sampled 1° increments.
- Collision among leaves in the **same axial tier** checked by convex polygon separating-axis tests for the complete opening path. Other-tier leaves are separated in the model by one leaf depth plus 20 mm **only on the flat-faced panoramic nose**. Adjacent physical leaf edges, hub, hinge mount and actuator solids are not tested.
- Each frame checks whether all material points could occupy a common longitudinal translation `dx`, outside the new fixed exterior surface (in the reserved stow annulus) and ahead of the original pressure head by at least the two-tier depth plus modest gap. **This permitted translation is a mathematical degree of freedom, not a designed rail**.
- A candidate is reported only if the *entire* path from closed to a centered clear radius within 10 mm of nominal is collision-free in this sampled 2D and axial-slot screen; it is not selected from an open-only screenshot.

## Executed results

| Case | Target clear R | Earliest sampled open stroke | Furthest blade radius in open state | Stow radial width | Nominal blade armour mass | Two-tier x-slot at open | Path screen |
|---|---:|---:|---:|---:|---:|---:|---|
| Compact 35° | 1.20 m | 60° | 1.811 m | 0.611 m | 1.33 t | +0.204 m | Narrow necessary constraints pass |
| Compact 35° | 1.45 m | None | — | — | 1.94 t | — | **Fails** complete-path clearance under these pivots |
| Panoramic 50° | 1.60 m | 62° | 2.415 m | 0.815 m | 2.36 t | +0.608 m | Narrow necessary constraints pass |
| **Panoramic 50°** | **1.80 m** | **62°** | **2.710 m** | **0.910 m** | **2.99 t** | **+0.298 m** | **Narrow necessary constraints pass** |

The 1.80 m center is geometrically compatible with the 50° nose's existing 2.0 m *flat* front facet. This is a meaningful advantage over the 35° compact nose, where an R=1.45 m closure would cross the boundary between its 1.2 m flat central face and conical shoulder; a single rigid planar iris is not naturally compatible with that kink.

The successful 1.8 m iris has a theoretical opaque storage annulus from r=1.80 to approximately r=2.71 m. Its 16 leaves total about **11.08 m² of projected armour material** including geometric overlap, which accounts for about 2.99 t of 27 g/cm² material. The storage annulus itself covers about 12.9 m² in projection, but that is not proof of 3D solids fit with mechanisms.

The open-state necessary pressure/exterior envelope test returns about **0.298 m of permissible common x-translation interval** between the exterior and pressure surface after counting the two 0.1963 m material thicknesses, 0.02 m level separation, and modest face clearances. It does not include a transmission, seals, bearing diameters, pressure-pane flange or structural supports. No physical rotational mount or longitudinal cam is designed.

### Critical: closing all the way

The mathematical sector union covers the disk for every r>0, and at r=0 all the sector tips meet. **This is NOT the same as a manufactured, completely sealed, 27 g/cm² central closure.** Every finite-sized, blunt mechanical tip requires a hub/overlap/capping solution, with mechanical nesting and impact seams. The current exact central meeting point is an *idealisation*, not an achieved physical closure. The two axial levels also leave stepped outer armour surfaces unless an additional transition mechanism is provided. We cannot honestly label the requested **flush, fully protected closed state** as achieved.

### The price of an iris storage ring: panoramic visibility

If the iris occupies an opaque storage ring and four independent 40° sector side windows are retained outside that ring (through the previously modelled 3.5 m crown), the corrected source L1 ray model gives:

| Candidate | Worst Pilot/NAV 60° cone | Worst Pilot/NAV forward hemisphere | Worst support forward hemisphere |
|---|---:|---:|---:|
| Rev 7 full original crown baseline | 100% sampled | **69.14%** | **5.47%** |
| Compact 1.2 m iris + outer side windows | 82.59% | 35.16% | 6.25% |
| Panoramic 1.6 m iris + outer side windows | 95.54% | 39.45% | 6.64% |
| **Panoramic 1.8 m iris + outer side windows** | **100% sampled** | **32.03%** | **4.30%** |

This is the **same ray geometry and unchanged crew** used for the corrected baseline; only the aperture layout changes. The parked blades occupy much of the region that would otherwise provide peripheral views. A visually elegant iris therefore does not automatically improve the usable panorama. The 1.8 m central iris has a forward cone, but compared with Rev 7 loses about half the Pilot/NAV forward hemisphere.

## Verdict

**Keep the central armoured iris as a genuinely interesting, geometrically constrained design hypothesis, but do not adopt it.** It improves on the giant external petals: the idealized moving leaves stay within the 4.5 m hull radius and out of the first bow sensor ring. Two-level packaging appears possible on the 50° flat-face nose, for the blade-only idealization.

**It has NOT met the user's central requirement:** *fully closed, flush, armoured protection with a real hub/leaf seam.* Nor does it yet preserve Rev 7's broad panorama. The smallest concrete follow-up, if chosen, is an **actual end-seal/tip closure and recessed two-level bearing package**, not a new general spacecraft redesign or another generic optimisation sweep. That mechanical mechanism must fit the 0.3 m available axial positioning window and avoid making the outer side glazing disappear. Stop if those demands cannot be satisfied.

## Reproduce / view

- `command/l1_armoured_iris.py`: reproducible polygon motions, all-stage same-tier overlap screen, source-hull axial-slot checks, original-eye visibility comparisons; `command/l1_armoured_iris_results.json`.
- `render/make_armoured_iris_viewer.py`: self-contained rotatable HTML `render/out/nose_armoured_iris_viewer.html`, selectable nose, 0–90° 16-blade motion, saved 1° collision states and the central aperture/stow-band geometry. Desktop and Android browser compatible in principle; HTML/JS syntax was validated, browser-specific operation not yet independently tested.

The animation is **visual evidence of a studied geometry**, not a certification of a 2226 manufacturing design.
