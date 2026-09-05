# LOOM 2226 — Post-Release Runtime, Data, Campaign and File-Management Closure v1.0

**Date:** 2026-09-05  
**Branch:** `feature/gis-navigator-convergence`  
**Status:** Post-Phase-6 work package. Not a Phase-6 MVP release blocker unless a defect discovered here invalidates already-established acceptance evidence.  
**Purpose:** Capture the runtime-root, phone file-management, deployment/update, diagnostics, world-data and campaign-persistence architecture decisions discovered during Phase-6 physical qualification so they are not lost after release freeze.

## 1. Executive decision

After Phase 6 freezes, LOOM should move from an implicit single-`LOOM_HOME` model toward explicit runtime authority roots:

```text
LOOM_APP_ROOT
  code, launchers, local cache, logs, test/runtime support

LOOM_DATA_ROOT
  canonical world/reference SQLite stores

LOOM_CAMPAIGN_ROOT
  mutable campaign state, campaign history, campaign database, replay/provenance
```

For the current Pixel installation the intended target is:

```text
LOOM_APP_ROOT
/storage/emulated/0/Download/LOOM_TEST

LOOM_DATA_ROOT
/storage/emulated/0/Documents/LOOM/data

LOOM_CAMPAIGN_ROOT
/storage/emulated/0/Download/LOOM_TEST/campaign
```

`LOOM_HOME` may remain as a compatibility input during migration but must no longer ambiguously imply that code, immutable/reference data and mutable campaign state share one authority root.

No database or runtime artifact should be deleted merely because a newer architectural target exists. Migration follows **audit -> prove active consumer paths -> quarantine -> regression -> remove later**.

## 2. Phone/runtime audit findings retained

The Pixel runtime was audited during Phase 6. Important facts:

- `/storage/emulated/0/Download/LOOM_TEST` is a deployment/runtime surface, **not a Git worktree**; it has no `.git` directory.
- The user launches the converged runtime from Termux with:

```bash
cd /storage/emulated/0/Download/LOOM_TEST || exit 1
python src/loom_gis.py \
  --nav-runtime-root /storage/emulated/0/Download/LOOM_TEST \
  --nav-planning-offline
```

- `src/loom_gis.py` is the current convergence launcher and sets/derives campaign/runtime state from the selected runtime root.
- `src/loom_solar_gis.py` contains an Android world-DB default pointing to `/storage/emulated/0/Documents/LOOM/data/LOOM_2226.sqlite3` and a matching CIVSTATE default.
- The current Android deployment helper `deploy/android/launch_gis.py` is stale relative to the actual converged launcher/runtime behavior and must be reconciled post-release rather than treated as production truth.
- A local backup exists under `.loom_backups/phase6-a45515902218/`; backup presence alone does not make that copy active.
- Campaign mutable artifacts currently include legacy JSON/history/report/cache/log files under `LOOM_TEST` rather than a campaign-specific SQLite authority.

## 3. Duplicate world-data copies: audit conclusion

The Pixel currently contains two apparent copies of the three principal data stores:

```text
/storage/emulated/0/Download/LOOM_TEST/data/
/storage/emulated/0/Documents/LOOM/data/
```

For `LOOM_2226_CIVSTATE.sqlite3` and `LOOM_2226_media.sqlite3`, the audited copies were byte-identical at the checkpoint.

For `LOOM_2226.sqlite3`, the files had different file-level SHA-256 values, but a deeper read-only audit established:

- identical schema hash;
- identical SQLite PRAGMA physical state relevant to the audit;
- identical table list and row counts;
- identical metadata and migration history;
- identical logical hashes for 41 of 42 tables;
- `knowledge_relationships` differed only when `rel_id` was included;
- both copies contained 925 `knowledge_relationships` rows;
- when `rel_id` was excluded, the complete semantic relationship set produced the **same canonical SHA-256**:

```text
TEST   925 f843073fff3b5fe5689d7e76013c37cd24bacfa55e38337857445d35bf3349bf
ACTIVE 925 f843073fff3b5fe5689d7e76013c37cd24bacfa55e38337857445d35bf3349bf
```

Therefore the two audited world DBs are **semantically equivalent at the established table-row level**; the observed difference is consistent with surrogate `knowledge_relationships.rel_id` resequencing rather than different world facts.

This removes the immediate fear of two conflicting semantic world states, but it does **not** justify leaving two plausible operational data authorities indefinitely.

### Decision

Treat `/storage/emulated/0/Documents/LOOM/data` as the intended active `LOOM_DATA_ROOT` on Pixel. Keep `/Download/LOOM_TEST/data` untouched until all launchers/updaters/tests are migrated and a smoke/regression run proves no active consumer still resolves against that copy. Then quarantine/rename before eventual removal; do not jump directly to deletion.

