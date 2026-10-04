# Phase 3B Kernel Validation Record 008 — Resolution Exposure and Pathwise Invariance

**Status:** PASS FOR ITEM 3 OF AUTONOMOUS-POLICY PRE-GATE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Development branch:** `offworld-mvp-phase3`
**Validated branch head before this record:** `cb896dda0b2129b99a379798135461a5a94c851e`
**Predecessor baseline:** `offworld-mvp-build4-mvp-r3-policy-firewall-2026-10-04` @ `5f3285b28e4ce05979afc52f29930f9966e79983`

## 1. Purpose

Close review item 3 before autonomous policy work:

- prove that increasing resolution by carving one explicit Agent out of an Aggregate does not itself change represented system totals when the Agent follows the same rule as the Aggregate;
- make the identity-selection and allocation-share basis explicit so the resolution transition cannot silently invent “25%”.

This record does not authorize autonomous behavior.

## 2. Test result

Executed on `quantifactus` from a fresh Git archive of `origin/offworld-mvp-phase3`.

`python3 -m unittest discover -s tests -v`

**66 tests executed; 66 passed.**

The new six resolution tests cover:

1. equal-member allocation derives the expected fraction;
2. equal-member allocation rejects an independently injected explicit share;
3. selection and allocation bases require source/authorization references;
4. explicit-share allocation requires an explicit share;
5. exposure reconciles cash, resources, claims and live beneficial ownership;
6. aggregate-only and exposed-Agent runs are pathwise resolution-invariant over the same five-period horizon.

## 3. First-class exposure plan

Added `ResolutionExposurePlan`.

Every exposure through the new plan path declares:

- plan id;
- source Aggregate;
- selected Agent id;
- represented member count exposed;
- selection basis;
- selection source/authorization reference;
- allocation basis;
- allocation source/authorization reference;
- explicit share only when the allocation basis requires it.

The runtime persists a `ResolutionExposureRecord` and an audit event containing the basis and derived allocation fraction.

## 4. Selection basis

The current classes are:

- `VALIDATION_FIXTURE_STABLE_ID`;
- `EXPLICIT_AUTHORIZED_ID`;
- `EVIDENCE_RULE`.

The invariance fixture uses:

- selection basis: `VALIDATION_FIXTURE_STABLE_ID`;
- selection ref: `FIXTURE:RESOLUTION_EQUIVALENCE:FIRM_01`.

This is explicitly a validation-fixture identity choice, not an empirical claim about which real firm would become causally significant.

## 5. Allocation basis

The current classes are:

- `EQUAL_MEMBER_PRO_RATA`;
- `EXPLICIT_AUTHORIZED_SHARE`;
- `EVIDENCE_DERIVED_SHARE`.

For equal-member allocation:

`fraction = members_exposed / aggregate_member_count`.

The fixture Aggregate represents four equal members and exposes one.

Therefore:

`1 / 4 = 0.25`.

The 25% share is derived. It is not separately authored.

Supplying `explicit_share=0.25` while claiming `EQUAL_MEMBER_PRO_RATA` is rejected.

## 6. Reconciliation at exposure

Before exposure the represented Aggregate holds:

- cash: 100;
- represented members: 4;
- RESOURCE_X: 40;
- VEH claim: 1.0;
- live VEH beneficial ownership: 1.0.

The exposure transfers 25% of fungible represented state to FIRM_01:

- cash: 25;
- represented members: 1;
- RESOURCE_X: 10;
- VEH claim: 0.25;
- live VEH ownership: 0.25.

The remaining Aggregate holds:

- cash: 75;
- represented members: 3;
- RESOURCE_X: 30;
- VEH claim: 0.75;
- live VEH ownership: 0.75.

Total represented state is unchanged by the resolution act.

## 7. Same-rule pathwise invariance

The comparison runs the same five-period horizon twice.

### Run A — aggregate only

FIRM_SECTOR represents all four members.

### Run B — exposed Agent

FIRM_01 is exposed before the first flow period. It remains constrained to the same aggregate-equivalent rule.

The common rule is a synthetic validation-only system flow of:

`4 currency units per represented member per period`.

