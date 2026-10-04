# Build 5 Implementation Authorization 005 — Sponsor/Operator Agent Test 005A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “On to sponsor”  
**Normative runtime identity:** generic `AGENT / PRIVATE_SPONSOR`  
**Design shorthand only:** mining/resource sponsor-operator

## 1. Authorized purpose

Implement the smallest FRD-aligned autonomous sponsor/operator slice needed to demonstrate that a private sponsor can decide whether to advance, finance, defer or abandon a project from admitted information and project/economic state without access to hidden scenario truth.

The authorized causal slice is:

`public information -> sponsor DecisionSnapshot -> SponsorProjectDecision -> scheduled sponsor action -> FinancingRequest or project-state transition -> later financier epoch -> fresh sponsor epoch -> DEVELOP or ABANDON`.

## 2. Generic Agent requirement

The sponsor shall use the existing generic Agent architecture:

`AgentState -> immutable DecisionSnapshot -> isolated policy -> immutable decision -> scheduled SYSTEM transition`.

No sponsor-specific runtime engine or company-only Agent substrate is authorized.

`PRIVATE_SPONSOR` is a domain specialization of the generic `AGENT` contract.

## 3. Sponsor decision semantics

The bounded sponsor policy may use only admitted Agent-visible state, including:

- Agent kind;
- capabilities;
- objectives;
- information references;
- sponsor beliefs and priors;
- admitted project lifecycle state;
- admitted project cash;
- admitted development cost.

The initial bounded actions are:

- `REQUEST_FINANCE`;
- `DEVELOP`;
- `DEFER`;
- `ABANDON`;
- `BLOCKED_UNKNOWN`.

The structural Test 005A policy shall introduce no arbitrary probability threshold.

Its directional evidence rule may compare the sponsor's current admitted belief with its own admitted prior:

- no legitimately admitted relevant observation -> `DEFER`;
- current belief <= prior -> `ABANDON`;
- current belief > prior and project cash < known development cost -> `REQUEST_FINANCE` for the exact shortfall;
- current belief > prior and project cash >= known development cost -> `DEVELOP`.

This is a structural rule, not a claim about real mining-company behavior.

## 4. Project and financing boundary

The sponsor decision shall not directly mutate project state or financial state.

A later scheduled sponsor-action SYSTEM may:

- validate the sponsor's authority/capability and project state;
- create a formal `FinancingRequest` when the outcome is `REQUEST_FINANCE`;
- transition the project to `ABANDONED` when the outcome is `ABANDON`;
- transition the project to `DEVELOPMENT` when the outcome is `DEVELOP`.

Funding remains a separate financier decision and later financing SYSTEM consequence.

Proposal or financing approval shall not imply successful development.

Test 005A may transition to `DEVELOPMENT`; it does not yet commission productive assets or claim successful construction.

## 5. Hidden-world firewall

The sponsor policy shall not receive:

- scenario resource quantity;
- scenario/universe identity;
- world seed/random state;
- kernel;
- scheduler;
- hidden resource registry.

The sponsor may react only to legitimately admitted information/beliefs and explicit project/economic facts.

Otherwise-identical hidden NULL/RICH worlds with identical admitted sponsor state must produce identical sponsor decisions.

## 6. Required fact contract

Test 005A shall explicitly admit and version at least:

- `project.STATUS`;
- `project.CASH_BALANCE`;
- `underwriting.DEVELOPMENT_CAPEX`.

UNKNOWN required values block rather than silently becoming numeric defaults.

## 7. Multi-epoch structural target

The positive-information structural chain shall demonstrate on one persistent kernel:

1. a legitimate public observation is published to sponsor and financier;
2. sponsor's fresh snapshot reflects the publication;
3. sponsor autonomously emits `REQUEST_FINANCE`;
4. scheduled sponsor action creates a formal financing request;
5. a later financier epoch evaluates that exact request;
6. approved finance is disbursed through the existing governed financing path;
7. a later fresh sponsor snapshot sees funded project cash;
8. the same sponsor policy emits `DEVELOP`;
9. scheduled sponsor action transitions project state to `DEVELOPMENT`.

The negative-information structural chain shall demonstrate:

1. sponsor receives legitimate negative information;
2. sponsor belief falls to/below prior;
3. sponsor emits `ABANDON`;
4. scheduled sponsor action transitions the project to `ABANDONED`;
5. no financing request or project funding is created.

## 8. Explicitly outside Test 005A

Not authorized by this slice:

- real BHP/Rio/etc. calibration;
- surface prospecting;
- construction/WIP execution after `DEVELOPMENT`;
- extraction;
- sale;
- reinvestment;
- transport/technology economics;
- strategic competition;
- learning beyond existing belief mechanics;
- production forecasting;
- settlement behavior.

## 9. Structural pass conditions

Test 005A passes only if:

1. sponsor uses the generic Agent/DecisionSnapshot/PolicyContext path;
2. policy hostile-access isolation remains intact;
3. hidden world state cannot alter sponsor choice before distinguishing information;
4. legitimate positive information can cause `REQUEST_FINANCE`;
5. legitimate negative information can cause `ABANDON`;
6. financing request is created only by a later scheduled SYSTEM transition;
7. requested financing equals the admitted development-cost shortfall;
8. financier evaluates the sponsor-created request through the existing bounded policy;
9. financing consequence remains scheduler-mediated;
10. a fresh post-financing sponsor epoch can choose `DEVELOP`;
11. project-state transitions are governed and lineage-bearing;
12. `DEVELOPMENT` does not imply successful construction/operation;
13. UNKNOWN required inputs block;
14. A1-A9 and existing accounting invariants remain satisfied;
15. deterministic replay and epoch parent linkage remain intact.

## 10. Epistemic standing

All underwriting/project numbers used in Test 005A remain synthetic structural fixtures unless separately authorized.

Passing this test establishes sponsor/operator agency mechanics only. It does not establish empirical mining-company behavior, economic calibration, or forecast validity.
