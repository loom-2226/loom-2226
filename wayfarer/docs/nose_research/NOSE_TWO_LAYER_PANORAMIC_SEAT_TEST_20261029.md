# Wayfarer L1: two transparent boundaries viewed from all six real command stations | 29 October 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT OPTICALLY, PRESSURE OR IMPACT QUALIFIED**

## Authority and actual narrow experiment

Bootstrapped live authority: `loom-2226/loom-2226` PR #432 is open, original Rev 7 source at `3485830a56dfead79b2ef8bba031a595b536fbb5`. All implementation and artifacts are research-only on `research/wayfarer-nose-l1-search-20261028`.

The preceding `NOSE_TRANSPARENT_GLAZING_NO_SHUTTERS_FINDINGS_20261029.md` proposed an *outer non-pressure transparent impact skin* and a *separate inner load-bearing transparent pressure hull*, with an unpressurised space between them. This is a two-boundary design; each of those boundaries could be an unspecified multi-ply laminate. **This test makes only the already proposed two boundaries explicit, without altering the pressure hull shape or L1 seats.**

Question: which lines of sight from actual Pilot, Navigator and S1–S4 eye positions pass through **both** transparent openings, and how much room is there for two illustrative material thicknesses? In particular, do the sightlines encounter dangerous grazing angles on either boundary?

## Reproduced source geometry

- Rev 7 six original eye positions and furniture: `l1_refine.py` + `l1_design_search.py` + source `l1_study`.
- **Original structural pressure-envelope shape unchanged**, ellipsoidal cross-section `x=2.35−2.15 √(1−(r/4.3)²)`; however a 3.5 m transparent aperture necessarily means **replacing some opaque existing pressure-hull material with hypothetical structural glazing**. The shape is retained; its material and pressure integrity are not qualified.
- Research exterior nose, **+1.2 m**, flat to r2.0 m, 50° facets beyond; not an authorized Rev 7 change.
- Outer glazing radius and inner pressure glazing radius both set to 2.8, 3.2 or 3.5 m.
- The existing bow sensor ring (inner radius ~2.9 m), original crew furniture and pressure-hull reference frames remain in the visibility path.
- Same 256 equal-solid-angle forward rays/eye as previous no-shutter experiment; 256 sampled Pilot/NAV forward-60° rays. Each ray is checked at both physical surfaces, the pressure frame, sensor ring, and furniture. The model keeps rays straight through the panes, i.e. **zero refraction, reflection, scattering, opacity or optical extinction**.

## Actual results

| Transparent crown radius | Pilot forward sky | Navigator forward sky | Worst support forward sky | Pilot/NAV forward 60° cone | Tightest gross gap *between both material layers* |
|---|---:|---:|---:|---:|---:|
| 2.8 m | 49.61% | 52.73% | 4.30% | 100% | 0.808 m |
| 3.2 m | 63.67% | 67.58% | 7.42% | 100% | 0.525 m |
| **3.5 m** | **72.66%** | **77.34%** | **10.94%** | **100%** | **0.352 m** |

For the 3.5 m configuration, out of 256 Pilot forward-hemisphere sample directions:
- **186** pass through both transparent apertures and the surviving frame/sensor/furniture tests;
- **14** are blocked by the opaque exterior beyond the 3.5 m crown;
- **20** are blocked by the modeled pressure-pane frame;
- **36** are blocked by existing interior geometry;
- **0** additionally blocked by the retained sensor ring *after the preceding ordered masks* (the sensors remain modeled; this is a conditional count, not an assertion of physical disjointness).

Navigator has 198 visible / 256 sampled directions (77.34%). Worst support stations S3/S4 each have 28 visible / 256 (10.94%), with the rest largely intercepted by the still-opaque pressure hull and/or source geometry.

The corrected original Rev 7 ellipsoidal/full-crown **Pilot/NAV worst is 69.14%**. The no-shutter angular 3.5 m candidate is therefore geometrically superior from the crew eyes, *if* the hypothesized transparent material and structures can exist.

### The significant optical caveat: high incidence at the inner glass

For the 3.5 m crown:
- **Pilot** visible rays: median inner glazing incidence **51.55°**, median outer **22.33°**; **59 of 186** rays meet at least one layer at ≥60° incidence.
- **Navigator** visible rays: median inner glazing incidence **52.47°**, outer **21.85°**; **66 of 198** visible rays reach ≥60° at one or both transparent boundaries.
- Incidence is based on the local mathematical surface normal. This is not a measured optical degradation. But thick, layered, mismatched refractive-index windows at such angles may have substantial reflection, refraction, image warping and optical artifacts. A real optical design must consider it before adopting 72.66% as *useful visual experience*.

### Physical separation of outer protection and inner pressure layer

We used **illustrative dense-layer thicknesses**, not proven material specifications:
- Outer protected skin: incumbent opaque 27 g/cm² mass allowance, **270 kg/m²**, if occupied by ALON-density 3,670 kg/m³ → **0.07357 m** normal thickness.
- Separate internal pressure glazing: the source's aggregate **2.13 t over ~25 m²** source panes → **85.2 kg/m²**; if occupied by fused-silica-density 2,210 kg/m³ → **0.03855 m** normal thickness.

The 3.5 m angular nose's closest axial gap between outer and inner **solid material boundaries**, after accounting for local facet angle and pressure-ellipsoid slope, is **0.35185 m**, near r=3.5 m. For 3.2 m, 0.52517 m; for 2.8 m, 0.80848 m. Thus there is gross space for a gap and at least 0.10 m *illustrative reserve*, without placing either layer in the habitable command deck.

That **does not establish a physical interspace of freely available structural depth**: there may be unmodeled peripheral mounts, reinforced structural windows, replaceable impact layers and supports. The source pane mass density scaling is only an illustration. Even a physically packaged pair may still fail high-velocity impact/pressure loading.

## Outcome / stopping condition

**Test passes only for both-boundary ray geometry and gross material-layer separation.** No new shutter mechanisms required. The 3.5 m crown is the leading non-canon experience candidate.

**Critical unearned leap:** 72.66% of directions are only geometrically unobstructed, not proven clear to human eyes through 7.36 cm dense external protective glazing and a separate 3.86 cm inner pressure glazing, especially given frequent oblique inner-pane incidence. And the new inner aperture must be genuinely load-bearing, a harder problem than a simple window surface replacement.

The next research question should stay narrow: **how much useful optical transmission is plausible for specified 2226 candidate refractive indices and coatings across these two glazings at these measured incidence angles?** Do not build a full optics engine or material law without a concrete optical-quality question. First, examine the per-seat viewing mask in the interactive research viewer and decide if the angles and obstruction profile look worth carrying forward.

## Artifacts

- `command/l1_two_transparent_layers_view_test.py` → `command/l1_two_transparent_layers_results.json` stores all per-seat per-crown 256-ray classifications, both surface intersection points, surface-normal incidence angles and gross two-surface clearance.
- `render/make_two_layer_seat_viewer.py` → `render/out/nose_two_transparent_layers_seat_viewer.html`: fully offline interactive view of forward sky for all six real source stations and three crown radii, plus a 2D cutaway showing the actual selected ray, both transparent boundaries and obstruction reasons.

**No source PR, Rev 7, canon or runtime mutation.**
