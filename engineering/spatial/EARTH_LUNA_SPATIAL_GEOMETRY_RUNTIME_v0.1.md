# LOOM 2226 — Earth–Luna Spatial Definition & Geometry Runtime v0.1

**Status:** ACTIVE ENGINEERING / NON-CANON RUNTIME DESIGN  
**Scope:** Earth–Luna vertical slice for HUD/Navigator integration  
**Generated runtime DB:** `data/LOOM_2226_SPATIAL_GEOMETRY.sqlite3` (definition/geometry cache; never physical-state authority)

## 1. Purpose

Provide one deterministic runtime surface where HUD and Navigator can discover both:

1. WORLD-backed Earth/Luna infrastructure; and
2. standard operational orbit targets that exist independently of stations.

This layer stores definitions and operational/render geometry. It does not replace WORLD, MEDIA, celestial ephemeris, shared spatial-state services, or Navigator physics.

## 2. Governing alignment with GIS/Navigator

This runtime follows the governing GIS/Navigator convergence architecture:

```text
WORLD / CIVSTATE / campaign persistence
              |
              +---- target/facility definitions
              |
SPATIAL DEFINITION & GEOMETRY DB
              |
              +---- operational geometry / render assets
              |
SHARED SPATIAL + NAVIGATION DOMAIN SERVICES
              |
              +---- authoritative epoch-dependent SpatialState
              +---- route / maneuver / arrival contracts
              |
GIS / HUD
```

Rules:

1. Navigation physics, ephemeris, propagation, route planning and execution remain authoritative domain services.
2. The geometry database MUST NOT store or become authority for propagated epoch-dependent position or velocity.
3. Standard-orbit rows are definitions/targets. Their `element_epoch_utc` anchors the declared element/reference definition; it is not a cached current state.
4. HUD/GIS has zero physics authority and renders typed service outputs.
5. GLB/GLTF assets, symbolic rings and meshes have zero navigation authority unless separately registered as operational geometry for a specific purpose.
6. There is no second Earth/Moon GM, ephemeris or orbital propagator in this database or builder.

The generated DB carries machine-readable metadata declaring:

- `database_role = DEFINITION_AND_OPERATIONAL_GEOMETRY`
- `state_authority = SHARED_SPATIAL_NAVIGATION_SERVICES`
- `propagated_state_storage = FORBIDDEN`

## 3. Authority split

- `data/LOOM_2226.sqlite3` — identity, facility facts, existing location/orbit model definitions and world authority.
- `geometry/earth_luna_spatial_geometry_seed.sql` — reviewable runtime schema plus explicitly non-facility standard-orbit definitions.
- `data/LOOM_2226_SPATIAL_GEOMETRY.sqlite3` — generated target-definition, operational-geometry and HUD metadata cache.
- MEDIA — approved reference imagery keyed through existing WORLD spatial entity IDs.
- shared spatial state/orbit services — authoritative epoch-dependent physical state.
- Navigator — authoritative navigation planning/execution using shared state contracts.
- HUD/GIS — consumer/presentation surface; owns neither physics nor world state.

The generated SQLite may later carry embedded GLB/GLTF BLOBs, but the preferred default is metadata + URI + SHA-256 so large assets remain replaceable and independently distributable.

## 4. First-class spatial objects

### Facilities

Facilities preserve the WORLD `entity_id` as `object_id`. No alias catalog or invented station naming is introduced.

### Standard orbits

Standard orbits are first-class targetable objects but are **not infrastructure**. They model useful operational target states such as Earth parking orbit, polar orbit, MEO/GEO references, lunar parking orbit and lunar polar orbit even when no station is present.

V0.1 seeded targets:

- `ORB-EA-VLEO-250`
- `ORB-EA-LEO-400`
- `ORB-EA-POLAR-500`
- `ORB-EA-HLEO-1500`
- `ORB-EA-MEO-20200`
- `ORB-EA-GEO-REF`
- `ORB-LU-LLO-100`
- `ORB-LU-POLAR-100`
- `ORB-LU-HIGH-1000`

These are engineering navigation references, not canon infrastructure and not claims of persistent traffic occupancy.

Resolving any of these at time `T` requires the shared spatial/navigation state service. The geometry database alone cannot answer "where is this target now?"

## 5. Geometry model

The runtime schema separates render and operational authority.

`geometry_assets` can hold:

- `HUD_SYMBOLIC` — lightweight marker/ring geometry;
- `RENDER_LOW` — distant/low-LOD render model;
- `RENDER_HIGH` — close visual model;
- future collision/navigation geometry only when explicitly registered with the correct operational authority.

A visually attractive GLB is never navigation authority merely because it exists.

Operational geometry is represented separately through:

- `local_frames`
- `operational_interfaces`
- `approach_corridors`
- `keepout_volumes`
- `visual_profiles`

This supports future docking ports, berths, approach axes, exclusion zones and traffic holding geometry without contaminating WORLD or replacing Navigator physics.

Local coordinates such as interface `x_m/y_m/z_m` are geometry in an object-local frame. They are not inertial world positions.

## 6. HUD/Navigator consumer contract direction

The intended flow for a facility is:

```text
WORLD identity/facts
       +
SPATIAL_GEOMETRY definitions/operational geometry
       +
shared authoritative SpatialState @ epoch
       +
MEDIA reference asset
       |
       v
canonical typed HUD/Navigator object
```

For a standard orbit:

```text
standard-orbit definition
       |
       v
shared spatial-state service
       |
       +---- position + velocity + frame @ requested epoch
       |
       v
Navigator planning / HUD rendering
```

HUD should be able to list and select standard orbits as well as physical facilities. Orbit rings are renderable target geometry; facilities can progressively acquire procedural or GLB models. Neither representation supplies propagated physical state.

## 7. Builder

Build locally with:

```bash
python -m loom.spatial.geometry_catalog \
  --world data/LOOM_2226.sqlite3 \
  --seed geometry/earth_luna_spatial_geometry_seed.sql \
  --output data/LOOM_2226_SPATIAL_GEOMETRY.sqlite3
```

The output database is reproducible and should not be hand-edited as source authority.

## 8. Qualification

The schema has an automated authority-firewall test which verifies that:

- the database declares itself `DEFINITION_AND_OPERATIONAL_GEOMETRY`;
- the shared spatial/navigation services are declared physical-state authority;
- propagated state storage is declared forbidden; and
- geometry/runtime tables contain no inertial position/velocity state columns.

Exact-head GitHub Actions unit regression passed at commit `0cc936342113cae1d0ca1bd5f1a3476593848fa2`.

## 9. Next detail pass

For the 31 existing Earth–Luna facilities:

1. adapt/reference existing WORLD `entity_location_models` and `orbit_geometry_models` through shared state resolution rather than copying resolved state into the geometry DB;
2. register approved MEDIA hero linkage;
3. derive/register the local/body/orbital frame required by each facility;
4. add facility-scale envelopes and symbolic/procedural geometry;
5. add GLB assets where useful;
6. define docking/berthing interfaces only where supported by world/engineering detail;
7. define approach/keep-out geometry separately from render geometry;
8. expose the joined object through the shared typed HUD/Navigator resolver.

Body-fixed Earth/Moon transforms and CR3BP-family state resolution remain physics/runtime capabilities, not geometry-database inventions.
