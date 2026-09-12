# E1.1 Mara Ceres Orientation Synthesis v0.2 — Empirical Closure

**Status:** PASS / EMPIRICALLY_TESTED  
**Layer:** SYNTHESIS  
**Scope:** bounded Ceres orientation synthesis only  
**PR:** #110  
**Branch:** `engineering/experience-one-e1-1-canon-context-projection-2026-09-12`

## Purpose

Close the bounded synthesis seam for the question:

> What is this place, and what should I notice?

The model receives only precomputed deterministic `ORIENT` and `INTERESTING` Canon Context query packets. It has no SQLite access, no campaign-state access, no ranking authority, no fact-selection authority, and no canon/state/calculation authority.

## Pixel empirical evidence

Runtime: Pixel / Android local qualification.

Unit tests:

- `test_path_exists_accepts_json_style_list_index` — PASS
- `test_path_exists_preserves_dotted_numeric_index_compatibility` — PASS
- `test_path_exists_rejects_malformed_brackets` — PASS
- `test_path_exists_rejects_out_of_range_and_negative_indices` — PASS
- `test_validator_accepts_exact_empirical_v01_grounding_shape` — PASS
- `test_validator_still_rejects_nonexistent_indexed_evidence` — PASS

Result: **ALL 6 TESTS PASS**.

Empirical run:

- schema: `LOOM_E1_1_MARA_CERES_ORIENTATION_SYNTHESIS_RESULT_V01`
- structural_pass: `True`
- structural_fail_reasons: `[]`
- assessment: `SUPPORTED`
- latency_s: `4.562`
- input_tokens: `1430`
- output_tokens: `255`
- output artifact: `/storage/emulated/0/Download/E1_1_MARA_CERES_ORIENTATION_SYNTHESIS_V02.json`

Evidence paths emitted by the model:

- `orient.facts.identity.value`
- `orient.facts.political_context.value`
- `orient.facts.transport_role.value`
- `interesting.items[0]`
- `interesting.items[1]`
- `interesting.items[2]`

## Exact empirical prose

> This is Ceres, a Belt logistics and exchange hub tied to family habitats, finance, certification, refining, cargo, construction, water, and reaction mass. Notice its network role: bulk materials, remass, commercial hulls, heavy repair, and Belt exchange. Key places are the highly trafficked Ceres Belt Exchange and Ceres Shipyard Arc, plus the restricted Ceres Metric & Loom Anchorage.

## Manual semantic review

**PASS.**

The prose remains inside the supplied deterministic evidence. It does not introduce unsupported events, motives, causal explanations, danger, significance claims, recommendations, or new lore. The named places and their restricted/high-traffic character are grounded in the supplied `INTERESTING` packet, while the Ceres role and context are grounded in the supplied `ORIENT` packet.

The previous v0.1 structural failure was a validator implementation defect: JSON-style list paths such as `interesting.items[0]` were valid evidence references but the validator accepted only dotted numeric list notation. v0.2 fixes that parser defect while preserving fail-closed behavior for malformed, negative, nonexistent, and out-of-range indices.

## Authority statement

This evidence does not alter authority boundaries:

- model SQLite access: `false`
- model calculation authority: `ZERO`
- model state authority: `ZERO`
- model canon authority: `ZERO`
- fact selection: deterministic/precomputed
- place ranking: deterministic/precomputed
- campaign mutation: `false`
- canon mutation: `false`

## Closure claim

For the bounded Ceres orientation question tested here, the synthesis seam is closed:

**deterministic Canon Context query packets -> grounded Mara prose**

This is not evidence that arbitrary world questions, unsupported locations, other epochs, or broader conversational synthesis are qualified. It does not close E1.1 as a whole.

## Next diagnostic layer

Per the E1.1 diagnostic precedence, the next unresolved layer is **PRESENTATION**: whether the user can discover, understand, and act on this grounded world context in the actual Experience One interface without being handed raw structured packets.
