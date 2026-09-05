# LOOM 2226 — Phase 6 MVP Closure Plan v1.0

**Date:** 2026-09-05  
**Branch:** `feature/gis-navigator-convergence`  
**Current code head at checkpoint:** `1b44079cf6d71cf47f1d5cf0f83f1a22a43931a8` (`Fix planner endpoint resolver syntax`)  
**Status:** Governing release-closure plan for the first converged GIS/Navigator MVP. Phase 6 is **not yet closed**; the final physical acceptance is reduced to unsupported-destination fail-closed verification plus duplicate-execute rejection.  
**Supersedes for MVP release gating:** the broader physical-acceptance requirements in `LOOM_2226_Phase6_HUD_Trajectory_Convergence_Work_Plan_v1.0.md`. Those requirements remain valid backlog for post-MVP HUD/trajectory work.

## 1. Release decision

Phase 6 will close on a **basic functioning converged MVP**, not on full old-Navigator rendering parity.

The MVP proves the authoritative gameplay/runtime loop:

```text
GIS / Atlas selection
 -> authoritative destination capability resolution
 -> Navigator route discovery
 -> preview
 -> planning commit
 -> explicit execute
 -> Navigator arrival
 -> one campaign persistence transition
 -> GIS refresh at the authoritative arrival state
```

Continuous sampled trajectory rendering, full route playback, FOLLOW SHIP, final HUD polish, and old-renderer visual parity are **not Phase-6 MVP release blockers**. They remain governed follow-on work and must not be replaced by fabricated geometry.

## 2. MVP acceptance criteria

Phase 6 MVP closes when all of the following hold:

1. The converged GIS is the operational surface and launches reliably on the supported local runtime.
2. Pixel/Android qualification uses Termux as the long-running Python host; Pydroid is not a release requirement.
3. Windows and Pixel run the same product behavior/source architecture; responsive presentation may differ, behavior may not fork.
4. Atlas/GIS body selection can be handed to NAV through the authoritative destination resolver.
5. Raw GIS entity IDs such as `PSY`, `VST`, or `DAV` do not enter Navigator as route tokens unless Navigator itself explicitly accepts them.
6. Unsupported bodies fail cleanly as `NAVIGATION UNAVAILABLE` (or equivalent truthful domain rejection), not as a leaked internal `unknown route token` workflow exception.
7. A known-supported physical route can be discovered, previewed, committed and executed from Pixel.
8. Execution advances canonical location, epoch, revision and remass exactly once using Navigator/campaign authority.
9. Exactly one `FLIGHT_ARRIVED` history record is created for the execution.
10. A second/stale execution attempt is rejected.
11. Restart/reload rebinds GIS planning to the persisted authoritative arrival state.
12. Candidate summary values use authoritative values; absent/inapplicable values render as `—`, never fabricated zeroes.
13. NAV/ATLAS contextual UI is usable at MVP level: mutually exclusive mode content, minimize/restore/close distinct from cancel, and map remains practically usable.
14. Unit/functional/frozen-oracle/Gate-C regression stack is green at the release head.

## 3. Explicitly deferred from the MVP gate

The following are valuable but deferred until diagnostic telemetry is operational or a dedicated post-MVP HUD/trajectory work package resumes them:

- continuous sampled trajectory parity / Gate B closure;
- route auto-fit perfection;
- visually dominant full terminal/torch trajectory centerline;
- authoritative timeline playback animation;
- `FOLLOW SHIP` camera mode;
- perfect minor-body navigation coverage beyond truthful capability resolution;
- retirement of the old Navigator renderer;
- elaborate desktop docking/floating behavior;
- Phase 7 SQL migration work.

If Navigator does not currently expose authoritative ordinary-space samples through the live planning seam, GIS may display authoritative phase anchors/relational semantics. It may not synthesize a fake continuous route merely to satisfy visual expectations.

## 4. Final implementation sequence

### M6.1 — Harden destination identity boundary

- All map/Atlas-derived destinations cross `/flight-planning/resolve` before discovery.
- The resolver delegates acceptance/token normalization to Navigator.
- Supported destinations use Navigator's canonical route token.
- Unsupported destinations are disabled/rejected cleanly.
- Explicit body-picker values remain a secondary known-supported path.