Therefore each period:

- aggregate-only run: `4 * 4 = 16`;
- exposed run: Aggregate `3 * 4 = 12` + Agent `1 * 4 = 4` = `16`.

The test compares the complete declared resolution-invariant totals after **every period**, not merely the terminal state.

Pathwise equality is true for all five periods.

## 8. Terminal comparison

Both runs finish with:

- represented cash: **180**;
- source-system cash: **920**;
- all non-boundary cash: **1100**;
- represented members: **4**;
- RESOURCE_X total: **40**;
- VEH claim total: **1.0**;
- live VEH ownership total: **1.0**;
- cumulative value paid to represented firms: **80**.

The exposed run partitions represented cash as:

- FIRM_SECTOR: **135**;
- FIRM_01: **45**.

Resources partition as:

- FIRM_SECTOR: **30**;
- FIRM_01: **10**.

Ownership partitions as:

- FIRM_SECTOR: **0.75**;
- FIRM_01: **0.25**.

## 9. Different fingerprints are expected

The aggregate-only and exposed-Agent runs have different terminal/run fingerprints because:

- one run has an additional Agent;
- one has a resolution event;
- one partitions transactions across two represented recipients.

Observed final methodology fingerprints:

- aggregate only: `6fa69a381e6997ffcc1683613b0bfddbf31b88ab5019be4b358094a294a7c361`;
- exposed Agent: `018469ac28e66e1cf7de91208fe47bb2e2adbb9a8555410ddde943f5ea1a3cbf`.

Observed scheduled result fingerprints:

- aggregate only: `8d96e982dd64a70f9700d15a8121466dbda417ad43918f89985b5f92b3a4e975`;
- exposed Agent: `33ee094a7c4ff2a071cf68c9fdc8440801857e73704cc49c0ff4888fe52c7960`.

Resolution invariance therefore compares modeled-world totals, not byte identity.

## 10. Causal interpretation

The verified rule is:

> exposing a represented actor at higher resolution must not by itself alter the modeled trajectory when that actor is constrained to follow the exact behavior its Aggregate representation would have produced.

Later divergence is permitted only after an admitted difference in information, belief, objective, policy, capability or other causal state.

That distinction is required before autonomous policies can be interpreted as causing divergence rather than merely changing implementation resolution.

## 11. Scope limitation

This fixture establishes invariance for:

- cash;
- represented member count;
- fungible resource holdings;
- beneficial claims/live ownership;
- deterministic per-member system flow.

It does not establish invariance for:

- indivisible physical assets;
- heterogeneous member composition;
- debt/liability structures;
- population cohorts;
- production functions;
- transport/network state;
- autonomous Agent behavior.

Additional invariance fixtures are required if those state families cross a future resolution boundary.

## 12. Documentation

Added:

- `PHASE3B_RESOLUTION_EXPOSURE_INVARIANCE_DECISION_001.md`;
- `offworld_kernel/resolution.py`;
- `offworld_kernel/resolution_fixture.py`;
- `tests/test_resolution_invariance.py`.

Updated:

- `OFFWORLD_MVP_GUIDING_FRD.md`;
- `OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md`;
- methodology fingerprint/lineage to include exposure records.

## 13. Remaining autonomous-policy blockers

Review item 3 is closed at the stated verification level.

Still open:

1. ensemble reporting guardrails for probability/weighted summaries and stochastic-variability terminology;
2. authored underwriting tables for price/revenue basis, capex, operating cost and lead time;
3. scheduler-valid property/generative coverage of all required identities;
4. signed boundary-position mirror reconciliation;
5. held-out/out-of-sample validation disclosure;
6. full code/Git hash in replay manifest;
7. genuine multi-rate synchronization fixture beyond timestamp ordering;
8. true staged multi-year WIP expenditure before commissioning.

Reciprocal AGENT -> AGGREGATE re-aggregation remains deferred until needed.

## 14. Result

The act of exposing FIRM_01 no longer introduces a free 25% modeling choice in the validation path, and the same-rule comparison is pathwise invariant across the tested horizon.

**Autonomous policy authority remains closed.**
