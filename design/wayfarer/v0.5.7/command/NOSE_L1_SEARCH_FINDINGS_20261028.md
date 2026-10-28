# Wayfarer Rev 7: nose/L1 computational experiment | 28 October 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT CERTIFIED**

Source: PR #432, head 3485830a56dfead79b2ef8bba031a595b536fbb5. The experiment did not change the governing canon, PR source geometry, runtime or the main spacecraft.

## Executed

- Reproduced 28/90 analytic outer-profile survivors, with extension counts 0, 1, 4, 6, 8, 9.
- Screened 2,000 deterministic parameter candidates using distinct interior, pressure and outer geometry; 533 with retained ring sensors passed the coarse Pilot/NAV 60° cone threshold.
- Checked 20 initial candidates against actual Rev 7 room obstacles, then 28 *diverse, unchanged-seat* candidates using a consistent baseline.
- Triangulated eight selected exterior shapes with 72 angular sectors; ray-triangle tests reproduced the analytic visibility percentages to the quoted four digits. All inspected meshes showed sampled positive pressure-head clearance. This is still concept-mesh geometry, not detailed CAD.
- Produced an interactive scaled, rotatable standalone HTML viewer with Rev 7 six-couch, eye, flight-deck and pressure-shell coordinates.

Scripts: command/l1_design_search.py, command/l1_refine.py, command/l1_facet_mesh_check.py and render/make_nose_search_viewer.py. Machine-readable JSON results alongside these scripts; viewer: render/out/nose_search_viewer.html.

## CRITICAL baseline correction

Rev 7 l1_study.py evaluates the crown for Pilot/NAV, but calls the older shoulder-window ray scorer for support stations. Its support-station 1.1–1.5% percentages thus **do not count all potentially visible sky through the adopted crown**. These values must not serve as the denominator for a new dual-glazing experiment.

The consistent re-evaluation models the original ellipsoidal outer surface and original pressure head as separate surfaces, uses the same 8 cm integrated frame as for candidates, retains the original sensor ring, and tests actual room obstruction.

### Consistent reference

| Station | Forward hemisphere | Forward 60° cone |
|---|---:|---:|
| Pilot | 69.14% | 100% sampled |
| NAV | 73.44% | 100% sampled |
| S1 | 7.03% | N/A |
| S2 | 7.81% | N/A |
| S3 | 5.47% | N/A |
| S4 | 6.64% | N/A |

These are conditional modelled visibility estimates. Source-reported Pilot/NAV ~75% uses its different test and remains a distinct metric. Each hemisphere uses 256 deterministic directions; each pilot cone 224.

## Unchanged-L1 candidates (integrated frame, retained sensor ring)

| Exterior extension / face / angle | Crown pattern | Total length | Worst Pilot/NAV forward | Worst Pilot/NAV 60° | Worst support forward | Pressure glazing area |
|---|---|---:|---:|---:|---:|---:|
| Original ellipsoidal bow | Current 2.8 m | 53.3 m | 69.14% | 100% sampled | 5.47% | 25.53 m² geometric / 25 m² declared |
| +0.8 m / 1.2 m / 35° | Radial 3.5 m | 54.1 m | 76.56% | 100% | 10.94% | 41.38 m² |
| +1.2 m / 2.0 m / 50° | Radial 3.5 m | 54.5 m | 72.66% | 100% | 10.94% | 41.38 m² |
| +0.8 m / 1.2 m / 35° | Radial 3.2 m | 54.1 m | 72.66% | 100% | 7.81% | 33.93 m² |
| +0.8 m / 1.2 m / 35° | Targeted 3.5 m | 54.1 m | 64.45% | 100% | 7.81% | 28.04 m² |

50° axial incidence is more grazing than 35° but **facet angle does not establish impact survival**. Original frontal dust collection projection is approximately π×4.5² = 63.6 m² for all nose candidates. All panes require protection at high speeds.

## Shutter packaging test

At 27 g/cm² armour-equivalent closed-shutter protection (270 kg/m²) and assumed stored effective density 1.375 t/m³:

| Glazing | Armour-equivalent material | Material volume alone | Illustrative gross shoulder pocket |
|---:|---:|---:|---:|
| 41.38 m² | 11.17 t | 8.13 m³ | ~5.5 m³ for 3.5 m crown |
| 33.93 m² | 9.16 t | 6.66 m³ | ~6.9 m³ for 3.2 m crown |
| 28.04 m² | 7.57 t | 5.51 m³ | ~5.5 m³ for 3.5 m crown |

These volumes **exclude** tracks, actuators, clearances, structure, and sensor conflicts. The 3.5 m radial shutter cannot stow in the assumed shoulder pocket; the 3.2 m radial shutter leaves only ~0.24 m³ gross difference before mechanisms, not proof of fit.

The 41.38 m² glazing requires about 1.39 t additional pressure-pane material above the declared 25 m² at 85 kg/m², but total dry mass, extra frames, centre of gravity and shutter mass accounting are unclosed. Shutter armour may replace existing armour, so do not automatically charge the entire 11.17 t as an *incremental* mass.

## Closure boundaries

- Rev 7 pressure head preserved: radius 4.30 m, original tip x=0.20 m and shoulder x=2.35 m. Usable interior radius 4.15 m.
- Sampled pressure-head axial gap was positive for inspected facet meshes, including 0.291 m for +0.8 m / 35° and 0.438 m for +1.2 m / 50°. This is neither normal armour thickness nor ballistic qualification.
- Rev 7 six couches, flight deck, ladderways, access and 2.28 m minimum walkway headroom remain unchanged for final alternatives; exploration variants that moved seats are NOT validated.
- Original 8.428 t / 12.995 m³ sensor-ring occupancy stays in place. Relocation variants are only visibility hypotheses; no undocumented L2 capacity was claimed.
- Opening larger transparent apertures in the existing pressure surface is a hypothesis, not a structurally verified pressure window.
- Glazing sealing, fracture, dust impact, shutters and swept volume, forward Metric-node collisions, and full added mass/CG remain unresolved.

## Decision and stopping condition

**No configuration has demonstrated full physical closure.** The leading blockers are shutter stowage and structurally credible pressure apertures. The computational search is a useful screening result, not a certified design.

Keep two non-governing directions:

1. **Visibility-first:** +1.2 m extension; central face 2.0 m; 50° facets; radial 3.5 m glazing. Gives 10.94% worst-support visibility versus 5.47% consistent reference and improves pilot forward sky, but the minimum protective material volume exceeds shoulder pocket capacity.
2. **Compact hypothesis:** +0.8 m extension; face 1.2 m; 35° facets; radial 3.2 m glazing. Gives 7.81% worst-support visibility at 33.93 m² glazing; shutter material nearly fills the estimated gross pocket and lower axial dust grazing must be dealt with.

**Smallest next experiment:** try *one* physically drawn, stowable, segmented shutter for the 3.2-m crown with the real sensor ring occupancy and 0.8 m circulation preserved. If it cannot fit, reduce windows or retain Rev 7 and improve sensor/remote visualisation. No main-ship redesign or new engineering framework is justified.
