# Build 5 Validation Record 009 — Sale / Revenue / Market Clearing Test 009A

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Branch:** `offworld-mvp-build5-sale-market-clearing`  
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_009_SALE_REVENUE_MARKET_CLEARING_TEST009A.md`  
**Executable anchor:** `7d5d76f0cbdfa4b1b38356a035c42d2ed983d629`  
**FRD mutation:** NONE

## 1. Result

Build 5 now implements a bounded sponsor inventory-sale decision followed by exogenous commodity-market clearing.

The verified causal slice is:

`realized extraction -> offworld inventory -> admitted market price/demand -> sponsor OFFER/DEFER decision -> CommodityMarketSystem clearing -> physical inventory transfer -> signed Earth-boundary payment -> project revenue`.

Sale does not create physical material.

Price does not create revenue by itself.

Revenue exists only when a clearing event transfers realized inventory and creates the corresponding financial transaction.

## 2. Research intake

The implementation was informed by the parked LOOM research library without promoting that research to runtime or FRD authority.

Advisory source:

- repository: `loom-2226/loom-research-lab`;
- commit: `80085a254be53bb46e290cd5ec802fc600e77bc2`;
- artifact: `projects/offworld_resource_economic_coupling/RESEARCH_BRIEF_v0.1.md`;
- source classification: `RESEARCH / NON-CANON / NON-RUNTIME / NON-AUTHORITATIVE / NON-QUALIFICATION`.

Research ideas used in Test 009A:

- keep commodity clearing as a SYSTEM rather than automatically making a market an Agent;
- expose market state to decision-bearing actors through a narrow typed interface;
- preserve both physical quantity and monetary consideration;
- constrain clearing by realized supply and declared demand;
- keep hidden scenario resource truth out of the market/policy interface;
- preserve provenance beneath later aggregation;
- avoid same-period macro feedback.

Research ideas deliberately not activated:

- endogenous commodity pricing;
- country-policy Agents;
- tariffs/quotas/export controls;
- stockpiles;
- strategic procurement/offtake;
- subsidies/taxes/royalties;
- local-content rules;
- alliances/sanctions/cartels;
- processing/refining;
- transport/logistics;
- multi-country economic coupling.

## 3. FRD preservation

The Test 009A branch was diffed against its parent operating/extraction head:

`41a96d783345f419ee2df008f5f75ee5d36b29fe`.

There is no diff to:

`simulation/offworld_mvp/OFFWORLD_MVP_GUIDING_FRD.md`.

The ODD/executable schema was updated because Test 009A adds executable interfaces.

The guiding FRD was not modified.

## 4. Generic Agent architecture preserved

The seller is the existing generic `PRIVATE_SPONSOR` Agent.

No seller-specific runtime class or market Agent was introduced.

The market is registered as:

`EARTH_MARKET_v0 / SYSTEM / EXTERNAL_COMMODITY_CLEARING`.

The bounded sponsor sale policy is:

`SPONSOR_SALE_V1`.

## 5. Sale policy identity

Policy semantic version:

`0.1`.

Policy semantics:

`BOUNDED_INVENTORY_OFFER_AGAINST_EXOGENOUS_MARKET_V1`.

Policy contract SHA-256:

`bd27674ddbf9404c9a7fc03c32a87461630d4d3125a3a90961e19019f175bbc9`.

Policy version:

`SPONSOR_SALE_V1:0.1:99d3dcdcbe6dffd1b558196a56b36cbe542fcd714a76d500fde8df57b0d0b79a`.

## 6. Sale request/decision contract

Test 009A adds immutable:

- `SaleDecisionRequest`;
- `SaleDecision`;
- `SaleDecisionOutcome`;
- `SaleReasonCode`.

Required admitted facts:

- `project.STATUS`;
- `inventory.AVAILABLE`;
- `market.UNIT_PRICE`;
- `market.REMAINING_DEMAND`.

Supported outcomes:

- `OFFER`;
- `DEFER`;
- `BLOCKED_UNKNOWN`.

## 7. Policy semantics

The sponsor policy contains no arbitrary price threshold.

It offers only when:

- Agent kind = `PRIVATE_SPONSOR`;
- objective includes `RETURN`;
- project = `OPERATING`;
- relevant resource information is possessed;
- capability includes `SELL`;
- realized inventory > 0;
- admitted exogenous unit price > 0;
- admitted remaining demand > 0.

When those conditions hold, offered quantity equals the admitted available inventory.

The sponsor does not determine actual cleared quantity.

## 8. Exogenous market envelope

Test 009A adds immutable `CommodityMarketEnvelope`.

The structural envelope contains:

- market-state id;
- year;
- resource id;
- buyer/clearing account;
- unit price;
- demand ceiling;
- currency/quantity units;
- source/rationale;
- epistemic standing;
- version.

Fixture:

- id = `MARKET-009A-1`;
- year = `10`;
- resource = `RES`;
- buyer = `earth_market`;
- buyer account kind = `EARTH_BOUNDARY`;
- price = `20 MODEL_CURRENCY_PER_RESOURCE_UNIT`;
- demand = `4 MODEL_RESOURCE_UNITS`;
- standing = `TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE`.

Envelope SHA-256:

`44dad8955ff8d35d03e0b620c6028bbfab8e3d914d8e47165219f4f445ea220a`.

## 9. Clearing rule

For an authorized OFFER:

`cleared_quantity = min(offered_quantity, current_offworld_inventory, remaining_declared_demand)`.

`transaction_value = cleared_quantity * exogenous_unit_price`.

The market SYSTEM:

- revalidates project/resource/market/counterparty linkage;
- caps clearing by current physical inventory;
- caps clearing by remaining immutable-envelope demand;
- reduces local inventory by cleared quantity;
- increases Earth-market inventory by cleared quantity;
- creates a signed-boundary REVENUE transaction;
- credits project cash;
- preserves decision/request/envelope lineage.

## 10. Demand exhaustion

Remaining demand is derived from:

`envelope demand - prior clearing quantity under the same market-state id`.

The envelope is immutable.

Completed clearing history is not rewritten to change price or demand.

A new economic assumption would require a new market-state id/version.

## 11. Market clearing record

Each successful sale creates immutable `MarketClearingRecord` containing:

- year;
- market-state id;
- actor;
- decision;
- project;
- resource;
- offered quantity;
- demand before;
- cleared quantity;
- demand after;
- unit price;
- transaction value;
- local inventory before/after;
- Earth-market inventory before/after;
- transaction id;
- causal event id.

## 12. RICH qualification case

Universe:

`RICH_PUBLIC_3`.

Prior Test 008A extraction:

`5`.

Sale decision:

`SDEC-5ce4b9ef5af28def92ec`.

Outcome:

`OFFER`.

Offered quantity:

`5`.

Market price:

`20`.

Declared demand:

`4`.

Clearing:

- cleared quantity = `4`;
- value = `80`;
- local inventory = `5 -> 1`;
- Earth-market inventory = `0 -> 4`;
- demand = `4 -> 0`;
- revenue transaction = `tx-000023`.

After sale:

- project cash = `80`;
- Earth market boundary = `-80`;
- hidden/realized resource remaining = `15`.

Sale does not alter remaining in-situ/recoverable resource.

## 13. SPARSE qualification case

Universe:

`SPARSE_PUBLIC_1`.

Prior Test 008A extraction:

`3`.

Sale decision:

`SDEC-a06f1314818b5094334e / OFFER`.

Offered quantity:

`3`.

Market price/demand remain the same:

- price = `20`;
- demand ceiling = `4`.

Clearing:

- cleared quantity = `3`;
- value = `60`;
- local inventory = `3 -> 0`;
- Earth-market inventory = `0 -> 3`;
- demand = `4 -> 1`.

After sale:

- project cash = `60`;
- Earth market boundary = `-60`;
- resource remaining = `0`.

## 14. NULL false-positive qualification case

Universe:

`NULL_FP_1`.

Prior Test 008A extraction:

`0`.

The same market envelope exists:

- price = `20`;
- demand = `4`.

The fresh sponsor sale snapshot legitimately contains:

`inventory.AVAILABLE = 0`.

Sale decision:

`SDEC-1ccd57ecd32fd49aca85`.

Outcome:

`DEFER`.

Reason:

`NO_SELLABLE_INVENTORY`.

No MarketClearingRecord is created.

No REVENUE transaction occurs.

After the attempted sale epoch:

- project cash = `0`;
- Earth market boundary = `0`;
- remaining demand = `4`;
- resource remaining = `0`.

The divergence from RICH/SPARSE is caused by realized post-extraction inventory, not hidden scenario access.

## 15. Revenue destination

Revenue is credited to:

`project_cash`.

It is not credited directly to the sponsor Agent account.

This preserves a later explicit decision boundary for:

- operating reserve;
- financier return;
- owner/sponsor distribution;
- local reinvestment;
- return to Earth;
- other uses of surplus.

Test 009A therefore does not prematurely answer distribution by baking ownership payouts into market clearing.

## 16. Signed Earth boundary

The Earth clearing account is an `EARTH_BOUNDARY` account.

A RICH sale of `80` produces:

- project cash `+80`;
- Earth boundary `-80`;
- boundary ledger/mirror `-80`.

A SPARSE sale of `60` produces the corresponding `+60/-60` pair.

The external boundary is not required to carry a fictitious pre-funded commercial cash balance.

## 17. Physical conservation

For every successful market clearing:

`local_inventory_before - local_inventory_after = cleared_quantity`.

and:

`market_inventory_after - market_inventory_before = cleared_quantity`.

No market clearing changes `ScenarioResource.remaining`.

A forged offer of `99` against local inventory `3` and demand `2` clears only `2`.

A forged offer of `99` against inventory `3` and demand `10` clears only `3`.

Thus neither Agent intention nor market demand can create physical material.

## 18. Demand conservation

Market demand cannot be over-cleared.

After RICH:

`4 -> 0`.

After SPARSE:

`4 -> 1`.

A second clearing under the same market-state id consumes only the remaining demand.

The same immutable sale decision cannot be cleared twice.

## 19. UNKNOWN and policy guards

Focused tests verify:

- UNKNOWN price -> `BLOCKED_UNKNOWN` before worker;
- UNKNOWN demand -> `BLOCKED_UNKNOWN` before worker;
- missing SELL capability -> `DEFER`;
- non-OPERATING project -> `DEFER`;
- zero inventory -> `DEFER`;
- nonpositive price -> `DEFER`;
- zero demand -> `DEFER`;
- policy evaluation alone mutates no inventory or cash.

## 20. World/system validation

The market SYSTEM rejects:

- wrong resource/market-envelope linkage;
- non-Earth-boundary buyer accounts;
- missing market envelope;
- mismatched sale year;
- missing/unauthorized sponsor information;
- duplicate clearing of the same sale decision.

The market envelope contains no hidden-resource field or scenario-resource handle.

## 21. Policy firewall

The sponsor sale policy executes through the existing isolated serialized-input worker.

Hostile probe access remains blocked for:

- kernel;
- scheduler;
- run/universe identity;
- hidden scenario resource registry;
- random/seed state;
- filesystem;
- network;
- environment;
- wall clock.

## 22. Persistent-state tamper protection

Both sides of the physical sale are already persistent fingerprinted state:

- local colony inventory;
- Earth-market inventory.

Focused tests demonstrate that raw mutation of either after a completed sale epoch causes the next decision-epoch boundary check to fail.

## 23. Accounting

A1 through A9 pass in:

- RICH sale;
- SPARSE sale;
- NULL no-sale epoch.

A8 recognizes the REVENUE payer as an Earth boundary.

The physical inventory transfer is additionally checked through the MarketClearingRecord identities.

## 24. Nine-epoch causal history

Test 009A extends the persistent chain to nine epochs:

1. public observation publication;
2. sponsor development-finance request;
3. financier development funding;
4. sponsor DEVELOP;
5. staged construction/commissioning;
6. sponsor operating-finance request;
7. financier operating funding;
8. sponsor OPERATE -> OPEX -> extraction;
9. sponsor sale decision -> market clearing.

Final epoch result fingerprints:

- RICH = `1066cd0bb211111bb963ffdaace5f920b7ba2e0c4bb524cd614ce2fea1c4143d`;
- SPARSE = `25f3595f34a93e1fcc90fd73c9d394a9dfcfe963b03821f02b19fa5ce8e16702`;
- NULL = `3e18b212e34ec19b929cd76334b6db3823057d9387c74181ed122d3c47b22065`.

## 25. Deterministic replay

Repeated complete RICH, SPARSE and NULL histories reproduce:

- sale DecisionSnapshot;
- sale decision;
- market-clearing record;
- financial transaction;
- physical inventories;
- decision-epoch records;
- terminal methodology fingerprint.

Replay is exact.

## 26. Executable identity

Executable `offworld_kernel` source-tree SHA-256:

`7ecbc281b5a0114385d0d63366d57857dd501f5c5131e107547cf35c9e8a37f0`.

Git-object reconstructed source-tree SHA-256:

`7ecbc281b5a0114385d0d63366d57857dd501f5c5131e107547cf35c9e8a37f0`.

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

## 27. Regression result

The governed kernel suite was executed from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`.

