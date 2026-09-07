# LOOM 2226 — Stage F 3D Navigator Rendering Bones

Date: 2026-09-07  
Status: **Stage-F implementation refinement — feature branch / NON-CANON until governed merge**

## Purpose

Refine Stage F so the existing Solar GIS becomes the foundation for a physically honest 3D Navigator/HUD renderer, without reopening Navigator physics or campaign authority.

The player-facing product remains the existing Solar GIS. The standalone `/3d` page remains a qualification surface only.

## Core rule

> **One playback epoch drives the whole rendered scene.**

For any playback cursor epoch `t`:

- Wayfarer ordinary-space state comes from the authoritative Navigator trajectory at `t`.
- Celestial bodies resolve from ephemeris/spatial authority at the same `t`.
- Moving infrastructure resolves from its authoritative parent/orbital state at the same `t`.
- HUD telemetry resolves from the same trajectory/state epoch.
- Playback/query time is read-only and must not mutate campaign time.

## 3D scene bones

Stage F should preserve physical coordinates separately from render scale and prepare the Solar GIS scene for actual 3D render objects:

- celestial bodies may be rendered as 3D meshes/spheres using authoritative ephemeris positions;
- Wayfarer may be rendered as a 3D ship object using authoritative spatial state;
- render-scale exaggeration is allowed for usability, but must never alter the underlying physical state;
- camera movement, projection and object rendering are presentation concerns only.

A future 3D asset must not become a source of position, velocity, orientation, physics or game time.

## Ordinary-space trajectory rendering

Where Navigator provides ordinary-space samples, render them exactly as authoritative J2000-ecliptic position/velocity state.

The renderer may use authoritative velocity vectors to orient a ship model or draw tangent/vector instrumentation.

Do not infer or manufacture a full XYZ acceleration vector from scalar acceleration telemetry.

Torch animation may be attached to the Wayfarer render object when the authoritative propulsion/torch state indicates an active burn.

## Metric-phase rendering

Metric transit remains relational, not ordinary-space occupancy.

At the last legitimate ordinary-space state:

1. render the ordinary ship through the real departure/staging geometry;
2. transition the visual representation into a metric-state presentation;
3. advance relational progress and metric telemetry without assigning a fabricated XYZ trajectory;
4. continue advancing all ephemeris bodies with playback time;
5. restore ordinary-space rendering only when Navigator again supplies a legitimate ordinary state.

A dashed or other relational connection may communicate source/destination relationship, but must be explicitly non-occupancy semantics.

## Endpoint / orbital-state bones

Stage F should not assume that a ship located "at Mars", "at Ceres", or at another body is physically located at that body's center.

The architecture should permit a navigation endpoint to resolve to a full six-dimensional departure/arrival state:

- position `(x, y, z)`;
- velocity `(vx, vy, vz)`;
- epoch;
- explicit reference frame;
- provenance / navigation grade.

Initial endpoint intent vocabulary should be compatible with:

- `BODY_DEFAULT` — current simple body-level behavior where no more specific local state exists;
- `STATION_MATCH` — match an orbital facility/station's authoritative orbital state for rendezvous/docking;
- `LOW_CIRCULAR` — standard low circular parking orbit;
- `HIGH_CIRCULAR` — higher staging/parking orbit;
- `EQUATORIAL_CIRCULAR`;
- `POLAR_CIRCULAR`;
- `ELLIPTICAL_TRANSFER` / phasing-style orbit where required.

These are endpoint-state generation choices, not renderer-owned orbital physics.

For docking/rendezvous, matching the station's actual orbital state is preferred over merely matching altitude.

Stage F does **not** need to implement a general orbital mission-design package. It only needs to avoid hard-wiring the renderer or route contracts to "body center = ship state" so a later orbital endpoint resolver can supply the correct state without redesigning the UI.

## Departure / arrival local detail

Default system-scale route presentation should stay simple.

When local authoritative geometry exists, the renderer should be able to reveal it by zoom/drill-down:

- departure orbit / station-relative state;
- local velocity vector;
- torch departure arc;
- metric establishment boundary;
- emergence / terminal ordinary-space geometry;
- arrival/capture/station-match geometry.

This is progressive disclosure, not a requirement to show detailed orbital mechanics at all times.

## Ephemeris playback requirement

During `PLAY ROUTE`, celestial bodies and moving infrastructure must advance with the same simulated playback clock as the ship.

A route played in accelerated real time therefore shows the solar system advancing through the corresponding simulated interval.

For a Mars → Ceres example, Mars should recede from its departure-time position while Ceres advances toward its arrival/intercept position. The route should not be animated against a frozen departure-epoch solar system.

## Stage-F implementation boundary

Stage F remains a representation/presentation phase.

It must not:

- change Navigator trajectory mathematics;
- invent ordinary-space state during metric transit;
- mutate campaign state during preview/playback;
- move campaign authority into GIS/HUD;
- replace the existing Phase-6 execution chain;
- make standalone `/3d` the player-facing Navigator.

## Stage-F acceptance additions

Before Stage F can be called complete:

1. `3D ROUTE` must produce a meaningfully 3D route-focused presentation in the existing Solar GIS, not merely a cosmetic tilt.
2. Ordinary Navigator XYZ geometry must remain authoritative and visibly respond to camera rotation.
3. Metric phases must remain visibly relational/non-occupancy.
4. Playback must use a single read-only playback epoch for ship, ephemeris scene and HUD telemetry.
5. The design must preserve a future path to 3D body meshes and a 3D Wayfarer model without changing physical authority.
6. The design must not hard-wire ship endpoints to celestial-body centers; a future orbital/station endpoint resolver must be able to provide a full six-dimensional state.
7. Add a numerical qualification check showing origin/destination body states and Navigator endpoint geometry use compatible epochs/reference frames.
8. Pixel physical acceptance and Windows semantic/usability acceptance remain required.
