# Build 5 Financier Policy Parameter Contract Candidate 0.1

**Status:** CANDIDATE / PRE-CONTRACT / SINGLE-AUTHORITY

The first autonomous financier policy shall not contain unversioned numeric constants for consequential behavior.

Each policy parameter record must contain:

- parameter id;
- semantic name;
- value;
- unit;
- authorization reference;
- epistemic/scenario status;
- sensitivity low/high;
- local perturbation for knife-edge testing;
- validity/version scope.

Minimum Test 001 parameters:

| Parameter | Unit | Required semantic role |
| --- | --- | --- |
| hurdle_rate | DIMENSIONLESS_ANNUAL_RATE | minimum required return |
| horizon_years | YEARS | decision evaluation horizon |
| agent_detection_rate | PROBABILITY | Agent-believed positive-signal rate when target exists |
| agent_false_positive_rate | PROBABILITY | Agent-believed positive-signal rate when target does not exist |

If the binary model represents false-negative rate separately, its relationship to detection rate must be explicit.

The parameter manifest shall also declare whether the Agent's observation-model likelihoods equal the world's observation-model likelihoods.

Exact equality requires the label:

`PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION`.

The policy version hash binds the canonical parameter manifest and policy code. Any change to value, bounds, perturbation, authorization reference, or likelihood-relation declaration changes the hash.

No baseline values are authorized by this candidate. They must be supplied through a later explicit authorization rather than invented in policy code.
