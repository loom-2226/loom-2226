# Long-run investment-rate source correction

This isolated successor changes the **country investment/value-added rate loaded for 2061 onward**. The 2060 country, sector and asset rows are byte-identical to the existing alpha=0.60 experiment; its capital exponent, productivity rebase, economic equations, depreciation, demographic path, trade, sector allocation and replacement-first accounting are unchanged. The frozen 2026 seed and 2031–2060 history were not rewritten.

## Source audit and rule

The old seed used the World Bank WDI national-account GFCF/GDP series for 77 economies and projected OECD 2024 destination GFCF/value-added for Myanmar, Nigeria and Taiwan. Its WEO bridge then updated GDP without updating the already-provided GFCF amount, so the frozen `investment/value_added` rates do not generally equal their WDI source percentages. UAE, Jordan and Laos carried WDI observations dated 2009, 2007 and 2016. All 80 frozen 2060 rates reconcile with the prior 2026 audit within `2.22e-16`.

The replacement uses the pinned [WDI national-account indicator NE.GDI.FTOT.ZS](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/NE.GDI.FTOT.ZS), last updated 2026-07-13 and acquired 2026-08-31 (`SHA-256 bdcba23035a47cefebc486ba17e12a1d8fbc977759668100b69c86b6bf86c5bc`). Each economy receives its latest 2025 or 2024 WDI percentage divided by 100. For a missing current national value, the generic fallback is the unweighted median of the **2024 WDI percentages for the 74 modeled economies with current WDI observations**, divided by 100. That median is **22.3283039488531%**. This is an authored pooled imputation, not an observation for its recipient.

There are 67 direct 2025 rates, seven direct 2024 rates and six fallbacks: **ARE, JOR, LAO, MMR, NGA, TWN**. The 80-row `INVESTMENT_RATE_PROVENANCE.csv` gives the old and new rates, source, source year(s), exact method, fallback flag, donor set and source hash. The rule contains no country-specific branches or endpoint targets. All 80 rates change numerically; 16 move by more than one percentage point and three by more than five.

The forward equation remains `I[c,t] = r[c] × VA[c,t]`. Only `r[c]` is replaced. The 2060 output row and its historical investment-demand normalization retain their frozen values; the new rate first appears in 2061. Subsequent trade/demand responses to that investment change follow the unchanged engine. A fixed rate through 2226 remains a model assumption.

Selected rate changes:


| ISO3 | Old rate | New rate | Change, pp | New source year | Fallback |
|---|---|---|---|---|---|
| NGA | 30.70% | 22.33% | -8.38 | 2024 | True |
| MMR | 28.60% | 22.33% | -6.27 | 2024 | True |
| LAO | 27.89% | 22.33% | -5.56 | 2024 | True |
| JOR | 26.75% | 22.33% | -4.42 | 2024 | True |
| ARE | 26.49% | 22.33% | -4.17 | 2024 | True |
| TWN | 25.58% | 22.33% | -3.25 | 2024 | True |
| CHN | 37.98% | 39.65% | +1.68 | 2024 | False |
| IND | 29.75% | 31.68% | +1.93 | 2025 | False |
| AGO | 10.38% | 10.62% | +0.24 | 2024 | False |
| USA | 20.86% | 21.35% | +0.48 | 2024 | False |


## 2190 and 2226 comparison

All monetary totals are **trillions of inherited constant-2015-USD-scale model proxy units**. Shares are within the 80 modeled economies, not the entire world.

| Year | Run | VA T | Capital T | Investment T |
|---|---|---|---|---|
| 2190 | Existing α=.60 | 548.976 | 3220.232 | 152.208 |
| 2190 | National GFCF | 514.514 | 2872.624 | 139.157 |
| 2226 | Existing α=.60 | 631.338 | 3859.596 | 175.024 |
| 2226 | National GFCF | 581.741 | 3287.021 | 155.436 |


Selected country shares (VA / capital / investment):


