# LOOM Wayfarer: sideways-sliding crown shutters | 28 October 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT CERTIFIED**

Live source checked: PR #432, `loom-2226/loom-2226`, Rev 7 head `3485830a56dfead79b2ef8bba031a595b536fbb5`. Isolated work branch `research/wayfarer-nose-l1-search-20261028`; no changes to the authoritative ship, main, runtime or existing PR.

## Objective and result

**Objective:** Explore unobtrusive, sideways/circumferential shutters, not forward-opening petals. Keep the unchanged pressure head, original sensor ring, ring-zero Metric nodes, six L1 crew locations, 9 m reference maximum diameter and at most 2 m extra closed nose length.

**Result: neither of the two straightforward sideways mechanisms closes physically and experientially.** An alternating half-glazed crown ring can store sector shutters azimuthally, but leaving the middle opaque destroys the Pilot/NAV forward view. Adding a separate central aperture restores the forward cone, but demands large central covers, external shoulder parking and a travel path that is neither flush nor mechanically proven.

## First trial: ring-only azimuthal shutters

Dividing the whole crown into alternating transparent and opaque 22.5° or 45° sectors provides one opaque sector to park each moving sector at the same radius, with no radial stacking. But the central r≤1.2 m disk remains opaque. For the existing Pilot/NAV forward 60° sample cone, **all 224 sampled rays for each seat intersect the pressure head inside r≈0.93 m**. A blind central disk consequently scores **zero** direct 60° cone visibility through both layers. The scheme fails the central operational purpose.

## Second trial: central view plus smaller independent side windows

We modelled a transparent central disk and four independently shuttered annular windows, first with 22° sectors and then 40° sectors. The four wider window centres are 45°, 135°, 225° and 315°, with lateral/azimuthal storage at 0°, 90°, 180° and 270°. Source L1 furniture, eye positions, bow sensors, pressure head, outer shell and room blockage were reused in the same visibility metric as the earlier corrected Rev 7 baseline.

| Measurement | Corrected Rev 7 full crown | Compact angular lateral study |
|---|---:|---:|
| Outer profile | Ellipsoid | +0.8 m, 35°, flat face radius 1.2 m |
| Glazing layout | Full crown radius 2.8 m | Central radius 1.45 m + four 40° windows to radius 3.2 m |
| Approx exterior opening protected | 25.50 m² | **20.94 m²** |
| Minimum Pilot/NAV forward 60° cone direct visibility | 100% sampled | **100% sampled** |
| Worst Pilot/NAV forward hemisphere direct visibility | **69.14%** | **46.48%** |
| Worst support station forward hemisphere direct visibility | **5.47%** | **3.12%** |

All fractions are model-based directional samples with source room obstacles and retained sensors; not certified operational field of view. The compact candidate reduces panoramic visibility despite its angular silhouette. In particular, achieving a clear Pilot/NAV cone is **not** the same as retaining the broad sky view that motivated the project.

The analogue tested with 22° side-window sectors yields still less sky. A +1.2 m / 50° panoramic nose requires about r=1.8 m transparent central access for a full sampled Pilot/NAV cone; covering that center with laterally parked rigid half-discs inside 4.5 m is even less attractive.

## Third trial: physical moving cover points on compact angular nose

The targeted 20.94 m² aperture was converted into **six actual protective material point-cloud panels**:

- Two thick, rigid half-discs protecting the r≤1.45 m central aperture. Each first lifts clear, then translates ±2.8 m along the y-axis while tilting by up to 35° to approach the angular shoulder. At every intermediate pose, the program gives the panel the most favourable axial x offset that remains exterior to the outer hull. This is **an optimistic kinematic degree of freedom**, not a manufactured track.
- Four 40° curved/conical annular plates over r=1.45..3.2 m, each rotating 45° in azimuth to an adjacent opaque sector after lifting outboard by approximately its 0.196 m equivalent material thickness plus a small gap.
- All panels use the same effective armour-areal protection as the source, **27 g/cm²**, with effective density about **1.376 t/m³**. The density comes from the source armour mass/volume ledger and is **not** a qualified materials law. Tests include front/back material samples.
- Sampled 11 progress positions for three operation orders: central first, side windows first, both simultaneously. The original pressure profile, unchanged front Metric-node face markers and sensor occupancy were not relocated.

| Motion-sequence comparison | Central covers first | Side windows first | Simultaneous |
|---|---:|---:|---:|
| Smallest sampled center-to-side panel point separation, after motion starts | **0.092 m** | **0.028 m** | **0.017 m** |
| Largest radius at any sampled pose | 4.323 m | 4.323 m | 4.323 m |
| Greatest central-cover stand-off during motion | 0.706 m | 0.706 m | 0.799 m |
| Stowed central-cover max stand-off | **0.557 m** | 0.557 m | 0.557 m |

The model returns no face-marker overlap at sampled poses, but **a 0.017 m or 0.028 m point separation is no proof of clearance of 0.196-m-thick mechanical plates, rails or seals**. The central-first path is the least-bad, at about 9.2 cm minimum point separation, but also has no demonstrated bracket clearance or continuous swept-solid guarantee. Some closed/partially lifted points correctly sit behind the armour surface as the front-protective panel starts at the glazed opening.

Crucially, in its *open* pose the central armour lies **as much as 0.557 m proud of the shoulder**, despite the optimistic adjustment to keep it from penetrating the hull. It does not become a concealed shutter. During translation it extends ~0.7 m away. That contradicts the desired sleek, largely unchanged ship silhouette.

## Decision

**Reject this particular six-panel low-profile sideways mechanism as currently unclosed.** The experiment identifies the real engineering trade: hide 27 g/cm² of armour for a continuous central panoramic aperture, and the storage material must occupy actual volume, leave the hull, or suppress other glass.

No successful shutter mechanism was found; neither Rev 7's declared 16 gore brow stowage nor the new angular crown earns mechanical qualification. This lane does **not** justify revising the pressure head, adopting new optical shielding, relocating sensors or reworking L1. The user-established prohibition on conspicuous external petal/flower mechanisms remains in force.

This does not disprove physically viable circumferential slats, articulated compact telescoping shields or alternative high-density shielding. It rejects the explicit mechanisms tested under current source assumptions. Work should resume only with a specific new physical arrangement that can improve visibility without exposed hardware or unresolved pockets.

## Reproducibility and visualisation

- `command/l1_circumferential_ray.py` and `command/l1_lateral_reserved_visibility.json` evaluate the actual source eyes, pressure and room rays.
- `command/l1_lateral_slide_sweep.py` and `command/l1_lateral_slide_sweep_results.json` move six real-coordinate protective shapes with 0.196 m equivalent thickness and record point separations, envelope limits and stand-off.
- `render/make_lateral_shutter_viewer.py` builds `render/out/nose_lateral_shutter_viewer.html`, a standalone downloadable HTML that depicts the observed **failed/unfinished mechanism**, with scene rotation, motion slider, three sequences and quantitative sampled clearance readout. It is explicitly not physically qualified CAD.

**Stopping condition met:** the first narrow non-flowering shutter proposals have been exercised, with the optical and storage constraint demonstrated. No new spacecraft architecture was required.
