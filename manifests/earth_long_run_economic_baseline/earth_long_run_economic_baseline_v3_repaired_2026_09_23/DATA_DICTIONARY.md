# v3 Earth economic baseline data dictionary

**Baseline:** `EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23`. This dictionary covers the actual annual country, sector, asset, boundary-repair, checkpoint and trajectory-summary schemas. The machine-readable contract is [FIELD_SEMANTICS.json](FIELD_SEMANTICS.json).

> **Monetary basis:** All modeled monetary fields are inherited constant-2015-USD-scale **model proxy** units. Capital is a modeled stock. Value added, gross output, investment, depreciation replacement and expansion investment are annual flows. They support within-model comparisons of modeled accounting states. They are not literal 2226 purchasing-power dollars, household income, wealth, market capitalization, GW, tonnes/year, or physical productive capacity.

> **ACCOUNTING STATE != PHYSICAL CAPACITY STATE.** Physical infrastructure requires an independently qualified mapping.

## Boundary and interpretation rules

- The 2060 row is the qualified starting boundary. Some fields there are inherited cached diagnostics; the Taiwan active-sector reconstruction changed primary modeled state without recomputing every cached 2060 diagnostic. Use 2061+ rows for v3 identities involving replacement, shares or productivity caches. Earlier Taiwan zero rows are historical model artifacts, not observations.
- `capital_share_alpha` is the inherited 2060 value at the boundary and the operative post-2060 exponent thereafter. It transitions toward 1/3 with a 20-year half-life. `labor_share` remains the frozen historical/source labor share. `labor_exponent_effective = 1 - capital_share_alpha` is the exponent used in post-2060 production.
- `cobb_douglas_A_2026` is an immutable historical coefficient. `A` is the operative coefficient rebased during alpha transition. Its level is not a cross-country technology ranking.
- `country_tfp_multiplier` follows the within-country PWT-derived frontier-growth transition plus decaying catch-up path. Its normalization is country-specific, so cross-country multiplier levels do not measure relative productivity. The old `legacy_tfp_regime` field carries the corrected method label.
- `investment_output_ratio` means investment/value added, and `capital_output_ratio` means capital/value added. Gross output is not either denominator. The canonical semantic names are `investment_to_value_added_ratio` and `capital_to_value_added_ratio`; serialized fields remain unchanged.
- Asset capital and investment are modeled allocations and inherited composition, not observed future asset-level holdings. Enabling indexes use modeled accounting proxies relative to each node’s own 2060 reference; they are not physical-capacity measurements.
- The signed 2024 OECD Taiwan ENERGY current-price VA remains negative. The repair record also preserves gross output and previous-year-price VA/output evidence. Its reconstructed 2060 and propagated 2226 fields are modeled accounting state, not observed Taiwan energy infrastructure.

For TWN/ENERGY, the signed OECD 2024 current-price VA is **−1,474.822915 USD million**; gross output is **65,382.8595 USD million**, and previous-year-price VA is **4,792.953024 USD million**. The universal active-sector rule reconstructed modeled 2060 VA of **8.736705409 billion proxy units**, gross output of **96.442257981 billion proxy units**, capital of **34.049788241 billion proxy units**, and employment of **38,737.8349**. The modeled 2226 state is a propagated accounting result. None of these figures measures GW, fuel throughput, or installed energy assets.

## Field catalog

For each field, the tables give the exact formula where derived and the unit/type. `FIELD_SEMANTICS.json` supplies the full per-field provenance, numerator/denominator, cross-country and cross-year comparability, valid and invalid interpretations, and canonical name. A dash means the value is copied or assigned rather than calculated from output fields.

