# LOOM 2226 — E1.1 Mara Synthesis Finding v0.1

**Status:** SECOND LIVE SYNTHESIS ATTEMPT PARTIALLY EXECUTED; REFERENCE BOUNDARY STILL TOO STRICT; V0.3 RETEST PENDING  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `SYNTHESIS/ADAPTER_BOUNDARY_FAILURE`, not data failure

## First empirical failure

The first Pixel live run of `e1_1_mara_grounded_synthesis.py` did not reach grounded synthesis. The model selected the correct semantic place but supplied the human-readable projected name:

`Ceres Metric & Loom Anchorage`

in the tool field named `target_entity_id`.

The deterministic compact query correctly failed closed because only the canonical identifier `CER-P05` was accepted:

`KeyError: Unknown projected place: Ceres Metric & Loom Anchorage`

This was not missing Ceres data. It demonstrated that the natural-language model/tool boundary requires deterministic entity-reference normalization before canonical query execution.

## v0.2 bounded correction

`src/loom_canon_entity_reference.py` introduced exact projected ID/name resolution and `e1_1_mara_grounded_synthesis_v02.py` changed the model-facing field to `target_reference`.

The model remained unable to access SQLite or bypass the canonical compact query.

## Second empirical run

Pixel execution of v0.2 produced:

- `why_restricted` — **FAIL**, while resolving `Ceres Metric & Loom Anchorage -> CER-P05` and reaching grounded synthesis;
- `who_runs_it` — **PASS**, resolving the same full projected name to `CER-P05`;
- the third case then failed before tool execution because the model supplied the context-shortened human reference `Metric & Loom Anchorage`;
- the exact-name resolver rejected that shortened reference with `KeyError: Unknown projected entity reference: Metric & Loom Anchorage`;
- because v0.2 wrote its result artifact only at the end, the process-level exception prevented a complete structured evidence artifact for the partially completed run.

Two distinct findings follow.

First, exact full-name resolution is still too strict for ordinary language inside an already-bounded Ceres context. Second, the empirical harness itself must preserve partial failures as evidence rather than terminating before checkpointing them.

The `why_restricted` failure is deliberately **not** being prompt-tuned yet. Its precise validation reason must be captured on the next run before changing query semantics or epistemic expectations.

## v0.3 bounded correction

The resolver now accepts one additional deterministic alias only when mechanically derivable from the active projection context: if a projected place name begins with the current context entity name plus a space, that exact prefix may be omitted.

Example inside the Ceres projection:

`Ceres Metric & Loom Anchorage` -> exact contextual alias `Metric & Loom Anchorage` -> `CER-P05`

This is not fuzzy matching, arbitrary suffix matching, embeddings, retrieval, or model inference. `Loom Anchorage` still fails closed. Ambiguous contextual aliases fail closed.

Resolver tests now cover:

- exact ID;
- exact projected name;
- exact context-qualified alias;
- case/whitespace normalization;
- rejection of arbitrary suffixes;
- unknown reference fail-closed;
- ambiguous full-name fail-closed;
- ambiguous context-alias fail-closed.

`e1_1_mara_grounded_synthesis_v03.py` additionally:

- records target/query adapter failures as case failures rather than crashing;
- checkpoints the result JSON after every case;
- preserves provider audit logging;
- prints explicit validation reasons for synthesis failures;
- leaves the model authority boundary unchanged.

## Authority result

Authority remains:

- model SQLite access = false;
- model calculation authority = ZERO;
- model state authority = ZERO;
- model canon authority = ZERO;
- resolver authority = deterministic resolution over already-projected entities only;
- compact query remains the deterministic fact-selection boundary;
- no fuzzy/entity-generative behavior and no hidden duplicate world state.

## Retest requirement

Before Mara synthesis earns any PASS claim:

1. run the updated resolver tests on Pixel;
2. run `e1_1_mara_grounded_synthesis_v03.py` against the real Ceres projection;
3. retain all four case results even if one fails;
4. inspect `why_restricted` failure reasons rather than tuning around them;
5. confirm the contextual alias resolves to `CER-P05`;
6. confirm unsupported sabotage and contradictory-user cases preserve epistemic discipline.

## Falsifier

Reopen/reclassify if contextual alias generation becomes fuzzy or non-deterministic, if ambiguous references are silently accepted, if normal user language still cannot be bounded without broad entity search, if the model bypasses canonical normalization, or if synthesis validation reveals that the compact query lacks the evidence needed for the question being asked.