## 4. Install/update provenance issues

`.loom_install_state.json` records the state of the baseline installation, not necessarily the current byte integrity of every file. During audit, its recorded world-DB baseline hash differed from both current world-DB file hashes. It should therefore be treated as an **installation receipt/provenance record**, not a continuously authoritative integrity manifest.

The current release/updater design also needs stronger mutable-state semantics:

- release manifests declare some runtime artifacts as `preserve_local`;
- current update behavior appears to preserve them primarily because the updater does not target them, rather than because a first-class preservation policy is enforced at runtime;
- the feature-branch release manifest was observed still referring to `source_ref: main`, which makes it unsuitable as authoritative feature-branch deployment provenance;
- manually downloaded branch patches bypass the updater and therefore bypass the release/install provenance model.

Post-release updater work should explicitly classify managed surfaces, for example:

```text
MANAGED
PRESERVED
MUTABLE
REFERENCE_DATA
CACHE
BACKUP
UNKNOWN
DRIFTED
```

An update should never overwrite campaign state merely because a file happens to sit under the same filesystem root as source code.

## 5. Runtime self-identification and `loom_doctor.py`

The phone should become observable without requiring repeated ad hoc Termux archaeology.

Implement a cross-platform `loom_doctor.py` or equivalent diagnostic command whose default mode is read-only and project-scoped. It should produce both a machine-readable manifest and a concise human report.

Minimum useful inventory:

```text
platform/device/runtime versions
source Git SHA / release ID when known
APP_ROOT / DATA_ROOT / CAMPAIGN_ROOT
resolved launcher/source paths
loaded module/source hashes
SQLite path, size, SHA-256, schema version, selected logical summaries
campaign state/history locations and revisions
cache/log locations
unknown or duplicate LOOM artifacts
release/install provenance
active environment variables relevant to LOOM
```

The tool should classify what is **present** separately from what is **actually resolved/loaded**.

Target output examples:

```text
LOOM_RUNTIME_MANIFEST.json
LOOM_RUNTIME_AUDIT.txt
```

A later `--publish` mode may package a **sanitized** diagnostic snapshot for GitHub so ChatGPT can inspect phone state directly through the repository connector. Publication must never include GitHub tokens, credentials, cookies or unrelated phone data.

## 6. Runtime `/diagnostics` surface

The local GIS server should eventually expose a localhost-only, read-only diagnostics endpoint derived from the same runtime manifest logic. This is more useful than filesystem inventory alone because it can answer what the live process has actually loaded.

Candidate contents:

```text
source/version identity
resolved root authorities
active DB paths/hashes/schema versions
campaign ID/state ID/revision/epoch/location
loaded contract versions
active cache path
selected diagnostic mode
process/runtime version
```

This endpoint observes authority; it does not become authority.

It should integrate with, rather than replace, `LOOM_2226_Runtime_Diagnostic_Telemetry_and_Forensic_Debugging_Plan_v1.0.md`.

## 7. Material Files / human file-management policy

Material Files was installed on the Pixel through F-Droid during the Phase-6 checkpoint to provide a usable human-facing filesystem browser.

Recommended use:

- bookmark `/storage/emulated/0/Download/LOOM_TEST`;
- bookmark `/storage/emulated/0/Documents/LOOM/data`;
- later bookmark the dedicated campaign root;
- inspect/check hashes/copy paths when useful.

Material Files is **not a LOOM runtime dependency** and should never be required by Python, launchers, update logic or campaign persistence. It is an operator convenience only.

Do not reorganize live files through the GUI until the root migration is complete and dependency checks prove which paths are safe to quarantine.

## 8. Campaign SQLite decision

A dedicated campaign database is the preferred long-term persistence architecture, but it should not be promoted to authority in one step.

### Development target

```text
LOOM_CAMPAIGN_DEV.sqlite3
```

Initially use it as a **shadow/write-through ledger** while the current qualified campaign JSON/history mechanism remains campaign authority.

Candidate campaign-domain tables/objects include:

```text
campaign metadata
state revisions / snapshots
events
flights
flight plans
executions
trajectory provenance
trajectory samples or segments where useful for replay/display
commands/actions
idempotency records
replay/provenance references
player/NPC campaign knowledge state where campaign-specific
```

Do not duplicate the canonical world database wholesale into campaign SQL. Campaign records should reference stable world/entity identities and store mutable facts that arise from the campaign.

For flights, preserve authoritative solved result/provenance rather than merely a pretty polyline. Useful fields may include solver/contract version, departure state identity, payload/result hashes, authoritative phase geometry and display samples when available.

