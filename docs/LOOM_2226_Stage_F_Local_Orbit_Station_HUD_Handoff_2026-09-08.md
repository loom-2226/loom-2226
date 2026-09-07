# LOOM 2226 — Stage F Local Orbit / Station / HUD Handoff Refinement

Date: 2026-09-08  
Status: **Stage-F implementation refinement — feature branch / NON-CANON until governed merge**

## Purpose

Extend the Stage-F 3D Navigator foundation so local orbital geometry, orbital stations, surface infrastructure, transition states, station rendezvous targets, atmospheric/surface approach states, and the Navigator→HUD handoff are represented cleanly and without inventing spatial truth.

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

Navigator should not own final docking sequencing. Its job is to deliver Wayfarer or another craft to a physically meaningful, time-stamped local transition state.

The HUD/local-flight surface then owns the player-facing proximity-operations workflow, while still consuming canonical spatial state rather than inventing local physics.

The reverse departure flow is symmetrical:

```text
docked / landed / local state
    ↓
HUD local maneuvering / undock / surface departure / clearance
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
- Wayfarer or shuttlecraft at its authoritative local/ordinary state;
- the body-relative orbit or station-relative geometry associated with the selected endpoint;
- nearby orbital stations and other moving infrastructure only where authoritative spatial/orbital state exists;
- surface infrastructure at authoritative body-fixed geographic coordinates;
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
- `SURFACE_APPROACH` — governed transition from orbital/entry navigation to local landing guidance for a selected surface site;
- `BODY_DEFAULT` — compatibility fallback only where no more specific local state exists.

These names alone are not sufficient. Each governed standard orbit or transition must eventually resolve to a complete state at epoch with explicit provenance.

Stage F must not silently invent altitude, inclination, phase, orientation, entry corridor, landing azimuth, hold point or approach geometry that has not been defined through an authoritative resolver.

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

## 7. Standard station transition geometry

LOOM should define a reusable governed vocabulary for station-local transition/reference points. Exact values should remain station/type-specific and must not be invented by the renderer.

Candidate semantic roles include:

- `RENDEZVOUS_GATE` — default Navigator→HUD handoff state;
- `APPROACH_HOLD` — traffic-control hold state;
- `FINAL_APPROACH_ENTRY` — start of close proximity/docking sequence;
- `DEPARTURE_GATE` — HUD→Navigator outbound handoff;
- optional station-specific approach corridors or keep-out-zone boundaries.

A station may expose one or several of these. The important architectural rule is that the point is defined relative to the station/local frame and resolves to an absolute 6D state through the station's authoritative orbit at game epoch.

## 8. Surface infrastructure must be geographically anchored

Every surface facility intended for local navigation, shuttle operations, 3D rendering, landing, takeoff, logistics, sensor range, or line-of-sight should have an authoritative body-fixed geographic location.

Minimum target contract for surface infrastructure:

- entity identifier;
- parent celestial body;
- body-fixed latitude / longitude or equivalent planetographic/planetocentric coordinates as appropriate;
- elevation / radius-above-reference-surface where known;
- named body-fixed reference frame;
- optional local orientation / heading / landing-pad axis;
- facility footprint or local reference geometry where relevant;
- provenance / confidence / navigation grade.

The shared spatial runtime must transform that body-fixed location into inertial/J2000-ecliptic position at any requested game epoch using the parent body's authoritative orientation/rotation model. Surface facilities are therefore not static points in inertial space.

If a facility lacks authoritative geographic coordinates, the renderer must show it as unresolved/provisional rather than assign a convenient location.

## 9. Standard surface-approach / landing transition states

Surface arrivals need the same explicit handoff discipline as station docking.

Selecting a surface destination should resolve to a governed approach sequence rather than "arrive at the facility marker".

Candidate semantic roles include:

- `ORBITAL_DEORBIT_GATE` — state from which deorbit / descent targeting begins;
- `ENTRY_INTERFACE` — atmospheric-entry transition where applicable;
- `TERMINAL_AREA_ENTRY` — transition from broad descent guidance to local approach;
- `LANDING_APPROACH_GATE` — HUD/local-flight handoff for final landing guidance;
- `SURFACE_HOLD` — optional traffic/weather/clearance hold state;
- `PAD_FINAL` / `RUNWAY_FINAL` / `VERTICAL_FINAL` — final approach family determined by vehicle and site;
- `SURFACE_DEPARTURE_GATE` — local-flight → orbital/Navigator outbound handoff.

For airless bodies, the atmospheric stages collapse naturally and the sequence may be orbital descent → terminal area → landing approach. For atmospheric bodies, entry interface, lift/drag constraints, heading alignment and terminal guidance are explicit parts of the chain.

The renderer or HUD must not invent these states. They are derived from the selected site's authoritative coordinates, body model, vehicle performance envelope, current epoch/state and governed mission/navigation rules.

## 10. NASA / international-practice baseline

LOOM should use real NASA/international spaceflight standards and operational conventions wherever those standards actually exist, and NASA-derived mission-design practice where no single universal standard exists.

Reference baseline includes:

- NASA Rendezvous, Proximity Operations and Docking (RPOD) guidance/operations practice;
- International Docking System Standard (IDSS) for compatible docking-interface geometry and docking initial-condition constraints;
- NASA/JSC rendezvous and proximity-operations concepts including approach corridors, hold points, keep-out concepts, collision avoidance and relative-motion targeting;
- NASA/JPL/NAIF reference-frame discipline for inertial, body-fixed, site-local and vehicle-local transformations;
- NASA/JPL ephemeris practice for time-resolved celestial-body state;
- NASA mission-design/orbital-mechanics conventions for transfer, phasing, rendezvous, capture, deorbit, entry/descent/landing and departure transitions.

Important qualification: there is not one universal NASA-defined altitude or geometry for every parking orbit, planetary shuttle landing approach or station rendezvous gate. Where NASA publishes a standard, LOOM should adopt it directly where compatible. Where NASA uses mission-specific targeting, LOOM should derive the transition state from the same orbital-dynamics/GN&C principles rather than invent a decorative constant.

NASA documentation distinguishes rendezvous, proximity operations and docking as separate phases, and NASA practice uses relative-motion stop/transition points, approach corridors, keep-out regions and defined docking-interface conditions rather than treating docking as a single endpoint. IDSS governs the physical docking interface and associated design/initial-condition envelopes. These practices are the model for LOOM's governed station handoff semantics.

## 11. Derived dynamics at every transition point

Every Navigator↔HUD transition point should be a **derived navigation state**, not merely a named marker.

At evaluation epoch `t`, the resolver should compute or retrieve as appropriate:

- absolute position and velocity in canonical inertial frame;
- parent-relative position and velocity;
- local orbital/site/station frame orientation;
- target-relative state;
- required/allowed relative velocity envelope;
- transfer/phasing/deorbit/approach geometry;
- safety corridor / keep-out / hold constraints where applicable;
- provenance and navigation-grade status.

These values should come from shared orbital dynamics and spatial services using accepted NASA/JPL-style reference-frame discipline and authoritative body/station/site data.

The UI may label a point `RENDEZVOUS_GATE` or `LANDING_APPROACH_GATE`, but the point's actual state is derived for that mission, target and epoch.

## 12. Everything spatial is 3D

LOOM should treat all relevant game-world spatial entities as three-dimensional state, even if some UI views are 2D projections.

That includes:

- celestial bodies;
- orbital stations;
- surface facilities;
- ships/shuttles;
- ordinary-space route segments;
- local approach/departure corridors;
- station rendezvous gates;
- landing/deorbit transition states;
- local terrain/landing references when introduced.

A 2D map, top view or schematic is a projection of 3D authority, never a separate geometry authority.

## 13. Time accuracy is mandatory

All celestial-body, station and surface-facility positions used by GIS, Navigator, local 3D views and HUD must be evaluated at an explicit LOOM game/query/playback epoch.

The target rule is:

```text
state(entity, t) → authoritative position + velocity + frame + provenance
```

not a static placement attached to the body name.

At any supported epoch `t`:

- celestial bodies resolve from ephemeris/spatial authority;
- orbital stations resolve from their governed orbital/spatial definitions;
- surface facilities resolve from body-fixed geographic coordinates transformed through the body's authoritative orientation/rotation state;
- station transition points resolve from station state + local transition geometry;
- surface transition points resolve from body/site state + mission-derived approach geometry;
- Wayfarer/shuttle ordinary state resolves from Navigator trajectory or current local state;
- moving infrastructure uses the same epoch;
- HUD relative geometry uses the same epoch.

During accelerated playback, all of these advance against the same read-only playback cursor. Playback does not mutate the authoritative campaign clock.

## 14. Reference-frame discipline

The local-orbit, station and surface system must preserve explicit transforms between:

- canonical heliocentric/J2000-ecliptic or existing Navigator frame;
- body-centric inertial frame;
- body-fixed rotating frame;
- site-local/topocentric frame;
- station/local orbital frame;
- ship-local tactical/HUD frame.

Transforms belong in the shared spatial runtime/service layer. GIS, Navigator and HUD must not implement independent hidden orbital or geographic transforms.

## 15. Stage-F work added by this refinement

Stage F should now explicitly preserve and/or qualify the following bones before final acceptance:

1. system 3D, local-body 3D, station 3D and surface-site 3D are views of the same canonical spatial state;
2. nearby orbital stations can be rendered only from authoritative time-resolved state;
3. surface infrastructure requires authoritative body-fixed geographic coordinates plus elevation/reference-surface semantics where available;
4. endpoint contracts can carry station/orbit/surface-local state without assuming body center;
5. a station endpoint can resolve to `STATION_MATCH` plus a governed terminal rendezvous/transition point;
6. a surface endpoint can resolve to a governed deorbit/entry/descent/landing transition chain appropriate to the body and vehicle;
7. Navigator→HUD and HUD→Navigator transition states are explicit application concepts;
8. standard orbit intents and station/surface transition roles are governed vocabularies, with actual state derived by authoritative resolvers;
9. NASA/IDSS/JPL/NAIF conventions are the reference baseline where applicable, with mission-specific dynamics derived rather than replaced by arbitrary constants;
10. all ephemeris bodies, orbital stations and surface sites can be evaluated at arbitrary supported game/query/playback time;
11. route playback uses the same epoch for ship, bodies, stations, surface facilities and HUD state;
12. metric transit remains relational/non-occupancy;
13. qualification identifies whether current Sequence-B exposes both departure and arrival ordinary-space geometry rather than cosmetically inventing a second curve.

## 16. Implementation sequencing recommendation

Do not solve all local orbital, docking and landing mechanics inside the renderer.

Recommended order after the current 3D presentation work:

1. inventory existing orbital stations and current spatial/orbit data quality;
2. inventory all surface infrastructure and identify missing geographic coordinates/elevations;
3. inventory whether standard orbit, docking, entry/descent/landing or site-frame definitions already exist elsewhere in LOOM;
4. define typed standard-orbit / station-state / surface-site / transition-point contracts;
5. implement shared time-resolved orbital and body-fixed spatial resolvers;
6. implement shared NASA-derived transition-state generation for rendezvous, docking handoff, deorbit and surface approach;
7. qualify body/station/site positions and frame transforms numerically at known epochs;
8. expose local scene objects through the existing spatial service;
9. bind Navigator endpoint selection to station/orbit/surface transition states;
10. hand terminal rendezvous or landing-approach state into HUD/local flight;
11. only then add richer docking, proximity-operation and landing UX.

No current world/canon station orbit, surface coordinate, endpoint parameter, transition geometry or landing profile is to be replaced or invented merely to satisfy Stage-F visuals.
