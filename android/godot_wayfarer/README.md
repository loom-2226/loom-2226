# LOOM 2226 — Wayfarer Godot Android GLB Smoke Test

**Workstream:** `workstream/wayfarer-3d`  
**Status:** EXPERIMENTAL / NON-GOVERNING  
**Purpose:** prove that deterministic LOOM Wayfarer geometry can move from SQL/JSON into a native Android-capable 3D editor/runtime without changing geometry authority.

## Authority chain

`geometry/wayfarer_geometry_seed.sql` → `src/wayfarer_geometry.py` → `geometry/wayfarer_geometry.json` → `src/wayfarer_glb_exporter.py` → `wayfarer.glb` → Godot Android.

The `.glb` file is an interchange/render derivative only. It is not canonical geometry authority. AI-generated meshes, Godot edits, and Blender edits must not silently flow backward into canon.

## Pixel preparation

From the repository root in Termux:

```bash
python src/wayfarer_geometry_server.py --build-only
python src/wayfarer_glb_exporter.py \
  --input geometry/wayfarer_geometry.json \
  --output android/godot_wayfarer/wayfarer.glb \
  --launch DOCKED \
  --radiators STOWED
```

The generated `wayfarer.glb` is intentionally git-ignored.

For a deployed-radiator test:

```bash
python src/wayfarer_glb_exporter.py \
  --input geometry/wayfarer_geometry.json \
  --output android/godot_wayfarer/wayfarer.glb \
  --launch DOCKED \
  --radiators DEPLOYED
```

## Godot Android test

1. Install the official Godot Android editor.
2. In Godot, import/open the folder `android/godot_wayfarer` from the Pixel checkout.
3. Let Godot import `wayfarer.glb`.
4. Run `main.tscn` / the project.
5. Confirm the ship loads at metre scale, the long axis is X, LOOM +Z launch side appears as Godot +Y, and touch drag orbits the camera.

This project is deliberately small. It is a renderer/import test, not yet the replacement for the Three.js Geometry Lab.

## Coordinate mapping

LOOM uses `(X,Y,Z)` where X is bow-to-aft, Y is transverse, and +Z is the launch-bay side. The exporter writes glTF coordinates as:

`(X_gltf, Y_gltf, Z_gltf) = (X_LOOM, Z_LOOM, -Y_LOOM)`

This is a right-handed mapping, preserves distances, keeps the ship long axis on X, and makes the launch side visually up in Godot.

## AI-seeded geometry policy

Future AI-generated 3D should enter through a quarantine layer, never as authority. A generated `.glb` may be loaded beside the deterministic Wayfarer as a visual proposal. Any accepted dimensions/topology must be explicitly measured, reviewed, parameterized, and written back to the LOOM geometry model before becoming design baseline or canon candidate.

Recommended first AI trials: launch-bay door/exterior treatment or one radiator mechanism. Do not start with a whole-ship AI replacement.