### Migration sequence

1. define campaign SQL schema/contracts;
2. shadow-write existing campaign transitions;
3. reconcile SQL against JSON/history after each qualified action;
4. prove replay/idempotency/revision behavior;
5. run unit + functional + persistence regression;
6. only then declare `LOOM_CAMPAIGN.sqlite3` the mutable campaign authority;
7. retain a reversible migration path and archive legacy state evidence.

Do not perform this authority migration inside Phase-6 closure.

## 9. Campaign vs world knowledge architecture

The canonical world DB contains world-model knowledge structures, including `knowledge_entities` and `knowledge_relationships`. These should not become a dumping ground for mutable campaign discoveries, beliefs, deceptions or per-character epistemic state.

Longer-term LOOM epistemic architecture should preserve the distinction:

```text
WORLD / GM AUTHORITY
objective world facts and canonical relationships

CAMPAIGN AUTHORITY
what happened in this campaign

PLAYER / NPC KNOWLEDGE-BELIEF STATE
claims, confidence, provenance, timestamps, salience,
verification state, possible false connections, deception,
limited second-order beliefs
```

Campaign events/incidents should be first-class spatial-temporal objects linking who/what/where/when so relationship inference can emerge from co-occurrence without corrupting objective canon.

## 10. Navigator capability boundary retained

Minor-body navigation acceptance is not determined merely by presence in world SQL.

At the current frozen Navigator baseline, route acceptance is governed by the Navigator endpoint registry exposed through `CIVSTATE_TOKEN_ENTITY` / associated alias resolution. Vesta/Psyche can exist as GIS/world entities and still truthfully be unavailable as Navigator route endpoints.

Therefore future support for additional endpoints should be an explicit qualified extension of navigation capability, not an implicit rule that every GIS entity ID is a route token.

This authority distinction should survive all post-release data-root and campaign-SQL changes.

## 11. Deployment layout target

Recommended normalized cross-platform model:

```text
APP ROOT
  src/
  deploy/
  logs/
  cache/
  diagnostics/

DATA ROOT
  LOOM_2226.sqlite3
  LOOM_2226_CIVSTATE.sqlite3
  LOOM_2226_media.sqlite3
  immutable/reference manifests

CAMPAIGN ROOT
  LOOM_CAMPAIGN.sqlite3
  diagnostics tied to campaign state
  replay/export/archive artifacts
```

Exact filesystem locations can differ by platform, but the authority classes and source behavior must not fork between Pixel and Windows.

## 12. Recommended post-release sequence

Execute after Phase-6 freeze unless a direct release-blocking defect emerges:

1. freeze/tag the exact Phase-6 MVP head and record physical acceptance;
2. implement explicit root resolver/contracts for APP/DATA/CAMPAIGN authority while preserving compatibility inputs;
3. align `src/loom_gis.py`, Android/Windows launchers and updater with the same resolver;
4. implement `loom_doctor.py` and startup/runtime manifest;
5. add read-only `/diagnostics` runtime identity endpoint;
6. classify updater-managed vs mutable/reference/cache/unknown files explicitly;
7. smoke-test Pixel and Windows on the same source behavior;
8. quarantine the redundant `LOOM_TEST/data` copy only after proof no consumer depends on it;
9. introduce `LOOM_CAMPAIGN_DEV.sqlite3` as a shadow ledger;
10. qualify dual-write/reconciliation before any campaign authority cutover;
11. implement broader diagnostic telemetry D0/D1/D2;
12. then resume deferred trajectory/HUD Gate-B work with observability in place.

## 13. Testing discipline

Before sending or deploying any new LOOM Python source:

- run unit regression tests;
- for substantive functional changes, run unit plus functional tests;
- reserve a full end-to-end production regression for finalization immediately before a production run/freeze.

Root migration, updater changes and campaign-persistence changes are substantive functional changes and therefore require both unit and functional qualification before deployment.

Do not hard-code runtime payload field names or timeline/mode codes across consumers. Prefer canonical typed/validated schemas plus adapters/accessors so new route/campaign/runtime strategies do not require scattered dictionary-key patches.

## 14. Completion criteria for this post-release work package

This work package is complete when:

- Pixel and Windows resolve explicit app/data/campaign authorities consistently;
- a runtime manifest can prove what source, databases and campaign state are actually loaded;
- updater behavior cannot silently overwrite mutable campaign state or create an ambiguous second operational world-data authority;
- stale/duplicate deployment data is quarantined/retired through a tested process;
- campaign SQL has been qualified before authority promotion;
- diagnostic evidence can be packaged without exposing secrets;
- deferred trajectory/HUD work can be debugged with correlated runtime evidence rather than manual log archaeology.
