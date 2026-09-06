# LOOM 2226 — Wayfarer Project File Manifest — 2026-09-06

**Status:** RECOVERY / SYNC MANIFEST  
**Purpose:** Identify the written, code, geometry, test and governing files needed to reconstruct the current Wayfarer engineering state from GitHub onto the Pixel or a desktop clone.

## Governing canon

- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`

## Current Wayfarer engineering documents

- `engineering/current/LOOM_2226_Wayfarer_3D_Geometry_and_Physical_Packaging_Plan_v0.1.md`
- `engineering/current/LOOM_2226_Wayfarer_Phase_3_Implementation_v0.1.md`
- `engineering/current/LOOM_2226_Wayfarer_Project_State_and_Pixel_Handoff_v0.2.md`
- `engineering/current/LOOM_2226_Wayfarer_Canon_Candidate_Specification_v0.1.md`

## Broader runtime/architecture documents

- `engineering/current/LOOM_2226_Integrated_HUD_Navigator_Architecture_and_Work_Plan_v1.0.md`
- `engineering/current/LOOM_2226_Integrated_Runtime_Architecture_and_Delivery_Workflow_v1.0.md`
- `docs/LOOM_PROJECT_HISTORY_ARCHITECTURE_PIXEL_BASELINE_2026-09-06.md`

## Geometry authority

- `geometry/wayfarer_geometry_seed.sql`
- `src/wayfarer_geometry.py`
- `src/wayfarer_geometry_server.py`

The runtime-generated `geometry/wayfarer_geometry.json` is derived output and may be regenerated from the seed/compiler rather than treated as hand-authored authority.

## Pixel viewer

- `web/index.html`
- `web/viewer.js`

Classic Three.js is cached locally by the server bootstrap under `web/three/three.min.js`; it is a runtime dependency/cache rather than LOOM-authored geometry.

## Blender builder

- `src/wayfarer_blender_builder.py`

## Tests

- `tests/test_wayfarer_geometry.py`
- `tests/test_wayfarer_blender_builder.py`
- `tests/test_loom_update.py`

## Legacy/reference source

- `canon/archive/LOOM_2226_Ship_Operations_Courier_Canon_Compendium_v1.0.md`

## Pixel synchronization

Current clone location:

`/storage/emulated/0/Documents/LOOM_GIT`

Termux path:

`~/storage/shared/Documents/LOOM_GIT`

Synchronize all committed files with:

```bash
cd ~/storage/shared/Documents/LOOM_GIT
git pull
```

Run Geometry Lab with:

```bash
python src/wayfarer_geometry_server.py
```

Then open:

`http://127.0.0.1:8000/`

## Recovery principle

If chat history is lost, the project should be recoverable from the governing canon, current engineering snapshot, canon-candidate specification, SQL parameter seed, geometry compiler, viewer, Blender builder and tests listed above.
