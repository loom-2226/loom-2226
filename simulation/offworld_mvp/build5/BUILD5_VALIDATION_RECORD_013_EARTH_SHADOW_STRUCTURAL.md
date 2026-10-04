# BUILD 5 VALIDATION RECORD 013 — EARTH SHADOW STRUCTURAL

Status: **STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED**

## Authority

Parent compaction head: `00b8568672f2115ee893cee8eb7f805af3408a5f`  
Authorization commit: `ea9d169`  
Initial implementation commit: `29ed8b157bf8b460f72f5435e62f65599624ffb6`  
Final executable candidate: `8a7dfacfb977cad9af356eaddf2a498c1b767a32`

Guiding FRD blob remained `1e4ebc11e2fde81f7dad87732bd6d563229ce935` and was not modified.

## Earned behavior

Test 013A extends the existing `EarthImpactLedger` into the FRD-required shadow
accounting layer. It records realized Earth/offworld consequences without modifying
Earth reference state or feeding impacts back into Earth propagation.

The explicit shadow channels are:

- capital diverted to offworld activity;
- capital returned to Earth;
- offworld purchases from Earth;
- Earth purchases from offworld ventures;
- migration from Earth;
- returning population;
- existing qualifying Earth-supplied expenditure;
- existing terrestrial FCF displacement.

Shadow classification is a derived SYSTEM/accounting consequence of already-realized
transactions or population movement. It emits no additional transaction and makes no
Agent decision.

The returning-population channel is structurally explicit but remains zero in Test
013A because no return-transport transition has yet been authorized. Test 013A does
not invent one merely to populate the field.

## Classification seam

The executable classification rules are bounded to already-known transaction purposes:

- Earth -> offworld `DISBURSE`, `PUBLIC_SUBSIDY`, or `OTHER_INVESTMENT` -> capital diverted;
- offworld -> Earth `RETURN_TO_EARTH`, `FINANCIER_RETURN`, or `OWNER_DISTRIBUTION` -> capital returned;
- offworld -> Earth `CAPEX`, `EXPLORATION`, `OPEX`, or `TRANSPORT_PAYMENT` -> offworld purchase from Earth;
- Earth boundary purchase from an offworld project-cash seller -> Earth purchase from offworld;
- realized Earth population decrement in the existing direct migration path or Test
  012 transport departure -> migration from Earth.

Other same-side transfers are not silently classified.

## Structural fixture

Canonical RICH fixture shadow output:

Year 1:

- capital diverted to offworld: `40`
- offworld purchases from Earth: `20`
- qualifying Earth-supplied expenditure: `20`
- terrestrial FCF delta: `-20`
- other Test 013 channels: `0`

Year 2:

- capital returned to Earth: `5`
- Earth purchases from offworld: `10`
- migration from Earth: `3`
- returning population: `0`
- other Test 013 channels: `0`

The fixture emits exactly four economic transactions and preserves total population at
`1000`. The adopted reference lineage remains `EARTH_REFERENCE_TEST013A_v1`; authored
reference FCF remains `100` before and after realized flows.

The same realized flow sequence produces the same shadow result under NULL, SPARSE and
RICH hidden-resource universes, demonstrating that shadow classification follows
realized causal state rather than hidden scenario truth.

## Hostile coverage

Test 013A verifies that:

1. shadow classification does not emit duplicate transactions;
2. same-side Earth/Earth and offworld/offworld transfers do not create shadow categories;
3. an Earth-boundary payment to a terrestrial seller is not mislabeled as an offworld purchase;
4. Earth reference lineage and reference-FCF input remain unchanged;
5. cash and population conservation remain intact;
6. shadow-state tampering changes the methodology/epoch fingerprint;
7. Test 012 passenger departure records Earth migration without changing its transport semantics;
8. returning population remains explicit zero rather than an invented return transition;
9. NULL/SPARSE/RICH hidden truth does not change classification when realized flows are held fixed.

## Regression history

Pre-candidate focused accounting/schema tests:

- 10/10 passed.

Committed initial candidate focused suite across schema, settlement, transport,
Earth-shadow, Kernel, Build 3/4 and accounting edges:

- 77/77 passed.

The first full governed run executed 295 tests and found one runtime-governance failure:
`earth_shadow_at` and `record_earth_migration` were newly public but unclassified by
the scheduled-execution API guard. No simulation/accounting assertion failed.

The fix made the migration recorder private (`_record_earth_migration`) and classified
`earth_shadow_at` as read-only. Targeted scheduled-runtime/schema/shadow regression on
the final candidate then passed 18/18.

## Final governed regression

Command:

`python3 -m unittest discover -s tests`

Executed on final executable candidate:

`8a7dfacfb977cad9af356eaddf2a498c1b767a32`

Result:

- 295 tests executed
- 295 passed
- 0 failures
- 0 errors
- runtime 427.919 s

## Executable provenance

Filesystem executable source-tree SHA-256:

`613bc542a5f05395bd73ee04498e08107b7773b39600c0e7726482bb8d41d5a9`

Git-object reconstructed executable source-tree SHA-256:

`613bc542a5f05395bd73ee04498e08107b7773b39600c0e7726482bb8d41d5a9`

Standing: `GIT_OBJECT_VERIFIED`.

## Size / bloat check

Executable Python LOC (`offworld_kernel/**/*.py`):

- compacted parent: `10,014`
- Test 013 final candidate: `10,128`
- net runtime growth: `114` lines (`1.14%`)

The full branch diff also contains the authorization, ODD schema reconciliation, one
52-line test fixture, and 80 lines of Test 013 tests. No parallel Earth macroeconomic
model was introduced.

## FRD / ODD standing

Guiding FRD diff from the compacted parent: `0` lines.

The executable ODD was reconciled to schema registry `ODD_SCHEMA_REGISTRY_0_15` and
records Test 013A shadow-accounting semantics.

## Explicitly not earned

Test 013A does not earn:

- Earth macroeconomic feedback or propagation;
- GDP, fiscal, monetary, labor, price, exchange-rate or sectoral response;
- endogenous Earth demand;
- conversion of reference FCF into spendable cash;
- a new Earth Agent or policy;
- return-trip transport or nonzero returning population;
- empirical calibration of displacement coefficients;
- coupled Earth/offworld macroeconomies.

## Conclusion

Test 013A structurally closes the minimal Earth-reference / realized-Earth shadow
accounting seam required by the MVP while preserving the adopted Earth reference as
immutable input authority.
