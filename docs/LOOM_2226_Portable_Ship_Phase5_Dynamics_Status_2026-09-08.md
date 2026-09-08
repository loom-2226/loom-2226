# LOOM 2226 — Portable Ship Qualification — Phase 5 Dynamics Status

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 5 IN PROGRESS — FEATURE BRANCH — NOT CANON  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`  
**Phase-4 closure parent:** commit `7c058fad6b55b1e660f4026676170168a569bebf`

## 1. Scope

Phase 5 is the standalone flight-dynamics qualification gate. It must remain independent of Navigator/HUD/GIS and machine-judge the ordinary 6DOF mechanics path.

The current increment establishes a small LOOM-owned deterministic kernel and an analytic qualification suite. It does not close Phase 5.

## 2. New artifacts

- `qualification/phase5/portable_dynamics.py`
- `qualification/phase5/test_phase5_dynamics.py`
- `qualification/phase5/wayfarer_phase5_adapter.py`
- `qualification/phase5/test_phase5_wayfarer_guardrail.py`
- `qualification/phase5/verify_all.py`

## 3. Mechanics implemented in the current kernel

The portable kernel currently includes:

- explicit inertial position/velocity and body attitude/angular velocity;
- body-to-inertial quaternion rotation;
- full 3x3 body-frame inertia tensor inversion;
- Euler rigid-body rotational dynamics;
- explicit `I_dot * omega` term for changing inertia;
- force in body and/or inertial frame;
- force application point relative to the current CoM;
- intrinsic body torque;
- force-to-torque mapping `tau = (r_app - r_CoM) x F + tau_intrinsic`;
- resource mass flow owned by the effector law rather than an extra generic rocket-equation momentum term;
- central feed cutoff when a mass-flow-producing effector has no resource;
- deterministic fixed-step RK4;
- deterministic event splitting at resource depletion;
- fail-closed singular/non-finite inertia handling.

The kernel is deliberately narrow and does not recreate a general spacecraft simulation framework.

## 4. Current analytic/known-answer coverage

The authored unit suite covers the Phase-5 case family at the mechanics level:

1. zero-force inertial coast;
2. single axial force known answer;
3. offset thruster initial coupled translation/rotation wrench;
4. symmetric opposing thruster pair producing pure initial torque;
5. pitch/yaw/roll principal-axis torque response;
6. combined 6DOF force/torque derivative;
7. resource depletion and deterministic feed cutoff;
8. central fail-closed feed cutoff independent of effector cooperation;
9. CoM migration changing the torque arm;
10. inertia migration including the `I_dot` term;
11. configuration-dependent mass-property provider semantics;
12. fail-closed singular inertia.

A separate Wayfarer guardrail suite checks:

- the qualified Phase-3 DOCKED wet mass/CoM seam;
- full Wayfarer rotational 6DOF fails closed with `WAYFARER_INERTIA_OPEN_NOT_QUALIFIED` rather than inventing missing inertia authority.

## 5. Development regression evidence and useful failure

The first local dynamics run executed 11 tests and exposed a real event-boundary defect in the initial RK4 depletion implementation. Resource quantity reached zero, but the discontinuous thrust cutoff was sampled incorrectly at the boundary, producing a small spurious post-depletion velocity increment.

Observed first-run discrepancy:

```text
v at nominal depletion = 5.524918093292486 m/s
later v              = 5.530473648848042 m/s
spurious delta       = 0.005555555555555536 m/s
```

The kernel was repaired by adding deterministic event splitting with left-limit evaluation for the pre-depletion substep and exact zero-resource state at the event boundary.

A second local regression then ran 12 mechanics tests and reported:

```text
Ran 12 tests in 0.185s
OK
```

The repair was made before the kernel was committed.

The repository-level Wayfarer guardrail tests have been authored against the actual inherited Phase-3 schema/seed/resolver artifacts. Their mandatory repository/Pixel execution is still pending.

## 6. Wayfarer inertia firewall

The current Wayfarer prototype has qualified mass and CoM authority, but the complete component/store inertia model needed for physical rotational 6DOF is still OPEN.

Phase 5 therefore does **not** fabricate a Wayfarer inertia tensor from nominal envelopes, point-mass approximations, renderer geometry, or chat assumptions.

`wayfarer_phase5_adapter.py` intentionally raises:

```text
WAYFARER_INERTIA_OPEN_NOT_QUALIFIED
```

when full 6DOF Wayfarer mass properties are requested.

This is a gate blocker to resolve deliberately, not an error to hide.

## 7. Still required before Phase 5 can close

At minimum:

1. execute the repository Phase-5 verifier and full test set;
2. obtain/derive a governed Wayfarer inertia model consistent with the Phase-2 contract without silently promoting OPEN geometry;
3. qualify actual dynamic CoM/inertia migration through the ship-class authority seam;
4. add independent analytic and frozen hostile-reference vectors, including NASA/NESC and/or Basilisk as appropriate;
5. run the mandatory Pixel acceptance suite;
6. repeat offline and compare deterministic hashes/numerics;
7. retain all failures and repairs as qualification evidence.

## 8. Gate state

**PHASE 5: OPEN — PORTABLE KERNEL ESTABLISHED; WAYFARER INERTIA + EXTERNAL REFERENCES + PIXEL ACCEPTANCE STILL REQUIRED.**

No merge is authorized.

Production SHIPCLASSES remains untouched.

Navigator/GIS/HUD physics-dependent implementation remains hard frozen.
