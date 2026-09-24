# Earth demographic lineage recovery — 2026-09-24

**Primary class:** data
**Status:** corrective authority-boundary record; no canon change; no economic trajectory change.

## Finding

The promoted v4 economic baseline correctly carries a 237-area UN WPP 2024 identity/demographic envelope, but its post-2100 `DEMOGRAPHIC_SENSITIVITY.json` is a diagnostic sensitivity, not an authoritative 2226 population state.

The sensitivity extrapolator takes each area's median 2091–2100 annual log population growth and working-age-share change, then exponentially decays those derivatives after 2100. CENTRAL uses 40/30-year half-lives. It is intentionally simple and does not model fertility, age-specific mortality, longevity medicine, migration, or cohort conservation.

Accordingly, FAST_DECAY, CENTRAL and SLOW_DECAY outputs MUST NOT be presented as the selected LOOM 2226 demographic state, country ranking, or forecast. In particular, the CENTRAL 237-area sum is diagnostic output only.

## Recovered prior LOOM demographic lineage

A 15 August 2026 project artifact, `LOOM_2226_Earth_Demographic_and_Social_Propagation_Model_v0.3`, records the prior demographic program lineage:

v0.1 working model -> adversarial review -> v0.2 cohort engine -> independent CSV audit -> v0.3 social/demographic integration.

That artifact is PROVISIONAL / PROPAGATION DESIGN CANDIDATE, not locked canon. It records a closed-humanity central control benchmark of **8.442B biological humans in 2226**, with median age 52.7, TFR 1.88, about 75.3M births/year, about 81.3M deaths/year, and slow natural decline.

The 8.442B value is explicitly MODEL-DERIVED + SETTING-CALIBRATION + PROPAGATION-DEPENDENT. It is therefore a recovered control benchmark, not a value to hard-code into the current baseline.

## Recovered mechanism

The prior program uses annual cohorts conceptually as `P[a+1,t+1] = P[a,t] * (1-q[a,t])`, with births generated from an age-specific fertility kernel. Fertility level and fertility timing are separate controls. The central TFR path recorded in v0.3 is 1.838 (2100), 1.802 (2125), 1.790 (2150), 1.815 (2175), 1.846 (2200), and 1.880 (2226), while mean childbearing age rises from about 30.21 to 39.0.

Longevity is modeled through survival/mortality rather than by multiplying population growth. Broad advanced medicine becomes widespread while premium longevity remains unequal. Off-Earth migration must conserve persons: every migrant is debited from an origin cohort and credited to a destination cohort.

## Current authority boundary

1. UN WPP 2024 remains the empirical/projected demographic boundary through 2100 for the 237 Country/Area identities.
2. The v4 post-2100 half-life outputs remain preserved as diagnostic sensitivity provenance only.
3. No post-2100 v4 sensitivity scenario is selected as authoritative demography.
4. The recovered 8.442B cohort result is the prior LOOM control benchmark, not governing 2226 Earth population and not a replacement value for the v4 sensitivity.
5. A production post-2100 demographic state requires recovery/reimplementation and qualification of the cohort lineage before Atlas/Postgres demographic materialization.

## Production gates retained from v0.3

- ingest the exact WPP 2100 single-age x sex ledger;
- implement two-sex/reproductive-structure cohorts;
- close or explicitly document the approximately 1% crude-birth-rate calibration residual;
- export reproducibility ledgers for all sensitivity cases;
- establish permanent off-world population dates from canon chronology;
- connect population propagation to habitat-capacity outputs;
- add hostile country/regional outlier review before promotion.

## Non-scope

This correction does not modify the qualified 80-economy economic trajectory, TWN/ENERGY reconstruction, economic source snapshots, SQLite, CIVSTATE, Solar Emergence, Navigator, canon, or the historical v4 sensitivity bytes. It prevents a diagnostic demographic tail from being mistaken for selected demographic authority and restores the prior cohort-model lineage as the required successor path.
