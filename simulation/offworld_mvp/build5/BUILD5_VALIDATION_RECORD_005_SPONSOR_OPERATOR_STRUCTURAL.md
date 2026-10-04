# Build 5 Validation Record 005 — Sponsor/Operator Agent Test 005A

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Branch:** `offworld-mvp-build5-sponsor-operator`  
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_005_SPONSOR_OPERATOR_TEST005A.md`  
**Executable anchor:** `1ac0f3893d063d1f2c02df08683c8fbc257eb650`

## 1. Result

The first bounded autonomous sponsor/operator policy is executable and passes its structural, hidden-state isolation, multi-epoch, financing-request, project-state, accounting, provenance and replay tests.

The sponsor remains an ordinary generic LOOM `AGENT` with `AgentKind.PRIVATE_SPONSOR`.

No sponsor-specific runtime engine was introduced.

The verified positive causal chain is:

`public information -> sponsor belief -> REQUEST_FINANCE -> scheduled FinancingRequest -> financier decision -> scheduled funding -> fresh sponsor snapshot -> DEVELOP -> governed project transition to DEVELOPMENT`.

The verified negative causal chain is:

`public information -> sponsor belief -> ABANDON -> governed project transition to ABANDONED`.

## 2. Sponsor policy identity

Policy:

`SPONSOR_OPERATOR_V1`

Semantic version:

`0.1`

Policy semantics:

`DIRECTIONAL_EVIDENCE_PROJECT_ADVANCEMENT_V1`

Policy contract SHA-256:

`039866b751f3358bb0119a8c01684495013b9b01c05efbca3b87d157ab241f47`

Policy version:

`SPONSOR_OPERATOR_V1:0.1:cc8042ce14bbe0c44e5e6416c02de5ac967460ce08922b798768ce0d18929cdc`

The policy introduces no arbitrary numeric behavioral threshold.

Its structural rule is:

- no legitimately admitted relevant observation -> `DEFER`;
- admitted current resource belief <= sponsor prior -> `ABANDON`;
- admitted current resource belief > sponsor prior and project cash < known development cost -> `REQUEST_FINANCE` for the exact cash shortfall;
- admitted current resource belief > sponsor prior and project cash >= known development cost -> `DEVELOP`.

Action-specific capabilities are required.

This is a validation rule, not a claim about real mining-company decision behavior.

## 3. Generic Agent architecture preserved

The sponsor uses the existing generic path:

`AgentState -> DecisionSnapshot -> PolicyContext -> isolated sponsor policy -> SponsorProjectDecision -> later scheduled SYSTEM transition`.

The sponsor policy receives:

- generic Agent identity/kind;
- capabilities;
- objectives;
- information references;
- beliefs;
- priors;
- admitted project status;
- admitted project cash;
- admitted development cost.

It does not receive:

- kernel;
- scheduler;
- hidden resource quantity;
- scenario-resource registry;
- universe identity;
- world seed/random state.

The sponsor therefore remains compatible with the long-term generic Agent architecture rather than introducing a company-specific decision substrate.

## 4. Sponsor protocol

Test 005A adds immutable:

- `SponsorProjectDecisionRequest`;
- `SponsorProjectDecision`;
- `SponsorProjectDecisionOutcome`;
- `SponsorProjectReasonCode`.

Supported bounded outcomes are:

- `REQUEST_FINANCE`;
- `DEVELOP`;
- `DEFER`;
- `ABANDON`;
- `BLOCKED_UNKNOWN`.

Required admitted fact keys are:

- `project.STATUS`;
- `project.CASH_BALANCE`;
- `underwriting.DEVELOPMENT_CAPEX`.

Required belief/prior key:

- `resource_exists`.

UNKNOWN required inputs block before policy-worker execution.

## 5. World-side action boundary

The sponsor decision itself does not mutate world or project state.

A later scheduled `SPONSOR_ACTION_EXECUTOR` performs the admitted consequence.

For `REQUEST_FINANCE`, the SYSTEM creates and submits a formal Build 5 `FinancingRequest`.

For `DEVELOP`, the SYSTEM performs the bounded lifecycle transition:

`PROPOSED -> DEVELOPMENT`

or:

`EXPLORING -> DEVELOPMENT`.

For `ABANDON`, the SYSTEM performs:

`PROPOSED -> ABANDONED`

or:

`EXPLORING -> ABANDONED`.

Test 005A deliberately does not define later transitions from DEVELOPMENT, OPERATING, FAILED or CLOSED. Those remain separately governed work.

The sponsor decision id is carried as a causal parent of the resulting financing-request/project-transition event.

## 6. Executable identity

Executable `offworld_kernel` source-tree SHA-256:

`088956532608ccadb226a753f9b9901e37a55c45884a0dfee8ec2e5ddd350d5c`

Git-object reconstructed source-tree SHA-256:

`088956532608ccadb226a753f9b9901e37a55c45884a0dfee8ec2e5ddd350d5c`

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

## 7. Regression result

The governed kernel suite was executed from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`

Result at the executable anchor:

**157 tests executed; 157 passed in 24.735 seconds.**

The preceding decision-epoch baseline contained 146 tests.