### Country annual/output records

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `blind_runtime_version` | Inherited 2060 runtime version tag; absent from later v3 annual rows. | assigned/copied; see provenance | text or integer label; label | empirical/source |
| `capital` | Modeled productive capital stock or allocated asset component; current-year K enters production. | sum_10(sector capital) | proxy USD; year-level stock | model state |
| `capital_share_alpha` | Country effective Cobb-Douglas capital exponent in 2061+; 2060 row carries inherited frozen alpha before the initial cap/rebase. | 2061+: 1/3 + (alpha_2060_capped_at_0.60 - 1/3) × 2^(-(year-2060)/20); 2060 inherited source operative alpha | ratio; ratio | model input |
| `country_tfp_growth` | Annual country TFP multiplier growth rate from frontier-growth transition plus decaying catch-up. | country_tfp_multiplier_t / country_tfp_multiplier_(t-1) - 1; transition from PWT-derived qualified inputs | ratio; ratio | model state |
| `country_tfp_multiplier` | Within-country TFP trajectory multiplier that scales all sector production in that country. | TFP_t = TFP_(t-1) × (1 + country_tfp_growth_t) | dimensionless multiplier; index | model state |
| `demographic_working_age_population` | Population in the demographic working-age frame. | population × demographic_working_age_share (2061+); 2060 inherited | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `demographic_working_age_share` | Demographic working-age population as a fraction of total population. | demographic_working_age_population / population; WPP medium to 2100, decaying tail later | ratio; ratio | derived diagnostic |
| `demography_source` | Demography source/regime label: frozen boundary, WPP medium to 2100, or decaying WPP tail. | assigned/copied; see provenance | text or integer label; label | model input |
| `depreciation_source` | Provenance label for depreciation rate; 2060 inherited, later current asset-weighted effective rate. | assigned/copied; see provenance | text or integer label; label | model input |
| `effective_labor_input` | Employment plus synthetic labor equivalents used in production. | employment + synthetic_labor_equivalent | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `employment` | Modeled biological employed people or sector allocation thereof. | sum_10(sector employment) | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `expansion_investment` | Annual investment allocated above funded replacement. | asset: investment - replacement_funded; sector: sum(asset expansion_investment); country 2060 inherited only | proxy USD/year; annual flow | derived diagnostic |
| `gross_output` | Modeled gross sector/country production including intermediate-input accounting. | sum_10(sector gross_output) | proxy USD/year; annual flow | model state |
| `investment` | Annual modeled investment flow allocated to productive capital; prior-year investment enters next-year stock flow. | 2061+: max(0, (1-w) × r2060 × VA + w × max(0, D + 3.4 × (VA - prior_VA) + 0.05 × (3.4 × VA - K))); w = 1 - 2^(-(year-2060)/20); D = sum(asset depreciation rate × current asset capital); 2060 inherited | proxy USD/year; annual flow | model state |
| `investment_output_ratio` | Annual investment divided by value added, despite historical output wording. | investment / max(EPS, value_added) | ratio; ratio | derived diagnostic |
| `iso3` | ISO 3166-1 alpha-3 modeled economy identifier. | assigned/copied; see provenance | text or integer label; label | model input |
| `labor_exponent_effective` | Labor exponent actually entering production in 2061+; absent in 2060 rows. | 1 - capital_share_alpha | ratio; ratio | model input |
| `labor_force` | Modeled labor-market participants. | labor_market_working_age_population × frozen 2060 participation rate (2061+); 2060 inherited | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `labor_market_working_age_population` | Population in the inherited labor-market working-age frame. | demographic_working_age_population × frozen 2060 labor-market frame ratio (2061+); 2060 inherited | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `labor_share` | Frozen historical/source labor share, not the post-2060 production labor exponent. | inherited 2060 historical/source labor share, held constant; not used as v3 labor exponent | ratio; ratio | empirical/source |
| `legacy_tfp_regime` | Historical field name carrying the implemented FRONTIER_GROWTH_TRANSITION_DECAYING_CATCHUP descriptor. | assigned/copied; see provenance | text or integer label; label | model input |
| `population` | Modeled total resident population. | assigned/copied; see provenance | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `post_weo_tfp_anchor_fallback` | Inherited 2060 fallback flag for the post-WEO TFP anchor. | assigned/copied; see provenance | text or integer label; label | empirical/source |
| `post_weo_tfp_anchor_method` | Inherited 2060 post-WEO TFP anchor method. | assigned/copied; see provenance | text or integer label; label | empirical/source |
| `real_value_added_growth` | Country year-over-year modeled VA growth. | current value_added / prior value_added - 1 if prior > 0, else 0 (2061+); 2060 inherited | ratio; ratio | derived diagnostic |
| `replacement_coverage_ratio` | Share of current asset replacement need funded by the country investment budget. | min(1, country investment / sum country asset replacement_need) when need > 0, else 1 (2061+); 2060 inherited | ratio; ratio | derived diagnostic |
| `replacement_investment_funded` | Sector/country replacement amount funded from current investment budget. | sector: sum(asset replacement_funded); country 2060 inherited only | proxy USD/year; annual flow | derived diagnostic |
| `replacement_investment_requirement` | Country annual depreciation replacement requirement, inherited at 2060. | 2061+: sum over assets(asset_depreciation_rate × asset capital); country field absent after 2060 | proxy USD/year; annual flow | derived diagnostic |
| `structural_regime` | Name of the structural labor, asset, and trade propagation regime. | assigned/copied; see provenance | text or integer label; label | model input |
| `synthetic_labor_equivalent` | Additional synthetic input expressed as equivalent workers; zero in this qualified run. | sum_10(sector synthetic_labor_equivalent) | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `synthetic_to_biological_employment_ratio` | Country synthetic worker equivalents per biological employed person. | synthetic_labor_equivalent / max(EPS, employment) | ratio; ratio | derived diagnostic |
| `trade_topology_regime` | Name of the endogenous revealed-accessibility trade topology rule. | assigned/copied; see provenance | text or integer label; label | model input |
| `value_added` | Net modeled sector/country value added at the annual accounting boundary. | sum_10(sector value_added) | proxy USD/year; annual flow | model state |
| `year` | Calendar year represented by this record. | assigned/copied; see provenance | text or integer label; label | model input |

