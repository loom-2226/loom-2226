# Implemented candidate model specification

**Designation:** `EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_CANDIDATE_2026_09_24`. **Status:** unpromoted empirical/scenario candidate. The v3 numerical model and its [equations](../earth_long_run_economic_baseline_v3_repaired_2026_09_23/MODEL_SPEC.md) remain the forward model. The candidate changes the **modeled 2026 sector seed** at qualifying signed-accounting anomalies and passes that seed through the unchanged 2026–2031, 2031–2060, and 2060–2226 algorithms. It also constructs a complete WPP identity/demographic envelope and separate tail sensitivities.

## 2026 qualifying rule

For each modeled country-sector with an OECD 2024 source row, require all of:

```text
current-price VA <= 0
current-price gross output > 0
previous-year-price VA > 0
previous-year-price gross output > 0
2026 modeled gross output > 0
2026 modeled employment > 0
2026 modeled VA <= 0
```

Signed current-price VA remains a source accounting observation; it is not corrected or clamped. For a qualifying node, modeled production value added at 2026 is reconstructed as:

```text
VA_reconstructed_2026 = modeled_GO_2026 × (PYP_VA_2024 / PYP_GO_2024)
K_reconstructed_2026  = VA_reconstructed_2026 × country_K_2026 / country_VA_2026
I_reconstructed_2026  = VA_reconstructed_2026 × country_I_2026 / country_VA_2026
```

Modeled gross output and employment at the node remain their positive 2026 values. Other sectors surrender proportional shares of country VA, capital and investment as needed to keep qualified country totals unchanged. Sector capital donors use the **four-asset reconstructed sector capital**, not the earlier scalar macro-sector allocation. Donor-sector asset-class capital proportions remain; the qualifying node's near-zero placeholder assets do not set its class mix. The node receives the country's qualified 2026 asset-class proportions. Country asset-class capital totals, total productive capital, VA, investment, gross output and employment remain conserved to floating-point tolerance.

An operative 2026 Cobb-Douglas A is inferred from repaired modeled VA, asset-backed K, employment, alpha and country TFP. The inherited historical `cobb_douglas_A_2026` field remains present as historical model-source lineage; `operative_A_2026` and the bridge's `cobb_douglas_A_2026_asset_rebuilt` identify the reconstructed production state. The production model has no TWN-specific constant or destination ranking target.

## Demography and controlled arms

WPP Medium through 2100 is parsed on `TPopulation1Jan`. The 15–64 working-age share is the sum of WPP age-group percentages starting at 15 through 60. The 2091–2100 median annual log population growth and median annual share change decay after 2100 using the unchanged v3 central 40/30-year half-lives and 0.20–0.80 share domain. Fast/slow scenarios use 20/15 and 80/60-year half-lives only for demographic sensitivity. All 80 central 2226 population and working-age-share numerical values equal the v3 outputs exactly.

`V3_CONTROL` is the untouched 80-economy frozen record. `SUCCESSOR_80` is the same 80 IDs, repaired from 2026. `SUCCESSOR_FULL` would require jointly qualified inputs for the added economies; none are fabricated here, so no full-economy economic trajectory exists. The 237-area demographic envelope is not misrepresented as a 237-economy economic run.

## Qualification boundary

The inherited 2031–2060 stage's 3 percentage-point maximum annual sector-investment-share movement gate remains in REVIEW at about 4.0094 points, as it was in the original pre-v3 frozen boundary. The candidate forward runner's annual gates passing does not erase that inherited upstream review. No threshold, model equation, source observation or active baseline pointer is changed.
