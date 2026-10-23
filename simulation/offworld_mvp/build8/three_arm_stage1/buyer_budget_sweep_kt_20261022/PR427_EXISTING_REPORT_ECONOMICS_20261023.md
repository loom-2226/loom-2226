# PR 427 existing-report economics (2026–2226)

TEST_ONLY / non-canon. 90 bodies, 20 sponsors. Read-only analysis of the existing saved buyer-budget sweep reports. No new simulations.

## 1. Break-even sale price by material family

For the 42 projects started in the medium case, lowest initial commitment = 0.4767797735, median = 0.96449001997 (mean of middle two), highest = 2.1812790852 model currency. Calculation is `(commitment / authored recoverable units) + authored unit opex`, assuming the full recoverable inventory can be sold within the four authored operating events. Ratio = calculated price / placeholder price. This is gross project-level revenue break-even, **not** sponsor cash-return break-even, and ignores distribution timing and shares. The reports record only two sales per project, so full-inventory sales are an assumption, not an observed result.

| Family | Placeholder/unit | Low price (ratio) | Median price (ratio) | High price (ratio) |
|---|---:|---:|---:|---:|
| Volatiles | 0.050 | 0.0696 (1.39x) | 0.1306 (2.61x) | 0.2827 (5.65x) |
| Silicates | 0.035 | 0.0610 (1.74x) | 0.1152 (3.29x) | 0.2504 (7.15x) |
| Metals | 0.075 | 0.0801 (1.07x) | 0.1498 (2.00x) | 0.3236 (4.31x) |

The existing non-Ceres chains are all assigned VOLATILES; silicates/metals figures are conditional applications of authored family quantities and costs, not realized family-specific projects. Authored recoverable quantities: volatiles 8, silicates 9, metals 7; unit opex 0.010, 0.008, 0.012 respectively.

## 2. Medium-case candidate pipeline

| Year | New positive A1 reviews | New quote-eligible | Projects started |
|---|---:|---:|---:|
| 2026–2036 (each) | 0 | 0 | 0 |
| 2037 | 51 | 36 | 12 |
| 2038 | 20 | 16 | 2 |
| 2039 | 12 | 9 | 1 |
| 2040 | 4 | 2 | 1 |
| 2041 | 2 | 2 | 1 |
| 2042 | 1 | 1 | 1 |
| 2043–2066 (each) | 0 | 0 | 1 |
| 2067–2226 (each) | 0 | 0 | 0 |
| TOTAL | 90 | 66 | 42 |

There are 24 no-quote candidate pairs. New positive studies and new quote eligibility both stop after 2042. Starts stop after 2066 **not because the clock ends or buyers run out**, but because the remaining candidates are unaffordable to sponsors: 2067 records 24 pending candidates, 16 sponsor `DEFERRED_NO_AFFORDABLE_ELIGIBLE_PROJECT` dispositions, 0 buyer-endowment blocks, 0 new positive studies, 0 new quote-eligible candidates, 0 new no-quote candidates, and 0 starts. The 24 pending count is candidate-level; 16 deferrals are sponsor-policy dispositions, not 16 additional unique candidates. The saved reports cannot establish a unique universal economic cause beyond these recorded diagnostics.

## 3. Gross money recycling

Committed = sum of `total_capital_commitment` for started projects in each saved report. Returned = report's `money_returned` (gross owner/financier distributions, **not exclusively sponsor receipts**). Ratio = returned / committed.

| Case | Total committed | Total returned | Ratio |
|---|---:|---:|---:|
| Low | 18.329347 | 1.600000 | 8.73% |
| Medium | 40.445678 | 3.360000 | 8.31% |
| High | 40.445678 | 3.360000 | 8.31% |
| Zero-conversion control | 5.280000 | 5.280000 | 100.00% |

The zero-conversion control removes mission-price conversion, not construction or sales. These ratios are not realized profit or sponsor-only repayment. All monetary amounts are synthetic model currency.

Sources: existing `low_report.json`, `medium_report.json`, `high_report.json`, `zero_conversion_control_report.json`, `RESULTS.md`, and their embedded authored scenarios in this directory. No input or runtime file modified.
