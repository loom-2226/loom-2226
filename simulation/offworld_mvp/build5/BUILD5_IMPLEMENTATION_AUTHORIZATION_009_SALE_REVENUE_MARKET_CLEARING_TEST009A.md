# Build 5 Implementation Authorization 009 — Sale / Revenue / Market Clearing Test 009A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “Go... [review the adjacent research library; one is on markets] ... there could be some useful items to consider with sale/revenue/marketing”  
**FRD mutation:** NOT AUTHORIZED FOR THIS TEST  
**Scope:** bounded sponsor sale decision plus exogenous commodity-market clearing after realized extraction

## 1. Research intake standing

Advisory research inspected read-only:

- repository: `loom-2226/loom-research-lab`;
- commit: `80085a254be53bb46e290cd5ec802fc600e77bc2`;
- artifact: `projects/offworld_resource_economic_coupling/RESEARCH_BRIEF_v0.1.md`;
- classification: `RESEARCH / NON-CANON / NON-RUNTIME / NON-AUTHORITATIVE / NON-QUALIFICATION`.

The research brief does not modify or supersede the Offworld MVP FRD.

Test 009A borrows only interface ideas compatible with already-authorized MVP scope.

## 2. Research ideas admitted now

The following research conclusions are useful at current MVP resolution:

1. commodity clearing should remain a SYSTEM mechanism, not an Agent merely because it produces prices/transactions;
2. sponsor/operator Agents may respond to admitted market state;
3. physical inventory and monetary consideration must both reconcile;
4. a sale must clear against actual available inventory and declared demand;
5. market state must not expose hidden offworld scenario resource truth;
6. realized transactions should preserve commodity, quantity, price, counterparty/boundary and provenance;
7. same-period macroeconomic feedback should not be introduced casually.

## 3. Research ideas explicitly parked

Test 009A does not authorize:

- endogenous commodity pricing;
- multiple competing sellers/buyers;
- country policy Agents;
- tariffs, quotas or export controls;
- strategic stockpiles;
- guaranteed offtake or price support;
- subsidies, royalties or taxes;
- local-content requirements;
- alliance/preferential-access mechanisms;
- sanctions/strategic denial;
- cartels;
- processing/refining;
- transport/logistics;
- multi-country economic coupling;
- same-period macro feedback.

## 4. Authorized causal slice

Implement:

`realized offworld inventory -> admitted exogenous market state -> sponsor sale decision -> CommodityMarketSystem clearing -> physical inventory transfer -> revenue transaction -> project cash`.

The market shall not read hidden resource truth.

The sponsor shall not directly mutate market or financial state.

## 5. Market SYSTEM contract

Test 009A shall introduce an immutable versioned exogenous market envelope containing at minimum:

- market_state_id;
- year/period;
- resource/commodity id;
- buyer or clearing account id;
- unit price;
- demand quantity ceiling;
- currency unit;
- quantity unit;
- source/rationale reference;
- epistemic standing;
- version.

The structural fixture shall use an `EARTH_BOUNDARY` clearing account consistent with existing signed-boundary accounting.

A market envelope is a SYSTEM input, not an Agent.

## 6. Sponsor sale request/decision

The existing generic private sponsor/operator Agent shall use a bounded sale policy through the established:

`AgentState -> DecisionSnapshot -> isolated policy -> immutable decision -> scheduled SYSTEM consequence`.

Required admitted facts:

- `project.STATUS`;
- `inventory.AVAILABLE`;
- `market.UNIT_PRICE`;
- `market.REMAINING_DEMAND`.

The sponsor must also legitimately possess the relevant resource-information reference already used by the operating chain.

Required capability:

- `SELL`.

Required objective:

- `RETURN`.

Supported outcomes:

- `OFFER`;
- `DEFER`;
- `BLOCKED_UNKNOWN`.

## 7. Bounded sale-policy semantics

The Test 009A sale policy shall contain no arbitrary price threshold.

It may OFFER only when:

- Agent kind = `PRIVATE_SPONSOR`;
- objective includes `RETURN`;
- project state = `OPERATING`;
- relevant information is admitted;
- `SELL` capability exists;
- inventory is positive;
- unit price is positive;
- remaining declared market demand is positive.

The policy's offered quantity shall be the admitted available inventory.

The market SYSTEM, not the sponsor, determines actual cleared quantity subject to current physical inventory and remaining demand.

UNKNOWN required facts shall produce `BLOCKED_UNKNOWN` before worker execution.

