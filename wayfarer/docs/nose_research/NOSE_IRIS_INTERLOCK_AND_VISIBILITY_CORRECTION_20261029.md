# Wayfarer central iris: interlocking joint and visibility correction | 29 October 2026

**RESEARCH / NON-CANON / NON-RUNTIME / NON-GOVERNING / NOT QUALIFIED**

Live bootstrap: `loom-2226/loom-2226` PR #432, unmodified source head `3485830a56dfead79b2ef8bba031a595b536fbb5`. The isolated research worktree remains on `research/wayfarer-nose-l1-search-20261028`. Original pressure head, sensor ring, Metric nodes, crew, runtime and PR untouched.

## Two narrow questions

1. Does a geometric interlocking joint improve **finite-clearance material continuity** without trapping the two leaf levels during the initial axial withdrawal?
2. Can the opaque iris stowage annulus still leave a worthwhile panoramic sky view, even if every other external sector beyond it were transparent?

We ran the smaller tests rather than inventing a new armour constitutive law or an entirely new nose.

## 1. Joint test: actual finite-clearance sections

The studied iris has **16 blades**, selected radius **1.76 m**, static armoured boss radius **0.12 m**, and original reference **27 g/cm² nominal full-column equivalent**, or **196.28 mm material depth** using the source's *effective accounting density*. The 50° angular external armour remains a **research assumption**. The pressure hull is unchanged.

Construct a 2D section at one seam in local tangential coordinate `s` and through-thickness axial coordinate `x`. Let the two moving materials occupy either side of a matched interface `s=f(x)`, with adverse recessions **0.5 mm per edge**, leaving **1 mm total local clearance**. Independently check normal material occupancy and whether the aft leaf could withdraw axially by its full 196 mm without colliding with the other half.

Three minimal shapes were executed:

| Joint | 3° overlap at r=0.12m | Worst *normal* material column, 0.5mm adverse edge error each | Can rear leaf peel axially? |
|---|---:|---:|---|
| Original complementary half-lap | 6.28 mm | **98 mm** (earlier report) | Yes |
| **Straight full-depth diagonal scarf** | **6.28 mm** | **165.0 mm** | **Yes** |
| Monotone releasable dogleg | 6.28 mm | 130.0 mm | Yes |
| Reversing interlocking labyrinth | 6.28 mm | 165.0 mm | **No, jams** |

These figures are **geometric occupied material column**, not an evidence-based conversion of that column into protection probability, thermal integrity, or ballistic-limit performance. In particular, a straight diagonal scarf can provide a narrow oblique interface and is *not* proof against an oblique high-speed strike. A reversing labyrinth with the same nominal material column causes as much as **5.28 mm lateral interpenetration** in the sampled required rearward withdrawal at the central boss; it needs a new release motion and is rejected under the current minimal mechanism.

The 3° full-leaf planar envelope still clears the 16-leaf **sampled cam** at 62°, with about **23.95 mm remaining axial positioning interval** and a central unobstructed radius of **1.75084 m**. But this does **not** qualify a complete manufactured scarf joint: we have not drawn the finite 3D tangential-clearance faces, hub gasket, seam-to-cam bearings, or their fatigue/shock behavior.

At the wider 4° lap, the 16-leaf cam has only about **9.67 mm available** and its clear radius falls to **1.74468 m** at 62°, missing the specified 1.76 m radius by more than the 1 cm tolerance. Thus increasing overlap or inventing a deeply interlocked joint is not cost-free.

**Result:** use a straight full-depth scarf as a simple geometry *research candidate*, not an approved impact seal. No tested shape fully maintains 196.3 mm of solid nominal material at every normal column under the 0.5 mm adverse edge recessions. Existing stress/fragmentation models and hypervelocity tests for spacecraft shields do not justify calling equal areal mass or an obstructed optical channel equivalent to a monolithic plate.

