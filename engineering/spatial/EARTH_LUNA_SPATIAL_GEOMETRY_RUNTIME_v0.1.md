# LOOM 2226 — Earth–Luna Spatial Geometry Runtime v0.1

**Status:** ACTIVE ENGINEERING / NON-CANON RUNTIME DESIGN  
**Scope:** Earth–Luna vertical slice for HUD/Navigator integration  
**Generated runtime DB:** `data/LOOM_2226_SPATIAL_GEOMETRY.sqlite3` (not source authority)

## 1. Purpose

Provide one deterministic runtime surface where HUD and Navigator can discover both:

1. WORLD-backed Earth/Luna infrastructure; and
2. standard operational orbit targets that exist independently of stations.

This layer does not replace WORLD, MEDIA, celestial ephemeris, or Navigator physics.

## 2. Authority split

- `data/LOOM_2226.sqlite3` — identity, facility facts, existing location/orbit models and world authority.
- `geometry/earth_luna_spatial_geometry_seed.sql` — reviewable runtime schema plus explicitly non-facility standard-orbit references.
- `data/LOOM_2226_SPATIAL_GEOMETRY.sqlite3` — generated HUD/geometry/runtime cache.
- MEDIA — approved reference imagery keyed through existing WORLD spatial entity IDs.
- spatial state/orbit services — epoch-dependent physical state.
- HUD/Navigator — consumers; neither owns world coordinates or geometry truth.

The generated SQLite may later carry embedded GLB/GLTF BLOBs, but the preferred default is metadata + URI + SHA-256 so large assets remain replaceable and independently distributable.

## 3. First-class spatial objects

### Facilities

Facilities preserve the WORLD `entity_id` as `object_id`. No alias catalog or invented station naming is introduced.

### Standard orbits

Standard orbits are first-class targetable objects but are **not infrastructure**. They model useful operational states such as Earth parking orbit, polar orbit, MEO/GEO references, lunar parking orbit and lunar polar orbit even when no station is present.

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

## 4. Geometry model

The runtime schema separates render and operational authority.

`geometry_assets` can hold:

- `HUD_SYMBOLIC` — lightweight marker/ring geometry;
- `RENDER_LOW` — distant/low-LOD render model;
- `RENDER_HIGH` — close visual model;
- future navigation/collision geometry registered explicitly with `navigation_authority=1`.

A visually attractive GLB is never navigation authority merely because it exists.

Operational geometry is represented separately through:

- `local_frames`
- `operational_interfaces`
- `approach_corridors`
- `keepout_volumes`
- `visual_profiles`

This supports future docking ports, berths, approach axes, exclusion zones and traffic holding geometry without contaminating WORLD.

## 5. HUD contract direction

The intended consumer flow is:

```text
WORLD identity/facts
       +
SPATIAL_GEOMETRY runtime object/geometry metadata
       +
shared epoch-dependent SpatialState
       +
MEDIA reference asset
       |
       v
HUD resolved object
```

HUD should be able to list and select standard orbits as well as physical facilities. Orbit rings are renderable target geometry; facilities can progressively acquire procedural or GLB models.

## 6. Builder

Build locally with:

```bash
python -m loom.spatial.geometry_catalog \
  --world data/LOOM_2226.sqlite3 \
  --seed geometry/earth_luna_spatial_geometry_seed.sql \
  --output data/LOOM_2226_SPATIAL_GEOMETRY.sqlite3
```

The output database is reproducible and should not be hand-edited as source authority.

## 7. Next detail pass

For the 31 existing Earth–Luna facilities:

1. ingest/reference existing WORLD `entity_location_models` and `orbit_geometry_models` rather than duplicating them;
2. register approved MEDIA hero linkage;
3. derive the authoritative local/body/orbital frame required by each facility;
4. add facility-scale envelopes and symbolic/procedural geometry;
5. add GLB assets where useful;
6. define docking/berthing interfaces only where supported by world/engineering detail;
7. define approach/keep-out geometry separately from render geometry;
8. expose the joined object through the shared HUD/Navigator resolver.

Body-fixed Earth/Moon transforms and CR3BP-family state resolution remain physics/runtime capabilities, not geometry-database inventions.
