# LOOM 2226 — Portable Ship Simulation Qualification — Phase 1 Decision

Date: 2026-09-08
Status: ENGINEERING / QUALIFICATION — FEATURE BRANCH — NOT CANON
Branch: `qualification/portable-ship-phase1-2026-09-08`
Parent authority: `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`

## 1. Governing constraints

This decision is subordinate to the live GitHub governing plan. Mandatory acceptance remains external to the LLM, Pixel-local after setup, offline-capable, deterministic, and code-judged. Navigator/GIS/HUD physics-dependent work remains frozen until the ship-common qualification gate passes. `loompy` remains RESERVED / NOT IMPLEMENTED.

No SHIPCLASSES schema decision is authorized by this document. The Pixel seam must pass first.

## 2. Phase 1 decision summary

Recommended role assignment:

- `PORTABLE_QUALIFICATION_KERNEL`: **small LOOM-owned NumPy 6DOF kernel, fixed-step deterministic integrator, qualified against analytic and frozen hostile-reference vectors.** This designation is CONDITIONAL until the supplied proof runs successfully on the Pixel itself.
- `SPACECRAFT_HOSTILE_REFERENCE`: **Basilisk**.
- `NASA_DEEP_REFERENCE`: **NASA JEOD + Trick**.
- `ASTRODYNAMICS_REFERENCE`: **Tudat/TudatPy**.
- `LOOM_RUNTIME_STRATEGY`: **LOOM simulation executive owns stable state/effector/regime contracts; ordinary dynamics uses a minimal portable kernel; external engines are reference/qualification generators rather than mandatory runtime dependencies.**
- `GN&C_STRATEGY`: **adopt Basilisk-style separation of dynamics, effectors, sensors, estimation, guidance and control as an architectural pattern; implement only the minimum portable typed interfaces and algorithms needed by LOOM, then qualify them against independent references.**
- `DO_NOT_REIMPLEMENT`: **do not recreate full JEOD, Basilisk, Tudat, SPICE/ephemeris machinery, high-order environment models, generic flight-control frameworks, or desktop simulation executives inside the Pixel runtime.** Reimplement only the narrow deterministic mechanics needed for the governed LOOM state contract when portability requires it.

## 3. Evidence-backed comparison

Scoring: 5 = strong fit, 1 = poor fit for this specific role. Scores are engineering judgments based on cited architecture/dependency evidence, not vendor quality rankings.

| Criterion | SimuPy Flight | Basilisk | JEOD + Trick | Tudat/TudatPy | JSBSim | LOOM small kernel |
|---|---:|---:|---:|---:|---:|---:|
| Rigid-body 6DOF | 5 | 5 | 5 | 4 | 5 | 5 |
| Spacecraft-specific dynamics | 3 | 5 | 5 | 5 | 2 | 4 |
| Dynamic mass / CoM / inertia | 3 | 5 | 5 | 4 | 3 | 3 initially |
| RCS / force / torque effectors | 4 | 5 | 5 | 4 | 4 | 5 by contract |
| GN&C ecosystem | 2 | 5 | 4 | 3 | 4 aircraft-centric | 2 initially |
| Orbit / frame discipline | 3 | 5 | 5 | 5 | 1 | 2 initially |
| Rendezvous / docking utility | 2 | 5 | 5 | 5 | 1 | 3 by extension |
| Deterministic reference use | 5 | 5 | 5 | 5 | 5 | 5 |
| Torch extensibility | 4 | 5 | 5 | 4 | 3 | 5 |
| Clean metric-regime separation | 4 | 4 | 3 | 4 | 3 | 5 |
| Android / Pixel viability | 2-3 | 1 | 1 | 1-2 | 2 | 5 |
| Offline after setup | 5 | 5 | 5 | 5 | 5 | 5 |
| Runtime footprint | 3 | 2 | 1 | 2 | 4 | 5 |
| CI/headless | 5 | 5 | 5 | 5 | 5 | 5 |
| License simplicity for LOOM use | 3 | 5 | 3 | 5 | 3 | 5 |
| Zero-budget maintainability | 3 | 4 as reference | 2 | 4 as reference | 4 | 5 |

### 3.1 NASA SimuPy Flight / NESC