Test 005A adds 11 focused sponsor/operator tests.

## 8. Positive four-epoch qualification chain

Fixture:

`RICH_PUBLIC_3`

The source public observation is:

`POSITIVE`.

The sponsor's post-publication admitted belief becomes:

`0.20 -> 0.50`.

### Epoch 1 — public information

The public institutional Agent publishes the legitimate observation to both:

- sponsor;
- financier.

Epoch result fingerprint:

`58fcbaa43787fe386da8dbdb5e87858070d6719de3274d2c2ea862f34d70ae01`

### Epoch 2 — sponsor requests finance

Sponsor decision:

`SDEC-5de34999a2023302c0ae`

Outcome:

`REQUEST_FINANCE`

Reason:

`POSITIVE_EVIDENCE_FINANCE_REQUIRED`

Project cash:

`0`

Known Test-only development cost:

`60`

Requested financing:

`60`

The request amount is the exact admitted shortfall:

`60 - 0 = 60`.

Epoch result fingerprint:

`78ecbd14b34568acd53d718d813115cbfad0c2930c633402b550c6dffd72cc02`

Its parent is exactly the Epoch 1 result fingerprint.

### Epoch 3 — financier responds

The existing bounded autonomous financier evaluates the sponsor-created financing request.

Outcome:

`APPROVE`

Scheduled financing consequence:

- financier cash: `100 -> 40`;
- project cash: `0 -> 60`.

Epoch result fingerprint:

`2bd527e3d86588f120df70ebf7f94b15d85de2f8f1712213b1ee4ced19d3d3c6`

Its parent is exactly the Epoch 2 result fingerprint.

### Epoch 4 — sponsor advances project

A fresh sponsor snapshot now observes project cash `60`.

Sponsor decision:

`SDEC-f358d59abe064230a27b`

Outcome:

`DEVELOP`

Reason:

`POSITIVE_EVIDENCE_FUNDED`

The later scheduled SYSTEM transition changes project state:

`PROPOSED -> DEVELOPMENT`.

Epoch result fingerprint:

`62089083b47caa56928bf438755e4527d624199ab1e999d1af7261fd8fa24979`

Its parent is exactly the Epoch 3 result fingerprint.

## 9. DEVELOPMENT does not imply construction success

At the end of the positive Test 005A chain:

- project status = `DEVELOPMENT`;
- project cash = `60`;
- productive/WIP asset count belonging to project `P` = `0`.

Therefore Test 005A's DEVELOPMENT state records the sponsor's governed decision to enter development.

It does not commission a mine, create productive capacity, imply successful construction, or transition to OPERATING.

This preserves FRD §20:

> proposal or funding shall not imply successful development.

## 10. Negative two-epoch qualification chain

Fixture:

`NULL_PUBLIC_1`

The source public observation is:

`NEGATIVE`.

Sponsor post-publication belief:

`0.20 -> 0.05882352941176470588235294118`.

### Epoch 1

Publication result fingerprint:

`0995672d28e70053f7e48fa7009710e6cfb465fa129d683ca6a74287bd3c5c04`

### Epoch 2

Sponsor decision:

`SDEC-27209cfcb95f947675a4`

Outcome:

`ABANDON`

Reason:

`NONPOSITIVE_EVIDENCE`

Scheduled project transition:

`PROPOSED -> ABANDONED`.

No financing request is created.

Final financial state:

- financier cash = `100`;
- project cash = `0`.

Epoch result fingerprint:

`122c380c9de568fc171ccb8ce4c5215a0e4ef99e83c65bde0acf3ba078b695d7`

Its parent is exactly the Epoch 1 result fingerprint.

## 11. Hidden-world isolation

Before publication, otherwise-identical RICH and NULL sponsor states produce identical:

- sponsor DecisionSnapshot;
- sponsor decision request;
- sponsor formal decision;
- isolated-worker fingerprint.

The pre-publication outcome is `DEFER` because the sponsor does not possess the relevant observation.

Thus hidden resource truth does not change sponsor behavior before distinguishing information legitimately reaches the Agent.

## 12. Financing-request integrity

The sponsor policy does not create a financing request.

Only the later scheduled sponsor-action SYSTEM may create it.

The formal financing request:

- references the sponsor;
- references the project;
- carries the requested amount;
- carries the development stage;
- discloses only an observation possessed by the sponsor;
- declares the existing Build 5 underwriting/belief/prior contract.

The sponsor-created request is the exact object later evaluated by the existing financier policy.

## 13. Exact-shortfall behavior

A separate fixture gives the project `20` units of existing project cash against a known Test-only development cost of `60`.

The sponsor requests:

`40`.

Thus the sponsor does not automatically request the full development-cost number.

It requests the admitted funding shortfall.

## 14. UNKNOWN behavior

When `underwriting.DEVELOPMENT_CAPEX` is UNKNOWN:

- policy worker is not invoked;
- outcome = `BLOCKED_UNKNOWN`;
- reason = `BLOCKED_REQUIRED_INPUT_UNKNOWN`;
- no financing request is created;
- no project-state transition occurs.

No numeric fallback is substituted.

## 15. Capability boundary

