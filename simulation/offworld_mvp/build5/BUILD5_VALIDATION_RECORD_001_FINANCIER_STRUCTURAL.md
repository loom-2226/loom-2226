# Build 5 Validation Record 001 — Autonomous Financier Structural Test

**Status:** STRUCTURAL PASS / PARAMETER AUTHORIZATION PENDING / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Branch:** `offworld-mvp-build5-autonomous-financier`
**Implementation head originally validated:** `4045201018e4c35266cd17fe62a08234099eef8b`
**Current branch head re-verified:** `1a4c854a364f1646367356ba1ab883727d170b6f`
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_001_FINANCIER_TEST001.md`

## 1. Result

The first bounded autonomous private-financier implementation is executable and passes its structural, isolation, behavioral, replay, and accounting tests.

It is **not yet a final Test 001 PASS** because the consequential policy parameter values used by the verification fixture remain explicitly `TEST_ONLY`, not project-owner-authorized policy baseline values.

No synthetic fixture value has been promoted by repeated use.

## 2. Regression result

Originally executed on `quantifactus` at implementation head `4045201018e4c35266cd17fe62a08234099eef8b` and re-executed from a fresh detached worktree at current branch head `1a4c854a364f1646367356ba1ab883727d170b6f`.

The governed suite is run from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`

Current live re-verification result:

**117 tests executed; 117 passed in 8.208 seconds.**

This includes all inherited Build 3/4 verification tests and the new Build 5 autonomous-financier tests.

Between the original implementation head and the current re-verification head, Git shows only two added Markdown records:

- `simulation/offworld_mvp/build5/BUILD5_VALIDATION_RECORD_001_FINANCIER_STRUCTURAL.md`;
- `simulation/offworld_mvp/build5/BUILD5_FINANCIER_POLICY_PARAMETER_PROPOSAL_0_1.md`.

No executable file changed in that interval.

## 3. Executable identity

Original implementation Git commit:

`4045201018e4c35266cd17fe62a08234099eef8b`

Current re-verification Git commit:

`1a4c854a364f1646367356ba1ab883727d170b6f`

Executable `offworld_kernel` source-tree SHA-256 at the current re-verification head:

`48393762bf0f151c826e4734d9c8caf0e73a9205b27a20a19e311bba7202014c`

Git-object source-tree SHA-256:

`48393762bf0f151c826e4734d9c8caf0e73a9205b27a20a19e311bba7202014c`

Git-object reconstructed source-tree SHA-256 at the current re-verification head:

`48393762bf0f151c826e4734d9c8caf0e73a9205b27a20a19e311bba7202014c`

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

The executable hash is unchanged from the original implementation head because the intervening commits are documentation-only.

## 4. Policy identity

Policy:

`FINANCIER_SCREENING_V1`

Policy semantics:

`MVP_VALIDATION_RETURN_PROXY_V1`

Test-only parameter-manifest hash:

`b4bf09605f4f48a07957b5bbf561ba33cf887ad2c0e68b3df722a9ef7f8de535`

Policy version, binding policy source and parameter manifest:

`FINANCIER_SCREENING_V1:0.1:3014a328a26629fe635c4b19cbf63846fa8a3dd818cb3f21081ad7dc6626c9d9`

The policy source is under the hashed executable tree:

`phase3b/kernel/offworld_kernel/policies/financier_v1.py`.

## 5. Pure policy boundary

The supported policy interface is:

`policy(serialized DecisionSnapshot, serialized FinancingRequest, serialized policy manifest, decision_key) -> decision payload`

Execution occurs in an isolated Python subprocess using serialized inputs.

The policy receives no kernel, scheduler, world-resource registry, run identity, universe identity, hidden resource state, or world random state.

The source-admission gate rejects forbidden imports, forbidden I/O/introspection calls, dunder access, and executable top-level policy statements.

The runtime worker denies policy-time imports and direct file access.

The hostile-access probe attempted access to:

- world/kernel state;
- world seed/hidden state;
- wall clock;
- system randomness;
- environment;
- filesystem;
- network.

Observed leak set:

`{}`.

## 6. UNKNOWN behavior

The request declares required dependencies:

- PRICE;
- EXPLORATION_CAPEX;
- DEVELOPMENT_CAPEX;
- OPERATING_COST;
- LEAD_TIME;
- belief `resource_exists`;
- prior `resource_exists`.

Missing required underwriting, belief, or prior state produces:

`BLOCKED_UNKNOWN / BLOCKED_REQUIRED_INPUT_UNKNOWN`.

The worker is not invoked when the protocol-level UNKNOWN gate blocks the request.

