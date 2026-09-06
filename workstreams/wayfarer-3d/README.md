# LOOM 2226 — Wayfarer 3D Workstream

**Branch:** `workstream/wayfarer-3d`  
**Status:** isolated active engineering workstream  
**Scope:** Wayfarer physical geometry, ship packaging, Android/Pixel 3D inspection, AI-seeded 3D generation, Blender export/builder, and canon-candidate ship specification only.

## Isolation rule

This branch is intentionally isolated from concurrent LOOM Navigator/GIS, Solar GIS, ephemeris, campaign-runtime, and other active workstreams. Changes in this workstream must not modify Navigator/GIS behavior, data schemas, runtime state, map rendering, ephemeris logic, campaign logic, or release artifacts unless a later integration step is explicitly approved.

The branch was cut from `main` on 2026-09-06 after Geometry Lab v0.2 and the Wayfarer project-state/canon-candidate documentation had been committed. Existing Navigator/GIS files remain visible because this is a branch of the same repository, but they are outside this workstream's change surface.

## Owned files and paths

Primary active files:

- `src/wayfarer_geometry.py`
- `src/wayfarer_geometry_server.py`
- `src/wayfarer_blender_builder.py`
- `geometry/wayfarer_geometry_seed.sql`
- `web/index.html`
- `web/viewer.js`
- `tests/test_wayfarer_geometry.py`
- `tests/test_wayfarer_blender_builder.py`
- `engineering/current/LOOM_2226_Wayfarer_3D_Geometry_and_Physical_Packaging_Plan_v0.1.md`
- `engineering/current/LOOM_2226_Wayfarer_Phase_3_Implementation_v0.1.md`
- `engineering/current/LOOM_2226_Wayfarer_Project_State_and_Pixel_Handoff_v0.2.md`
- `engineering/current/LOOM_2226_Wayfarer_Canon_Candidate_Specification_v0.1.md`
- `manifests/LOOM_2226_Wayfarer_Project_File_Manifest_2026-09-06.md`
- `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md` only when explicitly performing canon integration.

## Current milestone

Pixel Geometry Lab v0.2 is validated in Chrome/Android via local Termux server. It supports:

- deterministic geometry generated from SQL parameters;
- launch DOCKED/ABSENT state;
- radiator STOWED/DEPLOYED state;
- CUTAWAY, ZONES, CoM and OPEN-geometry overlays;
- engineering component metadata/provenance;
- current dry/wet mass and CoM display;
- classic Three.js local cache for Android compatibility;
- Blender Python builder using the same deterministic geometry payload.

Current screenshot-validated docked state: 1,158.5 t wet, 858.5 t dry, wet CoM x approximately 26.68 m.

## Geometry authority

`geometry/wayfarer_geometry_seed.sql` -> `src/wayfarer_geometry.py` -> `geometry/wayfarer_geometry.json` -> renderer(s).

Renderer output is never the geometry authority. AI-generated imagery or meshes are visual proposals unless converted into reviewed parameterized geometry and assigned explicit provenance.

## Next-step priorities

1. Preserve the existing Pixel engineering viewer as the reference inspection client.
2. Evaluate a richer Android-capable renderer/editor that can ingest glTF/GLB and be driven by AI-generated structured geometry.
3. Add a formal export adapter from Wayfarer geometry JSON to glTF/GLB so multiple renderers share one model transport format.
4. Refine physical geometry in small reviewed blocks: hull/armor, tank endcaps, launch-bay blister/doors, thrust cage, nozzle, radiator mechanisms.
5. Keep all newly proposed dimensions tagged DESIGN_BASELINE or OPEN until canon review.
6. Merge to `main` only through an explicit integration decision after tests and visual review.

## Pixel branch workflow

```bash
cd ~/storage/shared/Documents/LOOM_GIT
git fetch
git switch workstream/wayfarer-3d
git pull
python src/wayfarer_geometry_server.py
```

Return to the general LOOM baseline with:

```bash
git switch main
git pull
```

## Integration boundary

Navigator/GIS work should continue independently on `main` or its own dedicated branch. This workstream may eventually provide ship-state or geometry outputs to Navigator, but no direct coupling should be introduced until an explicit adapter contract is designed.
