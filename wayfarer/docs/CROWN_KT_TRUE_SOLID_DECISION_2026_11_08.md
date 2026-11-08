# Crown true-solid feasibility, kT decision 2026-11-08

**ALL bodies. ALL sponsors. 2026–2226.** Class: ENGINEERING SCREEN. **NOT CANON / NOT A CROWN CERTIFICATION.** Separate draft PR #475 from draft #474. Zero mass, pressure, impact, radiation, thermal, navigation or collision-clearance credit.

## Controlling physical stack, outside → inside

1. Thirty-seven separate, outward-removable 10 mm ceramic faceted nonpressure panes, [1,12,12,12] at radii [0,0.75,2,2.75,3.5] m. Option C nose x = −1.2 m (flat through r2 m), then 50° slope to r3.5 m; last ring stagger π/12.
2. Vacuum stand-off between panes and the first pressure-bearing ceramic.
3. **OUTER** 28 mm independently pressure-capable ceramic dome, source geometric apex X = −0.42 m.
4. AOI-2226 optogel between the two independent pressure-boundary solids. Current source declares fill volume 3.023 m³ and mass 3.04101485 t; actual CAD cavity volume must be compared, never overwritten to agree by fiat.
5. **INNER** 28 mm independently pressure-capable ceramic dome; this IS the pressure vessel bow closure, not a second copy, source apex X = −0.30 m.
6. Osteon frame, 1 m radial × 0.22 m axial brow ring and sixteen Strata tambour gore tracks.

The source meridian for either dome is `X(r)=3.043118226826−3.343118226826√(1−(r/4.3)²)`, clipped at radius 3.5 m; second surface uses the source 0.12 m axial offset. No fictional load-transfer mechanisms or new material parameters are admitted.

**Role-name resolution (kT 2026-11-08):** Both domes are independent pressure boundaries. Only **OUTER** (X−0.42m) and **INNER** (X−0.30m) identify them. The **INNER** is the PV bow closure. The existing source's old *backup/primary* words are obsolete; no apex is moved. The outer/inner interfaces mount to the Osteon/brow seat ring, which is physically cut into the PV and armour. Full source promotion must also remove the old duplicate PV cap.

## Source authority and mass

Pinned `canon-v2.5` commit: `bfa7dcfb12358b119d5e63773f30ed9d251a43fc`. Source SHA256: `88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1`.

Current source G1 still books crown components as `no_render` allocation solids. **They are not qualified physical placements.** The interim BRep candidate cuts the crown aperture from PV and armour and replaces their nose overlap in the viewer, without changing old source G1. This screen replaces their visualization with independent true build123d geometry, not their governing `wayfarer_v05_geometry.json` entries or existing mass ledger. A new source SHA and D9 STEP would be necessary before those BReps become installed and full G1–G12/D9 can certify them. kT has authorized a measured material-removal and replacement ledger; do not change any mass without reporting the changed value, CG and ECON delta. The 3.023m3 AOI mass basis is fixed despite its 2.489m3 modelled envelope. D9 threshold remains 0.01m3.

## kT aperture decision and measured source-mass disposition

The BRep candidate cuts only the original `pressure_vessel` and `armor` solids at the crown aperture/seat, retains all other existing installed solid geometry, and inserts a real annular Osteon/brow seat from source 1m radial width and 0.22m longitudinal height. INNER is the pressure vessel bow closure, not an overlapping shell. The three-object bow interface scan reports **zero** volumes above the unchanged 0.01m³ D9 limit.

- Original PV 11.356646m³ → 9.864411m³: **1.492235m³ removed**, equivalent to **2.017682t** at the original booked effective PV density 1.352121t/m³.
- Original armour 81.103032m³ → 71.460479m³: **9.642552m³ removed**, equivalent to **12.779636t** at its original booked effective density 1.325338t/m³.
- Total removed volume **11.134787m³**, corresponding to **14.797318t** on the original effective-density basis, **not yet debited to governing source G1**.
- AOI actual cavity 2.488661m³ vs retained booked **3.023m³** (conservative). The cavity volume discrepancy is an engineering fit issue, not permission to cut booked mass.
- Real source mass transfer and certification require updated state mass/CG/dv and a new source hash; the unchanged legacy v2.5 source certificate does not validate this work.

## Concrete blocker: authored spare-pane stowage envelope

The existing 7-spare allocation is a `no_render` box at x14.9–16.1m, y−3.35..−2.65m, z−0.5..+0.5m (1.2 × 0.7 × 1.0m, spatial diagonal **1.712m**). The source's largest outer-pane hoop chord is **1.812m**, and the spare inventory includes **two of that annular type**. A rigid 1.812m edge cannot fit inside ANY orientation of a box whose space diagonal is only 1.712m. Thus the seven current spare panes cannot be replaced by true independent installed BReps inside their existing authored hold without changing storage geometry, the pane design, or the spare configuration.

This is a real geometric contradiction, not a reason to fabricate a new tank/hold, shrink the panes, invent hinges, or silently keep the spare box as a fitted solid. Under kT's **no other geometry** instruction, the installed spare fit cannot be certified. The existing 0.385772t reserve-funded allocation remains in its historical mass ledger until a storage decision.

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