### Country-sector annual records

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `A` | Operative sector Cobb-Douglas coefficient at this annual state; rebased as alpha changes. | A_new = A_old × K^(alpha_old - alpha_new) × effective_labor^(alpha_new - alpha_old) when alpha changes | production coefficient in model input units; index | model state |
| `automation_enabling_index` | Sector machinery plus transport capital per worker relative to its own 2060 reference. | [(sector machinery capital + sector transport_equipment capital) / sector biological employment] / 2060 sector automation capital per worker | own-boundary index; index | derived diagnostic |
| `blind_runtime_version` | Inherited 2060 runtime version tag; absent from later v3 annual rows. | assigned/copied; see provenance | text or integer label; label | empirical/source |
| `capital` | Modeled productive capital stock or allocated asset component; current-year K enters production. | sum_5(current asset capital) (2061+); 2060 inherited/reconstructed | proxy USD; year-level stock | model state |
| `capital_productivity` | Inherited 2060 sector value added per capital; cached boundary diagnostic. | inherited from 2060 source row; not recomputed after TWN boundary reconstruction | proxy USD per proxy USD capital; ratio | derived diagnostic |
| `capital_share_alpha` | Country effective Cobb-Douglas capital exponent in 2061+; 2060 row carries inherited frozen alpha before the initial cap/rebase. | 2061+: 1/3 + (alpha_2060_capped_at_0.60 - 1/3) × 2^(-(year-2060)/20); 2060 inherited source operative alpha | ratio; ratio | model input |
| `cobb_douglas_A_2026` | Immutable historical 2026 Cobb-Douglas coefficient carried through annual sector records. | copied unchanged from qualified 2026 seed | historical production coefficient; index | model input |
| `compute_enabling_index` | Country compute capital per biological worker relative to its own 2060 reference. | [(COMPUTE machinery capital + COMPUTE other_assets capital) / country biological employment] / 2060 country compute capital per worker | own-boundary index; index | derived diagnostic |
| `country_tfp_growth` | Annual country TFP multiplier growth rate from frontier-growth transition plus decaying catch-up. | country_tfp_multiplier_t / country_tfp_multiplier_(t-1) - 1; transition from PWT-derived qualified inputs | ratio; ratio | model state |
| `country_tfp_multiplier` | Within-country TFP trajectory multiplier that scales all sector production in that country. | TFP_t = TFP_(t-1) × (1 + country_tfp_growth_t) | dimensionless multiplier; index | model state |
| `demography_source` | Demography source/regime label: frozen boundary, WPP medium to 2100, or decaying WPP tail. | assigned/copied; see provenance | text or integer label; label | model input |
| `depreciation_rate` | Effective annual sector depreciation rate weighted by current asset capital. | sum(asset depreciation rate × current asset capital) / max(EPS, sector capital) (2061+); 2060 inherited | ratio; ratio | derived diagnostic |
| `depreciation_source` | Provenance label for depreciation rate; 2060 inherited, later current asset-weighted effective rate. | assigned/copied; see provenance | text or integer label; label | model input |
| `effective_labor_input` | Employment plus synthetic labor equivalents used in production. | employment + synthetic_labor_equivalent | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `employment` | Modeled biological employed people or sector allocation thereof. | country labor_force × frozen 2060 employment rate; sectors receive normalized labor shares (2061+); 2060 boundary inherited/reconstructed | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `energy_abundance_index` | Prior-year modeled ENERGY gross output per current worker relative to own 2060 reference. | [prior-year ENERGY gross_output / current country biological employment] / 2060 country ENERGY gross_output per worker | own-boundary index; index | derived diagnostic |
| `expansion_investment` | Annual investment allocated above funded replacement. | sum_5(asset expansion_investment) | proxy USD/year; annual flow | derived diagnostic |
| `gross_output` | Modeled gross sector/country production including intermediate-input accounting. | value_added × frozen sector gross_output/value_added ratio (2061+); 2060 inherited/reconstructed | proxy USD/year; annual flow | model state |
| `investment` | Annual modeled investment flow allocated to productive capital; prior-year investment enters next-year stock flow. | sum_5(current asset investment) (2061+); 2060 inherited/reconstructed | proxy USD/year; annual flow | model state |
| `investment_share_of_country` | Sector investment share of country investment; allocation weight. | sector investment / country investment (2061+); 2060 inherited cached value | ratio; ratio | derived diagnostic |
| `io_demand_factor` | Trade-network weighted demand multiplier used in sector labor/investment allocation. | demand_factor from annual revealed-accessibility trade rewiring | dimensionless multiplier; index | model state |
| `io_demand_pressure` | Current trade-network demand factor relative to prior sector gross output scale. | max(EPS, base_2060_sector_gross_output × io_demand_factor / max(EPS, prior_sector_gross_output)) | dimensionless pressure; index | derived diagnostic |
| `iso3` | ISO 3166-1 alpha-3 modeled economy identifier. | assigned/copied; see provenance | text or integer label; label | model input |
| `labor_exponent_effective` | Labor exponent actually entering production in 2061+; absent in 2060 rows. | 1 - capital_share_alpha | ratio; ratio | model input |
| `labor_productivity` | Inherited 2060 sector value added per employed person; cached boundary diagnostic. | inherited from 2060 source row; not recomputed after TWN boundary reconstruction | proxy USD per employed person; ratio | derived diagnostic |
| `labor_share` | Frozen historical/source labor share, not the post-2060 production labor exponent. | inherited 2060 historical/source labor share, held constant; not used as v3 labor exponent | ratio; ratio | empirical/source |
| `labor_share_of_country` | Sector employment share of country employment; allocation weight. | sector employment / country employment (2061+); 2060 inherited cached value | ratio; ratio | derived diagnostic |
| `legacy_tfp_regime` | Historical field name carrying the implemented FRONTIER_GROWTH_TRANSITION_DECAYING_CATCHUP descriptor. | assigned/copied; see provenance | text or integer label; label | model input |
| `post_weo_tfp_anchor_fallback` | Inherited 2060 fallback flag for the post-WEO TFP anchor. | assigned/copied; see provenance | text or integer label; label | empirical/source |
| `post_weo_tfp_anchor_method` | Inherited 2060 post-WEO TFP anchor method. | assigned/copied; see provenance | text or integer label; label | empirical/source |
| `replacement_coverage_ratio` | Share of current asset replacement need funded by the country investment budget. | min(1, country investment / sum country asset replacement_need) when need > 0, else 1 (2061+); 2060 inherited | ratio; ratio | derived diagnostic |
| `replacement_investment_funded` | Sector/country replacement amount funded from current investment budget. | sum_5(asset replacement_funded) | proxy USD/year; annual flow | derived diagnostic |
| `replacement_investment_need` | Sector annual replacement need. | sum_5(asset replacement_need) | proxy USD/year; annual flow | derived diagnostic |
| `sector` | Model sector category; one of the ten sector groups. | assigned/copied; see provenance | text or integer label; label | model input |
| `structural_regime` | Name of the structural labor, asset, and trade propagation regime. | assigned/copied; see provenance | text or integer label; label | model input |
| `synthetic_labor_equivalent` | Additional synthetic input expressed as equivalent workers; zero in this qualified run. | sector employment × synthetic_labor_equivalent_ratio; country sum over sectors (2061+); 2060 inherited | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `synthetic_labor_equivalent_ratio` | Sector synthetic equivalents per biological employed person. | synthetic_labor_equivalent / max(EPS, employment) | ratio; ratio | derived diagnostic |
| `technology_productivity_multiplier` | Sector productivity multiplier from causal technology module; 1 in this qualified run. | causal_technology_state(compute_index, automation_index, energy_index, prior synthetic ratio, sector) returns multiplier | dimensionless multiplier; index | model state |
| `trade_topology_regime` | Name of the endogenous revealed-accessibility trade topology rule. | assigned/copied; see provenance | text or integer label; label | model input |
| `value_added` | Net modeled sector/country value added at the annual accounting boundary. | country_tfp_multiplier × technology_productivity_multiplier × A × capital^capital_share_alpha × effective_labor_input^labor_exponent_effective (2061+); 2060 inherited/reconstructed | proxy USD/year; annual flow | model state |
| `year` | Calendar year represented by this record. | assigned/copied; see provenance | text or integer label; label | model input |

