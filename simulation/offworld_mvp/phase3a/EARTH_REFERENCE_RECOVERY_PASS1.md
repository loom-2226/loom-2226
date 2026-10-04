# Phase 3A Earth Reference Recovery — Pass 1

**Status:** PRE-CONTRACT / RECOVERY EVIDENCE / NO REPAIR  
**Branch:** `offworld-mvp-phase3`  
**Snapshot inspected:** `earth-v0-1-9934d0ac-20260925`

## 1. Result

The first source-to-PostgreSQL pass establishes that the current Earth reference is not one homogeneous 2026–2226 formula. It is a stitched, promoted trajectory with explicit model boundaries and inherited engines.

The current pointer designates `EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24`, selected scenario `MED_CENTRAL__SYNTH_CENTRAL`, with the previous formal economic designation `EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24`.

The PostgreSQL projection is a query surface over those promoted artifacts. It is not itself the model authority.

## 2. Temporal structure established

### 2026–2100

The current projection preserves the promoted v4 economic trajectory through 2100. PostgreSQL derivations divide it into:

- `V4_2026_2030`
- `V4_2031_2059`
- `V4_2060_2100`

WPP 2024 Medium supplies the empirical demographic projection through 2100.

### 2100 boundary

The biosynthetic successor loads the complete v4 2100 checkpoint, replaces the labor interface, and rebases sector production `A` once so the selected biological + synthetic labor composition reproduces the existing 2100 sector value-added level.

The economic levels at 2100 are deliberately preserved. This explains why economy rows in PostgreSQL retain `V4_2060_2100` lineage while the control plane also contains `BIOSYNTHETIC_BOUNDARY_2100` for the boundary reinterpretation.

### 2101–2226

The coupled successor reuses the inherited v4 economic engine for capital accumulation, investment allocation, TFP, sector/asset structure and trade topology, while replacing the labor interface with the selected biological/synthetic/machine composition.

PostgreSQL marks these rows `BIOSYNTHETIC_2101_2226`.

## 3. Core economic recurrence established

The inherited v3/v4 runner hash recorded by the promoted v4 manifest is:

`32e927276fff88652780d041169d8e216fa2ecea1f0e34babb8f0b155a5b9c37`

For asset `a`, sector `s`, economy `c`:

`K[c,s,a,t] = (1 - delta[c,s,a]) * K[c,s,a,t-1] + I[c,s,a,t-1]`

Sector capital is the sum of current asset capital.

Production is Cobb-Douglas:

`VA[c,s,t] = TFP[c,t] * A[c,s,t] * K[c,s,t]^alpha[c,t] * L_eff[c,s,t]^(1-alpha[c,t])`

and gross output is:

`GO[c,s,t] = VA[c,s,t] * go_va_ratio[c,s]`

where the inherited `go_va_ratio` is carried in state.

Economy-level value added, gross output, capital and investment are sums/allocations over sector and asset state as appropriate.

## 4. Investment is not a simple fixed share after 2060

This is the first material finding for the Offworld MVP.

The post-2060 country investment budget is:

`target = max(0, depreciation_need + 3.4*(VA[t]-VA[t-1]) + 0.05*(3.4*VA[t]-K[t]))`

`w = 1 - 2^(-(t-2060)/20)`

`I[t] = max(0, (1-w)*national_rate*VA[t] + w*target)`

The constants are explicit experiment/model assumptions in `long_run_repair.py`:

- OECD capital/output target = 3.4
- alpha target = 1/3
- alpha transition half-life = 20 years
- investment transition half-life = 20 years
- capital/output gap adjustment = 0.05

Thus `earth_economic_year.investment` after 2060 is an endogenous model flow influenced by current output, prior output, current capital, depreciation need and a decaying national-rate anchor. It is not simply observed GFCF carried forward.

## 5. National investment-rate anchor

The current helper policy is:

`WDI_NATIONAL_GFCF_GDP_LATEST_2024_2025_MEDIAN_2024_FALLBACK_v1`

It uses World Bank WDI `NE.GDI.FTOT.ZS` (gross fixed capital formation as percent of GDP), latest 2025 then 2024 where available.

For missing economies it uses an authored pooled imputation: the unweighted median of 2024 values among modeled economies with a current observation.

Current mechanical replay of the helper over the 80 qualified economies returned:

- direct: 74
- fallback: 6
- fallback rate: `0.223283039488531`

Representative anchors:

- AUS: `0.24328717473155698`, direct 2025 WDI
- NGA: `0.223283039488531`, pooled fallback
- TWN: `0.223283039488531`, pooled fallback

The fallback is not an observation for NGA or TWN.

## 6. Investment allocation

Country investment first funds asset replacement.