If the project requires financing but the sponsor lacks `REQUEST_FINANCE` capability:

- outcome = `DEFER`;
- reason = `CAPABILITY_OR_OBJECTIVE_BLOCK`;
- no financing request is created.

Likewise, funded project advancement requires admitted `DEVELOP` capability.

## 16. Hostile-access isolation

The sponsor policy executes inside the same isolated serialized-input policy worker used by the previously qualified Build 5 policies.

The hostile-access probe exposes no access to:

- kernel;
- scheduler;
- scenario resource registry;
- universe/run identity;
- world seed;
- hidden resource state;
- wall clock;
- system randomness;
- filesystem;
- environment;
- network.

## 17. Decision-to-world separation

A focused test evaluates the sponsor policy against a legitimate positive-information snapshot outside any sponsor action transition.

The policy returns `REQUEST_FINANCE`.

After policy evaluation alone:

- project status is unchanged;
- project cash is unchanged;
- no financing request exists.

Only the later scheduled SYSTEM transition creates the request or changes lifecycle state.

## 18. Decision lineage

Sponsor-created consequences retain explicit decision lineage.

The formal `REQUEST_FINANCE` event carries the sponsor financing decision id as a causal parent.

The `DEVELOP` transition event carries the later sponsor development decision id as a causal parent.

The `ABANDON` transition event carries the sponsor abandonment decision id as a causal parent.

## 19. Decision-epoch tamper hardening

Test 005A strengthens the Build 5 persistent-state fingerprint used by the decision-epoch runtime.

Agent serialization now includes all currently modeled Agent-visible/runtime fields, including:

- account id;
- capabilities;
- objectives;
- runtime class;
- decision policy;
- information;
- beliefs;
- priors;
- history;
- asset/resource/claim holdings;
- lineage refs.

The MVP fingerprint also includes project lifecycle/ownership state and commitment state.

Hostile tests demonstrate that raw changes to:

- sponsor capabilities; or
- project lifecycle status

between epochs are detected as persistent-state tampering before another epoch may open.

This closes a latent gap that became material once sponsor decisions depended on capabilities and project state.

## 20. Accounting

All four epochs in the positive chain preserve A1 through A9.

The publication, sponsor-request, sponsor-development and project-state transitions do not themselves create unbalanced financial flows.

The financing epoch uses the previously qualified commitment/disbursement path.

The negative chain creates no financing flow.

## 21. Replay

Repeated complete positive sponsor chains reproduce:

- all four decision-epoch records;
- parent result links;
- sponsor financing decision;
- financier decision;
- sponsor development decision;
- final methodology fingerprint.

Deterministic chained replay is structurally verified.

## 22. Parameter standing

Test 005A uses the existing PRE-CONTRACT authored underwriting validation table.

The structural development-cost fixture is:

`60 MODEL_CURRENCY`.

The public/financier observation-likelihood values remain Test-only Build 5 parameters.

None are promoted by this test to:

- empirical mining-company data;
- calibrated sponsor behavior;
- production underwriting inputs;
- forecast authority.

## 23. Not yet earned

Test 005A does not establish:

- surface prospecting;
- construction/WIP execution after DEVELOPMENT;
- DEVELOPMENT -> OPERATING;
- FAILED/CLOSED lifecycle rules;
- autonomous extraction;
- autonomous sale;
- autonomous reinvestment;
- transport/technology economics;
- real sponsor/operator calibration;
- production forecasting;
- settlement dynamics.

## 24. Standing

Current earned standing:

- PRIVATE FINANCIER AGENT TEST 001: STRUCTURAL PASS;
- PUBLIC EXPLORER TEST 002A: STRUCTURAL PASS;
- PUBLICATION / CROSS-AGENT TEST 002B: STRUCTURAL PASS;
- GOVERNED DECISION-EPOCH RUNTIME TEST 004: STRUCTURAL PASS;
- PRIVATE SPONSOR/OPERATOR TEST 005A: STRUCTURAL PASS;
- SPONSOR REQUEST_FINANCE DECISION: PASS;
- FORMAL SPONSOR-CREATED FINANCING REQUEST: PASS;
- EXISTING FINANCIER RESPONSE TO SPONSOR REQUEST: PASS;
- REPEATED SPONSOR DECISION AFTER FUNDING: PASS;
- SPONSOR DEVELOP / ABANDON DIVERGENCE: PASS;
- GOVERNED PROPOSED -> DEVELOPMENT: PASS;
- GOVERNED PROPOSED -> ABANDONED: PASS;
- DEVELOPMENT DOES NOT IMPLY CONSTRUCTION/OPERATION: PASS;
- SPONSOR HIDDEN-WORLD FIREWALL: PASS;
- SPONSOR POLICY HOSTILE-ACCESS ISOLATION: PASS;
- CAPABILITY/PROJECT-STATE EPOCH TAMPER DETECTION: PASS;
- A1-A9: PASS;
- DETERMINISTIC REPLAY: PASS;
- FULL PROJECT LIFECYCLE: UNEARNED;
- EMPIRICAL VALIDATION: UNEARNED;
- PRODUCTION FORECAST STATUS: UNEARNED.