SimuPy Flight is deliberately built around NASA/NESC 6DOF verification cases. Its README states that the equations of motion are expressed through SimuPy, use SciPy numerical integration wrappers, and use SymPy/code generation; it ships implemented NESC atmospheric test cases and corresponding reference data. This makes it unusually valuable as a published 6DOF reference and harness source.

The same dependency chain is a Pixel risk: SciPy's compiled numerical stack and generated/symbolic dependencies are substantially more fragile on Android/Pydroid than NumPy alone. Therefore SimuPy Flight should remain a preferred NESC/reference-vector source even if its full package is not admitted to the Pixel runtime.

License: NASA Open Source Agreement 1.3.

Primary sources:
- https://github.com/nasa/simupy-flight
- NESC 6DOF test-case material referenced by that repository

### 3.2 Basilisk

Basilisk is the strongest spacecraft hostile-reference candidate. Its spacecraft module explicitly supports coupled translation and rotation and accepts state effectors and dynamic effectors; documented examples include thrusters, reaction wheels, fuel/slosh and external force/torque. Its architecture also exposes spacecraft state and mass-property messages and computes energy/momentum for validation.

Its current distribution is Python over C/C++ with prebuilt wheels targeting normal desktop platforms. Official material lists macOS, Linux and Windows; Android is not an advertised target. This is excellent for desktop/CI hostile comparison and poor as a mandatory Pixel dependency.

License: ISC.

Primary sources:
- https://github.com/AVSLab/basilisk
- https://www.hanspeterschaub.info/basilisk/Documentation/simulation/dynamics/spacecraft/spacecraft.html
- https://www.hanspeterschaub.info/basilisk/Documentation/simulation/dynamics/Thrusters/thrusterDynamicEffector/thrusterDynamicEffector.html

### 3.3 NASA JEOD + Trick

JEOD is the deepest NASA physical-reference candidate. JEOD 5.4 documents models for vehicles that translate and rotate in a space environment, organized across dynamics, environment, interactions and utilities, with model-level verification artifacts and integrated validation against best-estimate trajectory data. The current JEOD release is designed primarily for the Trick simulation environment and documents compiled-toolchain requirements.

This makes JEOD+Trick an excellent deep hostile reference and an obviously unsuitable mandatory Pixel runtime dependency.

Primary sources:
- https://github.com/nasa/jeod
- https://nasa.github.io/trick/

### 3.4 Tudat/TudatPy

Tudat is the strongest astrodynamics reference candidate. Current documentation supports translational, rotational, mass, custom and multi-type propagation; it also provides high-fidelity environment modeling, estimation, variational equations, mission design and SPICE-backed workflows. Published examples include coupled translational-rotational propagation and custom thrust modeling.

Its C++ core/Python binding architecture and scientific dependency footprint make it a desktop/CI reference rather than the preferred Pixel acceptance kernel.

License: Modified BSD.

Primary sources:
- https://docs.tudat.space/en/latest/user-guide/state-propagation/propagation-setup.html
- https://docs.tudat.space/en/latest/examples/tudatpy-examples/propagation/coupled_translational_rotational_dynamics.html
- https://docs.tudat.space/en/latest/examples/tudatpy-examples/propagation/thrust_satellite_engine.html

### 3.5 JSBSim

JSBSim is a lightweight, data-driven nonlinear 6DOF flight-dynamics/control engine and remains useful as an independent control/6DOF comparator. Its center of gravity is aircraft flight dynamics rather than spacecraft astrodynamics, so it should not own LOOM's spacecraft architecture.

License: LGPL 2.1.

Primary sources:
- https://jsbsim-team.github.io/jsbsim-reference-manual/
- https://github.com/JSBSim-Team/jsbsim

## 4. Game/simulation architecture lessons

These are architecture lessons, not qualification authorities.

### Children of a Dead Earth

Useful lesson: **equations first, gameplay second**. The developer explicitly describes implementing physics/engineering equations and allowing gameplay to emerge from them, while maintaining a 1:1 system-scale simulation and n-body orbital mechanics. For LOOM this supports keeping physical authority upstream of HUD/game abstractions rather than inventing gameplay-only maneuverability statistics.

Source: https://www.childrenofadeadearth.com/Overview.html

### Kerbal Space Program