For each sector/asset:

`replacement_need = delta * K`

If country investment is insufficient, replacement is funded proportionally by a common coverage ratio.

Only investment remaining after replacement is allocated to expansion. Expansion allocation depends on previous investment shares, demand pressure and relative capital productivity, then is distributed across asset classes using current asset-capital composition.

The implementation checks that allocated asset investment reconciles to country investment to relative residual <= 1e-12.

## 7. Representative PostgreSQL observations

These are stored reference values, not yet numerical replays from primitive inputs.

| ISO3 | Year | Value added | Investment | Capital | I/VA | Derivation |
|---|---:|---:|---:|---:|---:|---|
| AUS | 2026 | 1.7287036298518467e12 | 4.12288545182134e11 | 8.113842605984885e12 | 0.2384957942 | V4_2026_2030 |
| AUS | 2100 | 5.244813994187886e12 | 8.091110269341156e11 | 2.2075023945531742e13 | 0.1542687744 | V4_2060_2100 |
| AUS | 2101 | 5.250801207151263e12 | 7.445940020567866e11 | 2.211780503947652e13 | 0.1418057879 | BIOSYNTHETIC_2101_2226 |
| AUS | 2226 | 4.18736224498437e12 | 2.7225661008455405e11 | 1.4375296398396506e13 | 0.0650186428 | BIOSYNTHETIC_2101_2226 |
| NGA | 2026 | 5.854237888933206e11 | 1.7974924927373083e11 | 4.709612970552137e12 | 0.3070412455 | V4_2026_2030 |
| NGA | 2100 | 1.3656871641101322e13 | 2.175309559957753e12 | 4.912764155327083e13 | 0.1592831519 | V4_2060_2100 |
| NGA | 2101 | 1.3827941678389357e13 | 2.158768503296697e12 | 4.989948588202577e13 | 0.1561164021 | BIOSYNTHETIC_2101_2226 |
| NGA | 2226 | 1.6129709043112055e13 | 1.332487477562177e12 | 5.5234529242690805e13 | 0.0826107572 | BIOSYNTHETIC_2101_2226 |
| TWN | 2026 | 8.275422867496775e11 | 2.1164630758138257e11 | 3.076215319652366e12 | 0.2557528612 | V4_2026_2030 |
| TWN | 2100 | 8.879101900564764e11 | 1.4158924463456024e11 | 3.527306097614697e12 | 0.1594634753 | V4_2060_2100 |
| TWN | 2101 | 8.814811628717826e11 | 1.3650128377864801e11 | 3.5019279644606353e12 | 0.1548544535 | BIOSYNTHETIC_2101_2226 |
| TWN | 2226 | 6.082847124228246e11 | 5.7157767143263054e10 | 2.0821118454444363e12 | 0.0939654836 | BIOSYNTHETIC_2101_2226 |

A notable semantic point is already visible: NGA's stored 2026 I/VA ratio is about 30.704%, but the post-2060 national-rate anchor now used by the successor is the 22.3283% pooled WDI fallback. Those are different objects in different parts of the model lineage. They must not be conflated.

## 8. Phase 2 mapping

The existing PostgreSQL labels such as `QUALIFIED_MODEL`, `SELECTED_MODEL`, `DERIVED`, and `SELECTED_AUTHORITY` predate the Phase 2 normative vocabulary.

For Phase 3A they are preserved as historical governance metadata. They are not automatically treated as Phase 2 epistemic modes or qualification.

In Phase 2 terms, the Earth BAU trajectory has a **reference role**. That role does not make each underlying assertion an observation.

## 9. Blocking questions still open

The following are NOT ESTABLISHED by Pass 1:

1. exact construction of every 2026 economic seed field;
2. exact 2026–2030 and 2031–2059 annual recurrences and transition mechanics;
3. full currency/price basis behind the current PostgreSQL phrase `model proxy monetary units`;
4. whether the offworld MVP may interpret one model investment unit as a spendable capital unit without a conversion/accounting bridge;
5. complete field-by-field uncertainty behavior;
6. complete derivation of the WPP demographic fields and post-2100 mortality/fertility schedules;
7. exact current source path for every PostgreSQL row family;
8. numerical replay of selected PostgreSQL rows from immediate inputs.

Until item 3 and especially item 4 are resolved, `earth_economic_year.investment` is **not yet cleared as the monetary source for the MVP capital pool**.

## 10. Next pass

Pass 2 shall recover:

- 2026 seed construction;
- 2026–2060 stage mechanics;
- exact monetary/price semantics;
- source-to-field mapping for economic rows;
- a first exact numerical reconstruction, beginning with investment/capital because that is the MVP's immediate dependency.
