# LOOM 2226 — Stage F-PB State Continuity / “Tokyo Drift” Qualification

Date: 2026-09-08  
Status: **Stage F-PB design refinement — feature branch / NON-CANON until governed merge**  
Parent authority: `docs/LOOM_2226_Simulation_Physical_Authority_Work_Plan_Amendment_2026-09-08.md`  
Audit prerequisite: Stage F-PA closure on `feature/f-pa-physical-authority-audit-2026-09-08`

## 0. Documentary authority

This refinement is based on live GitHub authority, not chat recollection.

Governing sources fetched before this refinement:

- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `docs/LOOM_2226_Simulation_Physical_Authority_Work_Plan_Amendment_2026-09-08.md`
- `src/loom/application/contracts.py`

The governing engineering canon states that TORCH, METRIC and LOOM are physically distinct propulsion regimes; no drive silently performs another drive's conservation work. For Metric, the natural ordinary-state output is produced by the path-dependent continuous propagator `U^M_gamma`; desired arrival state is separate and any mismatch must be paid by torch, tugs, infrastructure or another explicit exchange. Frame-less local velocity is incomplete.

This document does not invent a metric momentum law, new machine constants, traffic rules, station orbits, or endpoint coordinates.

## 1. Problem statement

The historical “Tokyo Drift” concept is retained only in the physically constrained form:

> A metric trajectory may collapse into a useful ordinary-space orbit only when the metric propagator's natural terminal ordinary state itself lies on, or within the allowed matching tolerance of, that orbit. Metric is not an arbitrary exit-velocity setter.

A correct transition therefore requires continuity of the full ordinary-space boundary state, not just a convenient velocity magnitude.

At any ordinary-space propulsion-regime boundary, the minimum physical handoff is:

```text
(entity, epoch, reference frame, position vector, velocity vector,
 provenance, qualification)
```

Vehicle mass/engineering state accompanies the handoff but does not replace the spatial state.

## 2. Mandatory continuity chain

The F-PB/F-PE architecture must support the same explicit state through:

```text
SOURCE TRUE STATE
    ↓
ordinary-space propagation / torch, if used
    ↓
METRIC ACQUISITION ORDINARY BOUNDARY STATE
    ↓
U^M_gamma metric propagation
    ↓
METRIC COLLAPSE NATURAL ORDINARY BOUNDARY STATE
    ↓
ordinary gravitational/orbital propagation
    ↓
explicit torch/tug/infrastructure correction, if required
    ↓
RENDEZVOUS / AUTHORIZED ORBIT / TERMINAL STATE
```

There may be no hidden reset of position, velocity, epoch, frame, mass or provenance at a regime transition.

During metric transit, ordinary-space occupancy must remain absent where the governing trajectory model does not supply it. The acquisition and collapse boundaries are nevertheless real ordinary-space states and must be represented explicitly.

## 3. Tokyo Drift physical test

For a target body or station, define:

- `Z_nat`: natural metric-collapse ordinary state from `U^M_gamma`;
- `Z_desired`: desired authorized arrival/orbit/rendezvous state in an explicitly declared destination frame and epoch.

The matching problem is:

```text
Delta_Z_match = Z_desired - Z_nat
```

No contract or solver may silently set `Delta_Z_match = 0`.

For a body-centered ordinary state `(r, v)`, the post-collapse orbit must be derived from the actual terminal state using ordinary orbital mechanics. At minimum the qualification layer must be able to derive/check:

- body-relative position and velocity vectors;
- specific orbital energy;
- specific angular-momentum vector;
- bound / escape / impact classification;
- osculating orbital elements where the dynamical model makes them meaningful;
- periapsis/apoapsis or equivalent trajectory consequences;
- atmosphere/surface/keep-out intersection where relevant;
- remaining explicit velocity/state correction required to reach the authorized target.

A “perfect orbit” claim therefore means the actual collapse state produces that orbit within an explicit tolerance and fidelity model. Matching only speed, only velocity direction, or only altitude is insufficient.

## 4. Three required solution classes

Navigator qualification must distinguish at least:

### A. NATURAL_MATCH

`Z_nat` already satisfies the desired orbital/arrival state within the declared tolerance. Required ordinary momentum correction may be zero or negligible under the qualified model.

### B. CORRECTABLE_MATCH

`Z_nat` is physically valid but does not satisfy `Z_desired`. The residual must be exposed and paid by an explicit ordinary momentum-exchange system or authorized infrastructure.

### C. REJECTED_MATCH

The requested terminal state cannot be reached under the permitted metric path/environment/control/conservation envelope, or would violate physical/traffic constraints. The solver fails closed rather than manufacturing a terminal vector.

These classes are physics outcomes, not traffic-clearance outcomes. A physically valid NATURAL_MATCH may still be operationally prohibited by a body traffic regime.

