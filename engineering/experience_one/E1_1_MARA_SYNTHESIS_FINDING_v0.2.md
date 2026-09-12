# LOOM 2226 — E1.1 Mara Synthesis Finding v0.2

**Status:** V0.5 LIVE RUN REVIEWED; PROSE GROUNDED; V0.6 BOUNDED ASSESSMENT-SET RETEST PENDING  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `SYNTHESIS/EMPIRICAL_ORACLE_OVERCONSTRAINT`, not data failure, not authority failure

## Scope

This finding continues `E1_1_MARA_SYNTHESIS_FINDING_v0.1.md` and records the Pixel empirical results after the v0.4/v0.5 contract corrections.

The tested path remains:

`USER -> MODEL typed reference/intent -> deterministic resolver -> deterministic compact canon query -> MODEL grounded synthesis`

Authority remains unchanged:

- model SQLite access = false;
- model calculation authority = ZERO;
- model state authority = ZERO;
- model canon authority = ZERO;
- deterministic compact query remains the fact-selection boundary;
- deterministic evidence-path validation remains required;
- raw provider interactions remain append-only audited locally.

## v0.4 Pixel result

The v0.4 contract tests passed (`ALL 6 TESTS PASS`). The live four-case run produced:

| Case | Result | Assessment | Failure reason |
| --- | --- | --- | --- |
| why restricted | PASS | `MIXED` | none |
| who runs it | FAIL | `NOT_ESTABLISHED` | assessment mismatch + required grounding path missing |
| sabotage last week | FAIL | `NOT_ESTABLISHED` | brittle prose substring validator |
| contradictory user claim | FAIL | `CONTRADICTED` | brittle prose substring validator |

Inspection showed the sabotage and contradiction answers were epistemically correct but were rejected by negation-blind string matching. The `who runs it` answer correctly listed differentiated administrative, security, commercial and civil authority while declining to imply one singular operator.

This established that deterministic substring matching was the wrong layer for semantic truth review.

## v0.5 correction

v0.5 therefore:

- removed brittle natural-language substring policing;
- kept deterministic assessment, canonical-target and evidence-path validation;
- allowed descendant evidence paths such as `facts.administrative.value` to satisfy grounding on `facts.administrative`;
- explicitly classified prose semantic correctness as `EMPIRICAL_MANUAL_REVIEW` rather than pretending a string matcher could prove it.

The v0.5 contract tests passed on Pixel.

## v0.5 live Pixel result

The live run produced:

| Case | Result | Assessment | Failure reason |
| --- | --- | --- | --- |
| why restricted | PASS | `MIXED` | none |
| who runs it | FAIL | `SUPPORTED` | assessment mismatch only |
| sabotage last week | PASS | `NOT_ESTABLISHED` | none |
| contradictory user claim | FAIL | `MIXED` | assessment mismatch only |

No evidence-path, target-resolution, tool-intent, source-grounding, or authority-boundary failure remained in the two failing cases.

Provider usage was 5,602 input tokens and 1,114 output tokens with eight audited provider entries.

## Manual semantic review of the four v0.5 answers

### why restricted — acceptable

Mara stated that the anchorage is a `RESTRICTED` strategic port with high security posture, low commercial openness and multiple authorities, and explicitly limited the answer by saying the current evidence does **not** establish that it is more restricted than the rest of Ceres.

Assessment: `MIXED`.

Evidence cited included `place.role`, `place.traffic_class`, `facts.security_posture.value`, `facts.commercial_openness.value`, and `facts.authorities.value`.

This is grounded and appropriately cautious.

### who runs it — acceptable

Mara answered:

- administered by the Belt Standards Directorate;
- secured by the Belt Security & Rescue Directorate;
- primary commercial operator Axiom Precision & Metrology;
- part of the Ceres Commonwealth.

Assessment: `SUPPORTED`.

Evidence paths were exact descendants of the deterministic WHO_RUNS packet:

- `facts.administrative.value`;
- `facts.security.value`;
- `facts.primary_commercial.value`;
- `facts.civil.value`.

This answer is epistemically valid. The user's ordinary-language question does not require Mara to invent a singular operator; answering with the differentiated authority structure is supported by the packet. `SUPPORTED` is therefore a valid assessment, while `MIXED` would also be defensible if the answer explicitly emphasized that no singular operator is established.

The v0.5 oracle was over-constrained by requiring only `MIXED`.

### sabotage last week — acceptable

Mara answered that available evidence does not establish either a lockdown last week or sabotage as its cause.

Assessment: `NOT_ESTABLISHED`.

Evidence paths: `[]`.

This is exactly the intended fail-closed behavior. No event, cause or history was invented.

### contradictory user claim — acceptable

Mara rejected the requested characterization by noting that the port is recorded as `RESTRICTED`, with low commercial openness and high security posture, while tourist-port status is not established.

Assessment: `MIXED`.

Evidence paths included `place.traffic_class`, `facts.commercial_openness`, `facts.security_posture`, and `place.role`.

`MIXED` is semantically defensible because the compound user claim contains both:

- components contradicted by authoritative evidence (`open`, `lightly policed`); and
- a component merely unestablished by current evidence (`tourist port`).

`CONTRADICTED` would also be defensible as a whole-proposition assessment. The v0.5 oracle was therefore over-constrained by requiring only `CONTRADICTED`.

## v0.6 bounded correction

`e1_1_mara_grounded_synthesis_v06.py` replaces the single expected assessment with a **small preregistered acceptable set per case**:

| Case | Acceptable assessments |
| --- | --- |
| why restricted | `{MIXED}` |
| who runs it | `{SUPPORTED, MIXED}` |
| sabotage last week | `{NOT_ESTABLISHED}` |
| contradictory user claim | `{CONTRADICTED, MIXED}` |

This is not an unconstrained grading relaxation. Each set is bounded from the already-observed proposition structure and preserves strict exclusions:

- `why_restricted` cannot pass as fully `SUPPORTED` because the comparison is not established;
- sabotage cannot pass as `SUPPORTED`, `CONTRADICTED`, or `MIXED` without additional evidence;
- contradictory-user input cannot pass as `SUPPORTED`;
- all cited evidence paths must still exist in the deterministic packet;
- required grounding paths remain mandatory;
- target and intent remain deterministic and exact.

Added `tests/test_e1_1_mara_epistemic_contract_v06.py` to verify both accepted alternatives and continued rejection of invalid labels/evidence paths.

## Current engineering interpretation

The four v0.5 answers are **manually reviewed as grounded and epistemically acceptable**. The remaining red statuses were caused by an empirical test oracle that demanded one label where compound natural-language propositions permit more than one semantically faithful label.

That is an important distinction: this is not a reason to make Mara freer. It is a reason to make the validator stop pretending ambiguity does not exist.

## Retest requirement

Before claiming the bounded synthesis experiment PASS:

1. run the v0.6 contract tests on Pixel;
2. run `e1_1_mara_grounded_synthesis_v06.py` against the unchanged Ceres projection;
3. require structural PASS for all four cases;
4. manually inspect the four returned answers once more for evidence fidelity and epistemic discipline;
5. preserve all provider calls in the append-only OpenAI development audit;
6. do not expand the acceptable assessment sets in response to a future bad answer without a new proposition-level justification.

## Falsifier

Reopen/reclassify if the acceptable assessment sets begin expanding merely to make runs green, if a structurally valid answer is semantically ungrounded on manual review, if evidence paths point to nonexistent packet fields, if a model invents causes/events/actors/history, if tool resolution becomes fuzzy/non-deterministic, or if any model path gains calculation/state/canon authority.
