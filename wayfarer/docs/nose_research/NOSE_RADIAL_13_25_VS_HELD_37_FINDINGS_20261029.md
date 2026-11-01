# Wayfarer L1: large radial glazing from the central oculus vs held 37-panel reference
29 October 2026 · **RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT STRUCTURALLY / BALLISTICALLY / OPTICALLY QUALIFIED**

## Live authority and scope

Authoritative upstream: \`loom-2226/loom-2226\`, live PR #432 still open at source head \`3485830a56dfead79b2ef8bba031a595b536fbb5\`. This is an experiment on isolated branch \`research/wayfarer-nose-l1-search-20261028\`. No governing Rev 7, source PR, runtime or canon files changed.

The user explicitly **holds the existing 37-panel staggered outer-glazing concept**. Do NOT silently promote this experiment to canon, or displace the held reference.

Question: what is actually gained by twelve **larger radial trapezoid-like transparent panels supported near a circular centre window**, as opposed to the replaceable 37-tile no-shutter outer protective cover?

## Unchanged geometry and inputs

- Flat transparent nose through r=2.0 m, then 50° axisymmetric sloped outer skin to r=3.5 m; +1.2 m forward extension. The central circular protective window is r=0.75 m. Outer protected transparent area ~52.888 m²; original protection mass *allocation* 270 kg/m² (~14.28 t total) is preserved across candidate layouts.
- Three separately identifiable, nominally **outer-serviceable**, fixed exterior protective panel layouts:
  1. **13** = central circular panel, 12 continuous radial strips from r=0.75 m to r=3.5 m.
  2. **25** = central circular panel, 12 radial panels from r=0.75 to 2.0 m, 12 aligned outward panels from r=2.0 to 3.5 m. Visible spokes remain continuous; the one transverse ring at the slope transition adds a seam.
  3. **HELD 37** = central circular panel r≤0.75 m, 12 ring pieces to r=2.0 m, 12 to r=2.75 m, 12 staggered to r=3.5 m, unchanged from previous research.
- All use **original Rev7 inner pressure glazing and eye positions**, bow sensors, frames, furniture. No shutters. Each outer panel can in principle be replaced without depressurising the inner cabin, *provided independently releasable retainers exist*; they are not designed or verified in this experiment.
- 700 radial × 720 angular weighted samples for physical outer surface area. 4096 forward directional sky rays per Pilot/NAV, 1536 per support station. 5 / 10 / 20 mm projected **fully opaque** illustrative seam widths. No refraction, transparency loss, support flex or real peripheral frames.

## Executed comparison

| Geometry | Independent outer panels | Largest outer panel area | Largest protective material module | Opaque surface seam area @10mm | Pilot sampled forward sky @10mm |
|---|---:|---:|---:|---:|---:|
| **13** continuous radial | **13** | **4.260 m²** | **1,150 kg** | **0.125 m²** | **72.97%** |
| **25** radial split at slope transition | **25** | **3.360 m²** | **907 kg** | **0.285 m²** | **72.80%** |
| **37 HELD** staggered, compact | **37** | **1.909 m²** | **516 kg** | **0.554 m²** | **72.53%** |

At these higher sample counts, the nominal no-outer-seam Pilot sky score is **73.83%**. The 256-ray previous calculation gave ~72.66%, solely a sample resolution issue; no new crew or hull geometry. The 13 design gains just **0.44 percentage points** over the held 37 layout, though it reduces outer seam area from ~0.55 to ~0.13 m² and cuts panel count almost threefold. The 25 radial layout gains just **0.27 percentage points** over 37, with nearly twice the largest panel mass.

These are only forward-sky directional sample counts, not optical clarity or a physical proof that thin seams are unnoticeable to a person. The number of visible lines and their direction/aesthetics may matter subjectively even when total area differs little.

## Material shape / frame complications we cannot erase

The long radial 13-panel concept is **not a planar trapezoid design** while keeping the current axisymmetric surface. Each panel spans a real flat-to-cone kink at r=2.0 m, and the radial straight chord from the r0.75 to r3.5 exterior profile deviates from the prescribed nose surface by **~0.813 m at r2.0**. Therefore a single long piece must be formed across a substantial bend or the whole outer nose's profile redesigned. That numerical value is **radial chord mismatch**, not a global best-fit plane solution.

Splitting the long pane at r2.0 eliminates **that particular radial kink** from each piece, but 12 angular sectors on a smooth conical envelope are still not exactly flat panes. A tangent-plane construction can differ by about **0.142 m at the r3.5 sector edge** (15° from sector centre). If authentic large planar facets are desired, alter exterior geometry in a separate explicitly approved experiment and re-evaluate collision, clearance, visibility and pressure isolation. Do not pretend flat panels fit the existing continuous cone without consequences.

One large pane weighing ~1.15 t is not impossible in free fall; what matters for replacement is *moment of inertia, maneuvering and securing*, robotics/crew handling, microgravity disturbance, exposed surface and crack replacement economics. That cost grows while visibility gains stay small. The 25-panel split reduces that burden but remains nearly a 0.91 t protected piece.

**Important central oculus structural distinction:** The radial panels must be mounted to a **structural ring surrounding the independent central circular glazing**, not anchored to the transparent centre pane itself. At r=0.75 m the support-ring circumference is 4.712 m, with 12 panel interfaces occupying ~0.393 m arc each; radial segments widen to ~1.833 m arc at the r3.5 outer rim. No central ring structure or load transfer is qualified. A real opaque central ring could impose a stronger visual obstruction than the modeled idealized 10mm seam.

## Replacement / shielding limits

This research assumes that each panel has a separate footprint, accessible retention and a route **outward into space**, independent of the inner pressure hull. It **does not test** actual ring fastener access, adhesive/release, seals, rim distortion, acceleration loading, temperature cycling, precision join, adjacent structural overlap, support hardware, stress concentrations, fracture patterns or removal by a real robot. Crucially an optically attractive seam between outer armour panels is **not** necessarily a protective hypervelocity joint.

Dense nanoengineered transparent protective material remains a hypothetical 2226 technology, not a discovered or qualified ballistic material. The source 270kg/m² is a historic opaque shield *mass allowance*, not a valid prediction of transparency or hypervelocity strength. No pressure pane re-engineering is authorized by this research.

## Decision

**Retain the user's chosen 37-panel staggered reference.** The long radial-panels idea is aesthetically attractive and cuts nominal seam area significantly, but current sampled visibility improves by **less than half a percentage point** for much heavier, more awkward 1.15-tonne panels and an obvious real surface kink. The 25-piece radial split is a useful visually radial middle ground, but not sufficiently better in visibility to displace the held 37 layout.

If the appearance of uninterrupted twelve spokes proves important in an actual 3D nose experience, the *specific next narrow experiment* is to visualise the 13 vs 25 vs 37 design **from inside the L1 command deck**; neither this simple bow-projected viewer nor the scalar sky fraction resolves that perceptual preference. Never build new architecture or enlarge the physical surface model merely to justify a larger pane.

## Deliverables

- \`command/l1_radial_13_vs_25_vs_37.py\` and \`command/l1_radial_13_vs_25_vs_37_results.json\`: deterministic physical surface areas, mass, shape-break error, reference identity checks, seam ray counts.
- \`render/make_large_radial_comparison_viewer.py\`, \`render/out/nose_large_radial_vs_held_37_viewer.html\`: offline touch-friendly illustration, choose three layouts and 5/10/20 mm joint widths and all six crew seats; tap panels for mass/area; schematic service path, not actual removal simulation.

**No canon, source PR or runtime change.**
