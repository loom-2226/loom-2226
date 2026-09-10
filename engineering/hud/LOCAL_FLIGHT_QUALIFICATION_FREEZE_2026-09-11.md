# LOOM HUD / LOCAL FLIGHT — QUALIFICATION CLOSURE RECORD

Date: 2026-09-11
Status: REOPENED FOR CLOSURE CORRECTION — v0.21 CANDIDATE
Branch: `feature/hud-local-flight-contract-shell-v0.1-2026-09-09`
Authority: engineering qualification only; non-canon; non-Navigator targeting authority; no campaign writes.

## Why the v0.20 freeze was reopened

Pixel physical acceptance of v0.20 correctly returned `NOT_SOLVED`: terminal position and relative-velocity gates failed while lunar-clearance and remass gates passed. That is a material qualification defect, so the previous freeze is not treated as final.

Inspection found a second, more fundamental geometry issue: the qualification standoff target had been placed on the Moon's **far side** (`Earth -> Moon` outward radial). A direct two-burn Earth-side approach therefore had to cross the lunar body to reach the target, while the independent surface-clearance gate correctly prevented that. The solver was being asked to satisfy mutually hostile objectives.

v0.21 corrects the synthetic qualification target to the **Earth-facing lunar radial point** at `Moon radius + user standoff altitude`. This remains a synthetic qualification target only; it does not create a lunar orbit, station, docking point, or Navigator authority.

v0.21 also replaces the ad-hoc residual correction with a finite-burn lever-arm shooting correction and bounded line search. Every candidate is still re-propagated through the same Python-owned Earth+Moon gravity / Wayfarer torch / remass qualification dynamics.

## Closure gates

This slice may be re-frozen only after:

1. full Python regression passes on the v0.21 head;
2. Pixel physical acceptance runs `SOLVE RENDEZVOUS` from reset with torch off;
3. the quality panel reports either:
   - `SOLVED_TRANSLATIONAL_FEASIBILITY` with all four gates passing; or
   - a reproducible `NOT_SOLVED` result that demonstrates the bounded two-burn architecture itself cannot satisfy the terminal constraints, with that limitation explicitly preserved as the earned result.

Current explicit qualification gates:

- terminal position error <= 50 km;
- Moon-relative terminal speed <= 0.05 km/s;
- minimum lunar surface clearance >= 100 km;
- remaining remass > 0 t.

## Earned presentation / state baseline retained

- realtime Earth-Moon qualification scene using JPL/Hermite lunar state;
- NASA LRO optical Moon rendered at physical radius 1737.4 km;
- deterministic Wayfarer engineering geometry consumer;
- SHIP, CHASE and TRAJECTORY views with Pixel-oriented free-camera controls and reset;
- SHIP fixed-eye look semantics and off-screen Moon cue;
- geometry-derived Moon angular growth and START/MID/ARRIVAL preview checkpoints;
- live Moon range-rate / CLOSING / RECEDING telemetry derived from existing state vectors;
- non-mutating preview scrubber;
- Python-owned qualification propagation and browser presentation-only geometry.

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

## Next governed step after closure

Rotational / attitude-control engineering developed elsewhere may be brought into this lane only after its live repository authority, provenance, tests and qualification state are inspected.

**Import only through governed engineering authority.**

The import must not silently promote research artifacts, chat conclusions, mock values or unqualified geometry into flight-control authority. Integration must preserve the existing HUD consumer boundary and revalidate Pixel/Windows behavior plus all affected Navigator/Wayfarer interfaces.
