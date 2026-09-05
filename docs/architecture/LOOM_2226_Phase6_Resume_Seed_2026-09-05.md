# LOOM 2226 — Phase 6 Resume Seed — 2026-09-05

**Repository:** `loom-2226/loom-2226`  
**Branch:** `feature/gis-navigator-convergence`  
**Purpose:** New-chat handoff. Resume Phase 6 without reconstructing prior diagnostic history.

## Governing documents

Read first:

1. `docs/architecture/LOOM_2226_Phase6_MVP_Closure_Plan_v1.0.md`
2. `docs/architecture/LOOM_2226_Post_Release_Runtime_Data_Campaign_Closure_v1.0.md`
3. `docs/architecture/LOOM_2226_Runtime_Diagnostic_Telemetry_and_Forensic_Debugging_Plan_v1.0.md`
4. `docs/architecture/LOOM_2226_Repository_Hygiene_and_Versioning_Model_v1.0.md`

The Phase-6 MVP Closure Plan is the governing release gate. The Post-Release Runtime/Data/Campaign Closure document captures architecture discovered during physical qualification but must not broaden the Phase-6 gate.

## Exact Phase-6 checkpoint

Current code head before documentation-only checkpoint commits:

`1b44079cf6d71cf47f1d5cf0f83f1a22a43931a8` — `Fix planner endpoint resolver syntax`

The immediately preceding implementation commit `994948c616bb9afc9c6f5756d9d7177135f960c3` had a JavaScript syntax error; `1b44079...` is the corrected code head.

Relevant CI at `1b44079...` is green, including `mvp-contract`, `frozen-gis-navigation`, `unit-regression`, `frozen-flight-planning`, and `horizons-provider` in the six-check stack.

Phase 6 is **OPEN but narrowly**.

### Physical items already proven

- supported Pixel/Termux route discovery/preview/commit/execute works;
- Ceres -> Mars execution was physically observed;
- campaign state persisted and authoritative origin rebound to Mars;
- live logs reported `NAV TRAJECTORY Sequence-B payload available`;
- Cancel was physically tested after arrival and correctly cleared planning while preserving Mars as origin;
- full continuous sampled trajectory/HUD parity is explicitly deferred from MVP closure.

### Outstanding release acceptance

1. **Vesta fail-closed retest on current patched client**
2. **Psyche fail-closed retest on current patched client**
3. **duplicate/stale execute must reject HTTP 400 with no second campaign transition**
4. rerun same-head regression only if code changes after the physical tests
5. freeze/tag and record exact acceptance once those pass

No extra full supported flight is required simply to repeat already-proven execution unless needed to obtain duplicate-execute evidence.

## Exact next action on Pixel

Pixel runtime root:

`/storage/emulated/0/Download/LOOM_TEST`

Normal Termux launch:

```bash
cd /storage/emulated/0/Download/LOOM_TEST || exit 1
python src/loom_gis.py \
  --nav-runtime-root /storage/emulated/0/Download/LOOM_TEST \
  --nav-planning-offline
```

Browser:

`http://127.0.0.1:8766/`

### Vesta acceptance

Select Vesta from the map/Atlas planning path and trigger discovery.

Expected:

- UI reports `NAVIGATION UNAVAILABLE` or equivalent truthful rejection;
- server log contains `POST /flight-planning/resolve` returning HTTP 200/unavailable capability;
- **must not** leak `WorkflowError: unknown route token(s): ['VST']`.

Then repeat with Psyche. It must similarly fail closed and must not leak raw `PSY` Navigator token errors.

If the resolver call still does not occur, first verify the served `/app.js` contains the current base-planner patch markers (`CHECKING NAVIGATOR ENDPOINT` / `resolveAndStartDiscovery`) before adding or changing event-capture shims.

## Why Vesta/Psyche failed before the current patch

Before `1b44079...`, physical tests showed Vesta and Psyche entering Navigator directly as raw GIS IDs (`VST`, `PSY`) and generating `unknown route token` workflow errors. The server logs contained no `/flight-planning/resolve`, proving the earlier capture-layer guard did not own the decisive discovery path.

The current patch moves noncanonical destination resolution into the base planner path.

Navigator endpoint acceptance remains governed by the frozen Navigator registry (`CIVSTATE_TOKEN_ENTITY` / alias logic). Presence in world SQL does not automatically make an entity a navigation endpoint.

## Runtime/data audit conclusion — do not reopen during Phase 6 unless needed

The phone contains world/reference DB copies under both:

- `/storage/emulated/0/Download/LOOM_TEST/data`
- `/storage/emulated/0/Documents/LOOM/data`

The active Android GIS default resolves the world DB from `/Documents/LOOM/data`.

A deep read-only comparison proved the two `LOOM_2226.sqlite3` copies are semantically equivalent at the established table-row level. The only file/logical-hash discrepancy came from `knowledge_relationships.rel_id`; when that surrogate ID was excluded, all 925 relationships had the identical canonical hash:

`f843073fff3b5fe5689d7e76013c37cd24bacfa55e38337857445d35bf3349bf`

Do not delete either copy during Phase 6. Post-release root cleanup will make `/Documents/LOOM/data` the explicit Pixel `DATA_ROOT` and quarantine redundant deployment copies only after proving no consumer depends on them.

Material Files is installed on Pixel for human filesystem inspection/bookmarks. It is not a LOOM runtime dependency and nothing should be moved with it during Phase-6 closure.

## Post-release decisions already captured

After Phase-6 freeze:

- formalize `LOOM_APP_ROOT`, `LOOM_DATA_ROOT`, `LOOM_CAMPAIGN_ROOT`;
- intended Pixel roots: app `/Download/LOOM_TEST`, data `/Documents/LOOM/data`, campaign `/Download/LOOM_TEST/campaign`;
- reconcile stale deployment launchers/updater with `src/loom_gis.py`;
- implement read-only `loom_doctor.py` plus machine-readable runtime manifest;
- later add localhost-only `/diagnostics` runtime identity endpoint;
- make updater classifications explicit (`MANAGED`, `PRESERVED`, `MUTABLE`, `REFERENCE_DATA`, `CACHE`, `BACKUP`, `UNKNOWN`, `DRIFTED` or equivalent);
- treat `.loom_install_state.json` as install provenance/receipt rather than live integrity authority;
- introduce `LOOM_CAMPAIGN_DEV.sqlite3` as a **shadow/write-through ledger** while legacy JSON/history remains campaign authority;
- reconcile/qualify before promoting campaign SQL to authority;
- keep world/GM knowledge distinct from campaign events and player/NPC belief graphs;
- only after observability/root cleanup resume deferred trajectory/HUD Gate-B work.

## Engineering discipline

- before sending new Python: run unit regression;
- substantive functional changes: run unit + functional tests;
- full end-to-end regression immediately before production freeze/run;
- avoid hard-coded payload/timeline/mode keys scattered across consumers; prefer canonical typed/validated contracts and adapters/accessors;
- Pixel and Windows remain one source/product architecture, not device forks.

## Resume instruction

Do **not** redesign architecture first. Resume with the Vesta physical fail-closed acceptance on the current Pixel build. If Vesta passes, test Psyche. Then capture duplicate-execute rejection. If all pass and no code changes are required, close/freeze Phase 6 using the governing MVP Closure Plan. Post-release runtime/data/campaign cleanup starts only after that freeze.
