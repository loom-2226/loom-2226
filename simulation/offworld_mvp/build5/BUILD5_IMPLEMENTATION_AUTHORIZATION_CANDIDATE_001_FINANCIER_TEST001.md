# Build 5 Implementation Authorization Candidate 001 — Autonomous Financier Test 001

**Status:** CANDIDATE / NOT YET ACTIVATED / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Scope if activated:** first bounded autonomous private-financier vertical slice only

This candidate incorporates the hostile-review additions required before implementation begins.

## 1. Permitted implementation scope if activated

The first policy may:

- consume only a serializable immutable `DecisionSnapshot`;
- consume a formal immutable `FinancingRequest`;
- consume a versioned/hashes policy-parameter manifest;
- emit only a formal immutable `FinancingDecision`;
- use the deterministic decision key supplied through the policy interface.

The policy may not mutate world state. Commitment/disbursement remains a later scheduler/kernel transition.

All autonomous policy code shall reside under:

`simulation/offworld_mvp/phase3b/kernel/offworld_kernel/`

normally:

`offworld_kernel/policies/`

so it is covered by the executable source-tree hash.

## 2. Behavioral adequacy gate: identity is not enough

A constant policy can satisfy NULL/SPARSE/RICH information-isolation tests while exhibiting no meaningful decision behavior. Therefore Test 001 must include metamorphic and negative-control tests.

For cases in which all required inputs are KNOWN, define a comparable decision ordering for behavioral testing:

`REJECT < DEFER < APPROVE`.

`BLOCKED_UNKNOWN` is excluded from known-input monotonic comparisons.

Holding all other admitted inputs fixed:

- a more favorable admitted observation must produce a non-decreasing resource belief and must not lower the financing decision rank;
- a higher admitted PRICE must not lower the decision rank;
- a lower admitted DEVELOPMENT_CAPEX must not lower the decision rank;
- a lower admitted OPERATING_COST must not lower the decision rank;
- reverse perturbations must not improve the decision rank.

At least one deliberately favorable versus deliberately unfavorable pair must produce different decisions. This discrimination requirement prevents a constant policy from passing merely because "weak monotonicity" permits equality.

Negative controls:

- `ALWAYS_APPROVE` must fail the behavioral adequacy gate;
- `ALWAYS_REJECT` must fail the behavioral adequacy gate.

Passing accounting identities, replay, and information isolation is necessary but not sufficient for behavioral adequacy.

## 3. Hostile-access / policy-purity gate

The policy execution interface shall be a pure function of serializable admitted inputs:

`policy(snapshot, request, policy_parameters, decision_key) -> FinancingDecision`.

The policy shall not receive a kernel, scheduler, world object, resource registry, run identity, or world random state.

The hostile-access test must attempt and fail to:

- import or access world/kernel modules through the supported policy runner;
- read world seed or hidden state;
- read wall-clock or system time;
- use system randomness;
- read environment variables;
- perform filesystem I/O;
- perform network I/O.

The supported runner must enforce this boundary rather than merely rely on policy author discipline. If same-interpreter Python cannot enforce it credibly, Test 001 shall use a restricted subprocess or equivalent isolation mechanism over serialized inputs/outputs.

## 4. Policy parameter/version hash

The policy version hash shall bind both policy code and the complete parameter/belief-model manifest.

At minimum the manifest shall include:

- hurdle rate;
- investment horizon;
- agent observation-model detection rate;
- agent observation-model false-positive rate;
- any derived false-negative semantics;
- authorization reference for every parameter;
- unit;
- baseline value;
- sensitivity low/high;
- declared local perturbation used for knife-edge testing.

The policy manifest shall explicitly declare the relationship between:

- world observation-model likelihoods; and
- agent-believed observation-model likelihoods.

If agent likelihoods equal world likelihoods, this must be labeled explicitly as:

`PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION`.

That assumption means the Agent knows the sensor/observation likelihood model exactly. It does **not** mean the Agent knows hidden resource truth.

The policy-version fingerprint must change if code, hurdle, horizon, likelihood parameters, authorization references, or sensitivity bounds change.

## 5. Parameter-ensemble / knife-edge reporting

Test 001 shall run the policy across the declared parameter ensemble and local perturbations.

At minimum report:

`blocked_request_share = BLOCKED_UNKNOWN requests / total requests`

and:

`decision_flip_share = comparable requests whose decision outcome changes under the declared small parameter perturbation / comparable perturbed requests`.

Decision-flip share shall be reported by parameter as well as overall so a knife-edge hurdle, horizon, or likelihood assumption is visible.

The report shall also preserve the existing ensemble semantics:

- stochastic-key spread is variability;
- scenario spread is not probability;
- no probability weighting without explicit authority.

## 6. Information-equivalence and controlled-divergence tests

The original Build 5 Test 001 requirements remain.

Across NULL / SPARSE / RICH hidden worlds:

- identical admitted snapshots + identical request + identical policy parameters + identical decision key must produce identical FinancingDecision artifacts;
- hidden-world identity alone may not change a decision;
- after admitted observations/beliefs diverge, decisions may diverge only through those admitted differences.

Counterfactual tests shall change exactly one admitted input at a time and record the resulting decision difference or non-difference.

## 7. UNKNOWN gate

Required decision dependencies include:

- all five underwriting keys;
- required belief `resource_exists`;
- required prior `resource_exists`.

If any required dependency is UNKNOWN or absent, the policy must emit:

`BLOCKED_UNKNOWN / BLOCKED_REQUIRED_INPUT_UNKNOWN`

with the exact missing keys.

No required UNKNOWN may become zero, REJECT, or generic DEFER.

## 8. Reason-code gate

The decision protocol must support and test at minimum:

- `BELOW_RETURN`;
- `CEILING`;
- `CONCENTRATION`;
- `BLOCKED_REQUIRED_INPUT_UNKNOWN`;
- approval reason code;
- information-defer reason code.

Reason codes must be machine-auditable and tied to the admitted inputs/policy branch that produced them.

## 9. Time/unit gate

Underwriting price and cost inputs consumed by Test 001 must:

- carry explicit units;
- carry basis year;
- carry valid-from / valid-to years;
- be valid for the FinancingRequest year.

A timeless price/cost value is not admissible.

## 10. Accounting/replay gate

Build 5 entry already satisfies the scheduler-valid A1–A9 property prerequisite through Record 009.

Test 001 must additionally show that any approved decision which proceeds into commitment/disbursement/action state continues to pass:

- A1–A9;
- Build 4 invariants;
- scheduler-only mutation rules;
- replay determinism.

The replay manifest must carry:

- exact Git commit;
- executable code-tree SHA-256;
- verified commit/code linkage;
- policy version/hash;
- policy parameter-manifest hash;
- underwriting table id/version/fingerprint;
- input snapshot ids;
- scheduler/event/result fingerprints.

## 11. Pass condition

Build 5 Test 001 passes only if all of the following hold:

1. hidden-state isolation;
2. deterministic replay;
3. UNKNOWN blocking;
4. request/decision schema validity;
5. metamorphic monotonicity;
6. non-constant behavioral discrimination;
7. constant-policy negative controls fail;
8. hostile access/clock/I/O attempts fail;
9. parameter manifest is fully authorized and hashed;
10. observation-model knowledge relation is explicit;
11. ensemble blocked-share and flip-share metrics are reported;
12. A1–A9 and Build 4 invariants survive any resulting world transitions;
13. full replay provenance is complete.

## 12. Non-authorization

This document is a candidate only.

It does not yet authorize implementation of autonomous policy behavior. Activation requires an explicit project-owner authorization after review of this candidate.
