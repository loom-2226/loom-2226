# PR A — Tank capacity feasibility and substantive decision gate v0.1

**2026-09-17 | ENGINEERING / DERIVED SCREENING / NON-CANON | NO GEOMETRY MUTATION**

## Inputs (live main seed; verify SHA at execution)
`geometry/wayfarer_geometry_seed.sql` defines four tank cylinders, each x=18–32 m (14 m long), external diameter 3.0 m, centre radius 2.7 m, and 62.5 t normal inventory per tank. Total normal remass 250 t, protected water 50 t. Source records the tank shape as DESIGN_BASELINE, not a validated pressure vessel. Source `mass_elements` includes tank shells in the 150 t structure bucket; do not add shell mass again. The separate protected water is assigned a bookkeeping centroid x12.5 m in `src/wayfarer_geometry.py`, not an identified physical vessel.

## Upper-bound capacity calculation (NOT usable tank volume)
Four ideal full-length external cylinders: V_external=4*pi*(3/2)^2*14 = 126*pi = 395.840674 m^3. Per tank 31.5*pi = 98.960169 m^3. A 250,000 kg normal inventory requires effective average density >= 250000/395.840674 = 631.567 kg/m^3 **even under the impossible assumption that all external envelope is usable fluid**. With usable fraction f in (0,1), required density >=631.567/f kg/m^3; f includes wall thickness, domes, ullage, residuals, internal hardware and any excluded volume. Illustrative sensitivity ONLY: f=0.9 -> 701.74 kg/m^3; f=0.8 -> 789.46 kg/m^3; f=0.7 -> 902.24 kg/m^3. These are conditional arithmetic, NOT selected fluid densities or approved tank efficiencies. The 50 t protected reserve is additional to the 250 t and has no verified physical containment here. If both inventories were assigned to these same ideal external envelopes, 300000/395.840674 = 757.881 kg/m^3 at f=1, before segregation and real geometry; this is NOT permission to mix inventories.

## Geometric clearance issue
The nominal tank radial interval is 1.2–4.2 m from axis, within the 4.5 m nominal hull radius but leaving only 0.3 m external radial margin at the tank's outwardmost point. Four tank centres are at quadrature; nominal longerons at radius 2.45 m in same azimuths, so an axial longeron centreline lies inside each corresponding tank's 1.5 m radial cross section throughout x18–32 m. The seed longeron box is 0.28 m square and x14–50 m. This is a **potential direct tank/longeron geometry conflict**, not merely an X-overlap; precise collision/intentional penetrations must be checked in world coordinates. Launch bay spans x16–27.5 m and occupies +Z; its actual full geometry and extraction sweep need a separate check. No collision PASS asserted.

## Architecture decision — stop here
**Question:** Should the next design preserve the four existing 14 m × 3 m tank *external envelopes* and treat storage species/state plus usable-volume fraction as variables, allowing a reported FAIL if 250 t does not fit; OR authorize a revised tank-envelope geometry (within 57 m × 9 m hull and frozen torch/RCS/metric interfaces) to recover capacity and longeron clearance? The four-tank count and 250+50 t accounting remain fixed either way. Do not choose a fluid, wall thickness, reserve-vessel topology, or reroute a primary longeron by inference.

**Decision requested:** A = envelope-preserving feasibility-first, or B = permit parametric tank-envelope redesign within ship constraints. Both retain the frozen torch and require explicit longeron and launch-bay clearance. No implementation beyond this gate until selected.

## PR A status
Capacity screen DERIVED; baseline inventory and geometry READ; physical usable capacity OPEN; longeron clash POTENTIAL; protected-reserve vessel OPEN; reference GLB SHA/complete sweep and executable regression PENDING. No tank/feed topology selected and no GLB generated.
