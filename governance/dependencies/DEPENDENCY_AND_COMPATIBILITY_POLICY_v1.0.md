# LOOM 2226 — Dependency & Compatibility Policy v1.0

**Status:** DRAFT — GOVERNING AFTER PR #24 MERGE  
**Machine graph:** `governance/dependencies/component-map.yml`  
**Current compatibility declaration:** `manifests/current/LOOM_COMPATIBILITY.yml`

## 1. Purpose

LOOM contains several different kinds of relationship that must not be collapsed into one vague idea of “dependency.”

This policy distinguishes:

- authority;
- engineering constraint;
- runtime input;
- data/schema compatibility;
- generated/derived representation;
- platform/deployment packaging;
- external/vendor dependency;
- release distribution.

The goal is not to make every change expensive. The goal is to make hidden coupling visible before promotion/release.

## 2. Direction rule

The component graph is written **upstream -> downstream**.

An upstream change may require downstream review, revalidation or migration.

A downstream result may raise a finding about the upstream source, but it does not gain authority to mutate that source automatically.

Examples:

- a Wayfarer Blender/geometry closure problem may raise an engineering/canon finding; it does not resize the ship by itself;
- a Navigator discrepancy may challenge canon/engineering assumptions; it does not silently revise CANON II;
- a new canon constraint may force Navigator/SQLite/3D review; those systems do not auto-update merely because the canon file changed.

## 3. Absence rule

> **No edge is not proof of no dependency.**

The v1 graph is intentionally coarse in areas where the repository does not yet contain sufficiently explicit machine-level ownership metadata.

If a relationship is not registered, classify it as `UNKNOWN_UNREGISTERED` until inspected.

Do not infer independence from silence.

## 4. Edge confidence

- `ESTABLISHED` — directly supported by governing manifests/architecture/source relationships.
- `REGISTERED_COARSE` — clearly relevant at subsystem level, but not yet resolved to table/function/field-level ownership.
- `PROVISIONAL` — suspected useful dependency retained for review; must not become a hard gate without validation.

WALTER may hard-block only on a deterministic rule whose required relationship is established/preregistered. Coarse/provisional relationships support WATCH/REVIEW by default.

## 5. Downstream impact states

Every material upstream change classifies relevant dependents as one of:

- `UNCHANGED_COMPATIBLE` — reviewed and no compatibility action required;
- `REVIEW_REQUIRED` — impact cannot yet be excluded;
- `REVALIDATION_REQUIRED` — implementation/data remains structurally compatible but must be tested/qualified again;
- `MIGRATION_REQUIRED` — schema/data/interface transformation required;
- `BLOCKED_PENDING_UPSTREAM` — downstream work cannot proceed safely until upstream decision closes;
- `SUPERSEDED` — downstream artifact/version is retired by the change.

`No impact` is acceptable only after the declared dependencies were checked.

## 6. Compatibility manifest role

`manifests/current/LOOM_COMPATIBILITY.yml` is the project-wide compatibility declaration.

It records the current observed combination of:

- governing canon versions;
- scoped amendments;
- engineering baselines;
- runtime artifact hashes;
- schema/version locks;
- baseline DB hashes;
- media release asset identity;
- deployment/updater assumptions;
- platform launch surfaces;
- Wayfarer geometry authority/derived outputs;
- known vendor/runtime reproducibility gaps.

It is not a substitute for subsystem tests.

A compatibility declaration says **what is intended/observed to work together and what remains unresolved**.

## 7. Historical validation is not transferable by assumption

Validation attaches to the bytes/version actually tested.

The historical `manifests/INITIAL_BASELINE.md` records a validated world-DB hash different from the current release manifest's world-DB hash.

Both records are preserved.

The earlier validation must not be cited as validation of later bytes unless a separate record establishes that later validation.

This rule applies to code, databases, media, geometry and vendor dependencies equally.

## 8. Runtime release compatibility

The current runtime release set is hash-pinned by `manifests/release_manifest.json`.

Key invariants include:

- Navigator RC6.1 is paired with CIVSTATE schema `1.2-runtime` and the recorded exact CIVSTATE SHA-256;
- world and CIVSTATE baseline DBs are repository-backed release artifacts;
- the large media DB is a GitHub Release asset pinned by identity, size and SHA-256;
- mutable local campaign state/history/cache/output is preserved by the updater;
- the updater fails closed on required-file/source/size/hash errors.

Changing one of these does not automatically invalidate every other component, but it triggers compatibility review according to the graph.

## 9. Platform compatibility

Android and Windows are separate launch surfaces sharing the same governed source/release model.

Their launcher paths are compatibility surfaces, not canonical authority.

Governance must not normalize/move them merely for repository aesthetics.

A platform-specific fix should not silently alter the other platform unless the declared work item includes both.

## 10. Wayfarer 3D compatibility

The current hierarchy is:

```text
CANON II v2.4
   + scoped Wayfarer amendment v2.4a
        -> Wayfarer engineering
        -> geometry seed/compiler/server
        -> derived geometry JSON
        -> browser viewer / Blender builder
```

The generated JSON is regenerable output, not hand-authored geometry authority.

Three.js is a third-party viewer runtime dependency. The current Wayfarer recovery manifest does not record its exact version; this is a known reproducibility gap, not evidence that authoritative geometry is uncertain.

## 11. External/vendor dependency rule

External services/libraries may host, calculate, render or distribute LOOM material without becoming LOOM content authority.

For material vendor dependencies record, when relevant:

- provider;
- role;
- version/API contract;
- cost/license;
- data handling;
- portability/fallback;
- lock-in/deprecation risk.

Unpinned vendor versions are WATCH/REVIEW inputs by default, not automatic blocks unless a release rule requires reproducibility at that level.

## 12. WALTER Pack Inventory

WALTER uses the component graph as the registered pack list.

When a component changes, he should inspect known downstream members and ask whether each has an impact classification.

He must also remember the absence rule: an unregistered dependency is **unknown**, not safely absent.

The useful Walter behavior is therefore:

> Walter counts the pack we know about, then checks whether we are pretending the unlit part of the room is empty.

## 13. Release promotion

Before a production release, the compatibility declaration should be updated to the intended release set and tested at the required level.

A release promotion must not claim compatibility based solely on:

- file names;
- “latest” branch state;
- an older test against different bytes;
- local success with an unrecorded dependency;
- LLM judgment.

Compatibility is earned by exact state + appropriate validation.
