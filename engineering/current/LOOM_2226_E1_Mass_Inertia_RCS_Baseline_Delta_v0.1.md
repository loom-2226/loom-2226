# LOOM 2226 — E1 Mass / Inertia / RCS Baseline Delta v0.1

**Status:** ACTIVE ENGINEERING DELTA RECORD / NON-CANON  
**Date:** 2026-09-15  
**Scope:** Experience One rotational-flight authority recovery

## Purpose

Preserve the exact change path from prior HUD / Q4 / Computational Shipyard work into the E1 flight-physics model so those workstreams can later resume without reverse-engineering E1 changes.

## Prior baseline

### HUD / Q4

Prior Q4 engineering used:

- 1,158.5 t reference wet / docked state;
- balanced four-tank remass distribution;
- recovered 16-hardpoint RCS candidate;
- nominal 100 kN translation, 1.0 MNm pitch/yaw, 0.2 MNm roll screening envelope;
- one-cluster-out 75 kN translation, 0.75 MNm pitch/yaw, 0.1 MNm roll screening envelope;
- equivalent component-shape rigid-body approximation for finite attitude timing;
- 20% settle margin applied to ideal symmetric bang-bang rest-to-rest slews.

Those results were sufficient for a bounded HUD attitude qualification but were not final flight-control authority.

### Computational Shipyard correction

Later Shipyard inertia work correctly identified that the governed mass model did not contain complete centroidal inertia tensors for every physical component. It therefore preserved the fail-closed finding:

`WAYFARER_INERTIA_OPEN_NOT_QUALIFIED`

The centroid-only / parallel-axis result was retained as useful evidence but explicitly rejected as a complete vehicle inertia tensor.

## E1 change

E1 now establishes a deterministic configuration-aware engineering rigid-body model in `src/wayfarer_mass_inertia_authority.py`.

The model:

- preserves the existing mass ledger and mutable-store doctrine;
- computes mass and CoM from the declared configuration;
- restores known four-tank radial placement and launch offset;
- adds intrinsic component inertia using explicit equivalent-shape assumptions;
- applies the parallel-axis theorem about the assembled instantaneous CoM;
- requires symmetry and positive definiteness;
- retains the centroid-only tensor as a diagnostic comparator;
- exposes every equivalent-shape assumption in machine-readable output;
- changes tensor and response when remass, protected-water or launch state changes.

This is an **engineering rigid-body model for E1/RCS qualification**, not structural FEA and not a literal assertion that every subsystem is a homogeneous cylinder or box.

## RCS change

`src/wayfarer_rcs_inertia_requalification.py` reuses the prior Q4 actuator envelope as recovered engineering evidence and recomputes vehicle angular acceleration and finite attitude timing against the E1 configuration-aware tensor.

The actuator envelope is not silently promoted to final hardware authority. Still open:

- closed-loop GNC;
- final nozzle/gimbal hardware;
- actuator slew/rate dynamics;
- minimum impulse bit;
- finite plume geometry and deployed-radiator interference;
- RCS structural mount/load qualification;
- fluid slosh / flexible-body coupling where material.

## Why E1 is allowed to change the baseline

E1 prioritizes correct continuous spacecraft flight over preservation of prior geometry or renderer assumptions.

If RCS, torch, mass-property, orbital, local-flight or metric physics require different component placement or subsystem geometry, E1 may change it. Each material change must be recorded as another baseline delta with source, old state, new state, reason and downstream impact.

## Downstream impact

### HUD

Prior finite-attitude numbers are stale once the E1 tensor is qualified. HUD should consume E1 rotational state and timing through a governed interface rather than retain its old private rigid-body approximation.

### Navigator / local flight

Navigator-scale translation remains separate from rotational authority, but any executable maneuver that depends on finite attitude transitions must use the E1 tensor/RCS state rather than instantaneous reorientation.

### Computational Shipyard

The old Shape/Shipyard geometry remains useful ancestry. When Shipyard resumes, it should ingest the E1 equivalent-shape/tensor assumptions as an engineering branch delta, then replace them with higher-fidelity physical mass distributions where earned.

### 3D / semantic GLB

No visual geometry is authoritative merely because it resembles an equivalent shape. Rendering should adapt to the physical design after flight constraints stabilize.

## Authority boundary

This record does not change canon. It does not certify FEA, slosh, flexible-body dynamics, closed-loop GNC, final RCS hardware, torch hardware, or metric transport. It records the E1 engineering handoff and preserves recoverability of prior HUD/Shipyard efforts.