Useful lesson: **separate simulation fidelity by operational scale**. KSP's well-known patched-conic approach demonstrates the gameplay value of an intentionally bounded orbital approximation. LOOM should apply the same engineering discipline without copying the approximation blindly: use the lowest fidelity that passes the governed operational requirement, and escalate fidelity through explicit reference tiers.

### Juno: New Origins

Useful lesson: **one structured craft definition should drive both performance and visible craft behavior**. Juno exposes part-based construction, RCS, engine design, changing aerodynamic characteristics, telemetry and automation. That reinforces LOOM's same-authority rule: configuration/parts should affect both physical properties and representation rather than living in duplicate renderer-only data.

Source: https://store.steampowered.com/app/870200/Juno_New_Origins/

### Elite Dangerous

Useful lesson: **control-law presentation may be layered over underlying kinematics**. A pilot-assist mode or flight computer can radically change the user experience without changing the spacecraft's physical authority. For LOOM, future assist/autopilot belongs above actuator/dynamics truth and must be disable-able/auditable rather than embedded in the plant.

## 5. Runtime architecture decision

The recommended architecture is:

```text
SHIP PHYSICAL AUTHORITY
        ↓
LOOM SIMULATION EXECUTIVE
        ↓
+---------------- ordinary ----------------+
| portable deterministic 6DOF kernel       |
| force/moment effectors                    |
| mass / CoM / inertia recomputation        |
| environment modules by qualified tier     |
+-------------------------------------------+
        ↓
VehicleTrueState

separate regime seam:
ordinary 6D → METRIC_ACQUISITION → metricpy → NATURAL terminal 6D → residual qualification → ordinary

loompy → FAIL CLOSED / NOT IMPLEMENTED
```

The executive/state contracts are LOOM-owned. External simulators do not own campaign state or ship SQL. Frozen external vectors cross the boundary as qualification evidence only.

## 6. Pixel proof implementation

Feature-branch artifact:

`qualification/phase1/verify_pixel_6dof.py`

The proof intentionally requires only Python + NumPy. It implements:

- 13-state rigid body: inertial position/velocity, body-to-inertial quaternion, body angular velocity;
- fixed-step RK4;
- explicit custom force/moment callback seam;
- Euler rigid-body rotational equation with full 3x3 inertia input;
- free inertial coast known-answer test;
- injected constant force + principal-axis torque known-answer test;
- quaternion norm check;
- deterministic JSON + CSV output;
- SHA-256 output hashes;
- process exit code and explicit PASS/FAIL determined by code.

Local non-Pixel dry-run evidence on 2026-09-08:

- zero-force max absolute error: `0.0`;
- injected-wrench max absolute error: approximately `5.48e-11`;
- two repeated local runs produced identical JSON and CSV hashes;
- local result: PASS.

This is **not** the governing Pixel result. Phase 1 remains OPEN until the same artifact is executed on the user's Pixel, preferably once online/installed and then again with network disabled, and both runs produce numerical PASS with deterministic outputs.

## 7. Required Pixel execution

From a repository checkout containing this branch:

```text
cd qualification/phase1
python verify_pixel_6dof.py
```

Expected terminal marker:

```text
LOOM_PIXEL_6DOF_PROOF: PASS
```

Generated local artifacts:

```text
qualification/phase1/output/pixel_6dof_result.json
qualification/phase1/output/pixel_6dof_trace.csv
```

For the offline-repeat gate:

1. run once with dependencies already installed;
2. disable network connectivity;
3. run again unchanged;
4. retain both console results or generated output hashes;
5. require code-reported PASS both times.

## 8. Phase 1 gate status

Current status: **OPEN — AWAITING PIXEL EXECUTION.**

Completed:
- live GitHub governance bootstrap;
- external simulator/reference comparison;
- role recommendations;
- smallest practical portable proof artifact;
- local dry-run and deterministic repeat check.

Not yet completed:
- actual Pixel/Pydroid execution;
- offline Pixel rerun;
- governance freeze of the simulator-role decision after Pixel evidence.

Therefore:

**Do not design `LOOM_2226_SHIPCLASSES.sqlite3` around any simulator API yet.**

**Navigator/GIS/HUD physics-dependent implementation remains hard frozen.**

**No merge is authorized by this document.**
