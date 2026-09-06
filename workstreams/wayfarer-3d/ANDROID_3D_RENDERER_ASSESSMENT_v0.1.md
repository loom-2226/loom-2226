# LOOM 2226 — Android 3D Renderer Assessment v0.1

**Workstream:** `workstream/wayfarer-3d`  
**Status:** engineering assessment / non-governing  
**Date:** 2026-09-06

## Goal

Identify a richer 3D rendering/editing path that runs on Android and can consume AI-generated or AI-assisted geometry without displacing LOOM's deterministic ship-geometry authority.

## Architectural requirement

AI may propose meshes, surface detail, materials, panelization, or visual variants, but authoritative dimensions and system placement remain parameter-driven. The preferred interchange format should therefore be glTF/GLB generated from LOOM geometry JSON, with AI-generated meshes used as visual/reference layers or reviewed replacements for explicitly OPEN geometry.

## Candidates

### 1. Godot 4 Android editor — strongest candidate for interactive Android-native work

Godot provides an official Android editor and can create/develop 2D and 3D projects directly on Android. The Android editor remains early-access/experimental and the phone UX is not fully optimized; keyboard and mouse are recommended. Godot's Mobile or Compatibility renderer is preferred on Android rather than Forward+ for this workstream.

Strengths for LOOM:
- genuine Android editor, not just a viewer;
- can host interactive engineering controls, overlays, animation and state changes;
- imports standard 3D asset formats and can be scripted;
- can eventually export a dedicated Wayfarer inspection APK;
- can coexist with the current Termux/Git workflow.

Risks:
- editor UX on a Pixel-sized screen may be awkward;
- project complexity and asset import behavior need a real-device spike before adoption;
- do not migrate the geometry authority into Godot scene files.

### 2. Three.js / PWA — retain as reference engineering viewer

The existing Pixel Geometry Lab is already proven. Three.js supports glTF 2.0 via GLTFLoader and numerous modern material/compression extensions. It remains the lowest-friction browser-based inspection path and should not be discarded.

Recommended role:
- canonical lightweight engineering/debug viewer;
- fastest testing target for generated GLB;
- fallback if Godot editing is uncomfortable on phone.

### 3. Babylon.js — optional richer web-renderer spike

Babylon.js is a mature WebGL/WebGPU-capable 3D engine with strong glTF support and richer engine-level tooling than the current minimal Three.js viewer. It may be worth a later A/B test if Three.js becomes cumbersome, but migrating now would add risk without solving the primary Android editing requirement.

### 4. Google Filament — high-quality native renderer, not first choice for authoring

Filament is a physically based rendering engine designed for Android and includes glTF support. It is attractive for a future polished native inspection app but requires Android application development rather than offering an editor. It is therefore a later-stage rendering option, not the next workstream step.

### 5. Browser AI 3D generation — useful as a visual proposal source

Current browser AI 3D tools such as Meshy and Tripo can generate 3D models from text and/or images and export GLB. These are useful for creating visual proposals, surface-detail candidates, launch-bay components, radiator mechanisms, etc. They must not be treated as engineering geometry authority.

## Recommended architecture

```text
LOOM SQL parameters
    -> wayfarer_geometry.py
    -> wayfarer_geometry.json
    -> NEW deterministic glTF/GLB exporter
       -> Three.js Pixel viewer (reference)
       -> Godot Android project (interactive editor/viewer)
       -> Blender desktop builder/rendering
       -> optional AI-generated GLB visual proposal layer
```

AI-seeded mesh workflow:

```text
canon/design prompt + reference render
    -> AI 3D generator
    -> GLB candidate
    -> load beside deterministic LOOM geometry
    -> inspect fit / scale / interference
    -> accept only reviewed geometry or visual detail
    -> encode accepted dimensions back into SQL/parameter model
```

## Next implementation sequence

1. Add deterministic `wayfarer_geometry.json -> wayfarer.glb` export adapter with no AI dependency.
2. Load the same GLB back into the existing Three.js Pixel viewer and regression-check dimensions and component transforms.
3. Install Godot 4 Android editor on Pixel and perform a minimal GLB import/render spike using the generated Wayfarer GLB.
4. If Godot is usable on the phone, create a dedicated `android/godot-wayfarer/` project inside this workstream with orbit camera, component selection, state controls, cutaway/zones/CoM overlays.
5. Test one AI-seeded component as a non-authoritative visual layer, preferably the launch-bay exterior or radiator assembly rather than the whole ship.
6. Only after those tests decide whether Three.js remains primary, Godot becomes primary, or the two-client architecture remains permanent.

## Decision recommendation

Do not replace Three.js yet. Add GLB as the shared transport format and spike Godot Android. This preserves the working Pixel tool while opening a path to a genuine Android 3D editor and AI-assisted asset workflow.