Implementation checkpoint at code head `1b44079cf6d71cf47f1d5cf0f83f1a22a43931a8`:

- `src/loom/gis/flight_planning_http.py` resolves destination capability against the frozen Navigator endpoint registry (`CIVSTATE_TOKEN_ENTITY`) and reports unavailable entities without promoting GIS IDs into route tokens.
- `src/loom/gis/flight_planning.js` now sends noncanonical map/Atlas selections through `/flight-planning/resolve` before discovery and presents an unavailable state on resolver rejection.
- The immediately preceding implementation commit (`994948c616bb9afc9c6f5756d9d7177135f960c3`) exposed a JavaScript syntax error; the exact current code head fixes it.
- CI at `1b44079...` is green for the relevant six-check stack, including `mvp-contract`, `frozen-gis-navigation`, `unit-regression`, `frozen-flight-planning`, and `horizons-provider`.

Physical acceptance of the corrected client resolver is still outstanding and must not be inferred from CI alone.

### M6.2 — Physical supported-route closure

On the Pixel/Termux runtime, use a known supported endpoint pair (for example Mars -> Ceres or Ceres -> Mars):

1. select destination;
2. discover routes;
3. preview one selectable candidate;
4. verify credible summary fields / em dash for unavailable metrics;
5. commit;
6. execute;
7. verify arrived state in GIS;
8. restart and verify persisted origin/state;
9. attempt duplicate execute and verify rejection.

Full continuous route rendering is not required for this closure flight.

**Physical evidence already obtained before this checkpoint:**

- supported flight execution works on Pixel;
- at least one Ceres -> Mars execution completed through the converged surface;
- authoritative campaign origin subsequently rebound to Mars;
- campaign persistence/arrival behavior was observed after execution;
- live Navigator logs exposed `NAV TRAJECTORY Sequence-B payload available` during supported planning/execution;
- Cancel was physically exercised after arrival and correctly cleared planning state, preserving Mars as origin and returning the UI to destination selection without error.

Therefore **another full supported flight is not required merely to reprobe behavior already established**. The outstanding supported-route item is the stale/duplicate execute rejection if it has not yet been physically captured as HTTP 400 without a second campaign transition.

### M6.3 — Unsupported-destination smoke

Select at least one body not accepted by current Navigator (Vesta and Psyche are the chosen acceptance probes while still unsupported). Verify the UX reports navigation unavailability rather than passing its short GIS entity ID into Navigator discovery.

Important historical evidence:

- Before the base-planner resolver patch, Vesta reached Navigator as `VST` and leaked `WorkflowError: unknown route token(s): ['VST']`.
- Psyche similarly reached Navigator as `PSY` and leaked the corresponding raw workflow error.
- Those runs showed no `POST /flight-planning/resolve` in the server log, proving the earlier capture-layer-only guard did not actually own the decisive discovery path.
- The current patch moves the resolver into the base planner path specifically to close that gap.

**Next physical test, and the exact resume point for Phase 6:**

1. launch the current Pixel runtime from `/storage/emulated/0/Download/LOOM_TEST` with `python src/loom_gis.py --nav-runtime-root /storage/emulated/0/Download/LOOM_TEST --nav-planning-offline`;
2. select **Vesta** from the map/Atlas planning path and trigger discovery;
3. expected UI: `NAVIGATION UNAVAILABLE` (or equivalent truthful endpoint rejection);
4. expected server evidence: `POST /flight-planning/resolve` returns HTTP 200 with unavailable capability;
5. forbidden outcome: raw `WorkflowError: unknown route token(s): ['VST']`;
6. repeat with **Psyche** and require the same fail-closed behavior;
7. if the resolver path still does not fire, verify the served `/app.js` contains `CHECKING NAVIGATOR ENDPOINT` / `resolveAndStartDiscovery` before changing any further event shim.

The unsupported-body result is a capability boundary, not a world-SQL problem. Current frozen Navigator route acceptance is explicitly represented by its endpoint registry; adding Vesta/Psyche rows to the world SQLite alone does not make them navigable.

