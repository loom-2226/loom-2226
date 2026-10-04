# Build 5 Implementation Authorization 008 — Operating / Extraction Test 008A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “Go operating/extraction”  
**Scope:** bounded autonomous sponsor operating-cycle decision plus governed OPEX expenditure and physical extraction from an OPERATING project

## 1. Authorized purpose

Implement the smallest FRD-aligned operating/extraction slice after Test 006A.

The authorized causal chain is:

`OPERATING project -> sponsor operating decision -> operating finance if required -> fresh sponsor decision -> OPEX expenditure -> WORLD_SIM extraction -> realized resource depletion + offworld inventory`.

The sponsor remains the existing generic private sponsor/operator Agent.

No mining-specific Agent engine is authorized.

## 2. Generic Agent decision path

The bounded operating policy shall use:

`AgentState -> DecisionSnapshot -> isolated policy -> OperatingCycleDecision -> scheduled SYSTEM consequence`.

The policy may consume only admitted Agent-visible state and declared operating facts.

It shall not receive:

- hidden resource quantity;
- scenario resource registry;
- kernel;
- scheduler;
- world seed/random state;
- universe identity.

## 3. Operating request/decision contract

A bounded operating-cycle request shall identify at minimum:

- request id;
- year;
- project id;
- resource id;
- productive asset id;
- relevant admitted observation id;
- required fact keys;
- required belief/prior keys.

Required admitted facts for Test 008A:

- `project.STATUS`;
- `project.CASH_BALANCE`;
- `asset.CAPACITY`;
- `underwriting.OPERATING_COST`.

Required belief/prior key:

- `resource_exists`.

Supported bounded outcomes:

- `REQUEST_FINANCE`;
- `OPERATE`;
- `DEFER`;
- `BLOCKED_UNKNOWN`.

## 4. Bounded sponsor policy semantics

The Test 008A operating policy shall contain no arbitrary numeric behavioral threshold.

It may proceed only when:

- Agent kind = `PRIVATE_SPONSOR`;
- objective includes `RETURN`;
- project status = `OPERATING`;
- the relevant observation is legitimately possessed;
- current resource belief is greater than the Agent's own prior;
- productive asset capacity is positive;
- unit operating cost is KNOWN and nonnegative;
- required capabilities are admitted.

The planned production quantity is the admitted productive-asset capacity.

The planned operating-cycle cost is:

`planned_quantity * unit_operating_cost`.

If project cash is below that declared cost and the sponsor has `REQUEST_FINANCE`, the policy shall request the exact cash shortfall.

If sufficient cash exists and the sponsor has `OPERATE` and `EXTRACT`, the policy shall authorize the operating cycle.

If belief does not exceed prior, or project state/capability is unsuitable, it shall DEFER with explicit reason.

UNKNOWN required facts shall produce `BLOCKED_UNKNOWN` before policy-worker execution.

## 5. Working-capital recursion

Test 008A shall reuse the existing formal `FinancingRequest` and bounded financier policy for operating finance.

A sponsor `REQUEST_FINANCE` operating decision shall not itself create cash.

A later scheduled SYSTEM transition shall create the formal financing request for the exact operating-cash shortfall.

The existing financier then evaluates that request from its own admitted state and may approve/reject/defer under its existing Test-only policy.

A later sponsor epoch shall use a fresh snapshot reflecting any resulting project cash.

## 6. Structural fixture

To keep the operating-finance request inside the already qualified financier concentration ceiling, Test 008A may use a Test-only commissioned productive capacity of:

`5 MODEL_RESOURCE_UNITS_PER_OPERATING_CYCLE`.

Existing Test-only operating cost:

`4 MODEL_CURRENCY_PER_RESOURCE_UNIT`.

Therefore a full planned operating cycle costs:

`5 * 4 = 20 MODEL_CURRENCY`.

The Test 006A development cost remains `60`.

These values remain structural fixtures only.

## 7. Operating-cost execution

A scheduled operating SYSTEM shall spend authorized OPEX only when:

- project remains `OPERATING`;
- productive asset exists and is PRODUCTIVE;
- asset belongs to the project and is located at the project node;
- authorized planned quantity does not exceed asset capacity;
- project cash covers the full authorized operating-cycle cost;
- declared supplier/resource-allocation requirements are satisfied.

OPEX spending shall use an explicit double-sided transaction with `TxPurpose.OPEX`.

The operating cycle shall not create fixed capital.

## 8. Physical extraction resolution

Only a later WORLD_SIM extraction transition may consult realized/hidden remaining resource.

For Test 008A:

`actual_extracted = min(planned_quantity, resource.remaining)`.

The WORLD_SIM transition shall:

- reduce resource.remaining by actual_extracted;
- increase offworld resource inventory by the same amount;
- preserve resource conservation;
- record planned versus actual quantity and causal lineage.

No resource may be created when actual available resource is zero.

## 9. OPEX is paid for the attempted cycle

For the bounded Test 008A abstraction, the declared OPEX is paid for the attempted operating cycle based on planned capacity, not retroactively reduced to actual recovered quantity.

Therefore:

- RICH can spend full OPEX and recover full planned output;
- SPARSE can spend full OPEX and under-produce;
- NULL can spend full OPEX and recover zero.

This is a structural operating abstraction, not an empirical mining-cost model.

## 10. Hidden-world anti-cheating qualification

Test 008A shall include otherwise-equivalent positive-information worlds in which the sponsor/financier pre-extraction states are identical while hidden resource differs.

At minimum:

### RICH
Resource remaining >= planned capacity.

Expected physical result:
- full planned extraction.

### SPARSE
Resource remaining > 0 but below planned capacity.

Expected physical result:
- under-production capped by actual remaining resource.

### NULL false-positive
Resource remaining = 0 while prior admitted information remains sufficiently positive to produce the same operating decisions.

Expected physical result:
- identical sponsor operating decision;
- identical operating finance decision;
- identical OPEX spend;
- zero extraction;
- zero resource inventory increase.

Hidden resource may affect only the WORLD_SIM extraction result, not prior Agent decisions.

## 11. Physical and accounting identities

Test 008A shall demonstrate:

- resource depletion equals realized extracted quantity;
- offworld inventory increase equals realized extracted quantity;
- no negative remaining resource;
- planned quantity never exceeds productive capacity;
- OPEX cash transfer reconciles through A1-A9;
- zero-output NULL operation still records OPEX loss;
- extraction does not create revenue;
- sale remains a separate later action.

## 12. Required hostile/falsification cases

Test 008A shall verify at minimum:

1. non-OPERATING project cannot execute an operating cycle;
2. missing/wrong productive asset is rejected;
3. planned quantity above capacity is rejected;
4. missing `OPERATE` or `EXTRACT` capability prevents authorization;
5. UNKNOWN operating cost blocks before worker;
6. insufficient project cash causes exact finance request rather than extraction;
7. policy decision alone mutates neither cash nor resource;
8. hidden NULL/SPARSE/RICH truth cannot change sponsor or financier decisions when admitted state is identical;
9. zero hidden resource yields zero actual extraction;
10. partial hidden resource yields bounded partial extraction;
11. full hidden resource yields full planned extraction;
12. resource inventory and remaining stock reconcile;
13. OPEX is still spent in the zero-output NULL case;
14. A1-A9 pass;
15. repeated chained execution replays exactly;
16. raw operating/project/asset tampering between epochs remains detectable.

## 13. Explicitly outside Test 008A

Not authorized in this slice:

- resource sale/revenue;
- market demand/price clearing;
- profit/surplus distribution;
- debt service/dividends;
- reinvestment;
- operating shutdown/CLOSED semantics;
- repair/maintenance/expansion;
- stochastic equipment failure;
- detailed mining engineering;
- extraction grade/quality;
- transport/energy submodels beyond the declared operating-cost abstraction;
- empirical operating-cost calibration;
- settlement effects;
- production forecasting.

## 14. Epistemic standing

Passing Test 008A establishes structural operating/extraction mechanics only.

It does not validate real mine throughput, operating cost, recovery engineering, equipment reliability, geological grade, or production forecast accuracy.
