# BUILD 5 IMPLEMENTATION AUTHORIZATION 013 — EARTH SHADOW TEST 013A

Status: AUTHORIZED / STRICT MVP / STRUCTURAL ONLY  
Parent: `00b8568672f2115ee893cee8eb7f805af3408a5f`  
Branch: `offworld-mvp-build5-earth-shadow`

## Purpose

Close the bounded FRD seam between immutable Earth reference state and realized
offworld-caused Earth consequences using a shadow accounting layer only.

`DeltaEarth(t) = Earth_realized(t) - Earth_reference(t)`

## Authorized machinery

Extend the existing `EarthImpactLedger` so it separately records:

- capital diverted to offworld activity;
- capital returned to Earth;
- offworld purchases from Earth;
- Earth purchases from offworld ventures;
- migration from Earth;
- returning population;
- existing qualifying Earth-supplied expenditure and terrestrial FCF displacement.

The ledger is SYSTEM/ACCOUNTING state. It is not an Agent and makes no decisions.
Existing realized transactions and population transitions are the causal source of
shadow entries. No shadow entry may itself cause economic or population behavior.

The adopted Earth reference remains represented by immutable run/input lineage and
existing authored reference-FCF constraints. Test 013A may read that lineage but may
not mutate the reference trajectory, convert reference FCF into cash, or feed shadow
impacts back into Earth propagation.

## Classification rules

- Earth -> offworld financing/subsidy/investment: capital diverted.
- offworld -> Earth return/distribution: capital returned.
- offworld -> Earth supplier expenditure: offworld purchase from Earth.
- Earth boundary purchase of offworld production: Earth purchase from offworld.
- realized Earth population decrement: migration from Earth.
- returning-population category is explicit in the ledger; nonzero return execution
  is not invented by this test and remains zero unless an already-authorized return
  transition exists.

A single realized flow may contribute to a physical/economic accounting measure such
as qualifying supplied expenditure and also to its shadow-category classification;
those are different views, not duplicate transactions.

## Forbidden

No Earth macro feedback, GDP propagation, price response, fiscal/monetary response,
endogenous Earth demand, new Agent, new policy, new transport direction, return-trip
transport, or calibration claim. The guiding FRD is frozen.

## Acceptance

Test 013A passes only if NULL/SPARSE/RICH and hostile fixtures prove classification,
no double-emission of transactions, immutable Earth-reference lineage, population and
cash conservation, epoch tamper detection, deterministic replay, schema reconciliation,
and full governed regression.
