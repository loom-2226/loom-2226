# Crown true-solid feasibility, kT decision 2026-11-08

**ALL bodies. ALL sponsors. 2026–2226.** Class: ENGINEERING SCREEN. **NOT CANON / NOT A CROWN CERTIFICATION.** Separate draft PR #475 from draft #474. Zero mass, pressure, impact, radiation, thermal, navigation or collision-clearance credit.

## Controlling physical stack, outside → inside

1. Thirty-seven separate, outward-removable 10 mm ceramic faceted nonpressure panes, [1,12,12,12] at radii [0,0.75,2,2.75,3.5] m. Option C nose x = −1.2 m (flat through r2 m), then 50° slope to r3.5 m; last ring stagger π/12.
2. Vacuum stand-off between panes and the first pressure-bearing ceramic.
3. **Outer** 28 mm full-pressure ceramic dome, source geometric apex X = −0.42 m.
4. AOI-2226 optogel between the two independent pressure-boundary solids. Current source declares fill volume 3.023 m³ and mass 3.04101485 t; actual CAD cavity volume must be compared, never overwritten to agree by fiat.
5. **Inner/backup** 28 mm full-pressure ceramic dome, source apex X = −0.30 m.
6. Osteon frame, 1 m radial × 0.22 m axial brow ring and sixteen Strata tambour gore tracks.

The source meridian for either dome is `X(r)=3.043118226826−3.343118226826√(1−(r/4.3)²)`, clipped at radius 3.5 m; second surface uses the source 0.12 m axial offset. No fictional load-transfer mechanisms or new material parameters are admitted.

**Role-name conflict:** Existing v2.5 configuration calls the X−0.42 m surface *backup* and X−0.30 m surface *primary*. kT's new outside→inside ordering makes the inner surface the backup. The CAD overlay preserves **both positions**, and names by the new physical order. A future source promotion must reconcile the role labels, their mass association, and actual full-pressure isolation. Geometry is not silently moved.

## Source authority and mass

Pinned `canon-v2.5` commit: `bfa7dcfb12358b119d5e63773f30ed9d251a43fc`. Source SHA256: `88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1`.

Current source G1 still books crown components as `no_render` allocation solids. **They are not qualified physical placements.** This screen replaces their visualization with independent true build123d geometry, not their governing `wayfarer_v05_geometry.json` entries or existing mass ledger. A new source SHA and D9 STEP would be necessary before those BReps become installed and full G1–G12/D9 can certify them. No mass reallocation or threshold changes are authorized.

## Canon-dimensional details not yet provided

- Retainer clip/rib width, thickness, individual outer-release path, and physical connection design (0.120 t allocation exists but not a shape).
- Osteon frame cross-section and joints (source gives 1.8 t mass and 12 roots, no independently reconstructable BRep).
- Sixteen tambour track sections, drive sections and swept paths over the r2 m flat/slope break.
- Complete brow ring axial datum and retainer/frame mechanical relationship. Its 1 m radial width and 0.22 m height alone do not locate a unique installed solid.
- A uniquely constrained AOI cavity/free-surface geometry matching the simultaneously declared 0.12 m dome shift, 5.973 cm local free-normal minimum and 3.023 m³ fill. A generated gap envelope is an **evidence calculation**, not a fitted 3.023 m³ physical gel.

**STOP criterion:** If the crown overlay collides with `bow_sensors`, `pressure_vessel` or `armor`, or the gel envelope does not close, or any required part lacks enough canon dimensions for actual geometry, the status remains **HOLD**, regardless of the legacy source certificate being green. Do not notch unrelated source solids, change masses, relocate sensors, change geometry tolerances, or certify by excluding an inconvenient conflict.

## Text reconciliation list

1. `wayfarer/docs/L1_I4_CARRYOVER_CROWN_OPTION_B_2026_11_01.md`: historical heading explicitly expanded to supersede the *one-monolithic-pressure-dome* proposal and quote kT's approved twin-dome layered stack. The 2026-11-01 rejected alternative remains available for provenance.
2. No `canon/current/` text edit: current Canon II v2.5 does not assert the obsolete single-dome Option B arrangement.
3. **Outstanding source-text discrepancy (not edited without replacing the governing source hash):** `wayfarer/config/wayfarer_v05_inputs.json` contains a carry-over `command_layout.crown` string calling the old Option B single dome, although its operative `command_layout.crown_dome` structure describes the twin dome. Fix with source promotion, not by pretending v2.5's certified hash remains unchanged.

## Deliverables

`wayfarer/lab/crown_geom_v25.py` builds the individually named `crown_pane_01` … `crown_pane_37` (one physical BRep per tile), two 28 mm dome BReps, and a physically bounded AOI cavity envelope. Its report records bow-structure BRep intersections and volume differences. Viewer GLB includes the original 194 D9 solids **without alteration** plus 40 crown geometry nodes; the 37 panes export individually printable STLs. Mechanical printing and pane-seam fit remain untested.

**No canon changes. No merge. STOP for kT on measured evidence.**
