# LOOM 2226 — Portable Ship Qualification — Phase 5 Dynamics Status

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 5 IN PROGRESS — PHASE 5A PIXEL MECHANICS INCREMENT PASSED — FEATURE BRANCH — NOT CANON  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`  
**Phase-4 closure parent:** commit `7c058fad6b55b1e660f4026676170168a569bebf`

## 1. Scope

Phase 5 is the standalone flight-dynamics qualification gate. It must remain independent of Navigator/HUD/GIS and machine-judge the ordinary 6DOF mechanics path.

The current increment establishes a small LOOM-owned deterministic kernel, an analytic qualification suite, a Wayfarer mass/CoM seam, and a fail-closed inertia firewall. It does not close Phase 5.

## 2. Current artifacts

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

## 5. Development failures retained as qualification evidence

The first local dynamics run exposed a real event-boundary defect in the initial RK4 depletion implementation. Resource quantity reached zero, but the discontinuous thrust cutoff was sampled incorrectly at the boundary, producing a small spurious post-depletion velocity increment.

Observed first-run discrepancy:

```text
v at nominal depletion = 5.524918093292486 m/s
later v              = 5.530473648848042 m/s
spurious delta       = 0.005555555555555536 m/s
```

The kernel was repaired by adding deterministic event splitting with left-limit evaluation for the pre-depletion substep and exact zero-resource state at the event boundary.

The first two Pixel repository runs then exposed a separate portability defect in the Wayfarer adapter dynamic import path. The Phase-3 resolver depended on its sibling geometry resolver and, when loaded manually, also required temporary registration in `sys.modules` during dataclass construction. These failures were repaired without changing mechanics numerics. The final adapter commit used for Pixel qualification was:

```text
51d2332c04755087d22f1296c3d388e890cf73d0
fix: register Phase 3 resolver during dynamic import
```

## 6. Phase 5A Pixel acceptance evidence

The repository verifier executed on Pixel / Termux under:

```text
Android-17-aarch64-64bit-ELF
Python 3.13.13
aarch64
```

### Online-installed final run

Result:

```text
LOOM_PHASE5_VERIFY: PASS
```

Checks:

- `axial_known_answer`: PASS
- `depletion_event_cutoff`: PASS
- `required_files`: PASS
- `unit_suite`: PASS
- `wayfarer_inertia_guardrail`: PASS

Unit suite:

```text
14 tests
0 errors
0 failures
0 skips
```

Reference numerics:

```text
axial final r_N = [3.9999999999999805, 0.0, 0.0] m
axial final v_N = [1.9999999999999793, 0.0, 0.0] m/s
resource at depletion = 0.0 kg
v at 5 s = 5.524918093292486 m/s
v at 10 s = 5.524918093292486 m/s
trace samples = 1001
```

Input hashes:

```text
portable_dynamics.py
9bb3985ff936638a8a5338e5ac9a7daf83718203fc763498f6e17237352ea02b

test_phase5_dynamics.py
d779cd739200da57b6a538a925b3ac594d09c132971232f849d2d843f8d3a28d

test_phase5_wayfarer_guardrail.py
4d455499e4d01fb1e9dc7371c86a81a62adf179bfab34c59862b4d77fe16f213

wayfarer_phase5_adapter.py
1decadf6e1a3f29dd926fa8b9df24397232e0252a507e56d11bbe8628f8c86b8
```

Result hash:

```text
phase5_verification_result.json
5a8044ed590a6d0d11007a35de04e1099f28b3ff24452e9e6c100a97249e6d5a
```

### Mandatory offline repeat

With Wi-Fi and mobile data disabled, the same command was executed again:

```text
python verify_all.py
```

Result:

```text
LOOM_PHASE5_VERIFY: PASS
```

The result JSON hash matched the online-installed final run exactly:

```text
5a8044ed590a6d0d11007a35de04e1099f28b3ff24452e9e6c100a97249e6d5a
```

The input hashes, environment fields, unit results, and numerics matched exactly.

**Disposition:** the Phase 5A portable mechanics + Wayfarer authority-guardrail increment is PASSED on the target Pixel and offline-deterministic.

## 7. Wayfarer inertia firewall

The current Wayfarer prototype has qualified mass and CoM authority, but the complete component/store inertia model needed for physical rotational 6DOF is still OPEN.

Phase 5 therefore does **not** fabricate a Wayfarer inertia tensor from nominal envelopes, point-mass approximations, renderer geometry, or chat assumptions.

`wayfarer_phase5_adapter.py` intentionally raises:

```text
WAYFARER_INERTIA_OPEN_NOT_QUALIFIED
```

when full 6DOF Wayfarer mass properties are requested.

This is a gate blocker to resolve deliberately, not an error to hide.

## 8. Still required before Phase 5 can close

At minimum:

1. obtain/derive a governed Wayfarer inertia model consistent with the Phase-2 contract without silently promoting OPEN geometry;
2. qualify actual dynamic CoM/inertia migration through the ship-class authority seam;
3. add independent frozen hostile-reference vectors, including NASA/NESC and/or Basilisk as appropriate;
4. rerun the complete Phase-5 suite on Pixel after those executable inputs change;
5. repeat offline and compare deterministic hashes/numerics;
6. retain all failures and repairs as qualification evidence.

## 9. Gate state

**PHASE 5A: PASSED — PORTABLE MECHANICS + WAYFARER MASS/CoM SEAM + INERTIA FIREWALL QUALIFIED ON PIXEL/OFFLINE.**

**PHASE 5: OPEN — WAYFARER INERTIA + EXTERNAL HOSTILE REFERENCES STILL REQUIRED.**

No merge is authorized.

Production SHIPCLASSES remains untouched.

Navigator/GIS/HUD physics-dependent implementation remains hard frozen.
