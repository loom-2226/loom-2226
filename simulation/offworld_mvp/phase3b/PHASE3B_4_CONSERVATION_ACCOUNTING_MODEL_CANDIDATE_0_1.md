# Phase 3B.4 — Conservation and Accounting Model Candidate 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / DESIGN CANDIDATE

## 1. Financial conservation

MVP financial state uses explicit accounts and double-sided transactions. Every payment has a source and destination. A sale requires seller, buyer or clearing account, quantity, price rule and balanced transfer.

`EARTH_MARKET_v0` may be an external clearing boundary, but not an unledgered source of cash.

## 2. Earth capital-access boundary

Earth `INVESTMENT_REAL_PROXY` is modeled economy-wide GFCF flow on a constant-2015-USD-scale proxy basis. It is not cash. Therefore the FRD shorthand `P_c(t)=f I_c(t)` is not directly executable.

Required semantic chain:

`Earth investment proxy -> authorized capital-access bridge -> realized financing source/capacity -> allocation transaction -> actor account`.

The bridge must define basis, allocation rule, source/counterparty, units, displacement versus additionality, timing, public/private allocation, constraints and EarthImpactLedger treatment.

## 3. OWNER DECISION GATE

The economic meaning of that bridge cannot be selected as a technical default.

**A. Diverted-investment interpretation:** a scenario-authorized fraction of BAU investment proxy becomes offworld financing and creates an equal negative Earth-realized investment impact.

**B. Financing-capacity-index interpretation:** the Earth investment proxy only scales a separately authored financing pool. The pool is scenario/model state, not literal diverted GFCF.

**C. Explicit financing endowment:** the MVP receives separately authored public/private financing, using Earth reference only for scale/context. This avoids converting GFCF proxy into cash but weakens the FRD's direct capital-origin coupling.

This choice changes simulation meaning. Owner selection is required before the capital bridge, financial fixture or complete vertical slice can be frozen.

## 4. Resource conservation

For a resource identity, physical state reconciles initial quantity, remaining quantity, cumulative extraction and explicit physical loss. Extracted quantity reconciles inventory created plus modeled extraction loss. Economic reserve may change with technology/economics without changing physical mass.

## 5. Population conservation

Absent explicit births/deaths/transit mortality, migration conserves total realized population. Earth departure and offworld arrival are paired causal mutations. Earth reference remains immutable; EarthImpactLedger records the realized delta.

## 6. Ownership and project conservation

Assets/inventory/accounts have declared ownership. Transfers occur through events. Project spending reconciles transactions; installed/consumed materials reconcile inventory. Failure may destroy economic value but cannot erase historical flows.

## 7. External boundaries

External MVP boundaries remain ledgered and named. External does not mean unaccounted.

## 8. Future executable checks

The implementation must check financial reconciliation, resource/inventory balance, population migration balance, ownership transfer, project funding limits, and EarthImpactLedger reconciliation.
