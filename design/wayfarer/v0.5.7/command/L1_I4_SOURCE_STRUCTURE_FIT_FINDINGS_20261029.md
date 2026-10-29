# LOOM Wayfarer L1 I4: source structural cutaway and honest fit overlay
**29 October 2026 · RESEARCH · NON-CANON · NON-RUNTIME · NOT STRUCTURAL QUALIFICATION**

## User objective

Add the **actual spacecraft structure** to the existing I4 Command Commons, rather than leaving six seats, a broad command terrace and low-g work areas floating in a limitless schematic room. Keep the scene mobile-safe and visibly honest about places where unconstrained I4 does not fit the source ship.

Bootstrapped live GitHub upstream `loom-2226/loom-2226`, PR #432 OPEN, head `3485830a56dfead79b2ef8bba031a595b536fbb5`. No authority update. Source geometry extracted on research VM from `design/wayfarer/v0.5.7/out/wayfarer_v05_geometry.json` and `render/out/l1_scene.json`; only the sandbox research branch receives new files.

## Actual source geometry used

- Inner pressure vessel: `domecyl(xa=0.2, xb=2.35, xc=13.4, R=4.3, t=0.03)`; 8.6 m internal diameter. R4.3 is the source nominal cross-sectional radius.
- Original L1 floor: `sector(x0=3.0, x1=3.3, r0=0.9, r1=4.15, a0=0, a1=360)`. It is annular, **not** I4's solid 8.15 × 8.05m rectangle.
- Bow shoulder sensor ring reference envelope: `R=4.15, rin=2.9`, source `bow_sensors`.
- Source L1 ladder locations: `(Y,Z)=(+1.4,0),(-1.4,0)`, each indicated size 0.8m.
- Source dome surface analytically approximated from the source boundary: `X(r)=2.35 - 2.15 sqrt(1-(r/4.3)^2)` for `0≤r≤4.3`.

The sources are old Rev7 **geometry**. The previous 37 replaceable protective external panels, independent seamless inner domes and adaptive optogel remain non-canon research candidates; the visible curved glazing in this structural viewer is **an illustrated pressure-dome surface**, not a newly qualified transparent material.

### Essential coordinate limitation

I4's earlier freeform viewer uses `(Y,Z,H)` with `H=4-X`, so the physical **source ship axis X is mapped to apparent vertical H**, while the concept previously called `+Z` 'forward' in its deck plan. These two notions of forward are NOT simultaneously physically possible. The transparent shell exposes rather than resolves this inconsistency. An approved later CAD/LOOM integration must pick the real ship thrust / bow frame and remap I4's tier/crew relationship before claiming hull fit.

## Rendered structural elements

- Cutaway cylindrical inner pressure-hull envelope near L1 with semi-transparent sidewall panels.
- Curved, transparent/seamless bow pressure-dome *surface illustration* and bright shoulder attachment ring. Opaque ribs are NOT inserted through this pressure-dome glazing.
- Source sensor annulus inner/outer radii as an unobtrusive shoulder ring.
- Structural hoop/side stringer **illustrations** and limited conceptual columns under Pilot/Captain and Navigator decks. These are NOT demonstrated load paths.
- Source original L1 floor/radius outline and both ladder aperture locations available as a red/orange conflict overlay.
- Original I4 furnishings, six crew chairs, command stand, mission table and independent workbench all preserved.

## Quantified discrepancy (not concealed)

The I4 main-deck authored rectangle `Y width=8.15m`, `Z length=8.05m`, centre `(0,-0.56)`, has 65.608m² footprint.

Bounded plan sampling on a 700×700 regular grid yields:
- **13.783m²** of its footprint outside source L1 flooring `r=4.15m` (the region beyond the source structural floor outer radius).
- **2.545m²** of its footprint over the original source L1 central opening `r<0.9m`.
- It also lacks the two source ladder cutouts; their locations are displayed but not cut from I4's deck.

These are **plan-area discrepancies** only. Full 3D crew, cabinets, pressure dome, radiation/thermal, support mount and g-loading conflicts have not been tested. The floor mismatch alone establishes that I4, *as authored*, is NOT source-hull compatible.

**Do not move the source hull or claim 8.15m rectangular flooring fits inside the original 8.6m diameter pressure shell.** Whether to trim/cut the floor, redesign the central opening or reposition seats becomes a separate constrained design decision.

## Viewer, reproducibility, checks

- `render/make_l1_i4_structural_context.py`: directly derives actual structural parameters from the local source geometry JSON, computes bounded mismatch, overlays minimal graphics on the existing phone-safe Canvas2D I4.
- `command/L1_I4_SOURCE_STRUCTURAL_CONTEXT_20261029.json`: source geometries, nonphysical coordinate warning and mismatch figures.
- `render/out/wayfarer_l1_i4_with_source_structure_android.html`: standalone offline 3D, including controls **Pressure shell**, **Bow glazing**, **Rings + deck supports**, **Show fit conflicts**, the previous orbit / plan / side views and the existing interior layers. The viewport's rendered PNG static fallback is embedded directly in the HTML.

Validation actually executed:
- Python syntax + JavaScript syntax checks pass.
- Chromium phone emulation 412×915 and desktop 1260×940, WebGL/GPU disabled: 3 distinct camera render images each, structure/fit toggles and hiding all structure work, no reported page errors.
- JavaScript fully disabled: embedded 600×404 PNG fallback loads and stays visible.
- **Not verified on actual user's Pixel 10 / Android `content://` file viewer.**

Stopping condition: physical source envelope visible, honest dimensional conflict visible and six-role I4 interior retained in one mobile-safe viewer. No hull-fit or seat-structure certification, no runtime, Rev7, PR, or canon mutations. The next useful test is to try *trimming the I4 main floor within source r4.15 and retaining ladder/central opening*, then decide whether the current shared social/mission core can survive that physically constrained redesign.
