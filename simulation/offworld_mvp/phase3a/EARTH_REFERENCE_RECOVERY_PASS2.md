# Phase 3A Earth Reference Recovery — Pass 2

**Status:** PRE-CONTRACT / RECOVERY EVIDENCE / NO REPAIR  
**Branch:** `offworld-mvp-phase3`  
**Follows:** `EARTH_REFERENCE_RECOVERY_PASS1.md`

## 1. Result

Pass 2 recovers the near-term economic construction far enough to correct one important uncertainty from Pass 1:

**The 2026 monetary level is not an unspecified abstract proxy. The frozen seed explicitly identifies its macro provenance as `IMF_APRIL_2026_WEO_BRIDGED_WDI_CONSTANT_2015_USD`.**

That gives the 2026 value-added and GFCF quantities a documented constant-2015-USD basis in the source artifact.

This does **not** yet authorize CIVPROP to treat a modeled investment flow as a freely spendable cash budget. Currency basis and economic meaning are different questions. GFCF is an economy-wide fixed-capital formation flow, not a bank account conveniently left lying around for asteroid companies.

## 2. 2026 initial condition

The frozen empirical baseline manifest identifies:

- 2026 state: `FROZEN_EMPIRICAL_INITIAL_CONDITION`
- 2027–2031: `WEO_CONSTRAINED_EMPIRICAL_BRIDGE`
- source seed: `earth2026_frozen_seed_v0.8`
- near-term bridge: `earth2026_2031_cobb_douglas_v0.2`

The 2026 seed combines, at minimum:

- macro: IMF April 2026 WEO bridged to WDI constant 2015 USD;
- population: UN WPP 2024;
- employment/labor: ILOSTAT;
- production structure: OECD ICIO;
- factor shares and capital: PWT 11.0 plus later reconstruction/roll-forward work.

The 2026 seed therefore contains assertions with different evidentiary and derivation histories. Phase 2 semantics prohibit collapsing “2026 seed” into a single epistemic class.

## 3. 2026 value added and investment

The seed field `real_gdp` becomes the modeled country value-added level used by the economic trajectory.

The seed field `gross_fixed_capital_formation` becomes the 2026 country investment level.

For ordinary covered countries the seed records:

`gfcf_method = WDI_GFCF_SHARE_APPLIED_TO_REAL_GDP_LEVEL`

so:

`I_2026 = WDI_GFCF_share * real_GDP_2026`

For the original seed's missing GFCF-share cases, a different historical bridge was used. The frozen accounting report records fallback countries:

- MMR
- NGA
- TWN

The seed identifies the fallback method as:

`OECD_2024_DESTINATION_GFCF_TO_BOUNDED_VA_SHARE_FALLBACK`

This is distinct from the later post-2060 WDI pooled-median investment-rate policy recovered in Pass 1.

### Exact 2026 reconstruction check

The source seed and current PostgreSQL projection match exactly for the checked country-level value-added and investment fields:

| ISO3 | Seed real GDP | Seed GFCF | Seed ratio | Historical 2026 method |
|---|---:|---:|---:|---|
| AUS | 1,728,703,629,851.8467 | 412,288,545,182.134 | 0.23849579422556538 | WDI share applied to real GDP |
| NGA | 585,423,788,893.3206 | 179,749,249,273.73083 | 0.3070412454771048 | OECD bounded-VA fallback |
| TWN | 827,542,286,749.6775 | 211,646,307,581.38257 | 0.25575286117723584 | OECD bounded-VA fallback |

Current PostgreSQL contains those same 2026 values.

This confirms a source-to-PostgreSQL reconstruction for these fields, rather than merely observing similar endpoint behavior.

## 4. Capital construction at 2026

The v0.8 seed records country capital as a reconstructed real capital stock.

The sample inspected documents:

`capital_stock_method = PWT11_RNNA_RGDPNA_KY_ANCHOR_PLUS_ASSET_PIM_2024_2026`

The construction uses a PWT 11.0 2023 capital/output anchor and rolls four asset classes forward through 2024–2026:

- structures
- machinery
- transport equipment
- other assets

with asset-specific depreciation and annual national investment.

The resulting country capital is therefore a reconstructed stock aligned to the model's real-output accounting basis, not a directly observed 2026 market-value balance sheet.

## 5. 2026–2031 bridge

The near-term bridge deliberately preserves the already-qualified macro envelope year by year:

- population;
- demographic working-age population;
- labor-market working-age population;
- labor force;
- employment;
- country value added;
- country investment.

The Cobb-Douglas bridge report specifies:

- country output path: IMF April 2026 WEO real-GDP growth;
- demography: UN WPP 2024 Medium;
- production function: Cobb-Douglas;
- capital exponent: one minus latest valid PWT labor share through 2023;
- sector `A`: calibrated exactly at 2026;
- sector employment shares: fixed 2026 for the near-term bridge;
- country TFP: common country-year multiplier required to reconcile factor propagation to the WEO country path;
- investment: 2026 real investment intensity scaled by cumulative WEO GDP.

The asset bridge then carries the four reconstructed asset classes through this macro envelope.

