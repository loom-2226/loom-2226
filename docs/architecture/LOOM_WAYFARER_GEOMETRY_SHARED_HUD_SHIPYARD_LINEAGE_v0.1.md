# LOOM 2226 — Wayfarer Geometry Shared HUD / Shipyard Lineage v0.1

**Status:** CROSS-WORKSTREAM PROVENANCE / ARCHITECTURE NOTE  
**Date:** 2026-09-15  
**Authority:** descriptive lineage only; does not promote generated geometry or change canon/runtime authority

## 1. Purpose

Preserve the fact that the deterministic Wayfarer geometry stack is a shared upstream asset used across multiple LOOM workstreams, especially the HUD/renderer lane and the Computational Shipyard / Wayfarer 3D lane, and is now also consumed by Experience One qualification as a conservative committed-component material envelope.

This note prevents the geometry lineage from being rediscovered or forked into competing ship models.

## 2. Governing and deterministic source chain

Authority order for the shared Wayfarer geometry remains:

1. `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
2. `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`
3. provenance-tagged deterministic geometry inputs in `geometry/wayfarer_geometry_seed.sql`
4. deterministic compiler in `src/wayfarer_geometry.py`
5. generated `LOOM.Wayfarer.Geometry` JSON and downstream presentation/build products
6. Three.js, Blender, GLB, screenshots, renders and other generated representations as derivatives unless separately governed

The working pipeline is:

```text
Canon / approved engineering constraints
  -> geometry/wayfarer_geometry_seed.sql
  -> src/wayfarer_geometry.py
  -> LOOM.Wayfarer.Geometry JSON
  -> HUD / Solar GIS / Three.js presentation
  -> Blender / Computational Shipyard / GLB presentation-build derivatives
```

Generated meshes, GLBs, JSON exports and renders do not silently become ship canon or replace the SQL/Python source chain.

## 3. Shared geometry content

The deterministic model carries provenance-tagged parameters and component geometry for the current Wayfarer reference configuration, including:

- canonical 57 m overall length and 9 m nominal main-body diameter;
- forward pressure hull working envelope;
- four major tanks in quadrature;
- four principal longerons;
- central technical core;
- integrated planetary-launch bay and docked launch working envelope;
- four radiator root assemblies with intentionally OPEN detailed panel geometry;
- propulsion shadow-shield working envelope;
- reactor/torch working envelope;
- magnetic-nozzle working envelope;
- docking-collar placeholder geometry;
- current mass states and center-of-mass calculation inputs;
- explicit runtime vocabularies for launch, radiator, docking and torch states;
- provenance classes including `CANON`, `DESIGN_BASELINE`, `DERIVED`, `LEGACY_COMPATIBLE`, `VISUAL_REFERENCE`, `OPEN`, and `CANON_MASS_DESIGN_POSITION`.

The Phase-3 approximately 1,900 m² Loom controlled-boundary calibration is a regression surrogate only. It is not a literal translation-domain boundary solution and must not be used as one.

## 4. HUD lineage

Known HUD branch family includes:

- `planning/navigator-gis-hud-next-phase-2026-09-06`
- `feature/hud-local-flight-contract-shell-v0.1-2026-09-09`
- `feature/hud-wayfarer-attitude-envelope-v0.1-2026-09-11`

The Wayfarer-attitude branch was verified at:

`8b1637e3e6ff7ebb718aa3dfb7b3310be3b6ac2f`

HUD/rendering may consume generated geometry, semantic GLB and presentation metadata, but browser/renderer geometry has zero authority to recalculate mass properties, campaign state, navigation state, ephemerides, actuator truth, collision truth, or metric-domain physics unless separately governed.

The private research repository `loom-2226/loom-research-lab` contains the active non-runtime project `NAV_GIS_HUD_RENDERER_ACCELERATION`. Its work plan explicitly identifies semantic GLB / Shipyard authority work as an upstream runtime asset and R3 evaluates the same GLB as a common visualization format for HUD and Solar GIS. Promotion from that research project requires a separate upstream decision and qualification.

## 5. Computational Shipyard / shipbuilding lineage

Known Wayfarer shipbuilding branch family includes:

- `workstream/wayfarer-3d`
- `archive/pre-governance-2026-09-07-wayfarer-3d`
- `research/computational-shipyard-wayfarer-vertical-slice-2026-09-08`
- `research/computational-shipyard-wayfarer-vertical-slice-2026-09-08-ci`
- `research/physical-design-synthesis-wayfarer-s1-2026-09-08`
- `research/physical-design-synthesis-wayfarer-s1-2026-09-08-ci`
- `research/physical-design-synthesis-wayfarer-s2-2026-09-08`
- `research/physical-design-synthesis-wayfarer-s2-2026-09-08-ci`
- `engineering/wayfarer-flight-system-qualification-v1`

The Computational Shipyard Wayfarer vertical-slice branch was verified at:

`dc129ebb5999641c85138c3f263ec78b7e3495c5`

Shipbuilding/CAD/Blender work must regenerate from or remain traceable to the deterministic geometry source chain rather than hand-promoting a mesh. If packaging work discovers a real physical closure conflict, it must raise an engineering/canon finding rather than hiding the conflict in a model.

## 6. Experience One reuse

E1 PR #182, `E1: bind deterministic Wayfarer component geometry envelope`, deliberately reuses the same geometry authority instead of inventing an E1-specific ship geometry.

E1 use is narrow:

- launch state `DOCKED` includes the planetary launch;
- external attachment state `FREE` invents no external object;
- deployable state `STOWED` retains OPEN radiator geometry only as conservative containment bounds;
- the deterministic material/component envelope may be used for containment testing;
- the generated GLB is derivative confirmation only;
- the material envelope is not the relational/metric translation-domain boundary.

This closes only the `committed_component_geometry_envelope` input. It does not certify the translation-domain boundary, domain membership, domain size, local/causal compatibility, lattice coherence or overall geometric admissibility.

## 7. Shared invalidation rule

A material change to governing Wayfarer canon or the deterministic geometry inputs/compiler must trigger impact review for all consumers that depend on the changed geometry, including as applicable:

- Wayfarer 3D / Computational Shipyard outputs;
- semantic GLB products;
- HUD / Solar GIS presentation and selection geometry;
- local-flight attitude/envelope presentation;
- E1 committed-component containment evidence;
- later interference, sweep-volume, collision or packaging qualification.

A downstream renderer or mesh change does not flow authority upstream unless separately reviewed and promoted.

## 8. Authority firewall

This document records provenance and reuse. It does not:

- promote DESIGN_BASELINE or OPEN values to canon;
- certify exact 208-node placement;
- certify a translation-domain field boundary;
- turn GLB mesh geometry into physical authority;
- alter Navigator, campaign or runtime state;
- grant browser or LLM calculation authority.

The intended architecture is one deterministic ship geometry lineage, many governed consumers.
