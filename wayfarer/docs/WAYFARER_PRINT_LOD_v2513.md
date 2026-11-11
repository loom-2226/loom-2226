# Wayfarer NOSTROMO print LOD, v2.5.13

**ALL bodies. ALL sponsors. 2026–2226.** Print derivation ONLY, not canon geometry.

Canon Wayfarer remains true-scale in metres with source-booked mass and no protruding paint, lettering, bolts or fixture blocks. These are slicer/STL **output** overrides, applied AFTER selecting model scale and part splitting. Do not feed print dimensions back into the canon BRep, glTF, tank wall or thermal model.

| Print-only feature | STL derivation at target scale |
| --- | --- |
| Structural seam | 0.50 mm wide × 0.30 mm deep |
| Ring seam | 0.60 mm wide (structural +0.10 mm to survive layer lines), 0.30 mm deep |
| Fine sub-panel line | 0.35 mm wide; shallow recessed detail, never a through-cut |
| Bolts | Paint/decal dots only. No raised or cut bolt geometry |
| Detailed hull nozzle | 0.20 mm printer nozzle |
| Palette for physical paint guide | Lighten source CANON_FINISH sRGB by 10–20%; default 15% towards white |

For the paint guide, one repeatable reference calculation for each RGB sRGB channel is \`round(0.85 * canon_channel + 0.15 * 255)\`. This is **not** a change to glTF/canon finish and earns no spectral/thermal credit.

**At STL export:** scale the selected released, true-size part, then recreate structural/ring/sub-panel relief to the specified **print-space** widths/depths in a print-only copy. The full-size fine grooves remain whatever the canon model contains. Do not make walls porous or pierce the pressure vessel, and never imply a printer override alters source mass. If a feature would perforate a part at the selected scale, it must be dropped from the printable derivative, not altered in canon. No STL export is part of the six-state GLB release; this table is the authoritative *next STL derivation* profile.

**Decals:** Print \`wayfarer/render/decals/WAYFARER_NOSTROMO_DECALS_v2513.svg\` on transfer/decal medium at an appropriate scale for the chosen print. Artwork includes port and starboard WAYFARER registry, RCS/hatch hazard bands, docking marks and radiator-root NO STEP. All bolts are paint marks. Apply after paint. Nothing is extruded from the hull.

**Style:** clustered service markings around real hatches, RCS, collar and radiator roots; restrained seeded ±6% plate tone elsewhere. The canon GLBs carry plain glTF mosaic material variants only. All registry and hazard stencils live solely in this print-only SVG artwork and paint guide.
