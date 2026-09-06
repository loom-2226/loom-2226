# LOOM 2226 — Phase 6 Converged MVP Release Closure

**Date:** 2026-09-06  
**Branch qualified:** `feature/gis-navigator-convergence`  
**Qualified code baseline:** `1b44079cf6d71cf7f1d5cf0f83f1a22a43931a8` (`Fix planner endpoint resolver syntax`)  
**Documentation head before this closure record:** `1f660457edb8df430c101aa3d41627e6b0af6fb6`  
**Release status:** **PHASE 6 MVP CLOSED / PHYSICALLY ACCEPTED**

## 1. Closure decision

Phase 6 is closed on the basic functioning converged GIS/Navigator MVP defined by `LOOM_2226_Phase6_MVP_Closure_Plan_v1.0.md`.

The accepted authoritative loop is:

```text
GIS / Atlas selection
 -> authoritative destination capability resolution
 -> Navigator route discovery
 -> preview
 -> planning commit
 -> explicit execute
 -> Navigator arrival
 -> one campaign persistence transition
 -> GIS refresh/rebind at authoritative arrival state
```

This release does **not** claim Gate-B continuous trajectory/HUD parity, FOLLOW SHIP, full route playback, perfect minor-body endpoint coverage, campaign-SQL authority, or the post-release runtime/data-root redesign. Those remain explicitly deferred.

## 2. Physical Pixel acceptance evidence

Qualification runtime:

```text
Platform: Pixel / Android / Termux
APP/runtime root: /storage/emulated/0/Download/LOOM_TEST
Launch: python src/loom_gis.py --nav-runtime-root /storage/emulated/0/Download/LOOM_TEST --nav-planning-offline
```

### Supported flight and campaign authority

Previously established during the same Phase-6 qualification sequence:

- Ceres -> Mars supported route discovery, preview, commit and explicit execute completed through the converged GIS/Navigator surface.
- Navigator reported `NAV TRAJECTORY Sequence-B payload available` during live planning/execution.
- Campaign arrival persisted and the authoritative planning origin rebound to `MARS` after reload/restart.
- Cancel after arrival cleared planning state without mutating the authoritative Mars arrival.

### Corrected client physically loaded

Before the final unsupported-destination retest, the Pixel deployment was found to contain an older `src/loom/gis/flight_planning.js`. The exact qualified client file from code baseline `1b44079...` was deployed without modifying campaign or world databases.

Both source and live served `/app.js` were then physically verified to contain:

```text
CHECKING NAVIGATOR ENDPOINT
resolveAndStartDiscovery
```

This distinguished stale device deployment from a defect in the already-qualified source baseline.

### Vesta fail-closed acceptance

Physical result:

```text
POST /flight-planning/resolve -> 200
```

The prior forbidden failure did not recur:

```text
WorkflowError: unknown route token(s): ['VST']
```

Vesta therefore crossed the authoritative destination resolver and failed closed as an unavailable Navigator endpoint rather than leaking raw GIS ID `VST` into Navigator.

**Result: PASS.**

### Psyche fail-closed acceptance

Physical result:

```text
POST /flight-planning/resolve -> 200
```

The prior forbidden raw `PSY` Navigator workflow failure did not recur. Psyche crossed the same authoritative resolver boundary and was handled as unavailable capability.

**Result: PASS.**

### Duplicate/stale execute rejection

After the completed campaign flight and rebind, a direct second execution attempt was issued:

```http
POST /flight-planning/execute
Content-Type: application/json
{}
```

Physical response:

```text
HTTP/1.0 400 Bad Request
{"error":"GISFlightPlanningError: commit a route before execute"}
```

Immediately after the rejected execute, `/flight-planning.json` reported:

```json
{
  "session_id": "plan-5a40a1886e065ce8",
  "origin": "MARS",
  "destination": null,
  "priority": "BALANCED",
  "candidates": [],
  "preview_route_id": null,
  "committed_route_id": null,
  "preview_overlay": null,
  "campaign_state_sha256": "91acc762a511b71e1b2989460a0627e8fd1317b25a2c6a48bc7defdbb801da2c",
  "execution_available": true,
  "last_execution": null,
  "contract": "LOOM_GIS_FLIGHT_PLANNING_V1"
}
```

The stale execute was rejected before a valid committed plan existed and the session remained bound to authoritative `MARS` campaign state.

**Result: PASS.**

## 3. Final acceptance ledger

| Acceptance item | Final state |
|---|---|
| Shared Pixel/Windows source architecture | PASS |
| Supported route discover/preview/commit/execute | PHYSICAL PASS |
| Campaign arrival/persistence/rebind | PHYSICAL PASS |
| Cancel clears planning without mutating arrival | PHYSICAL PASS |
| Authoritative trajectory availability through Navigator | OBSERVED / PASS for MVP |
| Vesta fail-closed through resolver | PHYSICAL PASS |
| Psyche fail-closed through resolver | PHYSICAL PASS |
| Raw `VST` / `PSY` leakage prevented | PHYSICAL PASS |
| Duplicate/stale execute rejected | PHYSICAL PASS — HTTP 400 |
| Post-rejection authoritative origin | PHYSICAL PASS — MARS |
| Same-head CI/regression | PASS at qualified code baseline; no production-code change after qualification |

## 4. Release boundary

The qualified production-code baseline remains `1b44079cf6d71cf7f1d5cf0f83f1a22a43931a8`. Commits after that baseline through this closure record are documentation/handoff material and do not redefine the physically qualified production behavior unless explicitly stated.

The manual Pixel client replacement performed during acceptance was deployment correction to the exact qualified source file, not a new source-code change. No additional same-head regression is required by the closure plan solely for that deployment correction.

## 5. Deferred/open gates retained

The following remain open post-MVP and are not silently claimed by this release:

- Gate-B continuous sampled trajectory/HUD parity;
- route playback and FOLLOW SHIP;
- richer trajectory visualization and old-renderer parity;
- additional Navigator endpoint qualification such as Vesta/Psyche navigation support;
- runtime/deployment root normalization;
- runtime diagnostics/observability;
- campaign SQLite shadowing and later authority migration;
- redundant runtime-data quarantine/cleanup.

## 6. Authorized next workstream

With Phase 6 frozen, the next engineering workstream is the post-release runtime/devops/diagnostic foundation governed by `LOOM_2226_Post_Release_Runtime_Data_Campaign_Closure_v1.0.md`.

Priority sequence:

1. explicit `LOOM_APP_ROOT`, `LOOM_DATA_ROOT`, `LOOM_CAMPAIGN_ROOT` authority resolution with compatibility migration;
2. reconcile converged launcher behavior and updater/deployment provenance across Pixel and Windows;
3. implement read-only `loom_doctor.py` plus machine-readable runtime manifest;
4. add localhost-only read-only `/diagnostics` based on the same runtime identity model;
5. classify managed, preserved, mutable, reference-data, cache, backup, unknown and drifted artifacts;
6. smoke/functional qualification on Pixel and Windows;
7. quarantine redundant data copies only after active-consumer proof;
8. introduce `LOOM_CAMPAIGN_DEV.sqlite3` as a shadow/write-through ledger before any authority cutover;
9. resume Gate-B trajectory/HUD work with diagnostics operational.

## 7. Freeze declaration

**LOOM 2226 Phase 6 — Converged GIS/Navigator MVP is CLOSED and FROZEN as of 2026-09-06.**

Future runtime/devops, diagnostic, campaign persistence and HUD/trajectory work must proceed as a new engineering workstream and must not retroactively broaden or rewrite the Phase-6 acceptance gate.