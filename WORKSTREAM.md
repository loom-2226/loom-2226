# LOOM Workstream — Navigator / GIS / HUD

**Branch:** `planning/navigator-gis-hud-next-phase-2026-09-06`

## Purpose

This branch is the isolated Navigator / GIS / HUD planning and implementation workstream.

Primary scope:
- Navigator / GIS behavior
- Solar GIS visualization
- HUD integration
- ephemeris and route/runtime plumbing required by Navigator
- deploy/sync workflow for the active Navigator build
- Navigator-specific tests and planning

## Out of scope

Do not use this branch as the active workspace for:
- Wayfarer 3D geometry refinement
- Godot Android rendering experiments
- Blender builder work
- AI-seeded Wayfarer component modeling
- Wayfarer physical-packaging experiments unless required strictly as an upstream interface contract

Those belong on `workstream/wayfarer-3d`.

## Pixel checkout

Canonical local checkout name:

`/storage/emulated/0/Documents/LOOM_GIT_NAV`

This checkout should remain permanently on `planning/navigator-gis-hud-next-phase-2026-09-06` during active work.

Routine update and device sync:

```bash
cd ~/storage/shared/Documents/LOOM_GIT_NAV
git pull --ff-only
python deploy/loom_dev_sync.py sync
```

Do not switch this checkout to Wayfarer 3D branches. Do not use it as a general-purpose branch-switching workspace.

## Integration rule

Integration to `main` is deliberate and reviewed. Navigator/GIS commits should not carry Wayfarer 3D editor/runtime changes merely because the same repository is used.
