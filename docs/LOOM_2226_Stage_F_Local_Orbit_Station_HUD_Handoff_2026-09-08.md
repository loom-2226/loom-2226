# LOOM 2226 — Stage F Local Orbit / Station / HUD Handoff Refinement

Date: 2026-09-08  
Status: **Stage-F implementation refinement — feature branch / NON-CANON until governed merge**

## Purpose

Extend the Stage-F 3D Navigator foundation so local orbital geometry, orbital stations, station rendezvous targets, and the Navigator→HUD handoff are represented cleanly and without inventing spatial truth.

This refinement does not change campaign authority, Navigator solver authority, world/canon authority, or the existing Phase-6 execute chain.

## 1. Natural product handoff

The intended interaction boundary is:

```text
GIS / Navigator
    ↓
interplanetary route
    ↓
local body arrival geometry
    ↓
terminal rendezvous / transition state
    ↓
HUD / LOCAL FLIGHT
    ↓
proximity operations / hold / approach / docking / local maneuvering
```

Navigator should not own final docking sequencing. Its job is to deliver Wayfarer to a physically meaningful, time-stamped local transition state.

The HUD/local-flight surface then owns the player-facing proximity-operations workflow, while still consuming canonical spatial state rather than inventing local physics.

The reverse departure flow is symmetrical:

```text
docked / local state
    ↓
HUD local maneuvering / undock / departure clearance
    ↓
Navigator departure transition state
    ↓
interplanetary route
```

## 2. Two ordinary-space curves around metric transit

For mixed ordinary/metric travel, the preferred visual model is:

```text
origin orbit / station state
    ↓
real torch departure curve
    ↓
metric-entry boundary
    ↓
METRIC / RELATIONAL — no ordinary-space occupancy
    ↓
metric-exit / emergence boundary
    ↓
real terminal torch / capture curve
    ↓
destination orbit / station rendezvous state
```

Stage F must display only ordinary-space curves actually supplied by Navigator. It must not manufacture an arrival curve merely for symmetry.

A specific qualification task is therefore required: determine whether current Sequence-B route products expose authoritative ordinary-space geometry on both sides of metric transit. If only one side exists, record that as an upstream Navigator representation/solver gap rather than hiding it in the renderer.

## 3. Local body scene

When the player drills into origin or destination local space, the same Solar GIS / Navigator renderer should be able to include:

- the actual celestial body at the requested game epoch;
- Wayfarer at its authoritative local/ordinary state;
- the body-relative orbit or station-relative geometry associated with the selected endpoint;
- nearby orbital stations and other moving infrastructure only where authoritative spatial/orbital state exists;
- real ordinary-space departure/arrival trajectory samples;
- phase-boundary markers such as metric entry/emergence;
- velocity vectors and other telemetry only where authoritative values exist.

Render scale may exaggerate body/station/ship size for usability, but physical position and velocity remain separate and authoritative.

## 4. Standard orbital-state vocabulary

LOOM should develop a small canonical vocabulary of reusable orbital endpoint intents rather than relying on arbitrary ad hoc placement.

Initial vocabulary:

- `STATION_MATCH` — resolve to the selected station/facility's authoritative orbital state at the requested epoch;
- `LOW_CIRCULAR` — governed low circular parking orbit around the parent body;
- `HIGH_CIRCULAR` — governed higher staging/parking orbit;
- `EQUATORIAL_CIRCULAR` — governed circular orbit aligned with the parent body's equatorial plane where defined;
- `POLAR_CIRCULAR` — governed near-polar circular orbit;
- `ELLIPTICAL_TRANSFER` / `PHASING` — governed transfer/phasing family where appropriate;
- `BODY_DEFAULT` — compatibility fallback only where no more specific local state exists.

These names alone are not sufficient. Each governed standard orbit must eventually resolve to a complete 6D state at epoch:

- parent body / central object;
- orbital definition or authoritative source;
- position `(x, y, z)`;
- velocity `(vx, vy, vz)`;
- epoch;
- explicit reference frame;
- provenance / navigation grade;
- any validity or uncertainty metadata.

Stage F must not silently invent altitude, inclination, phase or orientation for an orbit that has not been defined through an authoritative resolver.

## 5. Orbital stations

Every station intended to participate in navigation, rendezvous, docking, local traffic, or 3D local rendering should ultimately have an authoritative time-resolvable orbital/spatial definition.

Minimum target contract for an orbital station:

- station entity identifier;
- parent body / parent frame;
- authoritative orbit or state-vector source;
- position and velocity at arbitrary supported game epoch;
- explicit reference frame;
- provenance / navigation grade;
- docking/rendezvous metadata;
- one or more local transition/reference points for Navigator→HUD handoff.