## 7. Information equivalence

NULL / SPARSE / RICH labels cannot affect a decision when the admitted snapshot, request, parameter manifest, and decision key are identical.

The regression suite supplies the same admitted state under all three hidden-world labels and requires identical formal `FinancingDecision` objects.

Therefore hidden-world identity alone does not affect the financier.

## 8. Controlled divergence and metamorphic behavior

Using the Test 001 binary observation model with prior 0.20:

- POSITIVE signal -> admitted belief `0.5` -> `APPROVE / APPROVED_POLICY_RULE`;
- NEGATIVE signal -> admitted belief `0.05882352941176470588235294118` -> `REJECT / BELOW_RETURN`.

Metamorphic tests also require, holding other admitted inputs fixed:

- higher PRICE cannot worsen the decision;
- lower DEVELOPMENT_CAPEX cannot worsen the decision;
- lower OPERATING_COST cannot worsen the decision.

The favorable/unfavorable fixtures produce at least one actual decision change, so a constant policy does not pass merely through weak monotonicity.

Explicit `ALWAYS_APPROVE` and `ALWAYS_REJECT` negative controls fail the behavioral-adequacy discrimination gate.

## 9. Decision branches

The policy exercises and tests:

- `APPROVED_POLICY_RULE`;
- `BELOW_RETURN`;
- `CEILING`;
- `CONCENTRATION`;
- `DEFER_MORE_INFORMATION`;
- `BLOCKED_REQUIRED_INPUT_UNKNOWN`.

A decision artifact cannot mutate world state.

An approved decision creates financing only in the later scheduled commitment/disbursement transition.

## 10. Observation-model knowledge

The test-only manifest declares:

`PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION`.

For the fixture:

- world detection rate = 0.80;
- Agent-believed detection rate = 0.80;
- world false-positive rate = 0.20;
- Agent-believed false-positive rate = 0.20.

The manifest validator requires exact equality when that relation is declared.

This means the Agent knows the observation likelihood model exactly. It does **not** know hidden resource truth.

## 11. Accounting / scheduler integration

The APPROVE case proceeds:

`DecisionSnapshot -> policy -> FinancingDecision(APPROVE) -> scheduled finance executor -> Commitment -> Disbursement`.

The validation fixture then checks A1 through A9.

All nine pass.

The REJECT case creates no commitment or disbursement and also passes A1 through A9.

Integrated runs remain scheduler-mediated and replay deterministically.

Replay provenance now separately carries:

- underwriting table manifest identity;
- policy/version/parameter manifest identity;
- Git/code linkage;
- scheduler/execution/result fingerprints.

## 12. Parameter-ensemble diagnostics

The fixture reports:

`blocked_request_share = 0.3333333333333333333333333333`

for the deliberately mixed known/UNKNOWN diagnostic set.

For a +0.01 local perturbation of the test hurdle rate around a deliberately near-threshold case:

`decision_flip_share = 0.5`

and:

`hurdle_rate flip share = 0.5`.

These are diagnostic fixture statistics, not estimates of real-world frequencies or uncertainty.

## 13. Remaining gate

The current parameter manifest is deliberately:

`TEST_ONLY / NOT_POLICY_BASELINE`.

Current synthetic fixture values are:

| Parameter | Fixture value | Unit | Sensitivity | Local perturbation |
| --- | ---: | --- | --- | ---: |
| hurdle_rate | 0.20 | DIMENSIONLESS_ANNUAL_RATE | 0.05–0.40 | 0.01 |
| horizon_years | 10 | YEARS | 5–20 | 1 |
| agent_detection_rate | 0.80 | PROBABILITY | 0.60–0.95 | 0.02 |
| agent_false_positive_rate | 0.20 | PROBABILITY | 0.05–0.40 | 0.02 |
| normalized_throughput | 10 | MODEL_RESOURCE_UNIT_PER_YEAR | 5–20 | 1 |
| max_concentration_fraction | 0.80 | DIMENSIONLESS_SHARE | 0.50–1.00 | 0.05 |

These values have **not** been interpreted as authorized by the statement "Agent authorized", because that statement authorized implementation, not unspecified numbers.

A final Test 001 PASS requires an explicit project-owner act authorizing these values or replacements.

## 14. Standing

Build 5 autonomous-financier code is now implemented and structurally verified.

Current standing remains:

- PRE-CONTRACT;
- SINGLE-AUTHORITY;
- NOT_EMPIRICALLY_VALIDATED;
- AUTONOMOUS FINANCIER IMPLEMENTATION AUTHORIZED;
- POLICY PARAMETER BASELINE NOT YET AUTHORIZED.
