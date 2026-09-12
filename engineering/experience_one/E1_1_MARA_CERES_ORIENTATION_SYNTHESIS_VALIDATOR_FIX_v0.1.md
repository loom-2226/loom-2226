# E1.1 Mara Ceres Orientation Synthesis — Validator Fix v0.1

Status: IMPLEMENTED / PIXEL RETEST PENDING

## Triggering evidence

The first Pixel run of `e1_1_mara_ceres_orientation_synthesis_v01.py` produced semantically grounded prose, but structural validation failed with `evidence_path_not_in_packet`.

The model cited valid deterministic packet paths using conventional JSON-style list notation:

- `interesting.items[0]`
- `interesting.items[1]`
- `interesting.items[2]`

The v0.1 validator accepted dotted numeric list segments such as `interesting.items.0.name` but did not parse bracket indices. The failure therefore diagnosed a validator implementation defect, not a synthesis authority failure and not missing evidence.

## Change

A new historical-preserving harness `e1_1_mara_ceres_orientation_synthesis_v02.py` fixes only path validation.

Accepted deterministic path forms now include:

- `orient.facts.identity.value.summary`
- `interesting.items.0.name`
- `interesting.items[0].name`
- `interesting.items[0]`

Malformed brackets, negative indices, wrong container types, and out-of-range indices fail closed.

The v0.1 harness is left unchanged so the original empirical result remains reproducible.

## Authority invariants

Unchanged:

- model SQLite access: false
- model calculation authority: ZERO
- model state authority: ZERO
- model canon authority: ZERO
- deterministic fact selection
- deterministic place ranking
- campaign mutation: false
- canon mutation: false
- manual semantic review remains required

No grounding rule is relaxed. The validator is only taught to resolve valid list-index syntax already present in the deterministic evidence packet.

## PASS requirement

Do not close synthesis from implementation alone.

PASS requires:

1. Pixel unit tests for valid bracket paths, dotted compatibility, malformed paths, negative/out-of-range indices, exact v0.1 grounding shape, and invalid indexed evidence;
2. empirical rerun of v0.2 against the same Ceres projection;
3. `structural_pass: true`;
4. exact prose remains semantically grounded under manual review;
5. no authority invariant changes.

Until then: `SYNTHESIS_SEMANTICALLY_PROMISING / GROUNDING_VALIDATOR_RETEST_PENDING`.
