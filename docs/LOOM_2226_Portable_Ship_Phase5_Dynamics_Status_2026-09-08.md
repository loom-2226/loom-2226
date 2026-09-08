# LOOM 2226 — Portable Ship Qualification — Phase 5 Dynamics Status

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 5 IN PROGRESS — PHASE 5A + 5B PIXEL INCREMENTS PASSED — FEATURE BRANCH — NOT CANON  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`  
**Phase-4 closure parent:** commit `7c058fad6b55b1e660f4026676170168a569bebf`

## 1. Scope

Phase 5 is the standalone flight-dynamics qualification gate. It must remain independent of Navigator/HUD/GIS and machine-judge the ordinary 6DOF mechanics path.

The current qualified increments establish a small LOOM-owned deterministic kernel, analytic qualification suite, Wayfarer mass/CoM seam, fail-closed inertia firewall, and deterministic audit of the inertia information that is actually supported by current authority. Phase 5 is not yet closed.

## 2. Current artifacts

- `qualification/phase5/portable_dynamics.py`
- `qualification/phase5/test_phase5_dynamics.py`
- `qualification/phase5/wayfarer_phase5_adapter.py`
- `qualification/phase5/test_phase5_wayfarer_guardrail.py`
- `qualification/phase5/verify_all.py`
- `qualification/phase5/wayfarer_inertia_audit.py`
- `qualification/phase5/test_phase5b_inertia_audit.py`
- `qualification/phase5/verify_inertia.py`

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

## 4. Mass-properties convention and external standard alignment

LOOM uses ordinary aerospace rigid-body mass-properties mechanics, not a bespoke inertia convention.

Required convention:

- SI units: kg, m, kg m^2;
- right-handed Wayfarer body frame;
- symmetric 3x3 inertia tensor;
- flight tensor expressed about the instantaneous vehicle center of mass in body-frame components;
- component centroidal inertia rotated into body-frame components before summation;
- component/store displacement shifted to system CoM with the parallel-axis theorem;
- configuration and store changes must update mass, CoM and inertia consistently;
- time-varying inertia is admitted explicitly in rotational dynamics.

Tensor storage follows the standard matrix convention used by the dynamics kernel. Products of inertia/sign convention must be fixed explicitly before external-vector qualification so NASA/NESC/Basilisk comparisons cannot be contaminated by notation-only sign differences.

External reference strategy remains:

- Basilisk — hostile spacecraft-dynamics reference;
- NASA JEOD + Trick — deep spacecraft dynamics reference;
- Tudat/TudatPy — astrodynamics reference where applicable;
- NASA/NESC published mass-properties formulations and frozen reference vectors — independent known-answer support.

Basilisk exposes current spacecraft mass, body-frame CoM and inertia, and supports time-varying mass properties. NASA/NESC published mass-properties guidance defines the inertia tensor and parallel-axis composite-body construction. These are reference/qualification authorities, not Pixel runtime dependencies.

## 5. Current analytic/known-answer coverage

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

A separate Wayfarer guardrail suite checks the qualified Phase-3 DOCKED wet mass/CoM seam and verifies that full Wayfarer rotational 6DOF fails closed with `WAYFARER_INERTIA_OPEN_NOT_QUALIFIED` rather than inventing missing inertia authority.

## 6. Development failures retained as qualification evidence

The first local dynamics run exposed a real event-boundary defect in the initial RK4 depletion implementation. Resource quantity reached zero, but the discontinuous thrust cutoff was sampled incorrectly at the boundary, producing a small spurious post-depletion velocity increment.

```text
v at nominal depletion = 5.524918093292486 m/s
later v                = 5.530473648848042 m/s
spurious delta         = 0.005555555555555536 m/s
```

The kernel was repaired by deterministic event splitting with left-limit evaluation for the pre-depletion substep and exact zero-resource state at the event boundary.

The first two Pixel repository runs then exposed a separate portability defect in the Wayfarer adapter dynamic import path. The Phase-3 resolver depended on its sibling geometry resolver and, when loaded manually, also required temporary registration in `sys.modules` during dataclass construction. These failures were repaired without changing mechanics numerics. Final adapter repair commit used for qualification:

```text
51d2332c04755087d22f1296c3d388e890cf73d0
fix: register Phase 3 resolver during dynamic import
```

## 7. Phase 5A Pixel acceptance — PASSED

Target environment:

```text
Android-17-aarch64-64bit-ELF
Python 3.13.13
aarch64
```

Final online-installed and mandatory offline runs both reported:

```text
LOOM_PHASE5_VERIFY: PASS
14 tests
0 errors
0 failures
0 skips
```

Checks passed: `axial_known_answer`, `depletion_event_cutoff`, `required_files`, `unit_suite`, `wayfarer_inertia_guardrail`.

Reference result hash was byte-identical online/offline:

```text
phase5_verification_result.json
5a8044ed590a6d0d11007a35de04e1099f28b3ff24452e9e6c100a97249e6d5a
```

**Disposition:** Phase 5A portable mechanics + Wayfarer authority-guardrail increment PASSED on target Pixel and offline-deterministic.

## 8. Phase 5B inertia-authority audit — PASSED

Phase 5B deliberately asks what inertia information current Wayfarer authority actually supports before any centroidal shape model is introduced.

The current Phase-3 mass authority provides mass and centroid locations. Therefore the parallel-axis contribution is mechanically derivable. Complete centroidal inertia is not yet governed for any current mass element/store and is not fabricated from Phase-4 renderer geometry.

Audit disposition:

```text
PARTIAL_PARALLEL_AXIS_ONLY_NOT_FLIGHT_AUTHORITY
WAYFARER_INERTIA_OPEN_NOT_QUALIFIED
```

DOCKED wet state:

```text
mass = 1,158,500 kg
CoM  = [26.676650841605525, 0.0, 0.14812257229175657] m
unresolved centroidal-inertia mass fraction = 1.0
parallel-axis tensor is symmetric and PSD
```

ABSENT wet state:

```text
mass = 1,125,500 kg
CoM  = [26.819635717458908, 0.0, 0.0] m
unresolved centroidal-inertia mass fraction = 1.0
parallel-axis tensor is symmetric and PSD
```

The ABSENT point-mass-only `Ixx = 0` result is retained as an explicit diagnostic demonstrating why the parallel-axis-only model cannot serve as physical roll inertia.

Pixel / Termux online-installed run:

```text
LOOM_PHASE5B_INERTIA_VERIFY: PASS
4 tests
0 errors
0 failures
```

Mandatory offline repeat produced the identical result hash:

```text
phase5b_inertia_verification_result.json
906810092821d23081e3068fbd3593a494532d008127684b1ee03e9578928464
```

Input hashes were unchanged between runs:

```text
test_phase5b_inertia_audit.py
670a1d4af1a28f5a073ec7ab08e72e2e1b49682d35dc6b33e2449e5cb80ddf9a

