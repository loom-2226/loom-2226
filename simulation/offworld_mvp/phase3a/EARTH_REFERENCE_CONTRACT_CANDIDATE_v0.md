# EARTH REFERENCE CONTRACT CANDIDATE v0

**Status:** PRE-CONTRACT / CANDIDATE / SINGLE-AUTHORITY  
**Authority:** NOT Authority Contract v1 qualified  
**Role:** Read-only Earth reference interface for Offworld MVP  
**Implementation authority:** NOT GRANTED  
**Canon status:** NON-CANON simulation reference

## 1. Purpose and epistemic boundary

This contract exposes a deliberately narrow Earth reference trajectory for the Offworld MVP.

**The Earth reference model is not a claim of scientific fact about Earth's future.**

It is a simulation/reference scenario of Earth from 2026 through 2226 under the modeled trajectory **prior to any economic impact from off-world activity**. Its future values are projections and model-derived reference state, not observations and not predictions asserted to become true.

Its purpose is counterfactual accounting:

`Earth_reference_without_offworld_impact(t)`

provides the baseline against which later realized simulation state can measure consequences attributable to off-world activity.

Therefore:

`REFERENCE != REALIZED`

and

`MODEL_OUTPUT != OBSERVED_FACT`.

The reference must remain immutable during a simulation run. Off-world actions may change realized Earth state or create deltas relative to the reference, but may never rewrite the reference trajectory.

## 2. Contract objective

Provide only the Earth quantities required to initialize and contextualize Offworld MVP while preserving:

- temporal lineage;
- semantic field identity;
- units/basis;
- provenance;
- exception/fallback state;
- reference-versus-realized separation;
- blocking behavior for unsupported requests.

Raw PostgreSQL column access is not this contract.

## 3. Admitted concepts

v0 admits exactly four value concepts.

### BIOLOGICAL_POPULATION

Meaning: modeled biological-human population for country/area and year.

Unit: persons.

Important: after the biosynthetic transition this is specifically biological population. It is not synthetic-person population, recognized-person population, machine-task capacity, or total effective labor.

### VALUE_ADDED_REAL_PROXY

Meaning: modeled country value-added level on the inherited constant-2015-USD-scale real accounting basis.

Unit/basis: constant-2015-USD-scale model proxy units per year.

Not: literal future nominal USD, guaranteed purchasing power, cash, or physical capacity.

### INVESTMENT_REAL_PROXY

Meaning: modeled economy-wide investment/GFCF flow on the inherited real accounting scale.

Unit/basis: constant-2015-USD-scale model proxy units per year.

Not: government budget, corporate cash, investable fund, financing availability, or actor spending authority.

### CAPITAL_STOCK_REAL_PROXY

Meaning: reconstructed/model capital stock on the inherited real accounting scale.

Unit/basis: constant-2015-USD-scale model proxy stock units.

Not: liquid wealth, market capitalization, national balance-sheet cash, borrowing capacity, or physical capacity in engineering units.

## 4. Temporal reference resolver

The selected Earth reference is a composite trajectory.

| Years | Required derivation |
|---|---|
| 2026-2030 | V4_2026_2030 |
| 2031-2059 | V4_2031_2059 |
| 2060-2100 | V4_2060_2100 |
| 2101-2226 | BIOSYNTHETIC_2101_2226 |

A consumer may not substitute another historical trajectory merely because it contains the same ISO3/year.

The resolver is semantic contract behavior, not a database optimization.

## 5. Required assertion shape

A successful lookup returns a typed assertion equivalent to:

```
EarthReferenceAssertion {
  trajectory_id
  derivation_id
  concept
  iso3
  year
  world_context
  perspective
  value_state
  value
  unit_basis
  provenance
  exception_flags
  uncertainty_state
  replay_status
  reference_role
}
```

Required values for this contract include:

- `world_context = REAL` for empirical/source claims used in lineage, or the appropriate reference-model context for projected/model state;
- `perspective = GOVERNANCE` for contract retrieval;
- `reference_role = EARTH_PRE_OFFWORLD_REFERENCE`.

The final world-context encoding must conform to the Phase2 model and may not collapse observed/source evidence and projected reference state into one epistemic class.

## 6. Lookup semantics

Conceptual interface:

```
EarthReference.get(
    concept,
    iso3,
    year,
    use,
    world_context,
    perspective
) -> EarthReferenceAssertion | BLOCKED
```

A request is admitted only when:

1. concept is one of the four v0 concepts;
2. ISO3 belongs to the admitted economic/reference domain for that concept;
3. year is 2026-2226;
4. the temporal resolver identifies the selected derivation;
5. required lineage and basis metadata are available;
6. requested use is compatible with the concept.

## 7. BLOCKED behavior

The interface returns BLOCKED rather than fabricating, coercing, silently falling back, or changing concepts when:

- concept is not admitted;
- year is outside admitted range;
- requested country/concept combination is outside coverage;
- temporal derivation cannot be resolved;
- requested use requires semantics the reference does not provide;
- a caller requests actor-spendable money directly from INVESTMENT_REAL_PROXY;
- a caller requests liquid financing from CAPITAL_STOCK_REAL_PROXY;
- a caller requests generic population where biological/synthetic/personhood distinction matters;
- required provenance or basis cannot be established.

UNKNOWN and BLOCKED remain distinct. Absence of an admitted assertion must not become zero.

## 8. Exception preservation

Historical/model exception state must survive retrieval.

At minimum the implementation metadata must be capable of preserving:

- source fallback/imputation;
- factor-share fallback;
- post-WEO TFP-anchor fallback;
- replacement underfunding;
- reconstruction/repair lineage;
- temporal-regime transition;
- any later exception shown to affect an admitted concept.

Exception metadata does not automatically invalidate a reference value. It tells the consumer what kind of modeled assertion it is.


## 8A. Source aberrations, remediation, and non-fabrication

The selected Earth reference contains documented remediations where source-data or source-to-model semantics produced pathological modeled state.

These remediations must not be described as tuning countries toward desired outcomes. They are lineage events responding to identifiable source-data aberrations or invalid source-to-model transformations. The original source observations remain preserved.

### Nigeria investment provenance

The frozen 2026 Nigeria seed inherited an OECD-ICIO fallback investment/value-added ratio of approximately **30.704%** because the ordinary national WDI GFCF/GDP source path was unavailable in that seed construction.

That fallback was not evidence that Nigeria's long-run investment rate should be 30.704%. It was a source-coverage fallback whose repeated use became materially consequential when propagated over the long horizon.

The later baseline architecture replaced that provenance with the governed national WDI GFCF/GDP policy, using the declared same-series pooled-median imputation when a direct WDI rate was unavailable. This correction occurred before v2.

A separate later remediation addressed the structural problem of holding national investment ratios and high factor shares effectively fixed over centuries. That later long-run transition was not a Nigeria-specific correction and Nigeria's eventual output share was never a calibration target.

Required interpretation:

- original 30.704% value = historical fallback provenance, not a long-run empirical truth;
- replacement = source-policy remediation, not outcome tuning;
- later investment/K-Y transition = general model-structure remediation, not a Nigeria override.

### Taiwan ENERGY source-accounting aberration

The qualified OECD 2024 source contains signed Taiwan ENERGY current-price value added of **-1,474.8229150813295 USD million** while simultaneously reporting positive current-price gross output of **65,382.8595 USD million**. The same source family reports positive previous-year-price value added (**4,792.9530 USD million**) and gross output (**52,908.1834 USD million**). The qualified 2026 model seed also has positive modeled gross output and employment.

The old seed transformation clamped the negative current-price VA to zero. In the production model this caused the chain:

`zero VA -> zero assigned capital -> Cobb-Douglas A = 0 -> permanent zero production`.

That was a model artifact produced by treating a signed accounting observation as evidence of no productive activity.

The remediation **did not alter the signed OECD observation**. It preserved the source value and reconstructed modeled accounting state using positive previous-year-price VA/output evidence plus the positive modeled activity evidence. The reconstruction rule was written generically and tested over the complete 80 x 10 sector matrix; **TWN/ENERGY was the only node satisfying its conditions**.

The reconstruction preserved country-level 2060 value added, gross output, capital, employment and investment totals by redistributing within-country sector shares.

Required interpretation:

- negative source VA remains negative in source provenance;
- negative accounting VA != zero physical/economic activity;
- reconstructed Taiwan ENERGY state is modeled accounting state, not a corrected observation;
- it is not an observed physical energy-capacity estimate;
- it is not a Taiwan-specific target or magic number.

### Other source/fallback remediations

The model also contains declared source-coverage treatments including:

- 2026 investment fallbacks where direct source coverage was unavailable;
- factor-share fallback for eight economies;
- post-WEO TFP-anchor fallback for ten economies;
- explicit replacement-underfunding rather than silently fabricating replacement investment;
- later demographic and biosynthetic transition assumptions.

These are not all the same epistemic operation. A source aberration, missing-source imputation, modeled reconstruction, structural assumption, and scenario assumption must remain distinguishable in provenance.

### Contract rule

Every admitted assertion affected by a remediation must preserve enough metadata to answer:

1. what original source value or absence triggered the treatment;
2. why direct propagation was invalid or unavailable;
3. what rule was applied;
4. whether the rule was general or country-specific;
5. which values remained immutable source evidence;
6. which values became modeled/reconstructed state;
7. what downstream rows were invalidated and recomputed;
8. whether the remediation changes epistemic standing or uncertainty.

