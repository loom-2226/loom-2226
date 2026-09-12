# LOOM 2226 — E1.1 Current-Place Handoff Empirical Closure v0.1

**Status:** PASS / EMPIRICALLY_TESTED  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**PR:** #110  
**Pre-closure branch head:** `bd552ee26779dea36bcf80071485f9898b301760`

## Question

Can Experience One hand the Navigator-owned current location into Canon Context without creating a merged authority, while:

1. surfacing unsupported locations honestly;
2. enforcing the temporal firewall between qualification state and 2226 canon;
3. allowing a positive Ceres control only when the temporal frame is explicitly compatible?

## Result

**PASS / EMPIRICALLY_TESTED.**

The Pixel run passed all preregistered cases and the unit regression passed all six tests.

This closes only the bounded current-place handoff seam. It does **not** qualify a generalized Experience Context merger, Mars Canon Context, or cross-era reference-canon composition.

## Pixel unit regression

Executed on the Pixel/Termux checkout after pulling PR #110 head.

Observed:

- `PASS: test_bad_operator_authority_fails_closed`
- `PASS: test_handoff_does_not_mutate_operator_context`
- `PASS: test_non_available_status_never_exposes_rejected_canon_payload`
- `PASS: test_supported_ceres_fails_closed_on_epoch_mismatch`
- `PASS: test_supported_ceres_positive_control_when_temporally_aligned`
- `PASS: test_unsupported_mars_surfaces_honest_human_boundary`

**ALL 6 TESTS PASS.**

## Pixel three-case discriminator

Harness:

`engineering/experience_one/spikes/e1_1_current_place_handoff.py`

Live campaign state:

`/storage/emulated/0/Download/LOOM_TEST/LOOM_STATE_V1.json`

Output artifact:

`/storage/emulated/0/Download/E1_1_CURRENT_PLACE_HANDOFF_RESULT.json`

Observed result schema:

`LOOM_E1_1_CURRENT_PLACE_HANDOFF_RESULT_V1`

### Case 1 — live unsupported location

Observed:

- case: `live_location_honest_miss`
- expected: `UNSUPPORTED_ENTITY`
- observed: `UNSUPPORTED_ENTITY`
- result: `PASS`
- human boundary: `Canon context is unavailable for the current location MARS.`

Interpretation:

Navigator remains location authority. Canon Context does not fabricate Mars material merely because a human-facing caller asks for context. The unsupported result survives to the human-facing boundary.

### Case 2 — Ceres epoch mismatch

Observed:

- case: `ceres_2027_temporal_firewall`
- expected: `TEMPORAL_MISMATCH`
- observed: `TEMPORAL_MISMATCH`
- result: `PASS`
- human boundary: `Canon context is unavailable because the campaign year 2027 does not match the canon reference year 2226.`

Interpretation:

A supported entity is not sufficient for composition. The temporal firewall is enforced before canon material is exposed. This preserves the same architectural principle already used elsewhere in LOOM: incompatible qualification/canon epochs must not be silently co-presented as one contemporaneous state.

### Case 3 — aligned Ceres positive control

Observed:

- case: `ceres_2226_positive_control`
- expected: `AVAILABLE`
- observed: `AVAILABLE`
- result: `PASS`
- human boundary: `Canon context is available for the current location CERES.`

Interpretation:

The handoff succeeds when both the entity and temporal frame are compatible, while Navigator still owns current location and Canon Context remains separately labeled read-only world/canon context.

## Authority result

The empirical run supports the following bounded claims:

- Navigator campaign state remains the sole current-location authority.
- Canon Context remains read-only world/canon context authority only for its supported/compatible projection.
- unsupported entity does not expose a fabricated canon payload;
- temporal mismatch does not expose a canon payload;
- human-facing refusal remains explicit rather than being smoothed into plausible prose;
- the handoff does not require a generalized Experience Context object;
- no model, browser, or projection layer gains calculation/state/canon mutation authority.

## Limits

This PASS does **not** establish:

- Mars Canon Context availability;
- a governed cross-era `reference canon` policy;
- permission to blend qualification-time state with 2226 world facts;
- natural-language Mara handling of these handoff statuses;
- a generalized multi-source context merger;
- completion of E1.1 as a whole.

## Next smallest seam

Preserve the current hard temporal firewall.

The next positive E1.1 work should use the disposable Ceres acceptance fixture rather than reinterpret the live Mars campaign state. The smallest next question is whether the existing deterministic Canon Context query surface can answer the preregistered Ceres questions (`What is this place?`, `What is interesting here?`) from the aligned acceptance fixture while preserving source/provenance and without introducing new canon.

Mara synthesis should consume only the already-qualified status/context packet and must surface `UNSUPPORTED_ENTITY` / `TEMPORAL_MISMATCH` honestly if those cases are later tested conversationally.

## Falsifier

Reopen this finding if any caller:

- exposes canon payload on `UNSUPPORTED_ENTITY` or `TEMPORAL_MISMATCH`;
- converts an unsupported/mismatched result into plausible world prose;
- silently treats 2027 qualification state as contemporaneous with 2226 Canon Context;
- lets Canon Context override Navigator current location;
- requires a merged shadow state to answer the bounded current-place question;
- mutates campaign or canon state through this handoff.
