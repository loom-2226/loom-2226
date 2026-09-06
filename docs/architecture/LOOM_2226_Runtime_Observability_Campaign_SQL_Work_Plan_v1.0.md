# LOOM 2226 — Runtime Observability and Campaign SQL Work Plan v1.0

**Date:** 2026-09-06  
**Workstream:** Post-Phase-6 runtime foundation  
**Target branch:** `feature/runtime-observability-foundation`  
**Status:** Governing implementation sequence for the next engineering workstream.

## Objective

Make the LOOM runtime self-identifying, diagnosable and deployment-safe before promoting a new campaign persistence authority. Then introduce a dedicated campaign SQLite database as a qualified shadow ledger before any authority cutover.

## Runtime authority contract

Introduce explicit authority roots with one canonical resolver shared by Pixel and Windows:

```text
LOOM_APP_ROOT       code, launchers, local cache/log/runtime support
LOOM_DATA_ROOT      canonical world/reference SQLite stores
LOOM_CAMPAIGN_ROOT  mutable campaign state, history, campaign SQL, replay/provenance
```

Initial Pixel target:

```text
APP_ROOT      /storage/emulated/0/Download/LOOM_TEST
DATA_ROOT     /storage/emulated/0/Documents/LOOM/data
CAMPAIGN_ROOT /storage/emulated/0/Download/LOOM_TEST/campaign
```

`LOOM_HOME` may remain temporarily as a compatibility input. Existing data is not moved or deleted during the first slice.

## Implementation sequence

1. Implement a typed/validated runtime root resolver and compatibility contract. Consumers stop independently guessing paths.
2. Integrate the resolver with the converged launcher while preserving current qualified behavior.
3. Implement read-only `loom_doctor.py` producing `LOOM_RUNTIME_MANIFEST.json` and `LOOM_RUNTIME_AUDIT.txt`, including source identity, roots, resolved/loaded DB paths and hashes, campaign identity/revision/epoch/location, caches/logs, provenance, drift and duplicates.
4. Add a localhost-only read-only `/diagnostics` endpoint derived from the same runtime identity model.
5. Reconcile Android/Windows launchers and updater with explicit managed-surface classes: `MANAGED`, `PRESERVED`, `MUTABLE`, `REFERENCE_DATA`, `CACHE`, `BACKUP`, `UNKNOWN`, `DRIFTED`.
6. Qualify Pixel and Windows against the same behavior/source architecture before moving or deleting anything.
7. Create `LOOM_CAMPAIGN_ROOT/LOOM_CAMPAIGN_DEV.sqlite3` as a development shadow ledger.
8. Define explicit campaign schema/migration metadata for campaign metadata, state revisions/snapshots, events/incidents, flights, flight plans, executions, trajectory provenance, commands/actions, idempotency, replay/provenance and campaign-specific knowledge references/state where appropriate.
9. Shadow-write qualified campaign transitions to SQL while existing JSON/history remains authority.
10. Reconcile JSON/history and SQL after each qualified action; disagreement is an error/evidence event, never silently resolved.
11. Qualify revision sequencing, flight arrival, exactly-once/idempotency, restart persistence, replay/provenance, failure/recovery and Pixel/Windows consistency.
12. Only after sustained reconciliation passes may a separate decision promote `LOOM_CAMPAIGN.sqlite3` to mutable campaign authority.
13. Quarantine redundant runtime data only after diagnostics prove no active consumer depends on it.
14. Resume deferred Gate-B trajectory/HUD work with observability operational.

## Campaign authority architecture

```text
campaign action
   ├── existing JSON/history       AUTHORITY
   └── LOOM_CAMPAIGN_DEV.sqlite3   SHADOW LEDGER
```

World entities are referenced by stable identities; canonical world facts remain in world/reference authority. The campaign database records what happened in this campaign rather than copying the canonical world database.

Longer term the authority layers remain distinct:

```text
WORLD / GM AUTHORITY
objective canonical world facts and relationships

CAMPAIGN AUTHORITY
what actually happened in this campaign

PLAYER / NPC KNOWLEDGE-BELIEF STATE
what an actor believes or claims, including confidence, provenance, timestamps,
salience, verification, deception and limited second-order beliefs
```

Campaign incidents/events should become first-class spatial-temporal objects linking who/what/where/when. This workstream establishes the storage boundary without prematurely implementing the full epistemic/rabbit-hole gameplay layer.

## Testing discipline

Before any new Python source is deployed or sent, run unit regression tests. Root migration, launcher/updater changes and campaign-persistence changes are substantive functional changes and therefore require unit plus functional tests. Reserve full end-to-end regression for the release/finalization point.

Prefer typed/validated contracts and accessors over scattered dictionary keys, mode strings or path literals.

## First implementation checkpoint

The first code checkpoint is intentionally narrow: runtime root contract/resolver plus compatibility behavior and tests. Do not move/delete data, create campaign authority, or modify flight behavior in that checkpoint.