## 5. Physical versus regulatory gate

Metric terminal-state acceptance has two independent gates:

```text
PHYSICAL CERTIFICATION
    - metric environment / control / thermal / conservation
    - valid U^M calibration
    - physically propagated terminal state

TRAFFIC / OPERATING AUTHORIZATION
    - permitted collapse volume / corridor / epoch
    - protected orbit / station keep-out
    - vehicle class / clearance / right-of-way
```

A populated body's authority may prohibit metric collapse in an otherwise physically valid low-orbit or station approach volume. That prohibition must not be encoded as fake orbital mechanics.

Likewise, a physically impossible or uncertified collapse may not be made legal merely because a traffic rule permits the region.

## 6. F-PB contract consequence

The existing `SpatialState` contract already provides an explicit epoch, frame, XYZ, VXYZ, provenance, navigation grade and uncertainty surface. F-PB should reuse/strengthen this contract rather than introducing a competing 6D representation.

New typed transition contracts must bind a `SpatialState` to:

- transition/boundary identity;
- incoming propulsion/dynamics regime;
- outgoing propulsion/dynamics regime;
- campaign revision / solution identity;
- natural versus desired versus corrected state semantics;
- source propagator / model / calibration identity;
- qualification result and residual;
- physical-certification status;
- traffic-clearance status kept separately;
- conservation/accounting provenance.

The contract must not contain renderer-specific geometry or infer missing ordinary coordinates during metric transit.

## 7. Hostile qualification case

The first dedicated hostile continuity test should use a route with a target body's ordinary orbital dynamics available at arrival.

Test structure:

```text
1. start from one explicit source ordinary state;
2. propagate to metric acquisition without state reset;
3. run a metric solution producing a natural collapse state;
4. transform collapse state into the declared target-centered inertial frame;
5. derive the resulting ordinary orbit from that exact state;
6. compare against a desired authorized arrival orbit/gate;
7. report the full residual;
8. if correction is required, charge it to an explicit torch/tug/infrastructure exchange;
9. reject any solution that obtains the desired state by overwriting the natural collapse state;
10. verify continuity of epoch/frame/provenance/mass across every boundary.
```

The test should exercise three target modes when the physical/traffic models exist:

- unconstrained natural collapse;
- metric path optimized for minimum subsequent ordinary correction;
- physically valid metric collapse constrained to an authorized arrival corridor/orbit.

Expected property: the constrained/optimized solver may reduce the ordinary correction residual, but may not arbitrarily choose terminal momentum independent of `U^M_gamma` and the conservation/certification model.

## 8. Failure conditions

F-PB/F-PE must fail qualification if any of the following occurs:

- a propulsion-regime boundary changes XYZ/VXYZ without an explicit physical propagator/exchange;
- a local velocity appears without a declared frame;
- collapse velocity is assigned from the requested target orbit rather than produced by the metric propagator;
- a body-center/location token is substituted for an actual 6D state;
- historical/rendered trajectory geometry is used to reconstruct current true state;
- metric relational transit is given fabricated ordinary XYZ;
- a correction residual disappears without a torch/tug/infrastructure/conservation ledger entry;
- traffic permission is treated as physical reachability;
- physical reachability is treated as traffic authorization;
- an approximate/reference state is silently upgraded to navigation authority.

## 9. Stage impact

This refinement changes the implementation order inside the already-governed physical-authority stages:

### F-PB

State-continuity and transition-boundary contracts are foundational and must be established before broad world-schema enrichment. Celestial/site/station/traffic contracts must consume the same spatial-state semantics.

### F-PC

Time-resolved station/surface states must resolve into the same state contract used by propulsion boundaries.

### F-PD

Authorized orbit/traffic classes produce desired physical states or constraints; they do not assign the ship's actual state.

### F-PE

Transition dynamics compares the actual incoming state with desired authorized handoff/rendezvous states and exposes residuals.

### F-PF

Torch/metric vehicle propagation advances one continuous true state and must close mass/momentum/energy/accounting according to each regime's governed model.

## 10. Qualification gate

Before F-PB is considered complete:

1. one canonical 6D ordinary-state representation is used across celestial, infrastructure, vehicle and trajectory boundary contracts;
2. propulsion-transition boundaries cannot exist without an explicit epoch/frame state where ordinary occupancy exists;
3. natural metric collapse state and desired terminal state are separate typed concepts;
4. terminal residual cannot be silently erased;
5. physical certification and traffic authorization are independent typed results;
6. ordinary orbital consequences can be derived from the exact collapse state;
7. a Tokyo Drift hostile test proves that a requested perfect orbit cannot be obtained by terminal-state overwrite;
8. metric transit remains relational/non-occupancy where required;
9. no existing campaign/world/canon value is promoted as a side effect of this contract work.