Capital obeys:

`K[c,s,a,t] = (1-delta[c,s,a]) K[c,s,a,t-1] + I[c,s,a,t-1]`

Country investment is taken directly from the qualified near-term macro envelope.

Replacement is funded first. Residual expansion follows frozen 2026 sector investment shares, then reconstructed 2026 asset composition.

Sector Cobb-Douglas `A` is recalibrated at 2026 using reconstructed capital, frozen employment, frozen value added and PWT factor share alpha.

For 2027–2031 a single country-year TFP multiplier scales sector raw production so the sector sum exactly reproduces the externally constrained WEO country value-added path.

Thus 2027–2031 is **not a free-running BAU forecast**. It is a WEO-constrained reference bridge.

## 6. 2031–2060 transition

The recovered `stage_mid.py` explicitly calls this the first genuinely structural post-WEO economy.

After the 2031 boundary:

- WEO GDP targets stop;
- WPP supplies population and working-age structure;
- 2031 labor-market frame, participation and employment rates remain fixed during this qualification;
- country TFP transitions from WEO-implied 2031 growth toward historical PWT growth;
- capital continues through the asset stock-flow recurrence;
- the 2031 country investment/value-added ratio initially defines the country investment envelope;
- labor reallocates gradually among sectors;
- investment reallocates gradually among sectors;
- OECD 2024 IO topology supplies demand structure;
- demand pressure and relative labor/capital productivity affect reallocation.

The stage's own source comments state:

`I_country[t] = frozen 2031 country investment/VA rate * VA_country[t]`

for this 2031–2060 stage.

This is another distinct investment regime. It must not be confused with either the 2026 seed rule or the later post-2060 capital/output feedback rule.

## 7. Investment regime map now established

The Earth reference contains at least three investment semantics:

### 2026 seed / near-term anchor

Observed/bridged GFCF intensity applied to constant-2015-USD real GDP, with explicit historical fallback methods where source coverage was absent.

### 2027–2031 WEO bridge

2026 real investment intensity propagated with the WEO-constrained country output path.

### 2031–2060 structural stage

Country investment envelope is the frozen 2031 investment/VA ratio times endogenous country VA; allocation becomes structurally endogenous.

### Post-2060 successor

The national-rate anchor transitions toward the capital/output feedback rule recovered in Pass 1. The current successor's national-rate source is a later WDI policy with its own fallback behavior.

This temporal distinction is essential for any CIVPROP capital interface.

## 8. Phase 2 interpretation

### World-context

The Earth BAU series occupies the **reference role**. Its future values are projections/model outputs, not observations merely because they are stored in PostgreSQL.

### Assertions and lineage

A country-year investment assertion must retain enough lineage to distinguish:

- source-observed GFCF share;
- historical fallback/imputation;
- WEO-constrained propagation;
- structural model propagation;
- post-2060 investment-policy transition.

A generic `investment` field without this temporal/derivation context is semantically insufficient for governed use.

### Reference versus realized

CIVPROP must not overwrite these reference rows. Any future Earth feedback belongs in realized state or a separately ledgered delta.

## 9. MVP capital-pool consequence

The earlier proposed interface

`P_c(t) = f * I_c(t)`

is now dimensionally more defensible because the source model documents a real constant-2015-USD monetary basis.

It is **not yet semantically authorized**.

The missing bridge is not primarily currency conversion. It is the economic interpretation:

> What fraction of economy-wide gross fixed capital formation can a modeled actor plausibly command for offworld investment, and under what institutional/ownership rule?

That is a model parameter / scenario-governance question. It cannot be inferred merely from the existence of GFCF.

Therefore the Earth recovery does not choose `f`. It exposes the quantity from which a later governed capital-allocation rule may derive an actor budget.

## 10. Remaining recovery work

Still NOT ESTABLISHED:

1. the exact generating code for the original v0.8 seed and every intermediate repair, although the frozen artifacts and provenance are present;
2. a complete field dictionary mapping every PostgreSQL economic field to source, formula, unit, temporal regime and uncertainty;
3. exact numerical replay of a 2027 WEO bridge row from immediate 2026 inputs;
4. exact numerical replay of a 2032 structural row;
5. exact numerical replay across the 2060 transition;
6. full treatment of price-basis consistency when PWT capital stock, WDI GFCF shares, WEO real growth and OECD structural shares are combined;
7. whether all post-2026 monetary stock/flow values preserve a sufficiently coherent constant-2015-USD interpretation for direct cross-year budget accounting.

## 11. Next pass

Pass 3 should now stop wandering through filenames like an archaeologist cursed by Python and build the thing we actually need:

**an Earth reference field-and-recurrence dictionary.**

For every PostgreSQL field it will record:

- definition;
- unit;
- world-context and role;
- source assertion(s);
- formula/transform;
- applicable years;
- transition boundary;
- historical governance label;
- Phase 2 mapping;
- known uncertainty;
- missingness/fallback behavior;
- whether admissible for the Offworld MVP;
- exact reconstruction status.

The first worked replay will target 2026→2027 and the second 2031→2032.