### Country-sector-asset annual records

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `asset_class` | Modeled productive asset category within a country-sector. | assigned/copied; see provenance | text or integer label; label | model input |
| `asset_depreciation_rate` | Inherited asset-specific annual depreciation fraction used in the stock-flow equation. | frozen qualified 2060 asset depreciation parameter | ratio; ratio | model input |
| `blind_runtime_version` | Inherited 2060 runtime version tag; absent from later v3 annual rows. | assigned/copied; see provenance | text or integer label; label | empirical/source |
| `capital` | Modeled asset allocation of sector capital stock. | K_asset,t = (1 - asset_depreciation_rate) × K_asset,t-1 + investment_asset,t-1 (2061+); 2060 inherited | proxy USD; year-level stock | model state |
| `expansion_investment` | Annual investment allocated above funded replacement. | asset: investment - replacement_funded; sector: sum(asset expansion_investment); country 2060 inherited only | proxy USD/year; annual flow | derived diagnostic |
| `investment` | Modeled asset allocation of sector annual investment flow. | replacement_funded + expansion_investment (2061+); 2060 inherited | proxy USD/year; annual flow | model state |
| `iso3` | ISO 3166-1 alpha-3 modeled economy identifier. | assigned/copied; see provenance | text or integer label; label | model input |
| `replacement_coverage_ratio` | Share of current asset replacement need funded by the country investment budget. | country-level min(1, investment_budget / sum_all_country_assets(replacement_need)) if need > 0, else 1 (2061+); 2060 inherited | ratio; ratio | derived diagnostic |
| `replacement_funded` | Asset replacement need funded under the country budget. | replacement_need × replacement_coverage_ratio | proxy USD/year; annual flow | derived diagnostic |
| `replacement_need` | Asset annual replacement need. | asset_depreciation_rate × current asset capital | proxy USD/year; annual flow | derived diagnostic |
| `sector` | Model sector category; one of the ten sector groups. | assigned/copied; see provenance | text or integer label; label | model input |
| `share_of_sector_capital` | Asset capital as share of its sector capital. | asset capital / max(EPS, sector capital) (2061+); 2060 inherited | ratio; ratio | derived diagnostic |
| `structural_regime` | Name of the structural labor, asset, and trade propagation regime. | assigned/copied; see provenance | text or integer label; label | model input |
| `year` | Calendar year represented by this record. | assigned/copied; see provenance | text or integer label; label | model input |

