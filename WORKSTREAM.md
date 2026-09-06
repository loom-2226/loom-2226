# LOOM Workstream — Wayfarer 3D

**Branch:** `workstream/wayfarer-3d`

## Purpose

This branch is the isolated Wayfarer 3D / physical-geometry workstream.

Primary scope:
- deterministic Wayfarer geometry and packaging
- Pixel / Android engineering inspection
- Three.js Geometry Lab
- GLB / glTF export
- Godot Android rendering and interaction
- Blender build/export support
- AI-seeded component experiments subject to deterministic validation
- Wayfarer canon-candidate physical specification and engineering notes

## Out of scope

Do not use this branch as the active workspace for:
- Navigator / GIS development
- ephemeris pipeline changes
- campaign/runtime logic
- Solar GIS / HUD work unrelated to Wayfarer 3D
- unrelated canon propagation or simulation work

Those streams may be referenced as dependencies, but their active development belongs on their own branches/checkouts.

## Pixel checkout

Canonical local checkout name:

`/storage/emulated/0/Documents/LOOM_GIT_3D`

This checkout should remain permanently on `workstream/wayfarer-3d` during active work.

Routine update:

```bash
cd ~/storage/shared/Documents/LOOM_GIT_3D
git pull --ff-only
```

Do not switch this checkout to Navigator/GIS branches. Do not use it as a general-purpose branch-switching workspace.

## Geometry authority

The authoritative path remains:

`SQL / parameter records -> deterministic geometry compiler -> geometry JSON -> GLB / Three.js / Godot / Blender`

Generated or AI-authored meshes are proposals only. They do not become engineering truth until reconciled back to governed parameters and validated.

## Integration rule

Integration to `main` is deliberate and reviewed. Wayfarer 3D changes should not be mixed into Navigator/GIS commits merely because the same repository is used.