A station may not be rendered as precisely located merely because world/canon says it is "at Mars" or "at Ceres". If its orbital state is not known, the renderer must treat the location as unresolved/provisional rather than fabricate coordinates.

## 6. Station rendezvous and HUD transition point

Selecting an orbital station as a Navigator endpoint should not mean "arrive at the station's exact docking port".

Navigator should target a governed **terminal rendezvous / transition state** associated with that station.

That state should be station-relative and should include at minimum:

- transition-point identifier;
- target station identifier;
- epoch;
- relative position;
- relative velocity target or allowed envelope;
- local reference frame;
- approach-side / corridor metadata if defined;
- provenance / navigation grade.

The station's absolute 6D state plus the transition-point definition yields the absolute Navigator terminal state at the requested arrival epoch.

From that point, control passes to HUD/local flight for proximity operations, hold points, traffic-control sequencing, final approach and docking.

This boundary keeps Navigator responsible for interplanetary/local arrival targeting while preventing it from becoming a docking minigame or proximity-operations controller.

## 7. Standard station transition geometry

LOOM should define a reusable governed vocabulary for station-local transition/reference points. Exact values should remain station/type-specific and must not be invented by the renderer.

Candidate semantic roles include:

- `RENDEZVOUS_GATE` — default Navigator→HUD handoff state;
- `APPROACH_HOLD` — traffic-control hold state;
- `FINAL_APPROACH_ENTRY` — start of close proximity/docking sequence;
- `DEPARTURE_GATE` — HUD→Navigator outbound handoff;
- optional station-specific approach corridors or keep-out-zone boundaries.

A station may expose one or several of these. The important architectural rule is that the point is defined relative to the station/local frame and resolves to an absolute 6D state through the station's authoritative orbit at game epoch.

## 8. Time accuracy is mandatory

All celestial-body and station positions used by GIS, Navigator, local 3D views and HUD must be evaluated at an explicit LOOM game/query/playback epoch.

The target rule is:

```text
state(entity, t) → authoritative position + velocity + frame + provenance
```

not a static placement attached to the body name.

At any supported epoch `t`:

- celestial bodies resolve from ephemeris/spatial authority;
- orbital stations resolve from their governed orbital/spatial definitions;
- station transition points resolve from station state + local transition geometry;
- Wayfarer ordinary state resolves from Navigator trajectory or current local state;
- moving infrastructure uses the same epoch;
- HUD relative geometry uses the same epoch.

During accelerated playback, all of these advance against the same read-only playback cursor. Playback does not mutate the authoritative campaign clock.

## 9. Reference-frame discipline

The local-orbit and station system must preserve explicit transforms between:

- canonical heliocentric/J2000-ecliptic or existing Navigator frame;
- body-centric frame;
- station/local orbital frame;
- ship-local tactical/HUD frame.

Transforms belong in the shared spatial runtime/service layer. GIS, Navigator and HUD must not implement independent hidden orbital transforms.

## 10. Stage-F work added by this refinement

Stage F should now explicitly preserve and/or qualify the following bones before final acceptance:

1. system 3D and local-body 3D are views of the same canonical spatial state, not separate universes;
2. nearby orbital stations can be rendered only from authoritative time-resolved state;
3. endpoint contracts can carry station/orbit-local 6D state without assuming body center;
4. a station endpoint can resolve to `STATION_MATCH` plus a governed terminal rendezvous/transition point;
5. Navigator→HUD and HUD→Navigator transition states are explicit application concepts;
6. standard orbit intents and station-local transition roles are defined as governed vocabularies, with actual orbital parameters/state supplied by authoritative resolvers;
7. all ephemeris bodies and orbital stations can be evaluated at arbitrary supported game/query/playback time;
8. route playback uses the same epoch for ship, bodies, stations and HUD state;
9. metric transit remains relational/non-occupancy;
10. qualification identifies whether current Sequence-B exposes both departure and arrival ordinary-space geometry rather than cosmetically inventing a second curve.

## 11. Implementation sequencing recommendation

Do not solve all local orbital mechanics inside the renderer.

Recommended order after the current 3D presentation work:

1. inventory existing orbital stations and current spatial/orbit data quality;
2. inventory whether standard orbit definitions already exist elsewhere in LOOM;
3. define typed standard-orbit / station-state / transition-point contracts;
4. implement a shared time-resolved orbital endpoint resolver;
5. qualify station/body positions numerically at known epochs;
6. expose local scene objects through the existing spatial service;
7. bind Navigator endpoint selection to station/orbit transition states;
8. hand terminal rendezvous state into HUD/local flight;
9. only then add richer docking/proximity-operation UX.

No current world/canon station orbit, endpoint parameter, or transition geometry is to be replaced or invented merely to satisfy Stage-F visuals.