### Taiwan active-boundary repair record

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `iso3` | ISO 3166-1 alpha-3 modeled economy identifier. | assigned/copied; see provenance | text or integer label; label | model input |
| `method` | Identifier for universal active-sector boundary reconstruction method. | assigned/copied; see provenance | text or integer label; label | model input |
| `reconstructed_capital_2060` | Reconstructed 2060 modeled ENERGY capital stock. | reconstructed_va_2060 × (country capital_2060 / country VA_2060) | proxy USD; year-level stock | model state |
| `reconstructed_employment_2060` | Reconstructed 2060 modeled ENERGY employment. | seed_employment_2026 / country employment_2026 × country employment_2060 | people; year-level modeled count | model state |
| `reconstructed_go_2060` | Reconstructed 2060 modeled ENERGY gross output. | reconstructed_va_2060 × (source_go_2024_pyp_usd_million / source_va_2024_pyp_usd_million) | proxy USD/year; annual flow | model state |
| `reconstructed_va_2060` | Reconstructed 2060 modeled ENERGY value added. | seed_go_2026 × (source_va_2024_pyp_usd_million / source_go_2024_pyp_usd_million) × (country VA_2060 / country VA_2026) | proxy USD/year; annual flow | model state |
| `sector` | Model sector category; one of the ten sector groups. | assigned/copied; see provenance | text or integer label; label | model input |
| `seed_employment_2026` | Qualified 2026 sector employment seed used by boundary reconstruction. | assigned/copied; see provenance | people; year-level modeled count | model input |
| `seed_go_2026` | Qualified 2026 sector gross-output seed used by boundary reconstruction. | assigned/copied; see provenance | proxy USD/year; annual flow | model input |
| `source_go_2024_current_usd_million` | OECD 2024 current-price sector gross output. | assigned/copied; see provenance | USD million; annual source accounting flow | empirical/source |
| `source_go_2024_pyp_usd_million` | OECD 2024 previous-year-price sector gross output. | assigned/copied; see provenance | USD million; annual source accounting flow | empirical/source |
| `source_va_2024_current_usd_million` | Signed OECD 2024 current-price sector value added. | assigned/copied; see provenance | USD million; annual source accounting flow | empirical/source |
| `source_va_2024_pyp_usd_million` | OECD 2024 previous-year-price sector value added. | assigned/copied; see provenance | USD million; annual source accounting flow | empirical/source |

