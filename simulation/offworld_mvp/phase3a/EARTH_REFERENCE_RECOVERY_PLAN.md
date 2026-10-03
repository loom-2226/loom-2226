# LOOM Offworld MVP — Phase 3A Earth Reference Recovery

**Status:** PRE-CONTRACT / PHASE 3A IN PROGRESS / SINGLE-AUTHORITY  
**Branch:** `offworld-mvp-phase3`  
**Purpose:** Recover and specify the actual LOOM Earth 2026–2226 PostgreSQL reference model before the offworld MVP consumes any Earth value.

## 1. Governing objective

Phase 3A shall establish, from the actual PostgreSQL holdings and their source/model lineage, what every Earth reference field means and how every annual value is produced.

The target is an inspectable specification of:

`Earth(t) = F(Earth(t-1), exogenous inputs(t), parameters, transformations)`

where that relationship actually exists. No recurrence shall be invented merely to make the model look tidy.

Recovery is descriptive. It shall not silently repair, reinterpret, rebase, or promote Earth holdings.

## 2. Read-only source boundary

Recovery shall inspect:

1. the live `loom_dev` PostgreSQL Earth/control schemas read-only;
2. the Git source artifacts, manifests, model specifications, code, tests, qualification records, and promotion records that produced the current PostgreSQL projection;
3. historical Earth branches only as archaeology where required to explain current lineage.

The dirty local `/home/ubuntu/LOOM_DEV` checkout is not treated as current Git authority. Source evidence must be tied to an identifiable Git ref/commit or PostgreSQL snapshot/artifact hash.

## 3. Current recovered PostgreSQL surface

Initial mechanical inspection found the Earth projection contains:

- `earth_area`
- `earth_biological_cohort_year`
- `earth_demographic_year`
- `earth_derivation`
- `earth_economic_year`
- `earth_labor_composition_year`
- `earth_legacy_labor_year`
- `earth_sector_asset_year`
- `earth_sector_year`

The control plane also contains variable semantics, temporal coverage, model context, source artifacts, import batches, and snapshot metadata.

The validated Earth snapshot identified by the existing projection documentation is:

`earth-v0-1-9934d0ac-20260925`

Existing documentation describes the PostgreSQL surface as an immutable query projection over promoted Git authority rather than an independent model authority.

## 4. Known temporal/model boundary requiring explicit recovery

Existing projection documentation states:

- WPP 2024 Medium Jan-1 age/sex data are used for 2026–2100;
- the selected `MED_CENTRAL__SYNTH_CENTRAL` coupled successor is used for 2101–2226;
- 2100 is retained as the explicit handoff boundary;
- legacy employment is distinct from post-2100 biological effective labor;
- synthetic-person facts unavailable before their modeled boundary are unavailable, not zero.

Phase 3A must verify these statements against the actual source lineage and executable transformations rather than merely repeat them.

## 5. Field recovery contract

For every consumable Earth field, Phase 3A shall establish where supported:

- table and column;
- proposition/semantic meaning;
- unit;
- currency/price/model-unit basis where applicable;
- geographic grain;
- temporal grain;
- valid interval;
- source/model identity;
- Phase 2 epistemic mode and derivation lineage;
- reference role;
- immediate dependencies;
- upstream source dependencies;
- exact transformation/formula/code path;
- parameter dependencies;
- treatment of missing/UNKNOWN/quarantined/stale/conflicting inputs;
- uncertainty treatment;
- transition/handoff behavior;
- whether stored, derived, recurrent, exogenous, or accounting identity;
- whether it feeds subsequent years;
- known limitations/misuse warnings;
- standing for intended offworld-MVP consumption.

If a property cannot be established, Phase 3A records it as NOT ESTABLISHED rather than inferring it.

## 6. Annual dependency reconstruction

The recovery shall derive the actual annual dependency graph from executable source and artifacts.

At minimum it shall determine how the following families relate through time:

- biological population and cohorts;
- births/deaths and age aggregates;
- legacy labor;
- post-2100 biological effective labor;
- synthetic population/effective labor;
- machine task capacity;
- sector value added;
- sector gross output;
- sector investment;
- sector capital;
- sector asset capital/investment/depreciation/replacement/expansion;
- economy-level value added/gross output/investment/capital.

For each recurrence, the exact t/t-1 dependency shall be recorded.

## 7. Numerical reconstruction

Phase 3A shall select representative countries and years and reproduce stored PostgreSQL values from their immediate dependencies and transformation rules.

The test set must include:

- a normal qualified economy;
- Nigeria;
- Taiwan;
- at least one pre/post-2100 boundary case;
- 2026 initialization;
- 2100/2101 handoff;
- 2226 endpoint.

A reconstruction is not successful merely because values are close. The expected replay tolerance and reason for any non-exactness must be stated.

## 8. Earth reference interface target

Phase 3A shall identify the minimum Earth-reference interface required by the MVP rather than granting the simulator broad SQL access.

Candidate MVP needs include:

- participating economy identity;
- reference investment flow;
- relevant population/migration basis;
- later, only if required, production/demand quantities used by the explicit Earth market clearing account.

No candidate field is approved for consumption merely by appearing in this list.

## 9. Specific investment question

Before the MVP may use:

`P_c(t) = f * I_c(t)`

Phase 3A must establish exactly what `earth_economic_year.investment` represents, including its unit/model-money basis, derivation, aggregation from sector/asset investment where applicable, temporal propagation, imputation/substitution history, and intended economic interpretation.

This is a hard dependency of offworld capital conservation.

## 10. Deliverables

Phase 3A shall produce:

1. **EARTH_REFERENCE_FIELD_DICTIONARY.md/json** — complete field semantics and Phase 2 classification.
2. **EARTH_REFERENCE_DEPENDENCY_GRAPH.md/json** — annual dependency/transformation graph.
3. **EARTH_REFERENCE_RECONSTRUCTION_REPORT.md** — representative numerical replay.
4. **EARTH_REFERENCE_ANOMALY_REGISTER.md** — defects, ambiguities, stale lineage, missing definitions, unresolved transformations, and known boundary problems without repair.
5. **EARTH_REFERENCE_MVP_INTERFACE.md** — minimal proposed read interface for the offworld simulation.
6. executable read-only verification/reconstruction tests where practical.

## 11. Exit criteria

Phase 3A may close only when:

- every PostgreSQL Earth field has a definition or explicit NOT ESTABLISHED disposition;
- all MVP-consumed Earth fields have traced lineage and transformations;
- annual recurrence/handoff rules are explicit;
- representative numerical rows can be reconstructed or any failure is recorded as a blocking anomaly;
- reference versus realized-state semantics are explicit;
- no recovery finding has silently changed the source model;
- the proposed MVP Earth interface is narrow enough that simulation code does not need arbitrary access to Earth storage.

## 12. Initial mechanical findings

The live PostgreSQL semantics registry currently exposes 21 semantic variables. Economic `value_added`, `gross_output`, `investment`, and `capital` are described there as `model proxy monetary units`, economic-area-year grain, with `QUALIFIED_MODEL` status under the existing pre-Phase-2 vocabulary. This terminology must be mapped, not blindly inherited, into the Phase 2 model.

The existing registry also explicitly warns that unavailable values before a modeled boundary do not mean zero.

These are recovery observations, not Phase 3 qualification decisions.
