# LOOM 2226 — Runtime / DevOps Status

Date: 2026-09-06
Status: **Converged baseline / physical Pixel acceptance complete**
Branch at capture: `integration/runtime-devops-convergence-2026-09-06`
Accepted integration head before this document: `06635d124b5f9573a77390baea02eb6760a04e05`

## 1. Accepted runtime topology

Pixel source checkout:

- `/storage/emulated/0/Documents/LOOM_GIT`

Active runtime topology:

- APP: `/storage/emulated/0/Documents/LOOM/runtime`
- DATA: `/storage/emulated/0/Documents/LOOM/data`
- CAMPAIGN: `/storage/emulated/0/Documents/LOOM/campaign`
- CACHE: `/storage/emulated/0/Documents/LOOM/cache`
- LOGS: `/storage/emulated/0/Documents/LOOM/logs`
- AUDIT: `/storage/emulated/0/Documents/LOOM/audit`
- BACKUPS: `/storage/emulated/0/Documents/LOOM/backups`

Legacy source retained for rollback:

- `/storage/emulated/0/Download/LOOM_TEST`

No source quarantine or deletion is authorized yet.

## 2. Physical Pixel qualification

The non-destructive migration path passed audit, stage, validate, activate, and post-cutover runtime qualification.

Migration stage/validate result:

- 555 files staged
- 555 files validated
- zero validation failures
- unknown classifier count: 0

The migrated Phase-6 loop was physically exercised on the Pixel:

- GIS launch: PASS
- Navigator provider/cache acquisition: PASS
- Mars → Ceres discovery: PASS
- preview: PASS
- planning commit: PASS
- execute: PASS
- canonical campaign transition: PASS
- GIS rebind at destination: PASS

Campaign transition evidence:

- before: revision 8, location `MARS`, state `S000008-1f8140b205a7`
- after: revision 9, location `CERES`, state `S000009-249837ce08c5`
- successful flight: `flight-e47fc2515426dacd`
- route: `MARS>CERES`
- campaign state and history hashes changed exactly as expected after successful execute
- failed execute attempts were shown to be non-destructive

The Android media/canon browser was also physically launched from the new topology after stale legacy-root cleanup:

- root: `/storage/emulated/0/Documents/LOOM`
- assets: 182
- browser: `http://127.0.0.1:8767/`
- result: PASS

## 3. Runtime authority contract

The runtime contract is explicit and split-root:

- APP owns installed code/runtime assets.
- DATA owns world/civilization/media databases.
- CAMPAIGN owns canonical campaign state/history.
- CACHE owns Navigator acquisition cache in split topology.
- updater may install APP and canonical DATA artifacts.
- updater must never install or overwrite CAMPAIGN authority.

`LOOM_HOME` remains compatibility input for APP only. Dedicated `LOOM_APP_ROOT`, `LOOM_DATA_ROOT`, and `LOOM_CAMPAIGN_ROOT` take precedence.

Campaign persistence remains JSON/history authoritative. Shadow campaign SQL is diagnostic/best-effort only and is **not authoritative**.

## 4. Deployment / update state

`deploy/loom_update.py` supports update and validate with deterministic root selection, digest checks, atomic writes, backups, and installation identity.

The release manifest is `LOOM_RELEASE_MANIFEST_V2` and remains a staging/convergence authority. Runtime artifacts are content-pinned. Campaign files remain preserve-local/non-installable.

Android and Windows GIS, Navigator, and media launchers use the root contract. Android planning defaults to provider-backed acquisition; `LOOM_NAV_PLANNING_OFFLINE` is an explicit cache-only qualification override.

## 5. Diagnostics / observability

Implemented:

- read-only `loom_doctor.py`
- runtime diagnostics manifest/audit
- deployment identity reporting
- runtime trace JSONL foundation
- localhost-only no-write diagnostics HTTP endpoint
- campaign revision/state/history/shadow-SQL diagnostics
- split-root Navigator cache diagnostics
- `loom_debug_bundle.py` one-shot physical-runtime bundle

The debug bundle is designed to collect a compact, allowlisted diagnostic package rather than requiring large manual Termux transcripts.

### Deferred: automatic diagnostic publishing

Automatic creation/publishing of debug bundles to GitHub is intentionally deferred until this runtime has been exercised for a while.

Future target behavior:

- create a sanitized bundle on selected triggers (new deployment qualification, fatal/unhandled runtime error, explicit health capture; possibly low-frequency heartbeat)
- spool locally if offline
- publish to a dedicated diagnostics branch/artifact surface, not normal source history
- never make diagnostics publishing a runtime dependency
- allowlist bundle content; do not upload arbitrary storage, credentials, tokens, or unrelated personal files

This is a future DevOps enhancement, not a blocker for the accepted runtime baseline.

## 6. Known architectural note: WORLD database mutability

The installed WORLD database hash is an install/baseline identity, not a permanent live-runtime invariant. GIS startup currently performs legitimate derived/runtime writes, including knowledge-relationship reseeding, which can alter the SQLite byte hash while leaving semantic row content effectively unchanged.

Do not enforce a post-launch immutable byte hash on the live WORLD database until canonical seed data and mutable derived/runtime state are separated architecturally.

## 7. Explicit non-goals / holds

Not authorized at this freeze:

- deleting or quarantining `/Download/LOOM_TEST`
- promoting campaign SQL to canonical authority
- broad WORLD database redesign
- changing frozen Phase-6 flight behavior
- touching Wayfarer work as part of runtime cleanup

## 8. Regression state

Exact-head CI for the accepted pre-documentation integration head `06635d124b5f9573a77390baea02eb6760a04e05` passed the Python regression suite.

This document records the accepted runtime/DevOps baseline for subsequent Navigator/GIS work.
