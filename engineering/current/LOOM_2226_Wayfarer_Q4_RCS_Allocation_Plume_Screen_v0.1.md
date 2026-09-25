# LOOM 2226 — Wayfarer Q4 RCS Allocation & Plume Screen v0.1

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Q4_Mass_Properties_RCS_Attitude_v0.2.md`  
**Consumes:** `WAYFARER_Q4_RCS_MOUNT_PLACEMENT_V0.1`, `WAYFARER_Q4_RCS_CONTROL_SCREEN_V0.1`

## 0. Authority boundary

This increment does not promote RCS hardware, plume geometry, control laws, or maneuvering values to canon. It tests whether the current 16-hardpoint / four-cluster Q4 candidate can reproduce the already-existing Q4 HUD force/torque envelope under a 25 kN per-mount cap, and it performs only the plume geometry checks supported by current repository geometry.

It does not create stronger downstream authority than the existing Q4 HUD envelope.

## 1. Bounded force-allocation model

`src/wayfarer_rcs_allocation.py` consumes the current sampled 45° vectoring screen and applies a deterministic projected-gradient allocator.

Each mount has five sampled force directions from the existing Q4 control screen. The allocator treats those directions as a convexified vectoring set subject to:

- non-negative channel command;
- sum of channel commands at one physical mount <= **25 kN**;
- no command from a failed logical cluster;
- target matching in six-dimensional force/torque space;
- torque normalized by a 20 m characteristic length for numerical conditioning only.

The convexified representation is a feasibility relaxation for continuous gimbal motion or sufficiently fast time-sharing. It is **not** a claim that one mount contains five simultaneous independent nozzles.

## 2. Screened authority targets

The allocator inherits the existing Q4 HUD envelope rather than inventing new values.

### Nominal

- pure translation: **±100 kN** on each of X/Y/Z;
- pure roll torque: **±0.20 MN·m** about X;
- pure pitch/yaw torque: **±1.00 MN·m** about Y/Z.

### One logical cluster out

- pure translation: **±75 kN** on each of X/Y/Z;
- pure roll torque: **±0.10 MN·m** about X;
- pure pitch/yaw torque: **±0.75 MN·m** about Y/Z.

All twelve signed pure-axis cases are tested for nominal operation and for each individual logical cluster A–D removed.

## 3. Current deterministic allocation result

The current candidate passes the bounded allocation screen for all requested pure-axis cases without exceeding the 25 kN per-mount cap.

Reference screen summary:

| configuration | worst normalized residual | maximum mount utilization |
|---|---:|---:|
| nominal | 9.95e-8 | 0.99396 |
| cluster A out | 4.08e-6 | 0.99352 |
| cluster B out | 3.58e-6 | 0.99889 |
| cluster C out | 4.74e-6 | 0.99335 |
| cluster D out | 5.17e-6 | 0.99787 |

The configured residual gate is `1e-4`; utilization must remain <= 1.0.

**Disposition:** `PASS_BOUNDED_ALLOCATION_SCREEN_NOT_FINAL_CONTROL_QUALIFICATION`.

This is materially stronger than the preceding rank-six screen: it shows that the inherited nominal and degraded HUD envelope is reachable in the current convexified actuator model without asking any surviving mount for more than its 25 kN sizing cap.

It still does not prove simultaneous multi-axis maneuver margins, nonlinear continuous gimbal realization, structural loads, power duty, or closed-loop stability.

## 4. Plume / interference geometry screen

`src/wayfarer_rcs_plume_screen.py` exposes the exhaust centerline corresponding to every sampled force direction and evaluates only geometry presently supported by the repository.

### Local hull

Every sampled exhaust axis points outward from the local cylindrical hull. The most oblique sampled axes retain a radial component of `cos(45°)`, producing a minimum geometric angle of **45° above the local hull tangent plane**.

Therefore an idealized straight plume cone with half-angle less than 45° would remain in the local outward half-space at the nozzle. This is a local hull result only; it does not clear external hardware.

No physical plume half-angle is presently asserted.

### Current launch envelope

The sampled exhaust centerlines are ray-tested against the existing planetary-launch working AABB derived from current geometry anchors. Current sampled centerlines do not intersect that envelope.

### Current docking collar

The sampled exhaust centerlines are ray-tested against the existing docking-collar placeholder envelope. Current sampled centerlines do not intersect that envelope.

### Radiators

Final radiator panel geometry remains explicitly `OPEN` in the current geometry compiler. The current x=33–38 m cardinal root locations are sufficient to motivate the 45° rotated RCS mount band, but they are not sufficient to certify finite plume-cone clearance.

**Radiator plume qualification remains OPEN.**

## 5. What is now supported

The current Q4 candidate has earned, at engineering-study level:

1. deterministic 16-hardpoint placement;
2. 45° sampled outward-exhaust vectoring screen;
3. nominal six-DOF wrench rank;
4. six-DOF wrench rank after any one logical cluster loss;
5. bounded pure-axis allocation at the existing nominal Q4 HUD envelope;
6. bounded pure-axis allocation at the existing one-cluster-out Q4 HUD envelope;
7. local hull exhaust-direction clearance;
8. centerline clearance against current launch and docking envelopes.

## 6. Still OPEN before full Q4 closure

- exact physical nozzle / gimbal hardware;
- actual plume half-angle and plume thermochemistry;
- finite-cone plume clearance against final radiator geometry;
- simultaneous combined-axis allocation margins and duty-cycle constraints;
- structural mount and hull torque/load qualification;
- minimum stable thrust and minimum impulse bit;
- RCS working fluid / exhaust velocity;
- Q5 electrical-bus and thermal closure;
- momentum-storage sizing and unload interval;
- closed-loop guidance/control qualification;
- final docking-contact dynamics.

## 7. Downstream disposition

- **Computational Shipyard:** `REVALIDATION_REQUIRED` before rendering candidate mounts/nozzles as qualified hardware.
- **Navigator:** `REVALIDATION_REQUIRED` before consuming the allocation envelope as vehicle-control authority.
- **HUD:** `REVALIDATION_REQUIRED` before displaying actuator-level cluster/nozzle state as anything above engineering candidate.

The existing Q4 HUD finite-attitude envelope remains the downstream bound until these remaining gates close.