### Trajectory summary envelope

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `baseline_id` | Current v3 baseline designation. | assigned/copied; see provenance | text or integer label; label | model input |
| `global_2226` | Object containing the 2226 sums of modeled VA, capital and investment. | assigned/copied; see provenance | text or integer label; label | derived diagnostic |
| `schema` | Trajectory-summary schema identifier. | assigned/copied; see provenance | text or integer label; label | model input |
| `top20` | Array of twenty country entries ordered by descending 2226 modeled VA. | assigned/copied; see provenance | text or integer label; label | derived diagnostic |
| `unit` | Trajectory-summary monetary-unit description. | assigned/copied; see provenance | text or integer label; label | model input |
| `years` | Years included in the compact top-20 trajectory summary. | assigned/copied; see provenance | text or integer label; label | model input |

### Trajectory summary global 2226 totals

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `capital` | Modeled productive capital stock or allocated asset component; current-year K enters production. | sum_80(country capital_2226) | proxy USD; year-level stock | model state |
| `investment` | Annual modeled investment flow allocated to productive capital; prior-year investment enters next-year stock flow. | sum_80(country investment_2226) | proxy USD/year; annual flow | model state |
| `value_added` | Net modeled sector/country value added at the annual accounting boundary. | sum_80(country value_added_2226) | proxy USD/year; annual flow | model state |

