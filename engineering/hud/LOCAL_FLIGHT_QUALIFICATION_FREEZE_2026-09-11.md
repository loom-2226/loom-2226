# LOOM HUD / LOCAL FLIGHT — FROZEN QUALIFICATION SLICE

Date: 2026-09-11
Status: FROZEN AFTER v0.21 PIXEL ACCEPTANCE
Branch: `feature/hud-local-flight-contract-shell-v0.1-2026-09-09`
Authority: engineering qualification only; non-canon; non-Navigator targeting authority; no campaign writes.

## Closure result

The HUD/local-flight translational qualification slice is frozen at v0.21 after successful software regression and Pixel physical acceptance.

v0.20 was reopened because its rendezvous feasibility solve correctly failed the terminal position and relative-velocity gates. Inspection then found that the qualification standoff target had been placed on the Moon's far side (`Earth -> Moon` outward radial), forcing a direct Earth-side two-burn approach to conflict with the independent lunar-surface-clearance gate.

v0.21 corrected the synthetic qualification target to the **Earth-facing lunar radial point** at `Moon radius + user standoff altitude` and replaced the ad-hoc residual update with a finite-burn lever-arm shooting corrector plus bounded deterministic line search. Every candidate continues to be re-propagated through the same Python-owned Earth+Moon gravity / Wayfarer torch / remass qualification dynamics.

This target remains a synthetic qualification point only. It does not create or imply a canonical lunar orbit, station, docking point, or Navigator targeting authority.

## Acceptance evidence

### Software regression

GitHub Actions `LOOM Python Regression` run 876 completed successfully on the v0.21 closure-candidate runtime head `9b2af4306f1eb95f896863836cce92e7c01ee06b`.

### Pixel physical acceptance

Pixel 10 Pro physical acceptance was run from reset with:

- time rate: 1x;
- torch: OFF;
- torch mode: CRUISE;
- standoff altitude: 1000 km;
- action: `SOLVE RENDEZVOUS`.

The v0.21 HUD quality panel reported:

- `SOLVED — TRANSLATIONAL FEASIBILITY`;
- terminal target error: **3.8 km**;
- Moon-relative terminal speed: **0.029 km/s**;
- minimum lunar surface clearance: **1003.8 km**;
- remaining remass: **239.7 t**;
- position gate: PASS;
- relative-velocity gate: PASS;
- surface-clearance gate: PASS;
- remass gate: PASS;
- selected iteration: 3 / 8;
- candidate count: 13.

Current explicit qualification gates were:

- terminal position error <= 50 km;
- Moon-relative terminal speed <= 0.05 km/s;
- minimum lunar surface clearance >= 100 km;
- remaining remass > 0 t.

All four gates passed.

## Earned baseline frozen in this slice

- realtime Earth-Moon qualification scene using JPL/Hermite lunar state;
- NASA LRO optical Moon rendered at physical radius 1737.4 km;
- deterministic Wayfarer engineering geometry consumer;
- SHIP, CHASE and TRAJECTORY views with Pixel-oriented free-camera controls and reset;
- SHIP fixed-eye look semantics and off-screen Moon cue;
- geometry-derived Moon angular growth and START/MID/ARRIVAL preview checkpoints;
- live Moon range-rate / CLOSING / RECEDING telemetry derived from existing state vectors;
- non-mutating preview scrubber;
- moving-Moon intercept preview;
- corrected Earth-facing lunar standoff qualification geometry;
- finite-burn iterative terminal-state corrector with bounded deterministic line search;
- explicit SOLVED / NOT SOLVED gates for terminal position, Moon-relative velocity, minimum surface clearance and remass reserve;
- successful Pixel translational-feasibility solve within all four gates;
- Python-owned qualification propagation and browser presentation-only geometry;
- no campaign writes.

## Explicitly excluded

### ATTITUDE / ROTATIONAL AUTHORITY NOT INCLUDED

This slice does not contain or imply qualified:

- RCS architecture;
- thruster placement or torque authority;
- inertia tensor or mass-property evolution;
- angular acceleration / angular-rate limits;
- flip duration or slew profile;
- attitude-control law;
- burn interruption caused by reorientation;
- executable accelerate-flip-brake rendezvous;
- docking or lunar-orbit insertion authority.

Rendezvous feasibility may assume instantaneous attitude reorientation solely to answer a translational feasibility question. That assumption must remain visibly marked `ATTITUDE TRANSITION UNQUALIFIED`.

`SOLVED — TRANSLATIONAL FEASIBILITY` does **not** mean solved attitude dynamics, executable flight control, Navigator targeting authority, docking qualification, or lunar-orbit insertion qualification.

## Next governed step

Rotational / attitude-control engineering developed in the parallel engineering lane may now be brought into this lane only after its **live repository authority**, provenance, tests and qualification state are inspected.

**Import only through governed engineering authority.**

The import must not silently promote research artifacts, chat conclusions, mock values or unqualified geometry into flight-control authority. Integration must preserve the HUD consumer boundary and revalidate Pixel/Windows behavior plus affected Navigator/Wayfarer interfaces.

## Reopen conditions

Reopen this frozen slice only for one of the following:

1. governed import of qualified Wayfarer rotational-control authority;
2. a material defect in the frozen translational/HUD baseline;
3. Navigator integration requiring an explicit contract change;
4. release/integration work required by the normal governed process.

Cosmetic feature expansion alone is not a reason to reopen the slice.
