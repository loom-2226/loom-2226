# LOOM 2226 — E1.1 Mara Synthesis Finding v0.1

**Status:** V0.3 LIVE SYNTHESIS RUN DIAGNOSED; VALIDATOR CONTRACT DEFECT CONFIRMED; V0.4 RETEST PENDING  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `SYNTHESIS/VALIDATION_CONTRACT_FAILURE`, not data failure

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

Two findings followed: exact full-name resolution was too strict for ordinary language inside an already-bounded Ceres context, and the empirical harness needed to preserve partial failures as evidence rather than terminate before checkpointing them.

## v0.3 bounded correction

The resolver accepted one additional deterministic alias only when mechanically derivable from the active projection context: if a projected place name begins with the current context entity name plus a space, that exact prefix may be omitted.

Example inside the Ceres projection:

`Ceres Metric & Loom Anchorage` -> exact contextual alias `Metric & Loom Anchorage` -> `CER-P05`

This is not fuzzy matching, arbitrary suffix matching, embeddings, retrieval, or model inference. `Loom Anchorage` still fails closed. Ambiguous contextual aliases fail closed.

`e1_1_mara_grounded_synthesis_v03.py` also:

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

## Persisted v0.3 answer inspection

The saved case outputs establish that the remaining failure was in the validator contract, not in source grounding.

### why_restricted

Mara answered that the anchorage is a `RESTRICTED` strategic port with high security posture (`0.8750064000000001`), low commercial openness (`0.1998359999999999`) and guarded outsider attitude (`0.32052143199999994`). It then explicitly stated that a direct comparison with the rest of Ceres and a proven causal explanation were not available from the current authoritative context.

Its returned status was mixed text:

`SUPPORTED for the listed characteristics; NOT AVAILABLE for a direct comparative or causal explanation`

and it cited:

- `security_posture`;
- `commercial_openness`;
- `outsider_attitude`;
- `authorities`;
- `role`;
- `traffic_class`;
- `strategic_importance`.

The answer was epistemically disciplined. The validator defect was twofold:

1. one scalar `epistemic_status` could not represent a mixed answer containing both supported description and an unsupported comparative/causal component;
2. the validator allowed only keys in `tool_packet.facts`, even though `role` and `traffic_class` are legitimate deterministic evidence in `tool_packet.place`.

### who_runs_it

Mara correctly identified:

- civil authority: Ceres Commonwealth;
- administration: Belt Standards Directorate;
- security: Belt Security & Rescue Directorate;
- primary commercial operator: Axiom Precision & Metrology.

This case passed cleanly.

### unsupported_sabotage_cause

Mara answered:

`NOT AVAILABLE from current authoritative context.`

with status `NOT_ESTABLISHED` and no evidence keys.

That status is semantically better than forcing the underlying proposition into the same label as an answer-grounding state. The sabotage proposition is not established by current evidence; Mara's statement about that lack of establishment is itself grounded.

### contradictory_user_claim

Mara rejected the requested characterization and stated that the anchorage is a restricted strategic port with low commercial openness and high security posture, while tourist-port status is not established.

It returned `CONTRADICTED_AND_NOT_AVAILABLE`, reflecting two distinct conditions in the user's compound claim: some components conflict with available evidence, while another component is merely unestablished.

Again, the model preserved the evidence boundary. The scalar status ontology was the limiting layer.

## v0.4 bounded contract correction

`e1_1_mara_grounded_synthesis_v04.py` replaces the overloaded scalar with a small explicit assessment vocabulary:

- `SUPPORTED` — available tool evidence establishes the proposition answered;
- `NOT_ESTABLISHED` — current tool evidence does not establish the requested proposition;
- `CONTRADICTED` — available tool evidence conflicts with the requested proposition;
- `MIXED` — the answer necessarily contains both established material and a component that is not established or is contradicted.

The response contract is now:

```json
{
  "answer": "...",
  "assessment": "SUPPORTED | NOT_ESTABLISHED | CONTRADICTED | MIXED",
  "evidence_paths": ["place.traffic_class", "facts.security_posture"],
  "target_entity_id": "CER-P05"
}
```

The deterministic validator now checks dotted evidence paths against the actual tool packet rather than assuming all evidence lives under `facts`.

Examples of valid paths:

- `place.traffic_class`;
- `place.role`;
- `facts.security_posture`;
- `facts.commercial_openness`;
- `facts.administrative`.

A model cannot create a valid citation by naming a plausible path: every path must exist in the actual deterministic packet or validation fails.

Expected assessments for the four empirical cases are:

| Case | Expected assessment |
| --- | --- |
| why restricted | `MIXED` |
| who runs it | `SUPPORTED` |
| sabotage last week | `NOT_ESTABLISHED` |
| open/lightly-policed tourist port | `CONTRADICTED` |

This is a contract correction derived from the persisted v0.3 evidence, not prompt tuning to force a green result. The underlying WORLD/CIVSTATE projection, compact query, entity resolver and authority boundaries are unchanged.

Added `tests/test_e1_1_mara_epistemic_contract_v04.py` to verify:

- both `place.*` and `facts.*` evidence paths can be valid;
- nonexistent evidence paths fail;
- mixed answers can cite supported place and runtime facts while disclosing unsupported comparison/causation;
- unsupported sabotage can be `NOT_ESTABLISHED` without fabricated evidence;
- contradictory claims require deterministic grounding;
- invalid assessment labels fail.

## Authority result

Authority remains:

- model SQLite access = false;
- model calculation authority = ZERO;
- model state authority = ZERO;
- model canon authority = ZERO;
- resolver authority = deterministic resolution over already-projected entities only;
- compact query remains the deterministic fact-selection boundary;
- evidence-path validation is deterministic against the returned tool packet;
- no fuzzy/entity-generative behavior and no hidden duplicate world state.

## Retest requirement

Before any Mara synthesis PASS claim:

1. run the v0.4 epistemic-contract tests on Pixel;
2. run `e1_1_mara_grounded_synthesis_v04.py` against the unchanged real Ceres projection;
3. retain all four cases and provider audit entries;
4. inspect any failure as evidence before changing the contract again;
5. require every cited evidence path to resolve against the actual tool packet;
6. do not claim comparison or causation that the deterministic packet does not establish.

## Falsifier

Reopen/reclassify if the four-state assessment vocabulary cannot represent normal bounded answers without ad hoc labels, if evidence paths allow nonexistent or model-created facts through validation, if contextual alias resolution becomes fuzzy/non-deterministic, if the model bypasses canonical normalization, or if the compact query genuinely lacks the evidence required by an E1.1 acceptance question.