## 8. Market-clearing rule

For one Test 009A clearing event:

`cleared_quantity = min(offered_quantity, current_offworld_inventory, remaining_declared_demand)`.

`transaction_value = cleared_quantity * exogenous_unit_price`.

A clearing event shall:

- reduce offworld resource inventory by cleared quantity;
- increase Earth-market resource inventory by cleared quantity;
- transfer transaction value from the signed Earth boundary account to project cash;
- record a REVENUE transaction;
- record the market envelope and sponsor-decision lineage;
- leave hidden/realized in-situ resource remaining unchanged.

No cleared quantity means no revenue.

## 9. Demand exhaustion

Remaining demand shall be derived from the immutable market envelope minus prior clearings under that same market-state id.

Multiple clearings may therefore exhaust but never exceed declared demand.

Changing price or demand requires a new market-state version/id rather than rewriting a completed clearing history.

## 10. Structural fixture

Test-only market state:

- unit price = `20 MODEL_CURRENCY_PER_RESOURCE_UNIT`;
- demand ceiling = `4 MODEL_RESOURCE_UNITS`;
- buyer = signed `EARTH_MARKET` boundary account.

These values are structural fixtures only.

They are not empirical commodity-market calibration or a forecast.

## 11. Required qualification cases

### RICH

Prior Test 008A extraction produces local inventory = `5`.

Sponsor offers `5`.

Declared demand = `4`.

Expected clearing:

- cleared = `4`;
- local inventory = `1`;
- Earth market inventory += `4`;
- revenue = `80`;
- project cash += `80`.

### SPARSE

Prior Test 008A extraction produces local inventory = `3`.

Sponsor offers `3`.

Declared demand = `4`.

Expected clearing:

- cleared = `3`;
- local inventory = `0`;
- Earth market inventory += `3`;
- revenue = `60`.

### NULL false-positive

Prior Test 008A extraction produces local inventory = `0`.

The market state remains identical, but the sponsor's fresh admitted inventory fact is zero.

Expected decision:

- `DEFER`;
- no clearing;
- no revenue.

This divergence is legitimate because it arises from realized post-extraction state, not hidden scenario leakage.

## 12. Physical and financial conservation

Test 009A shall demonstrate:

- local inventory decrease = cleared quantity;
- Earth market inventory increase = cleared quantity;
- transaction amount = cleared quantity * unit price;
- project cash increase = transaction value;
- signed Earth-boundary delta = negative transaction value;
- hidden/realized resource remaining is unaffected by sale;
- no sale can clear more than current local inventory or remaining market demand;
- A1-A9 remain satisfied.

## 13. Required hostile/falsification cases

Test 009A shall verify at minimum:

1. policy evaluation alone mutates no inventory or cash;
2. UNKNOWN price blocks before worker;
3. UNKNOWN demand blocks before worker;
4. no `SELL` capability prevents offer;
5. non-`OPERATING` project prevents offer;
6. zero inventory prevents offer;
7. zero/nonpositive price prevents offer;
8. zero demand prevents offer;
9. forged offer above inventory cannot create material;
10. forged offer above demand cannot exceed demand;
11. wrong resource/market-state linkage is rejected;
12. wrong buyer account kind is rejected;
13. duplicate clearing for one immutable decision cannot duplicate sale;
14. market state cannot see/use hidden resource truth;
15. sponsor policy hostile-access isolation remains intact;
16. local and Earth-market inventories are epoch-tamper-detectable;
17. deterministic replay is exact.

## 14. Revenue destination

Test 009A revenue shall enter the project's cash account, not bypass directly to sponsor personal cash.

This preserves later separation between:

- project revenue/cash;
- operating needs/reserves;
- owner/sponsor distributions;
- financier returns;
- local reinvestment;
- return to Earth.

The later question of “who gets a cut?” therefore remains a separate surplus/distribution decision rather than being hard-coded into sale clearing.

## 15. Explicitly outside scope

Test 009A does not authorize:

- surplus/dividend distribution;
- debt service;
- sponsor/financier return allocation;
- reinvestment policy;
- market-price formation;
- demand response to price;
- repeated dynamic price feedback;
- country/sector macro effects;
- transport or delivered-market location conversion;
- processing/refining;
- empirical price/demand calibration;
- production or economic forecasting.

## 16. Epistemic standing

Passing Test 009A establishes structural sale/revenue/clearing mechanics only.

Research-library material remains advisory and non-authoritative.

The FRD remains unchanged by this authorization.
