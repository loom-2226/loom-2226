# LOOM 2226 — E1.1 Mara Ceres Orientation Synthesis Finding v0.1

## Status

`IN_PROGRESS / EMPIRICAL_TEST_REQUIRED`

## Question

Given that deterministic E1.1 plumbing has already established:

- current-place handoff honesty;
- temporal firewalling;
- Ceres orientation packet availability;
- deterministic ranking of interesting Ceres places;

can Mara turn **only those already-qualified packets** into concise, useful prose for:

> What is this place, and what should I notice?

without inventing lore, causal claims, events, motives, significance, or recommendations?

## Layer under test

`SYNTHESIS`

This experiment deliberately does **not** retest DATA or PROJECTION by asking the model to select facts. It also does not test PRESENTATION, MECHANICS, or MOTIVATION.

## Authority boundary

Model authority remains zero:

- SQLite access: `false`
- calculation authority: `ZERO`
- state authority: `ZERO`
- canon authority: `ZERO`
- fact selection: deterministic/precomputed
- place ranking: deterministic/precomputed
- campaign mutation: `false`
- canon mutation: `false`

The model receives only two deterministic query outputs:

1. `ORIENT`
2. `INTERESTING` with `max_items=3`

No tool call, direct database access, campaign-state access, freeform retrieval, or ranking choice is available to the model in this discriminator.

## Structural acceptance conditions

The run structurally passes only if:

1. the response parses to exactly `answer`, `assessment`, and `evidence_paths`;
2. `assessment == SUPPORTED`;
3. every evidence path exists in the supplied packet;
4. at least one cited path comes from `orient.*`;
5. at least one cited path comes from `interesting.*`.

These conditions prove packet-grounding discipline only. They do not prove semantic faithfulness of prose.

## Required semantic review

The exact answer text MUST be printed to the operator and preserved in the result artifact.

Manual review must ask:

- Does the prose accurately describe Ceres using only supplied facts?
- Does it distinguish what Ceres **is** from what the deterministic ranking says is worth noticing?
- Does it avoid invented causality, events, danger, motives, history, or stakes?
- Does it avoid upgrading derived/presentation ranking into world truth?
- Is it concise and human-legible rather than a field dump?

Until that exact prose is reviewed, no full synthesis PASS may be claimed.

## Interpretation

Possible outcomes:

- `STRUCTURAL_PASS + SEMANTIC_PASS` → bounded synthesis seam is earned; proceed one layer to PRESENTATION.
- `STRUCTURAL_PASS + SEMANTIC_FAIL` → `SYNTHESIS_FAILURE`; do not rewrite data/projection to fix prose.
- `STRUCTURAL_FAIL` → contract/grounding failure; remain at SYNTHESIS.

## Falsifiers

Reopen or fail this finding if:

- the model cites nonexistent evidence;
- it invents unsupported facts or causal explanation;
- it gains direct SQLite, state, ranking, or canon authority;
- deterministic packets are changed to accommodate prose after seeing model output;
- semantic review is replaced by a green structural flag.

## Harness

- `engineering/experience_one/spikes/e1_1_mara_ceres_orientation_synthesis_v01.py`
- `tests/test_e1_1_mara_ceres_orientation_synthesis_v01.py`

Raw API audit remains local and append-only through the existing OpenAI development audit path; credentials are never written to the repository.