### M6.4 — Same-head regression

Required at the final release candidate head:

- Python compile/regression;
- Navigator frozen Gate-A oracle;
- Phase 4 GIS navigation qualification;
- Phase 5 flight-planning qualification;
- Phase 6 Gate-C execution qualification;
- Ephemeris/provider qualification where currently part of the branch stack;
- browser syntax checks for the shared planning, authoritative-selection, NAV/ATLAS drawer, and navigation-overlay modules.

At checkpoint head `1b44079...`, the relevant CI stack is green. If any code changes after the remaining physical acceptance, rerun the required same-head stack before freeze.

### M6.5 — Freeze

When M6.1–M6.4 are proven:

- mark Phase 6 MVP closed;
- record the exact source commit and physical acceptance evidence;
- freeze/tag the converged MVP before starting a new engineering workstream;
- retain Gate B as an explicit open visualization/parity gate rather than hiding it.

## 5. Physical acceptance ledger at 2026-09-05 checkpoint

| Acceptance item | State | Evidence / remaining action |
|---|---|---|
| Shared Pixel/Windows source architecture | PASS at code/CI level | Same converged source path; no Pixel-only product fork. |
| Supported route discover/preview/commit/execute | PHYSICAL PASS | Pixel supported flight executed; Ceres -> Mars observed. |
| Campaign arrival/persistence/rebind | PHYSICAL PASS | Origin became Mars after execution/reload. |
| Cancel clears planning without mutating arrival | PHYSICAL PASS | Mars remained origin; destination-selection state restored. |
| Authoritative trajectory availability through Navigator | OBSERVED | Live logs reported Sequence-B payload availability; full continuous HUD parity remains deferred. |
| Vesta fail-closed through resolver | **PENDING PHYSICAL RETEST** | Prior raw `VST` failure predates current base-planner patch. Test this first on resume. |
| Psyche fail-closed through resolver | **PENDING PHYSICAL RETEST** | Prior raw `PSY` failure predates current base-planner patch. |
| Duplicate/stale execute returns HTTP 400 and no second state advance | **PENDING FINAL EVIDENCE** | Required before Phase 6 freeze unless already captured in a durable log/evidence packet. |
| Same-head CI/regression | PASS at `1b44079...` | Rerun if code changes after physical retest. |

**Phase 6 closure verdict at this checkpoint: OPEN, but narrowly.** Do not broaden the gate with post-release runtime/file-management work.

## 6. Post-freeze priority and explicit separation

Runtime/data-root cleanup, phone file hygiene, campaign-SQL migration, and diagnostic observability are important but are **not Phase-6 release blockers** unless a newly discovered defect directly invalidates current acceptance evidence.

Immediately after Phase 6 freezes, execute the post-release closure work package recorded in:

`docs/architecture/LOOM_2226_Post_Release_Runtime_Data_Campaign_Closure_v1.0.md`

That work package incorporates and extends `LOOM_2226_Runtime_Diagnostic_Telemetry_and_Forensic_Debugging_Plan_v1.0.md` and the repository hygiene policy.

Initial priority remains:

1. formal runtime-root authority (`APP_ROOT`, `DATA_ROOT`, `CAMPAIGN_ROOT`);
2. `loom_doctor.py` / runtime manifest and observability;
3. campaign SQLite as a qualified shadow ledger before any authority migration;
4. quarantine, not deletion, of redundant runtime data copies after proof no consumer depends on them;
5. then resume deeper trajectory/HUD Gate-B work with diagnostics available.

## 7. Invariants retained

- GIS never becomes flight-physics authority.
- Navigator remains route/compile/execution/arrival authority.
- Campaign service remains the single mutable campaign-state authority until an explicitly qualified campaign-SQL migration changes that authority.
- Preview and planning commit do not advance campaign state.
- Execute is explicit and advances state at most once.
- Missing values are not fabricated.
- Missing trajectory geometry is not fabricated.
- Pixel and Windows remain one product architecture.
- World/reference SQLite and mutable campaign state are distinct authority classes.
