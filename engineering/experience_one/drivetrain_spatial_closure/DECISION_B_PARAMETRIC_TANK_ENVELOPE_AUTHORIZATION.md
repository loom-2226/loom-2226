# Decision B — Parametric tank-envelope redesign authorization

Date: 2026-09-17. Status: USER-AUTHORIZED DESIGN SEARCH / NON-CANON / NOT SELECTED GEOMETRY.

The user explicitly selected Option B: permit parametric redesign of the four tank envelopes within the existing Wayfarer shell and frozen interfaces. This supersedes the earlier decision hold between preserving existing 14 m x 3 m placeholder envelopes and permitting redesign. It does NOT select a tank design, remass species, feed topology, structural reroute, or certify capacity.

## Fixed constraints
- Four major tanks, 250 t normal remass, separately protected 50 t water reserve; no inventory double count.
- Existing 57 m nominal body and 9 m nominal diameter; no silent hull growth, torch modification, radiator/RCS/metric relocation or alteration of governing mass ledger.
- Preserve four-longeron load-path connectivity, launch-bay extraction and docking/crew/service clearances. Do not infer collision from X overlap alone: evaluate full 3D geometry and swept states.
- Preserve standalone torch interface and immutable reference geometry; the x=58 primary-axis visualization marker is not authorization to extend the physical hull.
- 24 m courier allowance remains planning sensitivity, not a certified contiguous bay.

## Authorized search variables
Tank length, transverse cross-section, radial/angular position, endcaps and arrangement, mounting allocations, manifold and service allocations, with documented constraints and candidate statuses. Four tanks must remain identifiable. Protected reserve location and segregation must be explicitly modeled as a separate design question; do not assume it fits inside normal tanks or consume reserve for torch.

## Required next sequence
1. Recover exact seed/geometry source and Phase 9–11 interface evidence; baseline tests before source changes.
2. Create parameterized candidate and constraint schema with fluid density, ullage, wall/endcap, insulation, residual and reserve allocations as *inputs*, not invented constants.
3. Run capacity sensitivity and actual 3D collision/swept-envelope checks across tank, longeron, core, bay, metric, RCS and torch references.
4. Report feasible candidates and Pareto tradeoffs (capacity, usable volume, structure, access, CoM/inertia, compactness) with unverified quantities marked HOLD.
5. Stop for a new substantive choice if selecting fluid/storage regime, moving frozen systems, changing longeron topology, changing ship envelope, or accepting a failed hard requirement becomes necessary.

## Immediate disposition
OPTION_B_AUTHORIZED; PARAMETRIC_DESIGN_PENDING; NO GEOMETRY_MUTATION; NO_PHYSICAL_CERTIFICATION.
