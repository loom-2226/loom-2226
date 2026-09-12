# LOOM 2226 — E1.1 Mara Synthesis v0.4 Diagnosis

**Status:** V0.4 LIVE RUN DIAGNOSED; STRUCTURAL VALIDATOR OVERREACH CONFIRMED; V0.5 RETEST PENDING  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `VALIDATION_CONTRACT_FAILURE`, not source-data failure and not demonstrated Mara hallucination

## Pixel empirical result

The Pixel v0.4 contract regression passed all six local tests.

Live v0.4 synthesis produced:

- `why_restricted` — PASS, assessment `MIXED`;
- `who_runs_it` — FAIL, assessment `NOT_ESTABLISHED`, reasons `assessment_mismatch` and `required_grounding_path_missing`;
- `unsupported_sabotage_cause` — FAIL, assessment `NOT_ESTABLISHED`, reason `unsupported_sabotage_asserted`;
- `contradictory_user_claim` — FAIL, assessment `CONTRADICTED`, reason `user_contradiction_repeated_as_fact`.

Usage: 5,602 input tokens, 1,061 output tokens, eight audited provider entries.

## Answer-level diagnosis

### why_restricted

Mara correctly returned `MIXED` and cited real packet evidence:

- `place.traffic_class`;
- `facts.security_posture`;
- `facts.commercial_openness`;
- `facts.governance_style`;
- `facts.authorities`.

It explicitly separated supported restrictive characteristics from an unestablished comparison with the rest of Ceres and from unproven causation. This is the intended epistemic behavior.

### who_runs_it

Mara answered that no single operator is identified, then correctly named:

- Belt Standards Directorate — administration;
- Belt Security & Rescue Directorate — security;
- Axiom Precision & Metrology — primary commercial authority;
- Ceres Commonwealth — civil authority.

It assessed the singular proposition as `NOT_ESTABLISHED` and cited descendant paths such as `facts.administrative.value`.

Two validator assumptions were wrong:

1. the test forced `SUPPORTED` even though the packet establishes differentiated authorities rather than one single operator;
2. the required-path matcher accepted only exact `facts.administrative`, not the equally valid existing descendant `facts.administrative.value`.

For the bounded v0.5 case, `who runs it?` is therefore treated as `MIXED`: the authority structure is supported, while a single operator is not established.

### unsupported_sabotage_cause

Mara said:

> The available evidence establishes that the Ceres Metric & Loom Anchorage is restricted, but it does not establish that it was locked down last week or that sabotage caused it.

Assessment `NOT_ESTABLISHED` was correct. The v0.4 validator falsely flagged the literal substring `sabotage caused` even though it occurred inside explicit negation. This is a negation-blind string-matcher false positive.

### contradictory_user_claim

Mara said the proposition is contradicted and explained that the anchorage is restricted, security-heavy and commercially closed rather than an open/lightly-policed tourist port.

Assessment `CONTRADICTED` was correct. The validator falsely flagged the quoted/rejected phrase `open, lightly policed` merely because the words appeared in the answer. This is another negation/stance-blind string-matcher false positive.

## v0.5 correction

`e1_1_mara_grounded_synthesis_v05.py` narrows deterministic validation to properties the deterministic harness can actually establish:

- assessment belongs to the bounded vocabulary and matches the preregistered case expectation;
- canonical target ID matches;
- every evidence path exists in the actual deterministic packet;
- required grounding is present;
- a descendant evidence path such as `facts.administrative.value` may satisfy a requirement on `facts.administrative`.

The validator no longer pretends that substring matching can establish the semantic truth of natural-language prose. Prose semantic correctness is explicitly marked `EMPIRICAL_MANUAL_REVIEW` in the v0.5 artifact.

This does **not** weaken model authority boundaries. It removes an invalid claim of deterministic semantic validation.

## Authority boundary

Unchanged:

- model SQLite access = false;
- model calculation authority = ZERO;
- model state authority = ZERO;
- model canon authority = ZERO;
- entity normalization remains deterministic over the supplied projection;
- compact-query evidence remains deterministic and read-only;
- evidence paths must resolve against the actual tool packet;
- no world/campaign mutation.

## Retest requirement

Before claiming the bounded Mara synthesis seam PASS:

1. run `tests/test_e1_1_mara_epistemic_contract_v05.py` on Pixel;
2. run `e1_1_mara_grounded_synthesis_v05.py` against the unchanged Ceres projection;
3. retain all four audited cases;
4. inspect the resulting natural-language answers, not merely the structural PASS bits;
5. require no invented facts, causes, operators, events or world state.

A structural green result is necessary but not alone sufficient for the final empirical synthesis claim.
