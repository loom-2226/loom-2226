# LOOM 2226 — Governance Adoption Step 6 Audit

**Date:** 7 September 2026  
**Status:** STEP 6 COMPLETE — DEPENDENCY GRAPH / COMPATIBILITY MODEL / WALTER PACK INVENTORY  
**Branch:** `governance/repository-control-baseline-v1`  
**PR:** #24

## Purpose

Encode LOOM's cross-component authority, dependency, compatibility, deployment and release relationships so upstream changes can trigger explicit downstream review without allowing downstream implementation to silently rewrite upstream authority.

No game, physics, canon, runtime, SQLite, media, launcher or 3D functional behavior is changed by this step.

## Files added

- `governance/dependencies/component-map.yml`
- `governance/dependencies/DEPENDENCY_AND_COMPATIBILITY_POLICY_v1.0.md`
- `manifests/current/LOOM_COMPATIBILITY.yml`
- `governance/agents/WALTER_PACK_INVENTORY_EXTENSION_v1.0.md`

Updated:

- `.github/workflows/loom-governance-advisory.yml`
- `governance/current/LOOM_SESSION_BOOTSTRAP.yml`

## Dependency model decisions

### Direction

The graph is upstream -> downstream.

An upstream authority/engineering/data change may require downstream review, revalidation or migration.

A downstream finding may challenge upstream assumptions but does not gain authority to modify them automatically.

### Absence rule

No dependency edge means `UNKNOWN_UNREGISTERED`, not proven independence.

This protects against false confidence while the v1 graph remains intentionally coarse in parts of runtime/data ownership.

### Edge confidence

- `ESTABLISHED`
- `REGISTERED_COARSE`
- `PROVISIONAL`

Only established/preregistered deterministic relationships are candidates for future hard gates. Coarse/provisional relationships support WATCH/REVIEW by default.

### Downstream impact states

- `UNCHANGED_COMPATIBLE`
- `REVIEW_REQUIRED`
- `REVALIDATION_REQUIRED`
- `MIGRATION_REQUIRED`
- `BLOCKED_PENDING_UPSTREAM`
- `SUPERSEDED`

## Major dependency chains encoded

### Runtime/game chain

```text
Canon I / Canon II / Canon III / Core Mechanics
        + runtime architecture
        + world/CIVSTATE data
             -> Python campaign/runtime authority
             -> Navigator / GIS / HUD-facing runtime
             -> release manifest
             -> updater/platform launch surfaces
             -> runtime release
```

The runtime architecture's existing rule remains intact: Python owns committed mutable campaign state/game time; LLM/browser/presentation layers do not silently become numerical state authority.

### Navigator chain

Navigator is registered as depending at subsystem level on:

- CANON II physical/ship constraints;
- Solar Atlas geography;
- Core Mechanics operational rules;
- runtime integration architecture;
- CIVSTATE DB exact schema/hash contract;
- world DB at coarse-grained runtime-data level.

### Media chain

```text
media DB release asset -> media-library runtime -> release manifest -> updater/release
```

The large media DB remains a GitHub Release asset, distinct from Git source history.

### Wayfarer 3D chain

```text
CANON II v2.4
 + scoped Wayfarer amendment v2.4a
      -> Wayfarer engineering
      -> SQL geometry seed / compiler / server
      -> derived geometry JSON
      -> browser viewer / Blender builder
```

The generated geometry JSON remains derived/regenerable output rather than hand-authored geometry authority.

Three.js is registered as a third-party viewer runtime dependency; its exact version is not recorded in the current Wayfarer recovery manifest and is therefore retained as a future reproducibility WATCH, not promoted into a current geometry/canon defect.

## Current compatibility declaration

`manifests/current/LOOM_COMPATIBILITY.yml` captures the currently observed compatible set without changing any artifact.

It records:

- canon baseline v2.4 and active canon source versions;
- Wayfarer v2.4a as an effective scoped governing amendment with baseline-registration reconciliation still required at the next canon baseline update;
- runtime architecture v1.0;
- current release manifest identity/blob;
- Navigator RC6.1 SHA-256;
- Solar GIS RC8 SHA-256;
- media-library/runtime-inventory hashes;
- world DB current release hash;
- CIVSTATE schema `1.2-runtime` and exact hash lock;
- media DB asset ID, size and SHA-256;
- Android/Windows launcher Git blob recovery identities;
- updater Git blob identity and local-state preservation contract;
- Wayfarer recovery branch/SHA and source hierarchy;
- known platform/vendor reproducibility gaps.

## Historical validation lineage finding

The historical initial runtime candidate records world DB SHA-256:

`ff5b1b6c4e971844847cdfe5b1c6da7a0e4081984b043e7c655345ad7a1a8267`

The current release manifest records world DB SHA-256:

`e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`

Governance preserves both records.

The earlier candidate's validation must not be silently cited as validation of the later bytes unless separate evidence establishes that validation.

No attempt was made in Step 6 to explain or reconcile the functional reason for the hash change because development/runtime investigation remains paused.

## Known compatibility gaps recorded, not activated as work

### Python runtime version

The current release manifest does not pin a Python interpreter version.

State: `NOT_PINNED_BY_CURRENT_RELEASE_MANIFEST`.

This is a reproducibility gap, not evidence of incompatibility. It becomes material when a future production release requires interpreter-level reproducibility.

### Three.js version

The current Wayfarer recovery manifest identifies `web/three/three.min.js` as a cached third-party runtime dependency but does not record an exact version.

State: future 3D release WATCH.

Neither gap opens a new WIP stream during governance adoption.

## WALTER evolution

No new Walter module was created.

His existing Bouvier-derived Pack Inventory is now backed by `component-map.yml`.

New operating rule:

> If Walter cannot see a member of the pack, he does not assume it left the house.

For load-bearing changes he can now inspect registered downstream members and look for an impact classification.

The advisory workflow was extended to:

- WATCH for load-bearing component changes without downstream impact/dependency language;
- WATCH when the release manifest changes without review/update of the compatibility manifest;
- verify that the dependency map and compatibility manifest are present;
- parse both YAML files in the live GitHub runner;
- parse the release manifest JSON;
- remain advisory and always exit successfully during adoption.

## Bootstrap integration

`LOOM_SESSION_BOOTSTRAP.yml` now conditionally loads the dependency map/policy/compatibility manifest for canon, engineering, runtime, data, asset/3D, deployment or release work.

Routine conversation does not need to load the entire dependency model by default.

## Stability result

Step 6 intentionally changed governance/control metadata only.

No functional game/runtime/physics/canon/database/media/launcher/geometry bytes were modified.

## Acceptance result

**PASS subject to the live advisory runner continuing to parse the new machine manifests successfully.** The workflow remains advisory; any parser warning is a governance defect to repair before enforcement authority is introduced.

## Next permitted action

**Step 7 only:** establish the formal Canon Change Request record mechanism and numbered CCR repository lifecycle, including promotion/disposition templates and downstream-revalidation linkage.
