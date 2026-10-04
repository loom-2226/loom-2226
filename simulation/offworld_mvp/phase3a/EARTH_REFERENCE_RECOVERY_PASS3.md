# Phase 3A Earth Reference Recovery - Pass 3

**Status:** PRE-CONTRACT / RECOVERY EVIDENCE / NO REPAIR  
**Branch:** `offworld-mvp-phase3`  
**Follows:** Passes 1-2

## 1. Purpose

This pass converts the recovered Earth trajectory into a first field-and-recurrence dictionary for the Offworld MVP boundary. It separates field meaning, production rule, temporal regime, and intended MVP use.

The Earth trajectory remains a **REFERENCE role**. CIVPROP shall not mutate it. Future reference rows remain projections/model-derived assertions, not observations merely because PostgreSQL stores them.

## 2. Core field dictionary

| Field | Meaning | Unit/basis | MVP use |
|---|---|---|---|
| `iso3` | economy identifier | model identity | yes, subject to identity qualification |
| `year` | model year | integer year | yes |
| population | total population reference | persons | yes |
| labor force | modeled labor force | persons | conditional |
| employment | modeled employed persons | persons | conditional |
| `value_added` | country real output/value added | 2026 source basis documented as constant-2015-USD aligned; long-run consistency remains a lien | scale/reference |
| `investment` | modeled GFCF/investment flow | real monetary flow aligned to reference accounting basis | conditional; not synonymous with cash |
| `capital` | reconstructed productive capital stock | real monetary stock measure | diagnostics/conditional |
| `gross_output` | production before intermediate-use netting | real monetary flow | not initial MVP budget |
| capital-share alpha | Cobb-Douglas capital exponent | fraction | model diagnostic |
| labor share | labor factor share | fraction | model diagnostic |
| country TFP multiplier/growth | productivity/reconciliation state | dimensionless/rate | not direct agent knowledge |
| WEO cumulative factor/growth | WEO-constrained macro input | dimensionless/rate | provenance/diagnostics |
| provenance/method fields | source and derivation labels | categorical | required metadata |

Raw-artifact and PostgreSQL names are not assumed interchangeable.

## 3. 2026 base

For country c:

`Y[c,2026] = frozen real_gdp[c]`

`I[c,2026] = frozen gross_fixed_capital_formation[c]`

For ordinary source-covered countries:

`I[c,2026] = WDI_GFCF_share[c] * Y[c,2026]`

Historical missing-share cases MMR, NGA and TWN used an explicit OECD bounded-VA fallback.

Capital is reconstructed from a PWT 2023 capital/output anchor and asset-level perpetual-inventory roll-forward through 2026.

The source provenance labels the macro basis `IMF_APRIL_2026_WEO_BRIDGED_WDI_CONSTANT_2015_USD`.

## 4. Investment recurrence

### 2027-2031

`I[c,t] = I[c,2026] * WEO_CUMULATIVE_REAL_GDP_FACTOR[c,t]`

Where the same output factor is used, I/Y remains at the 2026 intensity. This is a WEO-constrained reference recurrence.

### 2031-2060

`sI[c] = I[c,2031] / Y[c,2031]`

`I[c,t] = sI[c] * Y[c,t]`

Sector and asset allocation then becomes structurally endogenous.

### Post-2060

The successor transitions from a national investment-rate anchor toward capital/output feedback. The later pooled-WDI fallback recovered in Pass 1 belongs to this later policy family and must not be projected backward onto the 2026 seed.

## 5. Capital recurrence

At asset level:

`K[c,s,a,t] = (1-delta[c,s,a]) * K[c,s,a,t-1] + I[c,s,a,t-1]`

Replacement is funded before expansion. Exact replay therefore requires asset-level stocks, depreciation and allocation, not merely country totals.

## 6. Output recurrence 2026-2031

Sector production uses Cobb-Douglas. Sector productivity is calibrated at 2026. Later years propagate capital and labor, compute raw sector production, then apply one country-year TFP multiplier so sector value added sums to the WEO-constrained country target.

The TFP multiplier is a reconciliation/model state, not an independently observed productivity measurement.

## 7. Output recurrence 2031-2060

The structural stage removes the WEO country-output target. It combines WPP demographics, the 2031 labor-market frame, TFP transition toward historical PWT growth, asset stock-flow recurrence, gradual labor and investment reallocation, OECD IO demand topology, demand pressure, and relative productivity.

Country value added becomes an endogenous aggregation of sector production.

## 8. Replay A: 2026 to 2027

Recovered Australia 2026 boundary:

- Y = 1,728,703,629,851.8467
- I = 412,288,545,182.134
- K = 8,113,842,605,984.885
- population = 27,103,088
- employment = 13,844,988
- alpha = 0.453912258148193
- labor share = 0.546087741851807
- TFP multiplier = 1.0

Established recurrence:

`Y_2027 = Y_2026 * (1 + g_WEO_2027)`

`I_2027 = I_2026 * (Y_2027 / Y_2026)`

Asset capital propagates by PIM and sector production is reconciled to Y_2027.

**Exact independent numerical replay: NOT YET ESTABLISHED.**

The read-only interrogation has not yet supplied all immediate 2027 asset/sector intermediates required for an independent arithmetic replay. A stored final value shall not be back-filled and mislabeled as an independent derivation.

## 9. Replay B: 2031 to 2032

2031 is the boundary between the WEO-constrained bridge and structural post-WEO stage.

Established:

`sI_2031 = I_2031 / Y_2031`

`I_2032 = sI_2031 * Y_2032`

Capital continues through asset PIM. Labor and investment begin structural reallocation. TFP transitions toward the historical PWT anchor. Output is no longer imposed by WEO.

**Exact independent numerical replay: NOT YET ESTABLISHED.**

Knowing the recurrence family is not proof that a stored row was generated by it.

## 10. Offworld admissibility

Directly useful reference inputs include economy identity, year, population, value-added scale, investment/GFCF with derivation regime attached, and capital for macro diagnostics.

A governed bridge is required before converting country GFCF into actor spendable budget, national capital into liquid financing capacity, or sector production into private-firm revenue.

Agents must not receive hidden reconciliation multipliers or future reference state unless explicitly available to their perspective.

## 11. Phase 2 firewall

A typed Earth request must declare field, country scope, time, world-context, perspective, use, and required unit/basis.

A bare request such as `investment[AUS,2050]` is semantically incomplete for governed consumption.

## 12. Remaining liens

1. Exact 2026-to-2027 numerical replay.
2. Exact 2031-to-2032 numerical replay.
3. Exact 2060 transition replay.
4. Complete generating-code lineage for the original v0.8 seed.
5. Long-run price-basis consistency.
6. Complete PostgreSQL/source mapping for sector and diagnostic fields.
7. Machine-readable missing/stale/fallback semantics.
8. Phase 2 cross-phase warrant-root consistency before root structure is encoded in implementation.

## 13. Consequence

We know enough to define the shape, but not implement, an Earth reference interface:

`EarthReference.get(field, iso3, year, use, world_context, perspective)`

It must return a typed assertion carrying value or governed non-value state, unit/basis, temporal regime, derivation, provenance, fallback/imputation status, uncertainty, reference role, and admissibility/standing result.

Next pass: close the numerical replay obligations and the 2060 boundary before freezing the MVP Earth reference contract.