### Trajectory summary top-20 entries

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `country_name` | Country display name from qualified comparison mapping. | assigned/copied; see provenance | text or integer label; label | model input |
| `iso3` | ISO 3166-1 alpha-3 modeled economy identifier. | assigned/copied; see provenance | text or integer label; label | model input |
| `rank` | Position by descending unrounded 2226 country value added. | 1 + number of modeled countries with greater 2226 value_added | ordinal rank; label | derived diagnostic |
| `share_2226` | Country fraction of total modeled 80-economy value added in 2226. | country value_added_2226 / sum_80(value_added_2226) | ratio; ratio | derived diagnostic |
| `share_by_year` | Map of selected year strings to that country share of 80-economy VA in each year. | for each selected year: country value_added_year / sum_80(value_added_year) | ratio; ratio | derived diagnostic |
| `value_added_2226` | Country modeled 2226 value added used to rank top 20. | assigned/copied; see provenance | proxy USD/year; annual flow | model state |

### Checkpoint global records

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `capital` | Modeled productive capital stock or allocated asset component; current-year K enters production. | sum_80(country capital) | proxy USD; year-level stock | model state |
| `capital_output_ratio` | Capital stock divided by value added, despite historical output wording. | capital / max(EPS, value_added) | ratio; ratio | derived diagnostic |
| `employment` | Modeled biological employed people or sector allocation thereof. | sum_80(country employment) | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `investment` | Annual modeled investment flow allocated to productive capital; prior-year investment enters next-year stock flow. | sum_80(country investment) | proxy USD/year; annual flow | model state |
| `investment_output_ratio` | Annual investment divided by value added, despite historical output wording. | investment / max(EPS, value_added) | ratio; ratio | derived diagnostic |
| `population` | Modeled total resident population. | sum_80(country population) | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `sector_structure` | Map keyed by model sector containing global VA and capital shares at checkpoint year. | for each sector, compute global_va_share and global_capital_share | map of dimensionless shares; derived diagnostic | derived diagnostic |
| `synthetic_labor_equivalent` | Additional synthetic input expressed as equivalent workers; zero in this qualified run. | sum_80(country synthetic_labor_equivalent) | people or worker equivalents; year-level population/input stock | yes, as modeled counts |
| `synthetic_to_biological_employment_ratio` | Country synthetic worker equivalents per biological employed person. | synthetic_labor_equivalent / max(EPS, employment) | ratio; ratio | derived diagnostic |
| `value_added` | Net modeled sector/country value added at the annual accounting boundary. | sum_80(country value_added) | proxy USD/year; annual flow | model state |
| `weighted_legacy_tfp_level` | VA-weighted average of country-specific TFP multipliers; aggregate diagnostic, not a comparable TFP level. | sum(country_tfp_multiplier × country value_added) / global value_added | dimensionless weighted index; index | derived diagnostic |
| `weighted_technology_productivity_multiplier` | VA-weighted average sector technology multiplier. | sum(sector technology_productivity_multiplier × sector value_added) / global value_added | dimensionless weighted index; index | derived diagnostic |
| `year` | Calendar year represented by this record. | assigned/copied; see provenance | text or integer label; label | model input |

### Checkpoint sector-share object

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `global_capital_share` | Checkpoint sector share of global capital stock. | sum_80(sector capital) / global capital | ratio; ratio | derived diagnostic |
| `global_va_share` | Checkpoint sector share of global value added. | sum_80(sector value_added) / global value_added | ratio; ratio | derived diagnostic |

### Checkpoint sector-map key

| Field | Meaning | Exact formula / assignment | Units; type | Source class |
|---|---|---|---|---|
| `sector` | Model sector category; one of the ten sector groups. | assigned/copied; see provenance | text or integer label; label | model input |

## Source and verification

- Authoritative run provenance and hashes: [RUN_MANIFEST.json](RUN_MANIFEST.json), [BASELINE_MANIFEST.json](BASELINE_MANIFEST.json), [PROVENANCE.md](PROVENANCE.md).
- Semantic verification: `python3 -B -m unittest -v test_field_semantics.py` from this directory. It reads the pinned v3 outputs and never invokes the simulation.
- This dictionary and JSON are interface documentation. They do not change the current pointer, model code, equations, parameters or numerical outputs.