| Year | ISO3 | Old shares | New shares | VA change, pp | Capital change, pp | Investment change, pp |
|---|---|---|---|---|---|---|
| 2190 | NGA | 22.47% / 28.10% / 24.89% | 14.88% / 14.45% / 12.29% | -7.59 | -13.65 | -12.60 |
| 2190 | CHN | 16.75% / 22.98% / 22.94% | 18.50% / 27.78% / 27.12% | +1.75 | +4.79 | +4.18 |
| 2190 | IND | 13.64% / 11.47% / 14.64% | 15.32% / 14.39% / 17.95% | +1.68 | +2.92 | +3.31 |
| 2190 | USA | 12.98% / 8.67% / 9.77% | 14.08% / 10.10% / 11.12% | +1.11 | +1.43 | +1.35 |
| 2190 | AGO | 1.41% / 0.44% / 0.53% | 1.56% / 0.52% / 0.61% | +0.15 | +0.08 | +0.08 |
| 2226 | NGA | 26.23% / 34.48% / 29.05% | 17.56% / 18.34% / 14.68% | -8.67 | -16.14 | -14.37 |
| 2226 | CHN | 15.06% / 19.69% / 20.63% | 16.95% / 24.96% / 25.15% | +1.89 | +5.28 | +4.52 |
| 2226 | IND | 13.18% / 10.70% / 14.14% | 15.04% / 14.04% / 17.83% | +1.86 | +3.34 | +3.69 |
| 2226 | USA | 12.15% / 7.82% / 9.14% | 13.42% / 9.55% / 10.72% | +1.27 | +1.73 | +1.58 |
| 2226 | AGO | 1.73% / 0.55% / 0.65% | 1.95% / 0.68% / 0.77% | +0.21 | +0.13 | +0.12 |


Largest 2226 value added-share changes: NGA -8.67 pp, CHN +1.89 pp, IND +1.86 pp, USA +1.27 pp, IDN +0.59 pp, AGO +0.21 pp.

Largest 2226 capital-share changes: NGA -16.14 pp, CHN +5.28 pp, IND +3.34 pp, USA +1.73 pp, IDN +1.33 pp, AUS +0.42 pp.

Largest 2226 investment-share changes: NGA -14.37 pp, CHN +4.52 pp, IND +3.69 pp, USA +1.58 pp, IDN +1.00 pp, ARE -0.31 pp.

Nigeria’s 2226 **absolute** VA changes from 165.587 to 102.162 trillion proxy units; capital from 1330.903 to 602.954 trillion. China’s and India’s absolute VA and capital increase under their higher WDI rates. Angola’s own rate changes by only 0.24 percentage points; its higher share partly reflects the smaller aggregate denominator, while the coupled model may add indirect effects. These are consequences of the source rule, not fitted targets.

## Qualification and limits

Twelve focused successor tests and four inherited repair regressions passed. The 2060 boundary check found exact equality of 80 country, 800 sector and 3,200 asset rows; the 2061 rate residual was `2.78e-17`, with identical effective alpha. The full run reached 2226 with no inherited annual-gate failures. It contains 13,360 country-year rows; the 2190/2226 country–sector–asset aggregation residual was 0. Population, working-age measures, labor force, capital exponents and TFP-growth parameters matched the existing α=.60 path exactly. Reported employment differed at most 1.19e-07 persons through floating-point aggregation.

Fresh-process restoration of the complete 2226 checkpoint reproduced all six annual and endpoint country, sector and asset files byte-for-byte (`CHECKPOINT_RESTORE_CHECK.json`).

The 2026–2060 investment history still contains the old seed treatment because this task corrected only long-run initialization at the immutable 2060 boundary. The WDI indicator is a current-price national-account **share**; applying it to a constant-2015-USD-scale model VA is the inherited scenario conversion, not a measured real GFCF flow. The pooled median is uncertain for its six recipients, and holding any national rate fixed for 166 years is not empirically validated. This source correction does not validate the 2226 geography. The inherited weak internal capital diagnostic and TFP label discrepancy were not changed.

## Reproduction

In a fresh isolated copy with the pinned paths and hashes in `RUN_MANIFEST.json`, run `python3 -m unittest -v test_investment_rate_source.py test_alpha_transform.py`; then `python3 runner.py --alpha-ceiling 0.60 --stop-after 2061 --output-dir BOUNDARY_2061`, `python3 check_boundary.py`, `python3 runner.py --alpha-ceiling 0.60 --output-dir TRAJECTORY`, `python3 analyze_results.py`, `python3 runner.py --alpha-ceiling 0.60 --resume TRAJECTORY/complete_checkpoints/earth_2226.checkpoint.zip --output-dir RESUME_2226`, `python3 check_checkpoint_restore.py`, and `python3 write_report.py`. Output directories must not already exist. The preserved predecessor runs and canonical state were not modified.
