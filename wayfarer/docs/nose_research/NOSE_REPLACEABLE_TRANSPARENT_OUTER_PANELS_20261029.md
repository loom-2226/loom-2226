# Wayfarer L1: replaceable outer transparent tiles, without shutters | 29 October 2026

**RESEARCH / NON-CANON / NON-RUNTIME / NON-GOVERNING / NOT IMPACT, OPTICALLY OR STRUCTURALLY QUALIFIED**

## Authority / narrow question

Live bootstrap from \`loom-2226/loom-2226\` PR #432, head \`3485830a56dfead79b2ef8bba031a595b536fbb5\` (open). This experiment was run on isolated \`research/wayfarer-nose-l1-search-20261028\` with no modification to the source PR, Rev 7, canon or runtime.

Question: Could the hypothetical Wayfarer L1 no-shutter **outer transparent protective skin** consist of **individually replaceable** trapezoidal or hexagonal tiles, with visually unobtrusive seams, *without* changing the protected inner pressure-glazing boundary?

**Answer within the geometry-only model: yes, several layouts are serviceably segmented.** The minimum simple candidate is a 37-piece staggered curved-trapezoid arrangement, subject to a mechanical retention check. No claim is made that the panes themselves have a real impact-proof material law.

## Fixed, previous research geometry

- Exterior r≤3.5m, +1.2m nose extension, central flat radius r2.0m, outer slope 50°; source inner pressure ellipsoid, crew eyes, furniture, structural inner glazing ray frames, bow sensor ring unchanged.
- Total outer protective surface area **52.89m²**. Reference opaque-protection areal *mass allocation* **270kg/m²** → **14.28 tonnes** across **all** outer panels. This allocation would replace opaque hull shielding; **not necessarily be 14.28 tonnes of new ship mass** and definitely not certified equivalent protection.
- Outer tiles separate from the pressure containment; outer-only replacement is intended **from outside** without depressurising the command deck. The inner pressure glazing and its structural frame remain in place. Mechanical external independent retainers and robotic grapples are proposed service interfaces, not actually sized hardware.
- Curved/radially cut transparent tiles are assumed to conform to the candidate exterior envelope. Flat planar pieces do **not** automatically conform to a smooth 50° cone; a 12-sector flat chord-facet is **up to ~0.142m axially different** at r3.5m from the original axisymmetric cone. Therefore actual planar facet implementation must be rechecked for gross clearance, pressure isolation and view angles.

## Actual computed surface layouts

Tile areas are integrated over the flat+50° conical outer skin with ~504,000 polar surface samples. Hex tiling is a nearest-centre Voronoi hex grid on the bow projection, *projected* to curved 3D shell. Each seam is modeled as a nominal **fully opaque 10mm-wide XY projected band**, not a proven seal/retainer.

| Layout | Independently identifiable panels | Smallest outer piece | Largest outer piece | Largest shield-material mass | 10mm opaque seam surface area | Pilot full forward sky with seam |
|---|---:|---:|---:|---:|---:|---:|
| 12 large trapezoids in main annulus, centre disc + inner ring | 25 | 0.835m² | 3.360m² | **907kg** | **0.269m²** | **72.83%** |
| 12 staggered outer trapezoids per band, centre disc r0.90 | 37 | 0.835m² | 2.545m² | 687kg | 0.538m² | 72.56% |
| **12 staggered outer trapezoids per band, centre disc r0.75** | **37** | **0.900m²** | **1.909m²** | **516kg** | **0.554m²** | **72.53%** |
| Large hex lattice (1.6m pitch), default centred | 31 | 0.089m² | 3.319m² | 896kg | 0.626m² | 73.17% |
| Same large hexes, grid shifted +0.5333m | 25 | 0.302m² | 3.339m² | 902kg | 0.628m² | 73.05% |
| Medium hex lattice (1.2m pitch), default centred | 43 | **0.003m²** | 1.859m² | 502kg | 0.774m² | 72.51% |
| Same medium hexes, grid shifted +0.80m | 42 | 0.136m² | 1.940m² | 524kg | 0.854m² | 72.44% |

**Important resolution note:** This test uses **4,096 forward equal-solid-angle Pilot and NAV directions**, plus 1,536 per each support seat, retaining the previous source cabin furnishings, sensor and pressure-frame occlusion. The higher sample count yields a **73.83% Pilot no-outer-seam baseline** for the same geometry, versus 72.66% from the earlier 256-ray sample. They are *different sampling resolutions*, not changes to source room or design. At 10mm opaque seams, the compact-staggered option loses 1.31 **percentage points** from 73.83% → 72.53%; the 25 large trapezoids lose 1.00 point. A 5mm or 20mm seam can be selected in the results and viewer. These numerical loss estimates are discrete ray samples, not exact optical ray integration; actual ceramic seam diffusion and mounting effects unmodeled.

The near-zero hex boundary slivers are geometrically definable but **not acceptable independent service modules**. A trivial **grid translation** materially improves them, yet still causes 0.136m²/0.302m² edge tiles. More critically, 11–14 hexagonal tiles in the tested arrangements **cross the central-flat to sloped-facet r2m transition**, requiring bent shaped tiles or a split there, both of which complicate manufacture/replacement. Trapezoidal ring pieces respect that geometric break.

### Service constraints not to confuse with a proven mechanism

Each tile's footprint is a separate non-overlapping patch (the opaque seam band lies between patches). The design concept is a flush-mounted tile with exterior-accessible, independently releasable perimeter retention; **not** a lap joint that traps adjacent tiles or a continuous bonded transparent sheet whose entire crown must be replaced.

In the simple version, a tile disengages **outward into vacuum** with the internal pressure window remaining installed. Individual tile replacement never entails moving the original pressurised glazing. The service manipulator must handle momentum/inertia of up to about **516kg protective mass** for the compact trapezoid option, plus actual tile mounting hardware, in a microgravity setting. No retention forces, fastening scheme, curvature-compatible release path, thermal strain relief, seal, debris-ejecta pathway or tool access has yet been engineered. An opaque join also requires impact-integrity consideration; **minimising visible seam area is NOT proving the seam protects against micrometeoroids**.

## Why research favours segmented outer layers

The ISS Cupola has six **trapezoidal windows** and **removable/replaceable debris panes**, physically separate from its pressure panes; thus replaceability and pressure separation have proven precedent, **not framelessness or our scale**:

- [ESA Cupola: six trapezoidal windows, independent replaceability and pane roles](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Node-3_Cupola/Cupola)
- [NASA TFAWS 2024 presentation: window assembly, removable outer debris pane](https://tfaws.nasa.gov/wp-content/uploads/TFAWS2024-PT-24.pdf)

A 2026 technical review identifies transparent ceramic size/shape processing limits and use of tiled armour, while warning that tiled seams and structural response matter. An ALON manufacturer separately describes engineered joins in tiled transparent armour windows. Both concern terrestrial armour, not automatic equivalence to Wayfarer hypervelocity protection:

- [Ferreira et al., 2026, _Materials and Architectures for Laminated-Glass Transparent Armor Systems_](https://ceramics.onlinelibrary.wiley.com/doi/10.1002/ces2.70056)
- [Surmet, _Advances in Making Large ALON Transparent Armor Windows_](https://www.surmet.com/post/advances-in-making-large-alon-transparent-armor-windows)

## Decision and stop condition

**Keep the 37-tile compact staggered trapezoid layout as the leading external replaceable-glazing *geometry-only research candidate*.** It maintains a clean replacement module size (~0.9–1.9m² per tile), keeps each protective module under ~0.52t before mounts, respects the flat-to-cone break, and sacrifices only ~1.3 sampled Pilot forward-sky percentage points at a deliberately pessimistic 10mm opaque seam. No shutter storage annulus or motors return. The alternative 25-piece large trapezoid layout has slightly better forward views but individual tiles up to ~0.91t, which complicates repair handling.

Continue retaining both large and medium hex layouts as design alternatives if the aesthetics/gameplay justify more complex fabricated tiles and clipped rim pieces.

**Stop before claiming actual protection or design adoption.** What is missing is specific: an independently serviceable exterior mounting concept and any empirical/defensible nanoengineered transparent impact-layer material model, especially at joints. Do not enlarge this into a complete materials simulation, qualification system or new structural architecture just because we can draw lovely hexagons.

## Outputs

- \`command/l1_replaceable_outer_tiles.py\` and \`command/l1_replaceable_outer_tiles_results.json\`: deterministic projected tile masks, curved outer shell surface area and areal mass per module, seam-band area, actual per-seat ray intercepts and visibility at 5/10/20mm seam widths.
- \`render/make_replaceable_tile_viewer.py\` and \`render/out/nose_replaceable_outer_tile_viewer.html\`: offline touchscreen tiling comparison. Select any of seven presets, seam width, actual Pilot/NAV/S1–S4 eye, and tap an individual panel for its area/mass. Illustrates an **outward removal direction** without claiming actual kinematics.

Rev 7, PR #432, canon and runtime **untouched**.
