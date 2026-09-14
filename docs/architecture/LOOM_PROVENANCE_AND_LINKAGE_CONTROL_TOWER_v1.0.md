# LOOM Provenance and Linkage Control Tower v1.0

**Status:** GOVERNANCE / PROVENANCE / UPSTREAM CONTROL RECORD  
**Date:** 2026-09-15  
**Repository:** `loom-2226/loom-2226`

## Purpose

This document is the upstream control record for work that crosses repository, branch, research, engineering, HUD, Navigator/GIS, Computational Shipyard, and generated-asset boundaries.

Its job is not to duplicate every artifact. Its job is to make it possible to answer, later and unambiguously:

- where did this thing come from?
- which source is authoritative?
- which branches/projects consume it?
- which generated derivatives are stale after a change?
- what work must be revisited if an upstream source changes?
- where did we leave off in related efforts?

The machine-readable companion is `research/LAB_PROJECT_REGISTRY.yml`.

## 1. Repository roles

### Main repository — upstream authority and control tower

`loom-2226/loom-2226` owns:

- canon and governing engineering baselines;
- runtime / Navigator / GIS / HUD authority;
- authoritative deterministic geometry inputs and compilers;
- qualification and promotion decisions;
- the upstream inventory of Research Lab projects;
- cross-workstream provenance and consumer linkage.

### Research Lab — working research repository

`loom-2226/loom-research-lab` remains the working repository for research projects, experiments, evidence, reviews and methods.

Main does **not** maintain a second live copy of those trees. Instead, main records their project identity, status, source path, upstream relationships and promotion history. This avoids dual-live-source drift.

## 2. Current Research Lab inventory

At Research Lab main `e4196d0a8cc3944db267e8d31dc9ff04015f842c`, the upstream control tower recognizes:

| Project | Upstream control status | Lab source |
|---|---|---|
| Relational Foundations (RF) | Frozen research baseline | `projects/relational_foundations` |
| Anomaly / Phenomenology (AP) | Frozen research baseline | `projects/anomaly_phenomenology` |
| Foundations Consequences (FC) | Established; no active execution by default | `projects/foundations_consequences` |
| Deep Time Attunement (DTA) | Parked optional | `projects/deep_time_attunement` |
| NAV / GIS / HUD Renderer Acceleration | Active parallel research | `projects/nav_gis_hud_renderer_acceleration` |
| World Object Development | Parallel design research | `projects/world_object_development` |

The first five are represented by the Lab's top-level status/manifest records. World Object Development exists in the Lab tree with its own project manifest but is not currently listed in the Lab top-level project inventory/status overlay. Main therefore records it explicitly as a **registry-drift finding**, rather than allowing it to disappear from institutional memory.

## 3. Wayfarer deterministic geometry — shared authoritative lineage

The Wayfarer geometry model is a shared upstream asset used by multiple efforts. It is **not** an E1-only model and it is **not** a HUD-only or Shipyard-only model.

Authoritative chain:

```text
Canon II / Wayfarer Schematic Amendment
        ↓
geometry/wayfarer_geometry_seed.sql
        ↓
src/wayfarer_geometry.py
        ↓
deterministic generated geometry representation
        ↓
+----------------------+------------------------+
|                      |                        |
HUD / Three.js      Computational          other governed
presentation        Shipyard / Blender     consumers
                       ↓
                 semantic GLB derivative
```

Generated JSON and GLB files are derivatives. They do not outrank the SQL/Python/canon source chain.

### Known branch families using or developing this lineage

HUD / local-flight family includes:

- `feature/hud-wayfarer-attitude-envelope-v0.1-2026-09-11`
- `feature/hud-local-flight-contract-shell-v0.1-2026-09-09`
- related HUD/Navigator/GIS workstreams

Wayfarer 3D / shipbuilding family includes:

- `workstream/wayfarer-3d`
- `research/computational-shipyard-wayfarer-vertical-slice-2026-09-08`
- `research/computational-shipyard-wayfarer-vertical-slice-2026-09-08-ci`
- `research/physical-design-synthesis-wayfarer-s1-2026-09-08`
- `research/physical-design-synthesis-wayfarer-s2-2026-09-08`
- their CI companions