wayfarer_inertia_audit.py
8a38bad167c31ad4c3393b782a3c3cebdefc6d8967c278fae6523325d914327d

wayfarer_phase5_adapter.py
1decadf6e1a3f29dd926fa8b9df24397232e0252a507e56d11bbe8628f8c86b8
```

**Disposition:** Phase 5B inertia-authority audit PASSED on target Pixel and offline-deterministic. It qualifies the firewall and the derivable parallel-axis term; it does not qualify a Wayfarer flight inertia tensor.

## 9. Inertia firewall and next authority step

The complete component/store inertia model needed for physical Wayfarer rotational 6DOF remains OPEN.

No tensor may be fabricated from nominal hull envelopes, point-mass approximations, renderer-only geometry, or chat assumptions and then silently promoted to flight authority.

The next engineering increment shall create a candidate mass-distribution model with per-element provenance and approximation status. Each centroidal inertia contribution must be classified as one of:

- directly governed geometry/mass;
- derived from governed dimensions;
- explicit engineering approximation requiring qualification;
- unresolved / OPEN.

Renderer-only duplicate geometry cannot become physical authority merely because it exists. The integrated launch, working-fluid stores, primary structure, armor, thermal system, propulsion group and other coarse ledger masses require explicit mapping decisions before rotational propagation is authorized.

## 10. Still required before Phase 5 can close

At minimum:

1. establish and hostile-review a governed candidate Wayfarer centroidal mass-distribution model without silently promoting OPEN geometry;
2. qualify actual dynamic CoM/inertia migration through the ship-class authority seam;
3. add independent frozen hostile-reference vectors, including NASA/NESC and/or Basilisk as appropriate;
4. confirm Phase-1/Phase-5 attitude convention compatibility or provide frozen equivalence vectors;
5. strengthen integrated rotational trajectory cases and inertia validity checks;
6. rerun the complete Phase-5 suite on Pixel after executable inputs change;
7. repeat offline and compare deterministic hashes/numerics;
8. retain all failures and repairs as qualification evidence.

## 11. Gate state

**PHASE 5A: PASSED — PORTABLE MECHANICS + WAYFARER MASS/CoM SEAM + INERTIA FIREWALL QUALIFIED ON PIXEL/OFFLINE.**

**PHASE 5B: PASSED — DERIVABLE PARALLEL-AXIS INERTIA AUDIT + FAIL-CLOSED CENTROIDAL-INERTIA AUTHORITY QUALIFIED ON PIXEL/OFFLINE.**

**PHASE 5: OPEN — WAYFARER CENTROIDAL INERTIA MODEL + EXTERNAL HOSTILE REFERENCES + FINAL INTEGRATED PIXEL ACCEPTANCE STILL REQUIRED.**

No merge is authorized.

Production SHIPCLASSES remains untouched.

Navigator/GIS/HUD physics-dependent implementation remains hard frozen.
