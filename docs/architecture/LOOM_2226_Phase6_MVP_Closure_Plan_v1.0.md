# LOOM 2226 — Phase 6 MVP Closure Plan v1.0

**Date:** 2026-09-04  
**Branch:** `feature/gis-navigator-convergence`  
**Status:** Governing release-closure plan for the first converged GIS/Navigator MVP.  
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

### M6.3 — Unsupported-destination smoke

Select at least one body not accepted by current Navigator (for example Psyche or Vesta if still unsupported). Verify the UX reports navigation unavailability rather than passing its short GIS entity ID into Navigator discovery.

### M6.4 — Same-head regression

Required at the final release candidate head:

- Python compile/regression;
- Navigator frozen Gate-A oracle;
- Phase 4 GIS navigation qualification;
- Phase 5 flight-planning qualification;
- Phase 6 Gate-C execution qualification;
- Ephemeris/provider qualification where currently part of the branch stack;
- browser syntax checks for the shared planning, authoritative-selection, NAV/ATLAS drawer, and navigation-overlay modules.

### M6.5 — Freeze

When M6.1–M6.4 are proven:

- mark Phase 6 MVP closed;
- record the exact source commit and physical acceptance evidence;
- freeze/tag the converged MVP before starting a new engineering workstream;
- retain Gate B as an explicit open visualization/parity gate rather than hiding it.

## 5. Post-freeze priority

Before returning to deep trajectory/HUD debugging, implement the first useful slices of `LOOM_2226_Runtime_Diagnostic_Telemetry_and_Forensic_Debugging_Plan_v1.0.md`:

1. D0 diagnostic event/session contract and local append-only spool;
2. D1 Python/HTTP/Navigator/campaign/SQLite boundary tracing;
3. D2 browser correlation and renderer/UI diagnostics.

This observability work should make later Gate-B trajectory and advanced HUD work substantially cheaper to debug.

## 6. Invariants retained

- GIS never becomes flight-physics authority.
- Navigator remains route/compile/execution/arrival authority.
- Campaign service remains the single mutable campaign-state authority.
- Preview and planning commit do not advance campaign state.
- Execute is explicit and advances state at most once.
- Missing values are not fabricated.
- Missing trajectory geometry is not fabricated.
- Pixel and Windows remain one product architecture.
