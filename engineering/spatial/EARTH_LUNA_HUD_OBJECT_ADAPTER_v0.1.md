# LOOM 2226 — Earth–Luna Thin HUD Spatial Object Adapter v0.1

Status: ENGINEERING / NON-CANON / CHILD OF HUD-NAVIGATOR WORKSTREAM

## Purpose

Expose existing Earth–Luna infrastructure to HUD/GIS through one thin, governed object contract without opening detailed station-design work.

The governing v0.1 detail policy is:

- `detail_scope = THIN_WORLD_BACKED_V1`
- `detail_policy = STATION_COMPLEXITY_DEFERRED`

Station berth graphs, interior topology, exact physical scale, detailed throughput, staffing, docking trees and richer operational geometry remain deferred until separately earned.

## Authority boundary

The adapter joins existing authorities; it creates none:

- WORLD SQLite owns facility identity, classification, authorities, engineering classification, transport role and location/orbit model lineage.
- Shared spatial/navigation services own epoch-dependent physical state.
- SPATIAL_GEOMETRY owns non-state geometry/render/operational references.
- MEDIA/WORLD knowledge linkage supplies approved current HERO presentation media.
- HUD/GIS consumes the joined object and owns no orbital physics or facility lore.

## Contract

`LOOM_HUD_SPATIAL_OBJECT_V1` exposes, where present:

- canonical `entity_id` and display name;
- parent/system/facility classification;
- civil, administrative and security authority;
- commercial/institutional classification;
- WORLD placement/orbit-model metadata and epistemic/navigation-grade status;
- existing `infrastructure_engineering_profiles` row without filling null quantitative fields;
- existing `entity_transport_profiles` row;
- approved current HERO media key and its boundary note;
- SPATIAL_GEOMETRY symbolic/render references;
- shared `SpatialState` only when `resolve_object(entity_id, epoch)` is invoked.

`describe_object()` does not require the target to be physically resolvable. This permits surface/rotating-frame facilities to appear as governed selectable objects before their specialized state resolvers are qualified.

## Anti-fabrication rule

Null WORLD engineering values remain null. In particular, the adapter must not infer or manufacture exact station scale, mass, pressurized volume, berth count, throughput or staffing merely because a HERO image or structural archetype exists.

For `EAR-O01`, the approved media boundary explicitly states that exact physical scale, berth count, annual throughput, staffing and operating economics are not promoted by that record. The HUD adapter preserves that limitation.

## Current vertical slice

`EAR-O01` can now be described and resolved as one HUD object containing:

- LEO Atlantic Exchange identity;
- `ORBITAL_HABITAT_PORT` classification;
- authority/commercial/institutional context;
- `HABITAT_PORT` engineering archetype with unearned quantitative fields still null;
- EXTREME / PRIMARY GATE transport classification;
- approved HERO media reference;
- symbolic geometry reference;
- the exact shared WORLD-backed conventional-orbit `SpatialState` for the requested epoch.

No separate HUD coordinate calculation is introduced.

## Deferred station complexity

The following are intentionally out of v0.1 scope:

- detailed GLB station design;
- local docking/berthing topology;
- internal station geometry;
- detailed approach corridors and keep-out volumes;
- inferred dimensions/masses/volumes;
- inferred capacity/throughput/staffing;
- station-specific collision/navigation meshes.

The existing SPATIAL_GEOMETRY schema retains extension points for these later without forcing them into the current HUD contract.

## Qualification

`tests/test_hud_spatial_objects.py` verifies:

- thin contract identity and explicit deferral policy;
- WORLD engineering/transport and approved HERO joins;
- preservation of null quantitative station detail;
- symbolic geometry linkage;
- exact reuse of the injected shared `SpatialState`;
- metadata-only description for currently unresolved surface facilities;
- fail-closed unknown IDs.

These tests pass in the branch. Full stacked PR qualification may transiently reflect unrelated changes on the rapidly moving HUD base; those must not be repaired by introducing HUD ownership into this lane.
