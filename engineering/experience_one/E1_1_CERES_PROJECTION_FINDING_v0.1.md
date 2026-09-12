# LOOM 2226 — E1.1 Ceres Projection Finding v0.1

**Status:** EMPIRICAL PROJECTION + COMPACT QUERY TEST PASSED; E1.1 CONTINUES  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `PROJECTION_FAILURE` before `DATA_FAILURE`

## Empirical projection result

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

## Compact query increment

`src/loom_canon_context_query.py` adds a deterministic compact query layer over `LOOM_CANON_CONTEXT_PROJECTION_V1`.

Typed intents:

- `ORIENT`;
- `INTERESTING`;
- `WHO_RUNS`;
- `PLACE_DETAIL`.

The query layer does not read SQLite. It consumes only the already-built read-only projection and emits a small `LOOM_CANON_CONTEXT_QUERY_V1` packet with explicit provenance and epistemic status.

Natural-language interpretation may later map to these typed requests, but the model must not select authoritative facts, query SQLite directly, or invent missing facts.

The `INTERESTING` selection heuristic is presentation-only and explicitly marked `PRESENTATION_DERIVED_NON_AUTHORITY`; it cannot become canon/state authority.

## Pixel empirical compact-query result

On Pixel/Termux, the repository test module was executed directly because `pytest` is not installed in the current Termux Python environment. No test dependency was added solely for Pixel qualification.

Result:

- `ALL 6 TESTS PASS`;
- compact grounded orientation PASS;
- deterministic/non-authoritative interesting-place selection PASS;
- separated civil/administrative/security/commercial authority PASS;
- place-detail behavioral projection PASS;
- unknown-place fail-closed PASS;
- bad authority-contract fail-closed PASS.

The real Pixel-generated Ceres projection was then queried with `--intent ORIENT`.

Observed `LOOM_CANON_CONTEXT_QUERY_V1` result:

- `answer_kind = ORIENTATION`;
- context entity = `CER / Ceres`;
- identity fact = `SUPPORTED`, sourced from `WORLD.atlas_profiles`, source `CANON I v2.4 body/network world-state registry`;
- political context = `SUPPORTED`, sourced from `WORLD.regional_morphology`, source `Institutions & Organizations Register v1.2`;
- transport role = `SUPPORTED`, sourced from `WORLD.region_mobility`, source `Earth & Solar System Canon Atlas v3.2`;
- authority policy preserved `model_calculation_authority = ZERO`, `model_state_authority = ZERO`, `model_sqlite_access = false`, `read_only = true`;
- selection authority remains `PRESENTATION_DERIVED_NON_AUTHORITY`.

This is the first empirical E1.1 proof of the seam:

`governed WORLD/CIVSTATE -> read-only canon projection -> compact question-shaped evidence`

No model was required for this proof.

## Current interpretation

The ORIENT packet is compact enough to become a safe Mara/UI evidence input and remains explicitly provenance-bearing. That is materially different from handing a model the full 39 KB Ceres projection or direct SQLite access.

E1.1 should now test the other compact intents against the real projection, especially `INTERESTING` and `PLACE_DETAIL`, before introducing model synthesis.

## Falsifier

Reclassify toward `DATA_FAILURE` only if a user-relevant question cannot be answered after the governed projection has actually attempted to surface all relevant existing source classes, or if the available source facts are genuinely absent rather than merely unprojected.

Reopen the compact-query boundary if any intent drops required provenance/epistemic status, permits direct model SQLite access, elevates presentation ranking into authority, or requires hidden duplicate world state.
