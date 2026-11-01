# Wayfarer L1: improving the INTERNAL pressure glazing while HOLDING the 37-panel outer shield
**29 October 2026 | RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT PRESSURE/OPTICAL/IMPACT QUALIFIED**

## Authority / scope

Live GitHub bootstrap confirms \`loom-2226/loom-2226\` PR #432 open at original Rev 7 head \`3485830a56dfead79b2ef8bba031a595b536fbb5\`. Only this isolated research branch is changed. **The selected 37-piece staggered transparent OUTER protective cover is HELD exactly as specified**: one central r0.75m pane, 12 inner ring panes to r2.0m, 12 panes to r2.75m, 12 staggered panes to r3.5m; opaque outer seam width fixed at a nominal 10mm. The inner structural pressure-hull geometry, actual source station eyes/furniture, L1 bow sensor ring and +1.2m 50° angular exterior remain fixed.

Question: can the **inner structural window framing and/or size** improve sightline experience without touching the chosen outer 37-piece layout?

The reference inner frame is the earlier research model's **80mm meridional pressure members at every 45°, an 80mm ring at r1.15m, and an 80mm perimeter band**. These are view-blocking mathematical bands, not actual pressure-qualified structures. The ray experiment compares narrower bands, relocation of the *internal ring*, additional spokes, and modest aperture extensions along the same pressure ellipsoid.

## Executed run

The simulator reused the source \`l1_design_search.py\` ellipsoid/exterior ray intersections, \`l1_study.py\` interior furniture obstruction model and source sensor masks. The held 37-panel outer mask was applied at its actual exterior ray interception, and an independent candidate inner frame mask applied at the inner pressure-ellipsoid intercept. Counts are 4096 equal-solid-angle forward hemisphere rays per Pilot/NAV and 1536 per support station, with all ray/classification totals conserved.

| Inner structural frame hypothesis | Pilot forward sky | Navigator forward sky | Worst S1–S4 forward sky | Change in Pilot sky vs reference |
|---|---:|---:|---:|---:|
| **Reference:** 8 spokes, 80mm, ring r1.15m | **72.53%** | **72.63%** | **11.00%** | baseline |
| 8 spokes, 40mm, ring r1.15m | **75.78%** | **75.88%** | **11.26%** | **+3.25 pp** |
| 8 spokes, 40mm, ring r1.50m | **77.00%** | **77.05%** | **11.33%** | +4.47 pp |
| 8 spokes, 40mm, ring r2.0m | **77.71%** | **77.78%** | **11.20%** | **+5.18 pp** |
| 8 spokes, 80mm, ring r2.0m | 76.68% | 76.59% | 10.94% | +4.15 pp |
| 8 spokes, 40mm, ring r0.75m | 74.07% | 73.93% | 11.33% | +1.54 pp |
| 12 spokes, 40mm, ring r0.75m | 72.92% | 73.12% | 11.13% | +0.39 pp |
| **Unqualified optical ceiling**, ring r3.0m, 8 spokes, 40mm | 78.61% | 78.66% | 11.39% | +6.08 pp |
| Rim-only unrealistically unsupported inner window | 78.61% | 78.66% | 11.46% | +6.08 pp |

At 10mm opaque seams, the source interior baseline **Pilot blockage breakdown of 4096 forward rays** is: 223 opaque outer nose, 72 held 37-panel exterior seams, 581 existing interior furniture/occlusion, 249 inner 80mm frame, 2971 unobstructed. Narrowing the 8x80 frame to 8x40 at r1.15m reduces the final frame-blocked count from **249 to 116**. Moving the ring to r2.0m with the 40mm structure reduces that count to **37**. These are ordered, mutually exclusive masks; a blocked ray can in reality intersect more than one obstruction, so the count for any single reason is a waterfall not an independent overlap analysis.

### Why moving the central ring outward looks attractive (and is not earned yet)

The frame moved out from r1.15 to r2.0 is intercepted by far fewer real Pilot/NAV sightlines. It also corresponds to the exterior flat-to-facet radius, though inner and outer ring alignments are **not physically coincident** and are viewed through substantial parallax. Simply moving it inward to r0.75, in fact, worsened the panorama relative to retaining r1.15. Adding 12 meridians to match the outer 12-fold symmetry also worsened Pilot/NAV sky coverage in this experiment.

**Critical boundary:** a 40mm mullion has not been demonstrated capable of taking the same pressure loads as an 80mm one; moving an inner ring from r1.15 to r2.0 increases its unsupported central pane span and pressure loading. A ring at r3 is a deliberately unrealistic optical ceiling requiring very large pressure-proof unsupported glazing. None of these experiments demonstrate structural adequacy, crack arrest, redundant pressure containment, pressure cycling, optical transmittance or impact safety.

### Why expanding inner window radius doesn't help

Keeping outer 37-panel protective glazing capped at r3.5m, we tested inner transparent radius r3.5, r3.65 and r3.8 along the **same pressure ellipsoid**. Pilot and Navigator visibility results were **identical for all three radii** across the studied frame options, to this ray sample resolution. Support stations sometimes gained ≤0.07 percentage points, and most gains were zero. Because the outer shell becomes opaque beyond r3.5, opening more of the inner pressure hull does not create corresponding outside view. **Do not enlarge inner pressure glazing solely to chase visibility**, which would add pressurised window area and structural exposure for essentially no experience gain.

### Support stations are a separate issue

At reference, S1–S4 forward scores are ~11–12%. Their ordered blockage tally is dominated by no geometric direct line through the relevant front ellipsoid (~456–459 / 1536) and opaque outer shield (~649–651 / 1536), with relatively few frame-blocked rays (~7–11 / 1536). Even idealized frame removal gains little. To give the support positions actual panoramas, one would need a different view geometry or station sightline, such as an exterior side-window extent change or relocating/reorienting their eye positions. **Those are outside this fixed-37 outer and unchanged-station experiment.** Avoid pretending inner frame optimization will improve everybody.

## Decision / smallest next move

1. **HOLD the 37-panel exterior unchanged.** No shutter or exterior change earned.
2. Lead with a *hypothetical slimmer 8-spoke inner frame* at existing r1.15 ring: predictable ~**+3.25 pp Pilot forward-sky gain**, with least change to current internal support topology. The pressure-member strength still must be justified.
3. Keep *40mm 8-spoke + r2.0 ring* as a further non-canon upper candidate: a larger +5.18 pp gain, but a materially altered inner pressure-panel span. Do not accept on optical score alone.
4. **Do not promote 12-spoke inner framing simply for matching outer symmetry.** Sightline sampling says it is unhelpful.
5. **Do not expand the inner window radius past 3.5m** until the outer protected transparent extent changes for another demonstrated reason.

The functional stopper for actual adoption is the pressure-bearing **structural glazing design**, not the viewer: can we place a very high strength transparent pressure laminate and eight narrow structural members over the necessary span with redundancies, thermal behavior and cracking margin? Research this narrowly when needed. The known 2226 nanoengineering hypothesis may make it interesting, not automatically valid.

## Deliverables

- \`command/l1_inner_pressure_panorama_options.py\` and \`command/l1_inner_pressure_panorama_results.json\`: model and all combinations, including held outer 37-panel seams, all six source L1 stations, support-station blockage causality, and r3.5/3.65/3.8 inner radius results.
- \`render/make_inner_pressure_panorama_viewer.py\` and \`render/out/nose_inner_pressure_panorama_viewer.html\`: offline Android-friendly viewer with true per-seat sampled forward sightline masks and frontal 37-panel/pressure-frame overlay. Numerical display uses full 4096/1536 rays; painted sky uses 768 rays per station, deliberately separate resolutions.

**Rev 7, PR #432, canon and runtime untouched.**
