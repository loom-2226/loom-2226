# LOOM 2226 — Wayfarer RCS / Torch Recovery and Functional Priority v0.1

**Status:** ENGINEERING RECOVERY / NON-CANON / NON-FLIGHT-AUTHORITY  
**Date:** 2026-09-15  
**Purpose:** Preserve prior RCS, torch/remass, HUD and Computational Shipyard work, reconcile their authority, and make spacecraft functional closure outrank preservation of any prior visual or candidate design.

## 1. Governing design priority

Wayfarer must function correctly as a spacecraft before visual continuity or historical candidate preservation is allowed to dominate design.

Current propulsion / control geometry priority:

1. RCS / attitude-control hardware and control authority;
2. torch / remass feed / reactor / thrust-frame / nozzle closure;
3. metric distributed-node geometry and field certification;
4. detailed Loom-specific physical design later.

Prior work is evidence and ancestry, not a requirement to preserve a geometry that fails current physical closure.

## 2. Recovered RCS lineage

Important prior work exists in the unmerged Wayfarer flight-system qualification lineage, especially PR #96 and the HUD attitude-envelope family.

Recovered source lineage includes:

- PR #96, `Wayfarer flight system qualification framework`;
- validated source head `5aecbd98fd27063c5d5e7b4b352cc19e74f31627`;
- HUD branch `feature/hud-wayfarer-attitude-envelope-v0.1-2026-09-11`;
- `src/wayfarer_rcs_placement.py`;
- `src/wayfarer_rcs_wrench.py`;
- `src/wayfarer_rcs_allocation.py`;
- `src/wayfarer_rcs_gimbal_realizability.py`;
- `src/wayfarer_rcs_plume_clearance.py`;
- `src/wayfarer_q5_rcs_duty.py`;
- Q4/Q5 HUD attitude and power/thermal artifacts.

The recovered candidate used 16 hardpoints in four axial bands:

- FORE: x 5–8 m, cardinal azimuths;
- FORE_MID: x 17–20 m, 45-degree rotated azimuths to avoid launch/docking cardinals;
- RADIATOR_ROOT: x 35–38 m, 45-degree rotated azimuths to avoid cardinal radiator roots;
- AFT: x 43–46 m, cardinal azimuths.

The historical candidate further demonstrated, under its stated engineering assumptions:

- nominal six-DOF wrench rank;
- rank retention after removal of any one logical cross-strapped cluster;
- bounded allocation at a 25 kN per-mount sizing point;
- pure-axis and selected combined-wrench screens;
- conditional single-gimbal realizability inside a continuous 45-degree force cone;
- point/centerline plume-clearance screening;
- Q5 energy/thermal screening.

These are recovered **engineering-candidate results**, not current flight authority.

## 3. Current RCS recovery disposition

`src/wayfarer_recovered_rcs_candidate.py` re-expresses the useful hardpoint layout against the current deterministic Wayfarer geometry and preserves exact ancestry.

Current disposition:

`RECOVERED_RCS_HARDPOINT_CANDIDATE_GEOMETRY_COMPATIBLE_CURRENT_DYNAMICS_REQUALIFICATION_REQUIRED`

The recovered point locations remain clear of the current launch-bay and docking-collar primitive envelopes, and the radiator-root band remains rotated away from the four cardinal radiator roots.

This does **not** certify a finite plume cone, deployed-radiator sweep clearance, physical nozzle package, mount structure, minimum impulse bit, working fluid, closed-loop GNC or full flight dynamics.

## 4. Inertia authority correction

Computational Shipyard Phase 5B later established an important fail-closed rule:

`WAYFARER_INERTIA_OPEN_NOT_QUALIFIED`

The existing mass/centroid model supports a deterministic parallel-axis contribution, but the complete configuration-aware centroidal inertia tensor is not yet authority. In particular, point-mass treatment can badly understate roll inertia.

Therefore old Q4 torque targets and slew times are retained only as historical screening targets. They may not become present flight authority until the current mass-distribution/inertia model is qualified.

Relevant Shipyard lineage includes:

- `src/qualification/synthesis/shipyard_m2a_attitude_coupling.py`;
- `src/qualification/synthesis/vehicle_dynamics_contract.py`;
- `qualification/phase5/wayfarer_inertia_audit.py`;
- `docs/LOOM_2226_Portable_Ship_Phase5B_Inertia_Authority_2026-09-08.md`.

## 5. Torch/remass recovery

The earlier Q2 torch/remass study correctly rejected the naive interpretation that all 250 t of normal remass must be pure water. It screened an explicit multi-feed architecture as a useful candidate, with a water-first fallback, while retaining the 250 t normal-remass / 50 t protected-reserve accounting.

That work remains useful **candidate architecture evidence**, but later Computational Shipyard work is more conservative about physical feed-system selection.

Shipyard Phase 9:

- derived mode-specific feed demand from the working torch card;
- screened several tank/fluid-management architecture families;
- selected **none** because propulsion-to-tank interface requirements and component models were missing.

Shipyard Phase 10:

- separated four bulk tanks from possible header/collector/conditioning stages;
- prioritized common-header and local-collector topologies for further experiment;
- selected **no** feed topology.

Shipyard Phase 11:

- bounded inertial pressure head and hydraulic-power sensitivity;
- concluded that a pump/header-conditioned feed deserves next modeling priority;
- still selected **no** feed architecture.

Therefore the current upstream interpretation is:

> Multi-feed remains a useful candidate concept, but no physical remass-feed architecture is currently selected. The next engineering closure should model the propulsion inlet requirement and downstream header/pump/conditioning interface before tank or plumbing geometry is frozen.

## 6. Interaction with current metric work

The current 208-node metric-array baseline must coexist with real spacecraft hardware. It must not be allowed to consume surface/volume, service routing or thermal paths needed by qualified RCS or torch systems.

Accordingly:

- RCS hardpoints are recovered before metric placement is treated as mature;
- future RCS nozzle/plume envelopes become exclusion/interference constraints for metric-node placement;
- torch feed, thermal and propulsion geometry become shared packaging constraints;
- a metric array that prevents controllable local flight or viable torch operation is invalid, regardless of metric-field elegance.

## 7. Required next functional closures

RCS:

1. establish a current configuration-aware inertia model with explicit provenance;
2. re-run wrench/rank/allocation against that inertia and current CoM states;
3. select physical nozzle/vectoring architecture or replace it with a better actuator topology;
4. close finite plume cones against launch, docking, radiators and metric hardware;
5. close structural mount loads, minimum impulse behavior, working-fluid/feed demand and closed-loop GNC.

Torch/remass:

1. admit propulsion inlet pressure, transient duty-cycle and fluid-state requirements;
2. model header/pump/conditioning architectures independently of bulk tank storage;
3. propagate feed architecture into tank, manifold, thermal and structural geometry;
4. close reactor/shield/thrust-frame/nozzle and plume interfaces;
5. only then promote physical feed/plumbing geometry.

Metric:

Continue the 208-node design-baseline work, but re-check placement as RCS and torch exclusion envelopes become physically qualified.

## 8. Non-claims

This recovery does not promote PR #96 to canon, does not certify the old HUD torque targets, does not establish a full inertia tensor, does not select an RCS nozzle, does not select a torch feed architecture, does not certify a metric boundary, and does not perform detailed Loom design.

The rule is simple: **reuse prior work when it survives current physics and geometry; replace it when it does not.**
