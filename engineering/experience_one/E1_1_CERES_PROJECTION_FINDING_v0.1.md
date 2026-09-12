# LOOM 2226 — E1.1 Ceres Projection Finding v0.1

**Status:** EMPIRICAL PROJECTION TEST PASSED; E1.1 CONTINUES  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `PROJECTION_FAILURE` before `DATA_FAILURE`

## Empirical result

The Pixel-generated `LOOM_CANON_CONTEXT_PROJECTION_V1` successfully projected governed Ceres information from the real WORLD/CIVSTATE runtime databases without mutation or model access.

Observed projection availability:

- 5 Ceres places;
- 55 influence edges;
- 10 actor-exposure records;
- system demography present;
- system economy present;
- mobility present;
- regional morphology present.

The projected places are materially differentiated by existing governed data. Examples include different governance style, commercial openness, security posture, outsider attitude, traffic class, authorities, commercial actors, strategic importance and transport/economic centrality.

Therefore the current primary failure hypothesis is **not that Ceres lacks world data**. The immediate product problem is that existing structured world texture is not yet projected into a compact, query-shaped form consumable by Experience One interfaces.

## Authority result

The empirical projection declared and preserved:

- read-only access;
- model SQLite access = false;
- calculation authority = deterministic source only;
- state authority = none;
- canon mutation = false;
- campaign mutation = false.

G2 therefore still holds for this increment.

## Current bounded increment

`src/loom_canon_context_query.py` now adds a deterministic compact query layer over `LOOM_CANON_CONTEXT_PROJECTION_V1`.

Typed intents:

- `ORIENT`;
- `INTERESTING`;
- `WHO_RUNS`;
- `PLACE_DETAIL`.

The query layer does not read SQLite. It consumes only the already-built read-only projection and emits a small `LOOM_CANON_CONTEXT_QUERY_V1` packet with explicit provenance and epistemic status.

Natural-language interpretation may later map to these typed requests, but the model must not select authoritative facts, query SQLite directly, or invent missing facts.

The `INTERESTING` selection heuristic is presentation-only and explicitly marked `PRESENTATION_DERIVED_NON_AUTHORITY`; it cannot become canon/state authority.

Unit tests cover orientation, deterministic interesting-place selection, authority separation, place detail, unknown-place fail-closed behavior and authority-contract fail-closed behavior. Pixel empirical execution is still required before this increment earns an empirical claim.

## Falsifier

Reclassify toward `DATA_FAILURE` only if a user-relevant question cannot be answered after the governed projection has actually attempted to surface all relevant existing source classes, or if the available source facts are genuinely absent rather than merely unprojected.