Result at the executable anchor:

**221 tests executed; 221 passed in 150.153 seconds.**

The preceding operating/extraction baseline contained 200 tests.

Test 009A adds 21 focused sale/market tests.

## 28. ODD standing

The executable ODD schema registry is advanced to include:

- sale request/decision types;
- sale outcomes/reason codes;
- commodity-market envelope;
- market-clearing record;
- associated unit contracts.

ODD narrative now records bounded exogenous market clearing as a SYSTEM mechanism.

The FRD is unchanged.

## 29. Not yet earned

Test 009A does not establish:

- endogenous price formation;
- price elasticity/demand response;
- multiple competing buyers/sellers;
- bid/ask matching;
- market-maker behavior;
- processing/refining;
- delivered transport costs;
- tariffs/quotas;
- strategic stockpiles;
- country policy;
- multi-country/sector macro coupling;
- surplus/dividend distribution;
- financier return allocation;
- sponsor distribution;
- reinvestment;
- shutdown/CLOSED;
- empirical commodity-market calibration;
- economic forecast validity.

## 30. Standing

Current earned standing:

- OPERATING / EXTRACTION TEST 008A: STRUCTURAL PASS;
- SALE / REVENUE / MARKET CLEARING TEST 009A: STRUCTURAL PASS;
- GENERIC SPONSOR SALE POLICY: PASS;
- COMMODITY MARKET AS SYSTEM: PASS;
- IMMUTABLE EXOGENOUS PRICE/DEMAND ENVELOPE: PASS;
- DEMAND-LIMITED CLEARING: PASS;
- INVENTORY-LIMITED CLEARING: PASS;
- PHYSICAL INVENTORY TRANSFER: PASS;
- SIGNED EARTH-BOUNDARY REVENUE: PASS;
- REVENUE TO PROJECT CASH: PASS;
- NULL ZERO-INVENTORY -> NO REVENUE: PASS;
- MARKET HIDDEN-TRUTH ISOLATION: PASS;
- RESEARCH-LIBRARY AUTHORITY FIREWALL: PASS;
- A1-A9: PASS;
- DETERMINISTIC REPLAY: PASS;
- ENDOGENOUS MARKET: UNEARNED;
- SURPLUS / RETURN DISTRIBUTION: UNEARNED;
- EMPIRICAL VALIDATION: UNEARNED;
- PRODUCTION / ECONOMIC FORECAST STATUS: UNEARNED.
