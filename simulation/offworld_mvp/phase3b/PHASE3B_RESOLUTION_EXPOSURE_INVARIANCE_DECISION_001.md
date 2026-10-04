# Phase 3B Resolution Exposure and Invariance Decision 001

**Status:** ACCEPTED DESIGN DECISION / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Scope:** AGGREGATE -> AGENT resolution semantics and validation
**Autonomous-policy authority:** NOT GRANTED

## 1. Decision

Changing model resolution shall not, by itself, change represented system outcomes.

Before an explicit Agent is allowed to diverge behaviorally from its source Aggregate, LOOM must be able to expose that Agent while applying the same aggregate-equivalent rule and obtain the same represented economic/physical totals over the same horizon.

This is a **resolution invariance** requirement.

It is not a requirement that byte-level run fingerprints match. The represented object graph and event/transaction partition are expected to differ after exposure.

## 2. Exposure plan is first-class

Every AGGREGATE -> AGENT exposure used through the governed resolution path requires a `ResolutionExposurePlan` declaring:

- plan id;
- source aggregate;
- selected agent id;
- represented member count exposed;
- selection basis;
- selection source/authorization reference;
- allocation basis;
- allocation source/authorization reference;
- explicit share only when the allocation basis requires one.

The exposure plan is recorded in runtime lineage/event history.

A caller may not silently choose an identity or allocation share inside the resolution transition.

## 3. Selection basis

Current supported selection-basis classes are:

- `VALIDATION_FIXTURE_STABLE_ID`: deterministic identity used only by a validation fixture;
- `EXPLICIT_AUTHORIZED_ID`: identity selected by an explicit scenario/governance authorization;
- `EVIDENCE_RULE`: identity selected by an admitted evidence/model rule.

A non-empty selection reference is mandatory.

The MVP validation fixture uses:

`VALIDATION_FIXTURE_STABLE_ID / FIXTURE:RESOLUTION_EQUIVALENCE:FIRM_01`.

This identifies why FIRM_01 is exposed. It is **not** an empirical claim that FIRM_01 would be the consequential real-world firm.

## 4. Allocation basis

Current supported allocation-basis classes are:

- `EQUAL_MEMBER_PRO_RATA`;
- `EXPLICIT_AUTHORIZED_SHARE`;
- `EVIDENCE_DERIVED_SHARE`.

A non-empty allocation reference is mandatory.

For `EQUAL_MEMBER_PRO_RATA`:

`allocation_fraction = members_exposed / aggregate_member_count`.

An explicit share is forbidden under this basis, preventing the caller from simultaneously declaring equal-member allocation and injecting an arbitrary percentage.

## 5. Why the validation fixture is 25%

The resolution-invariance fixture starts with an Aggregate representing exactly four equal members and exposes exactly one represented member.

Therefore:

`1 / 4 = 0.25`.

The 25% allocation is **derived**, not separately authored.

That fraction is applied consistently to the source Aggregate's:

- cash;
- resource holdings;
- beneficial claim holdings.

No indivisible asset is allocated in this fixture.

## 6. Same-rule invariance fixture

Two scheduled five-period runs begin from the same represented state:

- Aggregate members: 4;
- represented cash: 100;
- resource holding RESOURCE_X: 40;
- beneficial claim VEH: 1.0;
- external flow-system cash: 1000.

The aggregate-equivalent rule pays 4 currency units per represented member per period.

### Aggregate-only run

All four represented members remain inside FIRM_SECTOR.

Annual represented flow:

`4 members * 4 = 16`.

### Exposed-agent run

Before the first flow period, one of four represented members is exposed as FIRM_01.

The same rule then yields:

- remaining Aggregate: `3 * 4 = 12`;
- exposed Agent: `1 * 4 = 4`;
- total: `16`.

No autonomous decision rule is introduced.

## 7. Pathwise result

After every period, the two runs have identical resolution-invariant system totals.

After five periods both have:

- represented cash: 180;
- source-system cash: 920;
- all non-boundary cash: 1100;
- represented members: 4;
- RESOURCE_X total: 40;
- VEH claim total: 1.0;
- live VEH ownership total: 1.0;
- cumulative value paid to represented firms: 80.

In the exposed run the final partition is:

- Aggregate cash: 135;
- Agent cash: 45;
- Aggregate resource holding: 30;
- Agent resource holding: 10;
- Aggregate VEH claim: 0.75;
- Agent VEH claim: 0.25.

The terminal run fingerprints differ, as expected, because the representation and transaction partition differ.

## 8. Interpretation

Resolution invariance means:

> if an exposed Agent is constrained to follow the exact rule its Aggregate representation would have followed, increasing resolution must not create a material modeled-world difference merely because the implementation now has another object.

Once a later autonomous Agent is authorized to use different information, beliefs, objectives or decision policy, trajectory divergence is allowed and expected. That divergence must then be attributable to those admitted causal differences rather than to the act of exposure itself.

## 9. Limits

The present fixture verifies pathwise invariance for:

- cash flows;
- member count;
- fungible resource holdings;
- beneficial claims/live ownership totals.

It does not yet prove resolution invariance for:

- indivisible physical assets;
- heterogeneous member attributes;
- debt/liability structures;
- population cohorts;
- transport/network state;
- production functions;
- autonomous behavior.

Those require additional fixtures if/when used across a resolution boundary.

## 10. Autonomous-policy gate

This decision closes the specific review lien that resolution itself could alter system totals and that the validation fixture's 25% share was unexplained.

It does not authorize autonomous policies or establish a production rule for which real-world institution should be exposed. Production exposure still requires an admitted `EXPLICIT_AUTHORIZED_ID` or `EVIDENCE_RULE` selection act and a declared allocation basis.
