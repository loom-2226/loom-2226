# Experience One — Metric-Domain Traffic Seam v0.1

**Scope:** SUPPORTS_E1 only  
**Governing finish line:** Ceres → Neptune on Pixel  
**Workplan anchors:** F2 deterministic route alternatives; F5 execute/commit/arrive

## Why this exists

Experience One requires an honest deterministic Ceres → Neptune route. The metric-domain work is therefore permitted only to the extent needed to prove that the chosen E1 route is physically admissible through LOOM's moving local-domain geometry and produces a defensible Neptune collapse handoff.

This seam connects already-merged authority:

`Navigator route samples -> shared celestial state -> moving domain centers -> metric-domain checker`

It does not create another planner or ephemeris.

## E1 acceptance sequence

1. Take the authoritative Ceres → Neptune candidate selected by the E1 Navigator path.
2. Reuse its sampled metric trajectory and epochs; do not recompute flight geometry here.
3. Hydrate only the active metric-domain policies from shared celestial-state authority.
4. Run the merged multi-segment domain checker.
5. If the candidate is admissible, continue E1. Do **not** build a detour solver merely because one could be useful later.
6. If a real E1 blocker is found, add the smallest deterministic bypass capability required and requalify the same Ceres → Neptune run.
7. At Neptune-domain contact, preserve the collapse state needed for the local-flight/HUD handoff. Local orbit/rendezvous remains post-collapse work.

## Hard scope guards

- no generalized Solar route planner before E1 demonstrates a blocker;
- no A/B/C radius canon decision in this seam;
- no UI/presentation changes;
- no new destination catalogue;
- no Mara coordinates, ephemeris, trajectory, authorization, or execution authority;
- no second campaign state store;
- no work on Earth/Luna facilities unless it directly blocks the Ceres → Neptune run.

The decision rule remains the E1 workplan's rule: **close seams, not horizons.**