A remediation may correct a source-to-model failure. It may **not** retroactively convert the repaired modeled value into an observation or scientific fact.

## 9. Reference immutability

The Earth reference is immutable during Offworld simulation.

If off-world activity causes:

- investment diversion;
- Earth-side expenditure;
- changed production;
- changed population;
- changed capital;
- resource imports;
- technological spillovers;
- ownership income;
- fiscal effects;
- migration;

those effects belong to `Earth_realized` and/or an explicit delta ledger.

Required identity:

`Earth_realized(t) = Earth_reference(t) + causally-accounted simulation effects`

where the actual update mechanics may be nonlinear and need not literally be arithmetic addition.

No realized event writes backward into Earth_reference.

## 10. Financial firewall

No v0 reference assertion is spendable merely because it is denominated on an economic scale.

Specifically:

`INVESTMENT_REAL_PROXY -> actor_budget`

is prohibited without a separate governed bridge.

That bridge must define:

- institutional allocation/access mechanism;
- scenario/model parameterization;
- payer/source account;
- receiving actor/account;
- conservation treatment;
- timing;
- whether allocation displaces reference Earth investment or is additional realized activity;
- causal event/provenance.

The accessible fraction `f` is not an Earth fact and may not be inferred merely because the simulator needs one.

## 11. Population firewall

Post-2100 generic database `population` is insufficiently typed for governed consumption.

v0 exposes only `BIOLOGICAL_POPULATION`.

Synthetic persons, recognized persons, machine-task capacity, labor supply, and effective labor are separate concepts and are outside v0.

## 12. PostgreSQL role

PostgreSQL is an approved query representation only insofar as its selected rows faithfully project the recovered selected trajectory.

Storage does not create epistemic authority.

Phase3A established exact equality for the admitted country-level value fields across the selected 16,080-row, 80-economy, 2026-2226 trajectory, with biological-population mapping applied after the biosynthetic transition.

The interface must still enforce the temporal resolver and semantic typing rather than exposing raw columns.

## 13. Reproducibility basis

The contract candidate relies on the recovered Phase3A evidence set, including:

- temporal derivation partition;
- PostgreSQL-to-selected-artifact equality;
- country-sector-asset reconciliation;
- boundary continuity;
- fallback/exception census;
- inherited monetary-basis documentation.

Replay status must remain visible per assertion or derivation. Historical qualification labels are not automatically translated into Authority Contract v1 standing.

## 14. Explicit non-claims

This contract does not claim:

- that the 2026-2226 Earth trajectory will occur;
- that long-run economic values are scientific facts;
- that the model is an empirically validated forecast over two centuries;
- that scenario assumptions are observations;
- that reference investment is available off-world capital;
- that reconstructed capital is finance;
- that the selected biosynthetic future is uniquely likely;
- that absence of off-world effects is a prediction.

It defines a controlled **business-as-usual/reference simulation** so off-world causal effects can be measured against a stable baseline.

## 15. Deferred concepts

Not admitted in v0:

- gross output;
- employment;
- labor force;
- effective labor;
- synthetic persons;
- recognized persons;
- TFP;
- sector productivity;
- trade topology;
- asset-level capital;
- sector-level values;
- prices;
- exchange rates;
- government revenue;
- firm balance sheets;
- borrowing capacity;
- consumption;
- literal future purchasing power.

These may be added only when a concrete simulation requirement justifies recovery and contract expansion.

## 16. Governance status

This document is PRE-CONTRACT and SINGLE-AUTHORITY.

It does not:

- release LOOM Authority Contract v1;
- qualify historical Earth artifacts under v1;
- grant implementation authority;
- reopen Phase2;
- resolve the Phase0 D0.18 versus Phase2 primitive-root inconsistency.

The root inconsistency must be resolved before Phase3B implementation encodes warrant-root structures.

## 17. Acceptance tests for a future implementation

An implementation conforming to this candidate must demonstrate at minimum:

1. all four concepts resolve to the correct temporal derivation;
2. no v4 row after 2100 can be silently returned as current reference;
3. post-2100 population resolves specifically as biological population;
4. unsupported concepts return BLOCKED;
5. missing values do not become zero;
6. exception metadata survives retrieval;
7. reference rows are immutable during simulation;
8. actor-budget requests cannot directly consume investment proxy as cash;
9. identical pinned inputs produce identical assertions;
10. provenance can trace an assertion back to its selected artifact lineage.

## 18. Next governance step

Before formal Phase3B state-model work encodes authority roots, the owner must resolve the contradiction between:

- Phase0 D0.18: authority roots remain extensible and "exactly two roots" was rejected; and
- the Phase2 normative candidate: two primitive roots, evidentiary and authorization.

Until resolved, this candidate deliberately avoids defining a closed primitive-root ontology.
