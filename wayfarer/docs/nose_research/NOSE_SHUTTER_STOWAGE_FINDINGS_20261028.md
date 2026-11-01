# Wayfarer nose: radial shutter stowage experiment | 28 October 2026

**Research only. Non-canon, non-runtime, non-governing and not certified.**

Source: PR #432 at `3485830a56dfead79b2ef8bba031a595b536fbb5`. Builds directly upon the same-day controlled view search (branch `research/wayfarer-nose-l1-search-20261028`). This experiment changes no Wayfarer source geometry, no L1 stations, no main-ship structures and no runtime.

## Question

Can a physically segmented armour-equivalent shutter protecting an enlarged 3.2 m crown stow against the existing exterior shoulder (r=3.2–4.5 m), without invading the original pressure head, expanding the diameter beyond 9.0 m or disturbing the forward Metric-node ring?

The answer for a **simple radial sliding/nested tambour under the tested assumptions is no**. The failure is geometric, not a need for more software.

## Executed necessary constraints

- Original Rev 7 pressure ellipsoid r=4.30 m, tip x=0.20 m and shoulder x=2.35 m.
- Idealised faceted exterior r up to 4.50 m and the actual first 16 forward Metric-node face coordinates from `out/wayfarer_v05_geometry.json`.
- 27 g/cm² shutter areal protection, effective material density 1.375 t/m³: equivalent single-layer thickness **0.1964 m**. The calculation excludes mechanisms, tracks, structural spacing, and any bending or fold penalties.
- Tested exposed glazing and available annular exterior areas, meridional travel lengths, necessary number of nested layers and whether stacks intrude into the pressure head.

| Exterior / crown | Shutter cover area | Available shoulder surface | Area margin | Shutter meridian / stow meridian | Minimum lengthwise layers | Pressure-head result for nested layers |
|---|---:|---:|---:|---:|---:|---|
| +0.8 m, 35°, radius 3.0 m | 33.52 m² | 43.15 m² | +9.63 m² | 3.40 / 1.83 m | 2 | Intersects |
| +0.8 m, 35°, radius 3.2 m | 38.27 m² | 38.39 m² | **+0.12 m²** | 3.64 / 1.59 m | **3** | **Intersects** |
| +0.8 m, 35°, radius 3.5 m | 45.98 m² | 30.68 m² | **−15.30 m²** | 4.01 / 1.22 m | 4 | Intersects |
| +1.2 m, 50°, radius 3.2 m | 43.07 m² | 48.92 m² | +5.85 m² | 3.87 / 2.02 m | 2 | Intersects |
| +1.2 m, 50°, radius 3.5 m | 52.89 m² | 39.10 m² | −13.79 m² | 4.33 / 1.56 m | 3 | Intersects |

All areas are idealised, unsegmented mathematical surface-area capacity. A positive area margin is **necessary but not sufficient**; even 0.12 m² would be consumed immediately by practical rails and separation.

For the compact 3.2 m case, its three equivalent material layers would have total normal thickness ~0.589 m, before drives or clearance. The actual inward-normal swept stack intersects the pressure-head surface. The minimum calculated signed **axial** pressure clearance is −0.429 m for three layers, not a qualified wall penetration depth. One single layer fits only narrowly in the model (minimum +0.051 m).

As a sensitivity check, making three idealised layers clear the pressure head would require single-layer equivalent thickness at most ~0.0793 m, or an effective protective density of **at least 3.40 t/m³ at the same 270 kg/m²**, before rails and spacing. That is a change to the assumed material/architecture, not a discovered fit.

The first forward Metric-node ring contains 16 faces of 0.35 m diameter at x=2.05 m, radius about 4.463 m. This falls in the geometric shoulder region. We checked the positions but did **not** prove clearance of the node assemblies or their necessary angular/field of regard; a shoulder stowage concept cannot assume the collar is empty.

Stowing over the **outside** of the 9.0-m diameter instead of inside it also introduces a dimensional violation: even one outward equivalent layer on the 35° facets would expand the diameter by about **0.225 m**, unless the exterior were redesigned to recess it. That would violate the current assumption that the main outer diameter is retained.

## Decision

**Reject the tested simple radial-shoulder tambour as physically unclosed.** The 3.5 m crown additionally fails the single-layer exterior annular surface-area budget. Do not call any shutter concept feasible just because a rendered petal can slide.

The existing Rev 7 layout already supplies near-complete Pilot/NAV forward 60° visibility in the source studies. The corrected visibility improvement for supports with the new 3.2 m radial crown is 5.47% → 7.81% worst station. Under current assumptions, this modest improvement does **not** justify adding 7.52 m³ armour-equivalent shutter material plus an as-yet-unresolved mechanism.

**Best next design decision:** retain Rev 7 as the current baseline and stop pursuing a radial panoramic crown unless a distinct, externally protected stowage geometry is demonstrated. Existing sensors plus digital views can serve support positions. The 3.5 m, 50° visual concept remains parked for possible low-speed future redesign, not an adopted configuration.

This experiment does **not** prove every possible hinged, revolving, folding or higher-density shutter arrangement impossible. It isolates the particular straightforward stowage claim that failed.

Files: `command/l1_shutter_stowage.py`, `command/l1_shutter_stowage_results.json`, and the metrically scaled section `render/out/nose_shutter_stowage_section.svg`.
