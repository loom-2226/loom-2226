# General project economic lifecycle, test-only (PR #427)

## Run results

- Scope traversed: 90-body catalog, 20 sponsors, 16 executors, 201 years (2026–2226).
- **Actual physical projects initiated: ONE (CERES, ISRO, HAL / L&T).** This is not an all-body physical project activation. The code currently instantiates only one physical project state; it does not independently evaluate/start projects for every eligible body and sponsor. That requirement remains INCOMPLETE.
- Held-2026 price source: saved PR427 A_VEHICLE_MISSION_PAIRS.csv, SHA-256 in input_identity.json and reports; status PRICED_TEST_ONLY, not calibrated real prices.
- 73 bodies without supported mission quote are UNPRICED, listed in annual_money_report.json.
- Exact Ceres reference parity: PASS. 8,798 ordered transactions per run; ordered transaction and event projections equal, zero tolerance, no identifier rename. See equivalence_report.json.
- Normal conversion: 1 funded physical project (2039), 1 completed (2042), 2 sales and 2 return distributions (2041–2042). Zero conversion: 0 funded, completed, sales, or returns. Both 201-year runs completed.
- Annual money-return amounts and sponsor-exhaustion fields for both runs are in annual_money_report.json (201 rows each). Money returned means financier plus owner distributions, excluding local reinvestment and reserves.

## One traced kernel chain

1. 2039: ISRO funds Ceres project and pays a held-2026 PRICED_TEST_ONLY mission quote through real kernel transfers.
2. 2039–2040: construction spends 0.030 + 0.030 model currency using kernel development operations.
3. 2041: PLACEHOLDER extraction, real kernel sale tx-001476, then 0.020 financier + 0.020 owner returns, 0.040 local reinvestment and 0.020 reserve.
4. 2042: PLACEHOLDER extraction, real kernel sale tx-001530, then 0.000 financier + 0.040 owner returns, 0.040 local reinvestment and 0.040 reserve.
5. 2044–2045: owner-return provenance leads to treasury appropriations of 0.020 (tx-001620) and 0.040 (tx-001666) into ISRO Route1 budget. These are scripted, not independent decisions.

## REAL / PLACEHOLDER

| Element | Classification | Meaning |
|---|---|---|
| Kernel transfers, construction, sales, distributions, appropriations | REAL CODE PATH | Actual kernel operations on synthetic inputs |
| Ceres parity | REAL EXACT TEST | Ordered kernel transactions and event projections match original reference |
| 2026 mission quote table | PRICED_TEST_ONLY | Authored proxy, not calibrated market price |
| Four extraction outputs | PLACEHOLDER | Synthetic resources; NOT scientific observations |
| Material-family allocations and physical economics | PLACEHOLDER | Authored scenario, not measured deposits |
| A1/A2 studies | TEST_ONLY_STUDY | Not spacecraft missions |
| 90-body, 20-sponsor, 16-executor Route1 clock | REAL CODE PATH | All present, but not 90 independent physical projects |

## Unmet objective

The generic six-method lifecycle is parameterized, but the full-clock runner exercises only one instantiated physical project. It does NOT yet satisfy all eligible bodies and sponsors independently initiating projects and recycling capital. No main-branch merge or canon promotion.
