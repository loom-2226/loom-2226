# Decision C — Conditional shell widening; cabin and shuttle priority

Date: 2026-09-17. Status: USER-AUTHORIZED CANDIDATE SEARCH / NON-CANON / NO HULL CHANGE IMPLEMENTED.

User direction: keep the first pass simple. Permit modest local shell expansion/widening as a candidate **only if** it does not materially interfere with astrodynamics, torch, RCS or metric interfaces. Primary packaging goal: preserve cabin and shuttle space. This amends Decision B's no-hull-growth constraint for **studies only**, not the canonical 57 m x 9 m envelope or frozen interfaces.

## Simple candidate order
1. Baseline: preserve nominal shell, pressure-hull/cabin and complete shuttle stow/extraction volume. Search four-tank repositioning and cross-section changes in nonprotected space.
2. If baseline fails, allow local symmetric tank-region fairings/widening, not a whole-ship rescale or axial stretch. Parameterize outward extent, X span, added volume, surface area and assumed structural mass. Do not select a numerical width before measuring interfaces.
3. Evaluate at least a no-widening control and one bounded local-widening candidate under identical fluid-property sensitivities; preserve the 250 t normal and separately protected 50 t inventories.

## Protected spaces and no-go interfaces
- Cabin: preserve current pressure-hull envelope and access/service egress; no borrowing cabin volume for tanks.
- Shuttle: preserve actual stowed geometry, bay clearances and complete extraction swept path, including doors; a stationary AABB-only check cannot pass this gate.
- Torch: frozen GLB/vehicle interfaces, shadow shielding, nozzle, frame and physical-plume hold; no implied torch redesign.
- RCS: hardpoint locations and plume/actuation clearances; no blanket assumption that a fairing near a thruster is harmless.
- Metric: node identities and existing candidate placement; measure boundary/node clearance and field-physics hold rather than claiming zero effect.
- Astrodynamics: changes to external profile, mass, centroid, inertia, radiator view factors, docking/launch operations and attitude control must be assessed; 'no material interference' is a verification gate, not an assumption. In vacuum, widening does not automatically imply aerodynamic drag, but it can change launch/deployment, projected area, thermal exposure, inertia and attitude authority.
- Four longerons and radiator assemblies retained; modifications to frozen structure require separate review.

## Decision rule
Prioritize cabin and shuttle protection. Choose the smallest candidate modification that passes measured 3D containment, swept clearances and mass/inertia/control checks; if materiality thresholds or relevant source geometry are absent, report HOLD, not PASS. Preserve 57 m length; do not edit canonical diameter without governed approval. Reserve storage and fluid properties remain unresolved.

## Immediate execution
Build a lightweight parametric screening model (four tanks, explicit reserve allocation, fixed protected volumes, optional local fairing) and run sensitivity tests before committing geometry changes. Record all candidate dimensions and assumptions, source hashes, collision categories and failures. Stop for a further decision only if the search requires altering a frozen interface, materially affecting dynamics or selecting an unverified fluid/storage regime.

Disposition: LOCAL_SHELL_WIDENING_SEARCH_AUTHORIZED_CONDITIONALLY; CABIN_AND_SHUTTLE_PROTECTED; GEOMETRY_NOT_YET_CHANGED; NO_CERTIFICATION.
