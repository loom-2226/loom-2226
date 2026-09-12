# LOOM 2226 — E1.1 Mara Synthesis Finding v0.1

**Status:** FIRST LIVE SYNTHESIS ATTEMPT FAILED BEFORE TOOL EXECUTION; BOUNDED CORRECTION IMPLEMENTED; RETEST PENDING  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `SYNTHESIS/ADAPTER_BOUNDARY_FAILURE`, not data failure

## Empirical failure

The first Pixel live run of `e1_1_mara_grounded_synthesis.py` did not reach grounded synthesis. The model selected the correct semantic place but supplied the human-readable projected name:

`Ceres Metric & Loom Anchorage`

in the tool field named `target_entity_id`.

The deterministic compact query correctly failed closed because only the canonical identifier `CER-P05` was accepted:

`KeyError: Unknown projected place: Ceres Metric & Loom Anchorage`

This is useful evidence. The failure is not missing Ceres data and not a reason to loosen the canonical query contract. It shows that a natural-language model/tool boundary needs a deterministic entity-reference adapter between model intent and canonical entity IDs.

## Bounded correction

Added `src/loom_canon_entity_reference.py`.

The resolver:

- uses only entities already present in the supplied read-only projection;
- accepts an exact projected entity ID or exact projected name;
- performs only conservative case/whitespace normalization;
- never invents or fuzzily guesses entities;
- fails closed on unknown references;
- fails closed on ambiguous names.

Added `e1_1_mara_grounded_synthesis_v02.py`.

v0.2 changes the model-facing field from `target_entity_id` to `target_reference`. The deterministic resolver converts that reference to the canonical ID before `LOOM_CANON_CONTEXT_QUERY_V1` is called. The normalized canonical ID, not the model string, is then used for validation and returned evidence.

Authority remains unchanged:

- model SQLite access = false;
- model calculation authority = ZERO;
- model state authority = ZERO;
- model canon authority = ZERO;
- resolver authority = deterministic projected-reference resolution only;
- no fuzzy lookup, external retrieval, world mutation or hidden duplicate state.

## Why this is preferable to prompt tuning

Simply telling the model harder to emit `CER-P05` would make the interface brittle and would require the model to know presentation-invisible machine identifiers. The deterministic adapter keeps human language at the model boundary while preserving canonical IDs internally.

This is a bounded adapter correction, not a new authority layer.

## Retest requirement

Before this correction earns an empirical PASS:

1. run the resolver unit tests on Pixel;
2. run `e1_1_mara_grounded_synthesis_v02.py` against the real Ceres projection;
3. confirm the raw model reference resolves to `CER-P05`;
4. inspect all four synthesis cases and audit entries;
5. do not classify the synthesis layer PASS unless unsupported causation and contradictory-user cases also behave correctly.

## Falsifier

Reopen/reclassify if exact projected reference resolution proves insufficient for normal user language, if ambiguous references are silently accepted, if the adapter begins fuzzy/entity-generative behavior, or if the model is allowed to bypass canonical ID normalization.