Verified historical heads captured during this provenance pass:

- HUD Wayfarer attitude branch: `8b1637e3e6ff7ebb718aa3dfb7b3310be3b6ac2f`
- Computational Shipyard vertical slice: `dc129ebb5999641c85138c3f263ec78b7e3495c5`

The exact commit values are historical resume points, not declarations that those branches remain current.

### E1 reuse

Main PR #182, `engineering/e1-committed-component-geometry-envelope-2026-09-15`, intentionally reuses the same deterministic geometry lineage to construct the conservative committed component envelope for E1.

This is a **consumer binding**, not a fork of Wayfarer geometry authority.

The Research Lab renderer project has a corresponding provenance record in Lab PR #61 so renderer/GLB research also knows where the shared geometry originates.

## 4. Change-backpropagation rule

Any substantive change to a shared authoritative asset must be traceable to every dependent effort.

For Wayfarer geometry, a change record must state:

1. the exact authoritative file(s) changed;
2. the reason and governing decision;
3. exact PR and commit;
4. whether canon changed or only engineering/detail geometry changed;
5. which HUD consumers may change;
6. which Shipyard/Blender/GLB consumers may change;
7. which E1 or later engineering qualification artifacts may change;
8. which generated JSON/GLB assets need regeneration;
9. which research fixtures, screenshots, benchmarks or conclusions are stale;
10. which qualification or acceptance tests must be rerun.

No generated derivative may silently become the new source of truth because it happens to be visually better or more detailed.

## 5. Research-to-main promotion rule

Research may live in the Lab; promotion lives in main.

A Lab result that should affect LOOM must carry:

- project id;
- exact Lab commit;
- source artifacts/evidence;
- research disposition;
- claimed upstream impact;
- forbidden/non-claims;
- proposed main files/contracts affected;
- qualification plan;
- rollback or rejection path.

Then a separate main PR performs the actual integration. Main records the promotion, rejection, supersession or partial adoption.

This keeps research creativity cheap while keeping production authority expensive and traceable.

## 6. Resume protocol for old branches and projects

When returning to an older HUD, Shipyard, GIS, Navigator or research effort:

1. start from this control tower and `research/LAB_PROJECT_REGISTRY.yml`;
2. identify the branch/project's recorded source dependencies;
3. compare those dependencies to current main;
4. determine whether generated assets are stale;
5. regenerate from current authoritative inputs where required;
6. carry forward only changes that still survive current governance/canon;
7. record the new branch/PR as a successor rather than rewriting historical provenance.

This is especially important for old GLBs and geometry JSON. Their usefulness as visual evidence does not imply current authority.

## 7. Why main holds the registry but not duplicate live research

The clean architecture is:

```text
MAIN
  authoritative runtime / canon / engineering
  authoritative cross-project registry
  promotion decisions
  shared-asset provenance
          ↑       ↓
          | governed handoff / provenance pointers
          |
RESEARCH LAB
  active experiments
  methods
  evidence
  reviews
  parked/frozen research projects
```

Copying all Lab files into main as another live research tree would create exactly the record-keeping problem this control tower is intended to prevent. Main therefore consolidates **identity, status, provenance, linkage and promotion history**, while the Lab remains the single working copy of research artifacts.

## 8. Immediate known cross-effort linkage

The most important live linkage discovered in this pass is:

```text
Wayfarer canonical / deterministic geometry
       ├── HUD / local-flight presentation
       ├── Computational Shipyard / 3D / GLB
       ├── NAV/GIS/HUD renderer research fixtures
       └── E1 committed component geometry envelope
```

A future modification made to satisfy any one of these consumers must therefore be reviewed against the others before it is treated as complete.

## 9. Companion records

- `research/LAB_PROJECT_REGISTRY.yml` — machine-readable project and linkage registry.
- `research/README.md` — upstream research archive rules and pointer to this control tower.
- Main PR #182 — active E1 consumer binding to deterministic Wayfarer geometry.
- Research Lab PR #61 — provenance-only renderer-research record of Wayfarer HUD / Shipyard linkage.

This document may be superseded by a later version, but historical versions should remain available through Git history.
