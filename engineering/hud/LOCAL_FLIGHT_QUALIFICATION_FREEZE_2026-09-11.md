# LOOM HUD / LOCAL FLIGHT — FROZEN QUALIFICATION SLICE

Date: 2026-09-11
Status: FROZEN QUALIFICATION SLICE
Branch: `feature/hud-local-flight-contract-shell-v0.1-2026-09-09`
Authority: engineering qualification only; non-canon; non-Navigator targeting authority; no campaign writes.

## Freeze boundary

This freeze closes the current HUD/local-flight qualification slice after the trajectory-quality pass. The slice has earned a usable presentation and translational-feasibility baseline, but it does **not** qualify operational flight-control authority.

Included in the frozen slice:

- realtime Earth-Moon qualification scene using JPL/Hermite lunar state;
- NASA LRO optical Moon rendered at physical radius 1737.4 km;
- deterministic Wayfarer engineering geometry consumer;
- SHIP, CHASE and TRAJECTORY views with Pixel-oriented free-camera controls and reset;
- SHIP fixed-eye look semantics and off-screen Moon cue;
- geometry-derived Moon angular growth and START/MID/ARRIVAL preview checkpoints;
- live Moon range-rate / CLOSING / RECEDING telemetry derived from existing state vectors;
- qualification-only forward propagation, moving-Moon intercept search and terminal-state rendezvous feasibility preview;
- iterative terminal-state correction with explicit position, relative-velocity, surface-clearance and remass quality gates;
- trajectory quality presentation with SOLVED / NOT SOLVED status;
- non-mutating preview scrubber;
- Python-owned gravity/thrust/remass propagation and browser presentation-only geometry.

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

## Next governed step

Rotational / attitude-control engineering developed elsewhere may be brought into this lane only after its live repository authority, provenance, tests and qualification state are inspected.

**Import only through governed engineering authority.**

The import must not silently promote research artifacts, chat conclusions, mock values or unqualified geometry into flight-control authority. Integration must preserve the existing HUD consumer boundary and must revalidate Pixel/Windows behavior plus all affected Navigator/Wayfarer interfaces.

## Reopen conditions

Reopen this slice only for one of the following:

1. governed import of qualified Wayfarer rotational-control authority;
2. a material defect in the frozen HUD/translational baseline;
3. Navigator integration requiring an explicit contract change;
4. release/integration work needed to promote this branch through the normal governed process.

Cosmetic feature expansion alone is not a reason to reopen the frozen slice.
