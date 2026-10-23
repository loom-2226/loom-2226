# PR 427 price and sale-life sweep — TEST_ONLY, non-canon

90 bodies, 20 sponsors, 2026–2226 inclusive. Nine fresh rendezvous cases, with uniform annual Earth buyer inflow 1,000 model currency. No body names, body size factors, or governor in the sweep controls. All nine cases have a hashed authored scenario, a per-case scenario hash, and a shared sweep identity hash. Values are synthetic.

| Price | Sale events | Starts | Sponsors ever | Bodies ever | Last start | Committed | Returned | Return / commit | Sponsor-capital deferrals |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| x1 | 2 | 42 | 19 | 42 | 2065 | 40.4457 | 3.3600 | 8.31% | 3,049 |
| x1 | 3 | 42 | 19 | 42 | 2065 | 40.4457 | 5.0400 | 12.46% | 3,049 |
| x1 | 4 | 42 | 19 | 42 | 2065 | 40.4457 | 6.7200 | 16.61% | 3,049 |
| x3 | 2 | 42 | 19 | 42 | 2065 | 40.4457 | 10.0800 | 24.92% | 3,049 |
| x3 | 3 | 42 | 19 | 42 | 2065 | 40.4457 | 15.1200 | 37.38% | 3,049 |
| x3 | 4 | 42 | 19 | 42 | 2065 | 40.4457 | 20.1600 | 49.84% | 3,049 |
| x10 | 2 | 42 | 19 | 42 | 2065 | 40.4457 | 33.6000 | 83.07% | 3,049 |
| x10 | 3 | 42 | 19 | 42 | 2065 | 40.4457 | 50.4000 | 124.61% | 3,049 |
| x10 | 4 | 42 | 19 | 42 | 2065 | 40.4457 | 67.2000 | 166.15% | 3,049 |

**No setting produces starts after 2066.** In fact, all nine high-buyer cases last start in **2065**. Additional sale proceeds do not automatically replenish sponsor project-selection budgets. The reported return is gross owner/financier distributions, not exclusively sponsor cash and not a reinvested sponsor balance. The nine identical start counts therefore do not establish that price is economically irrelevant; they reveal a missing recycling link in this particular test model.

## Authored variables and provenance

The original `run_multi_project.py` `PortfolioCampaign.on_year` hard-coded sales at `operation_year_1` and `operation_year_2`, while it executed four operating events (`operation_year_1` through `operation_year_4`). The new runner changes only the sale-event dispatch **in memory**, using authored `sales_caps` 2, 3, and 4. It does not edit that parent file. For the assigned VOLATILES proxy, recoverable stock is 8 units and extraction is 2 units per operation, so four operations exhaust the authored stock. Three is the midpoint between the existing two sales and four. **This is a sale-event cap, not a change to the four-event physical operating schedule**; the distinction matters.

The original scenario contains METALS, SILICATES and VOLATILES, but no ORGANICS. The new scenario adds an explicitly synthetic ORGANICS placeholder with unit price 0.040, quantity per operation 2, recoverable 8, and unit opex 0.010. This is not calibrated geology or evidence of organic resources. Parent `family_assignment` sets **all 90 bodies to VOLATILES**, so only the volatile row is actually exercised by these nine runs. All four authored family price rows are scaled uniformly x1, x3 or x10. The inactive families must not be described as having been independently tested.

Placeholder unit prices before multiplier: VOLATILES 0.050, SILICATES 0.035, METALS 0.075, ORGANICS 0.040. The current high buyer budget 1,000 is retained; rendezvous mission quotes and sponsor commitments remain unchanged across cases. There is no governor, name preference, or body-size multiplier.

## Verification and identity

- Authored scenario SHA-256: see `input_identity.json`.
- Sweep run identity SHA-256: `3203f285b2ea56baa8e99d5ac704a1d709d7f81fb03b7b10307dde66d39387cb`.
- Each case's effective scenario SHA-256: in `summary.json` and its corresponding case report.
- Route 1 exact control: **PASS**, `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430`.
- Ceres ordered equivalence: **PASS**, 8,798 transactions per side, 290 events, no mismatch.
- Selector hidden-world tripwire: **PASS**.
- World SQLite baseline SHA-256: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.

Inputs and the previous reports were not modified. This report does not imply any canon promotion.
