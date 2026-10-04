# Build 5 Implementation Authorization 006 — Project Development Lifecycle Test 006A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “Go project lifecycle”  
**Scope:** governed execution of sponsor-entered DEVELOPMENT through staged construction WIP to OPERATING or FAILED

## 1. Authorized purpose

Implement the smallest FRD-aligned project-development lifecycle slice needed after Sponsor Test 005A.

The authorized causal slice is:

`Sponsor DEVELOP -> project DEVELOPMENT -> staged construction/WIP -> completion resolution -> OPERATING or FAILED`.

This slice governs physical/economic project execution. It does not create a new Agent role.

## 2. Runtime responsibility

Construction execution remains a SYSTEM process.

The sponsor remains the Agent that decides whether to enter DEVELOPMENT or ABANDON before development.

The construction/lifecycle SYSTEM may only act on:

- an explicit immutable development plan;
- project state;
- project cash;
- declared supplier/resource-allocation capacity;
- declared development-cost and schedule inputs;
- existing WIP state.

It shall not act on hidden resource truth.

## 3. Development plan contract

Each bounded development plan shall identify at minimum:

- stable plan id;
- project id;
- construction WIP id;
- commissioned asset id;
- supplier account;
- asset location;
- required development cost;
- explicit staged spending schedule;
- planned completion year;
- commissioned capacity;
- plan version.

The staged schedule shall reconcile exactly to required development cost.

No hidden default staging pattern is authorized.

## 4. Construction execution

A scheduled construction stage may spend only when:

- project status is DEVELOPMENT;
- the stage is declared by the immutable plan;
- the stage has not already executed;
- project cash is sufficient;
- applicable supplier/resource-allocation capacity is available.

A successful stage shall:

- move project cash to the declared supplier;
- create or add to the same persistent ConstructionWIP identity;
- record fixed-capital formation;
- preserve financing/source lineage;
- record stage outcome and causal event lineage.

A blocked stage shall not partially invent spending. It shall record a bounded blocked outcome and leave cash/WIP unchanged for that stage.

## 5. Completion resolution

At or after the declared completion year:

### OPERATING

The project may transition DEVELOPMENT -> OPERATING only when:

- accumulated net WIP equals the declared required development cost;
- all required stages were successfully spent;
- WIP has not already been commissioned or written off.

The lifecycle SYSTEM shall then:

- commission the WIP into a PRODUCTIVE asset;
- preserve book value;
- assign declared structural capacity;
- transition the project to OPERATING;
- record causal lineage.

### FAILED

If the project reaches completion resolution without satisfying the declared construction requirement:

- project state shall transition DEVELOPMENT -> FAILED;
- any remaining construction WIP shall be explicitly written off;
- no productive asset shall be created;
- unspent project cash remains cash;
- financial spending already incurred remains ledgered.

FAILED is therefore distinct from sponsor ABANDONED.

## 6. WIP write-off

The existing ConstructionWIP model shall be extended to represent explicit write-off.

WIP identity shall reconcile:

`accumulated_cost = commissioned + written_off + remaining_wip`.

A WIP write-off is an economic-value loss, not a reverse cash transaction.

A1-A9 accounting/physical checks shall be updated accordingly.

## 7. Hidden-world independence

Construction execution and completion shall not query hidden resource quantity.

Otherwise-identical construction plans and realized construction inputs shall produce the same OPERATING/FAILED result in hidden NULL and RICH resource worlds.

A NULL-world project may therefore become OPERATING if construction succeeds. Later extraction may reveal the economic consequences.

## 8. Structural qualification targets

Test 006A shall demonstrate:

1. Test 005A positive chain reaches DEVELOPMENT with financed project cash;
2. one persistent WIP identity receives staged expenditure across multiple years;
3. staged construction uses the declared development plan;
4. successful full construction commissions exactly one PRODUCTIVE asset;
5. project transitions DEVELOPMENT -> OPERATING only after commissioning conditions pass;
6. successful construction leaves no remaining net WIP;
7. a constrained stage produces a recorded blocked outcome rather than overspending;
8. incomplete construction at completion transitions DEVELOPMENT -> FAILED;
9. failed construction writes off existing net WIP;
10. FAILED creates no productive asset;
11. unspent project cash remains reconciled after failure;
12. hidden NULL/RICH resource truth cannot alter construction resolution when construction inputs are identical;
13. direct lifecycle mutation outside scheduler context remains blocked;
14. plan/project/WIP raw tampering between epochs is detected by persistent-state fingerprints;
15. A1-A9 remain satisfied after every lifecycle epoch;
16. chained deterministic replay remains exact.

## 9. Explicitly outside Test 006A

Not authorized by this slice:

- surface prospecting;
- geology-dependent construction success;
- autonomous extraction;
- resource-production operations;
- sales;
- operating-cost execution;
- reinvestment/distributions;
- depreciation policy beyond existing verified mechanics;
- repair/expansion;
- sponsor decisions from FAILED;
- CLOSED lifecycle semantics;
- transport/technology economics;
- empirical construction calibration;
- production forecasting;
- settlement dynamics.

## 10. Epistemic standing

All cost, stage, capacity and resource-allocation values used by Test 006A remain synthetic structural fixtures unless separately authorized.

Passing this test establishes lifecycle mechanics only. It does not validate real offworld construction costs, schedules, success rates or mining performance.
