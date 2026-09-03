# LOOM 2226 — Repository Hygiene and Versioning Model v1.0

**Status:** Governing Phase 1 repository policy for GIS / Navigator convergence  
**Date:** 2026-09-03  
**Branch:** `feature/gis-navigator-convergence`

## 1. Decision

LOOM runtime source will use stable production filenames. Git history, tags, release manifests, schema versions and contract versions carry lineage. Version-heavy filenames are compatibility artifacts only and are not the canonical development surface.

## 2. Canonical runtime source names

The repository already contains stable-name, byte-identical copies of the qualified sources:

```text
src/loom_solar_gis.py
src/loom_navigator_core.py
src/loom_navigator.py
```

Current compatibility copies remain temporarily:

```text
src/LOOM_Solar_GIS_v0.12.9_RC8_Draggable_Graph_Nodes.py
src/LOOM_Navigator_MVP_v1.0_RC6.1_CIVSTATE_Launch_ANDROID.py
```

The stable-name files are now the canonical development targets for convergence work. Compatibility copies must not diverge silently. They remain only until deployment tooling and qualification no longer require them.

## 3. Source lineage

Version lineage is represented by:

```text
Git commit SHA
Git tag
release ID
release manifest
schema version
contract version
artifact SHA-256
```

Do not create new production source filenames solely to encode a release number, RC number or feature description.

## 4. Branch model

```text
main
  qualified / production reference

feature/gis-navigator-convergence
  active GIS / Navigator convergence development

release/*
  stabilization only when a convergence release candidate exists
```

No architectural convergence changes are to be developed directly on `main`.

## 5. Artifact policy

### Git-tracked

- Python
- JavaScript
- HTML templates / presentation source
- SQL schema definitions
- SQL migrations
- typed contracts / schemas
- manifests
- tests
- documentation

### Controlled runtime artifacts

- production SQLite snapshots
- large media SQLite payloads
- mutable campaign/runtime state
- generated caches and reports

Large payloads remain release assets when ordinary Git distribution is inappropriate.

## 6. Database evolution

Schema evolution must not be represented by ad hoc replacement databases alone.

Target structure:

```text
sql/
  schema/
  migrations/
  views/
  seeds/
```

Migrations are numbered and must record source schema, target schema, validation queries and Git lineage. The migration framework itself is introduced in Phase 7; this Phase 1 policy reserves the structure and establishes the rule now.

## 7. Release manifest requirements

Every production release must declare at minimum:

- release identifier;
- source Git reference / commit;
- required artifacts;
- SHA-256 for each artifact;
- exact byte size where practical;
- schema compatibility;
- contract compatibility when contracts exist;
- locally preserved mutable state;
- release-asset identifiers for external payloads.

The existing `manifests/release_manifest.json` remains the qualified production manifest until a tested convergence release supersedes it.

## 8. Compatibility-copy rule

During convergence, legacy version-heavy source files may remain for updater and regression compatibility, but:

1. they are frozen compatibility references;
2. new functional development occurs against stable-name sources;
3. changes must not be manually duplicated across multiple monolith copies;
4. if a compatibility copy is needed for qualification, it must be generated or explicitly synchronized from the canonical source;
5. final removal waits until the relevant deployment and regression dependencies have migrated.

This avoids filename archaeology without breaking the known-good deployment path prematurely.

## 9. Runtime invariants preserved by Phase 1

Phase 1 changes repository authority and versioning discipline only. It does not change:

- navigation physics;
- flight planning behavior;
- execution behavior;
- CIVSTATE behavior;
- campaign-state authority;
- GIS rendering behavior;
- Android runtime paths;
- updater production behavior.

## 10. Phase 1 completion state

The following are established:

- stable canonical GIS filename exists;
- stable canonical Navigator core filename exists;
- stable Navigator launcher/wrapper exists;
- byte identity with the qualified compatibility sources is preserved at the Phase 0 baseline;
- production baseline remains pinned by release/tag/hash;
- convergence work has a dedicated feature branch;
- versioning and artifact policy is explicit;
- legacy filenames are demoted to compatibility status rather than deleted prematurely.

**Phase 1 is complete at the repository-policy level.** Runtime manifest and deployment migration to the stable filenames is intentionally deferred until it can be regression-tested without disturbing the frozen production baseline.
