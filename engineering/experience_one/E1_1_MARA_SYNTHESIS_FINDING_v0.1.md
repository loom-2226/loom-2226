# LOOM 2226 — E1.1 Mara Synthesis Finding v0.1

**Status:** V0.3 LIVE SYNTHESIS RUN COMPLETE; 1/4 CASES PASS; EPISTEMIC/VALIDATION SEMANTICS UNDER REVIEW  
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

## v0.3 empirical run — complete four-case evidence

Pixel/Termux resolver regression:

- `ALL 8 TESTS PASS`;
- contextual alias resolution PASS;
- arbitrary suffix rejection PASS;
- ambiguous contextual alias fail-closed PASS.

Live v0.3 synthesis result:

- `why_restricted` — **FAIL** — `Ceres Metric & Loom Anchorage -> CER-P05`; reasons: `epistemic_status_mismatch`, `used_fact_key_not_in_packet`;
- `who_runs_it` — **PASS** — `Ceres Metric & Loom Anchorage -> CER-P05`;
- `unsupported_sabotage_cause` — **FAIL** — contextual alias `Metric & Loom Anchorage -> CER-P05`; reason: `epistemic_status_mismatch`;
- `contradictory_user_claim` — **FAIL** — contextual alias `Metric & Loom Anchorage -> CER-P05`; reason: `epistemic_status_mismatch`.

The run completed without crashing and wrote all four cases. Usage was 4,938 input tokens and 847 output tokens; eight audited provider entries were written for the four two-turn cases.

### Immediate interpretation

The entity-reference adapter is no longer the active blocker for these cases. Both the full projected name and the exact context-qualified alias resolved deterministically to `CER-P05`.

The remaining failures are concentrated in **epistemic-status semantics and answer-validation semantics**, not entity resolution or missing source data.

`why_restricted` also used at least one evidence reference that the validator did not recognize as a literal `facts` key. Before changing the prompt or compact-query schema, the persisted v0.3 case artifact must be inspected to determine whether the model cited a legitimate packet field outside `facts` (for example place role/traffic metadata), invented a key, or exposed a genuine evidence-shape mismatch.

Likewise, the three `epistemic_status_mismatch` results must be inspected at the answer level before changing expectations. A single status field may be conflating at least two different questions:

1. whether the **underlying requested proposition** is established by authoritative evidence; and
2. whether Mara's **meta-answer** about support/non-support is itself grounded.

For example, a grounded answer that says "current authoritative context does not establish sabotage" can itself be well-supported while the sabotage proposition remains unavailable. That distinction must be evaluated from the actual saved outputs, not repaired by forcing a preferred label.

No synthesis PASS is claimed from this run.

## Authority result

Authority remains:

- model SQLite access = false;
- model calculation authority = ZERO;
- model state authority = ZERO;
- model canon authority = ZERO;
- resolver authority = deterministic resolution over already-projected entities only;
- compact query remains the deterministic fact-selection boundary;
- no fuzzy/entity-generative behavior and no hidden duplicate world state.

## Next discriminator

Inspect the saved `E1_1_MARA_SYNTHESIS_RESULT_V03.json` case outputs, specifically:

- each `model_answer_parsed.epistemic_status`;
- each `model_answer_parsed.used_fact_keys`;
- each `model_answer_parsed.answer`;
- the corresponding `tool_packet` fields.

Do not prompt-tune or relabel expected statuses until those concrete outputs show whether the defect is in the model instruction, validator ontology, packet shape, or query evidence.

## Falsifier

Reopen/reclassify if contextual alias generation becomes fuzzy or non-deterministic, if ambiguous references are silently accepted, if normal user language still cannot be bounded without broad entity search, if the model bypasses canonical normalization, or if synthesis validation reveals that the compact query lacks the evidence needed for the question being asked.