External scientific context: NASA's [Hypervelocity Impact Physics](https://hvit.jsc.nasa.gov/hypervelocity-testing/impact-physics.html) and [Shield Reference Documents](https://hvit.jsc.nasa.gov/reference-documents/), and ESA's [Hypervelocity impacts and protecting spacecraft](https://www.esa.int/Space_Safety/Space_Debris/Hypervelocity_impacts_and_protecting_spacecraft). No standard monolithic ballistic-limit equation is claimed applicable to this moving joint.

## 2. Corrected optics: previous four-sector results were overstated

**Important reproducibility correction.** In `command/l1_armoured_iris.py` the iris visibility helper selected the *minimum signed* azimuth angle difference instead of **minimum absolute angular distance** from the four window centres. The signed check erroneously admitted rays outside the intended ±20° angular sectors. That inflated the published four-window Pilot/NAV forward-hemisphere values in the earlier iris reports. The helper has now been corrected and the primary generated result JSONs and existing viewers regenerated on this *research branch only*. Historical prose reports have a visible erratum pointing here. The original corrected Rev 7 baseline's own aperture calculation is unaffected.

With **the same unchanged source Pilot/NAV eyes, L1 furniture, pressure head, reference sensor ring, R1.76 iris, fixed 0.12 m hub** and opaque stowage annulus to r≈2.702 m:

| Central iris arrangement | Worst Pilot/NAV sampled 60° cone | Worst Pilot/NAV forward hemisphere | Worst support forward |
|---|---:|---:|---:|
| R1.76 iris plus **four actual 40° external windows** | **98.66%** | **26.17%** | 3.91% |
| Iris plus hypothetically **fully transparent outer annulus** | **98.66%** | **32.81%** | 4.30% |
| **Original corrected Rev 7 full-crown comparison** | 100% sampled | **69.14%** | 5.47% |

**The continuous outer annulus is an *unprotected optical upper-bound test*.** There is no retractable shutter or structural glazing qualification for that ring. Its 32.81% value cannot be presented as a practical design. And even in that unrealistic optimistic case, broad sky visibility remains far below Rev 7.

The earlier roughly **32–33% figure for the four-window version was WRONG**. Correct four-sector geometry is around **26%**. This error is substantial to the design decision, and now explicitly preserved as an erratum rather than silently overwritten.

## Decision

**Continue to preserve the central iris as an interesting non-canon *mechanical* candidate, but do not declare it ready for the Wayfarer command deck.** There are two independent blockers:

- No established *manufacturable, impact-resistant* finite-clearance joint capable of meeting the nominal protected closure requirement. The straight scarf is geometrically more efficient than the naive half-lap, but lacks ballistic evidence.
- The central iris's **large opaque storage annulus inherently consumes much of the view**. Changing the outer four windows to an impractically transparent full ring recovers only a limited fraction.

A new elaborate leaf abstraction, magic material or ship-wide redesign is not justified by those results. We have a small executable model and a hard visibility ceiling. Next useful choice is primarily **experiential**: inspect the working 3D model and decide whether the forward central viewpoint is sufficiently valuable to accept the loss of panorama. Otherwise prefer a simpler smaller-viewer architecture or return to source Rev 7 experience testing.

## Reproducible outputs

- `command/l1_iris_joint_kinematics.py` / `command/l1_iris_joint_kinematics_results.json`: 2D physical interface shapes, finite gap occupancy and axial undercut check; 2°, 3°, 4° gross footprint cam replay.
- `render/make_iris_joint_viewer.py` / `render/out/nose_iris_interlocking_joint_viewer.html`: offline touchscreen-friendly interactive joint-section viewer (blade shape, gap, axial withdrawal); not an impact simulation.
- `command/l1_iris_visibility_upper_bound.py` / `command/l1_iris_visibility_upper_bound.json`: exact four-sector test versus nonphysical fully transparent outer-annulus upper bound.
- `command/l1_armoured_iris.py`: correct `abs(angdiff)` in window selection, re-generated `l1_armoured_iris_results.json`, `l1_iris_two_tier_cam_results.json` and the associated prior HTML viewers.
