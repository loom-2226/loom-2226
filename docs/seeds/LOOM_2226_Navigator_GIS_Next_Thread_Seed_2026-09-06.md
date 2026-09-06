# LOOM 2226 — Navigator / GIS Next-Thread Seed

Use this file to start a new planning thread after runtime/DevOps convergence.

## Start-of-thread instruction

We are continuing LOOM 2226 from a physically accepted migrated runtime baseline. Do **not** reopen runtime migration, campaign authority, or updater redesign unless a new Navigator/GIS requirement truly demands it.

The current accepted runtime/devops and GIS/Navigator status are recorded in:

- `docs/LOOM_2226_Runtime_DevOps_Status_2026-09-06.md`
- `docs/LOOM_2226_GIS_Navigator_Status_2026-09-06.md`

The frozen physically accepted Pixel runtime baseline is preserved separately. The active development/convergence branch at this handoff is `integration/runtime-devops-convergence-2026-09-06`.

## Runtime baseline to assume

Pixel topology:

- source checkout: `/storage/emulated/0/Documents/LOOM_GIT`
- APP: `/storage/emulated/0/Documents/LOOM/runtime`
- DATA: `/storage/emulated/0/Documents/LOOM/data`
- CAMPAIGN: `/storage/emulated/0/Documents/LOOM/campaign`
- CACHE: `/storage/emulated/0/Documents/LOOM/cache`
- AUDIT: `/storage/emulated/0/Documents/LOOM/audit`

Legacy `/storage/emulated/0/Download/LOOM_TEST` remains retained only for rollback. Do not delete/quarantine it yet.

Campaign JSON/history remains canonical. Shadow SQL remains diagnostic only. Campaign SQL authority promotion is not authorized.

The live WORLD SQLite database can legitimately change byte hash during runtime because GIS writes derived/runtime state. Treat the repository hash as an installation baseline, not a permanent live hash invariant.

Automatic debug-bundle publishing to GitHub is a **saved future DevOps enhancement**, intentionally deferred until the accepted runtime has been exercised for a while. A one-shot `loom_debug_bundle.py` exists now.

## GIS / Navigator baseline to assume

The physically accepted Phase-6 loop is:

GIS selection → Navigator endpoint resolution → Navigator route discovery → route preview → planning commit with no campaign write → explicit execute → Navigator arrival computation → exactly one canonical campaign transition → historical overlay → GIS rebind at destination.

Physical Mars → Ceres acceptance passed on the migrated Pixel runtime:

- revision 8 → 9
- `MARS` → `CERES`
- `/preview` 200
- `/commit` 200
- `/execute` 200
- GIS displayed `ARRIVED · CERES · REV 9`

Preserve the distinction between planning commit and campaign execution.

Navigator is authoritative for endpoint registry, route discovery, flight compilation/calculation, and route-layer truth. GIS owns interaction, presentation, map behavior, and route-comparison UX. Campaign persistence remains its own authority.

Vesta/Psyche are currently unavailable because they are not declared Navigator endpoints; that is deferred coverage, not a regression.

## Purpose of the new thread

We are **not** starting with implementation. We want to plan the next evolution of the Navigator/GIS application now that runtime foundations are stable.

Begin by reviewing the current architecture and UX, then develop a defensible staged work plan for what comes next.

The discussion should explicitly consider:

1. **Product experience** — what the ideal user flow should be from map exploration through destination selection, route comparison, preview, commit, execute, arrival, and later historical review.
2. **Navigator vs GIS responsibilities** — preserve authority boundaries and avoid duplicating navigation truth in UI code.
3. **Trajectory presentation** — distinguish current abstract/authoritative route layers from future sampled trajectories, continuous playback, and live FOLLOW SHIP behavior.
4. **HUD design** — determine what flight data should be visible before, during, and after execution and ensure displays consume authoritative payloads rather than inventing missing physics.
5. **Endpoint coverage** — plan expansion to minor bodies, infrastructure nodes, orbital stations, and other useful destinations without hard-coding special cases throughout consumers.
6. **Route comparison** — improve comparison of time, remass, holonomy, confidence, metric/torch posture, and operational tradeoffs.
7. **Historical navigation** — route history, prior flights, playback, and relationship to the GIS timeline.
8. **Temporal/spatial simulation** — decide how much motion should be represented between departure and arrival and what needs additional physics/ephemeris support.
9. **Operational UX** — useful diagnostics/health indications without exposing engineering clutter during normal play.
10. **Pixel/Windows parity** — define which next features must qualify on both platforms.
11. **Qualification gates** — sequence work into small, testable phases that cannot silently break the accepted Phase-6 loop.

## Constraints

- Preserve current Phase-6 behavior until explicitly superseded.
- Avoid broad runtime/root redesign.
- Do not promote campaign SQL authority.
- Do not touch Wayfarer as part of Navigator/GIS planning.
- Prefer typed/validated canonical payloads and adapters/accessors over hard-coded dictionary keys or mode strings.
- Unit regression tests before any code release; substantive functional changes require unit + functional tests; reserve full end-to-end regression for final physical qualification.
- Treat endpoint authority and campaign persistence authority as hard architectural boundaries.

## Recommended first question in the new thread

**“Given the accepted Phase-6 Navigator/GIS baseline, what should the application become next? Review the current architecture and UX, identify the highest-value gaps, and propose a staged plan before we write code.”**
