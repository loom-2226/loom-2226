# Candidate field and semantic notes

The unchanged v3 [data dictionary](../earth_long_run_economic_baseline_v3_repaired_2026_09_23/DATA_DICTIONARY.md) and [field semantics](../earth_long_run_economic_baseline_v3_repaired_2026_09_23/FIELD_SEMANTICS.json) remain the definitions for inherited annual country, sector and asset fields. Candidate additions below do not rewrite those source meanings.

| Candidate field / file | Meaning and basis |
|---|---|
| `COUNTRY_EVIDENCE.json.economies[].iso3` | WPP 2024 Medium Country/Area ISO3 identity, including separate modeled economies and territories; not a sovereignty assertion. |
| `population_2026` | WPP `TPopulation1Jan` in people, converted from source thousands. Forecast-source 2026 estimate, not a July population. |
| Layer `class` | `DIRECT`, `DERIVED_FROM_QUALIFIED_METHOD`, `FALLBACK`, or `UNAVAILABLE`. `DIRECT` means a value is present in the named qualified source snapshot, not that a future projection was observed. `UNAVAILABLE` never means numerical zero. |
| `macroeconomic_envelope.gdp_2026_constant_2015_usd` | WDI constant-2015-USD GDP level bridged with IMF WEO 2026 real growth when method is present. It is a macro source envelope, not ten-sector modeled VA. Missing values stay null. |
| `COVERAGE_REPORT.json.macro_2026_coverage` | Coverage against the 189-economy available-source GDP denominator. It is **not** a full-world economic coverage rate. |
| `DEMOGRAPHIC_SENSITIVITY.json` | WPP Medium through 2100; median 2091–2100 log population growth and working-age-share change decayed toward zero after 2100. Central 40/30 years is v3; fast 20/15 and slow 80/60 are authored sensitivity choices. Working-age share clamped to the inherited 0.20–0.80 domain. |
| `RECONSTRUCTION_TRACE.json.source_current_va_2024` | Original signed OECD current-price accounting observation, USD million. Never overwritten by modeled positive VA. |
| `reconstructed_modeled_va_2026` | `2026 modeled gross output × 2024 PYP VA / 2024 PYP gross output`, in model proxy units. It is a production reconstruction, not an OECD source observation. |
| `operative_A_2026` | Production parameter inferred from reconstructed modeled VA, capital, employment, country TFP and alpha. Historical `cobb_douglas_A_2026` is retained separately. |
| `CANDIDATE_2060_MANIFEST.json.status` | Explicit inherited 2031–2060 review status. It does not designate a governed frozen baseline. |
| Candidate annual economic values | Inherited v3 constant-2015-USD-scale model proxy units. No physical capacity, purchasing-power forecast, canon or synthetic labor is inferred. |

The source stack does not establish sovereign/territorial legal status from WPP `Country/Area` alone; that political identity field is unresolved here. The 2026 asset rows contain null asset investment, so 2026 asset-class investment composition is unknown. No zero is substituted.
