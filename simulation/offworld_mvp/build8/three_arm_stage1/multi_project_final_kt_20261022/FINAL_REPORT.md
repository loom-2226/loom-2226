# LOOM PR #427 — 2026–2226 all-body, all-sponsor project-selection experiment

**SELECTION: Box 3 rule re-implemented. Boundary admission NOT used. Firewall checked by tripwire test only.**

## Result

All 90 roster bodies and all 20 campaign sponsors were included in the 201-year campaign clock (2026–2226). This means *considered*, not that each body or sponsor necessarily qualified or started a project. Each sponsor's reviewed-positive candidates are ordered by lowest total commitment (including a held 2026 full mission quote), then earliest eligibility year, then roster index. The corrected selector can select multiple affordable candidates per sponsor in a year and carries the remaining capital forward within that callback. Actual starts remain subject to separate kernel accounts, real transfers, and finite buyer funding.

| Metric | Rendezvous main | A1 flyby price comparison | Zero conversion |
|---|---:|---:|---:|
| Annual rows | 201 | 201 | 201 |
| Projects started | 1 | 1 | 1 |
| Projects completed (reported) | 1 | 1 | 1 |
| Distinct bodies started | 1 | 1 | 1 |
| Distinct sponsors started | 1 | 1 | 1 |
| Sales | 2 | 2 | 2 |
| Return events | 3 | 3 | 3 |
| Money returned (model units) | 0.08000 | 0.08000 | 0.08000 |
| Commitment tie groups counted across annual callbacks | 0 | 0 | 7,198 |
| Bodies without a usable 2026 full mission quote | 24 | 54 | 24 |

**Tie dominance:** The zero-conversion control has 7,198 tie-group occurrences because setting mission conversion to zero makes many commitments identical, and deferred candidates recur across annual callbacks. These are not 7,198 independent unique ties. The structural earliest-year/roster-index tie break is applied. Main and flyby cases have zero ties.

**Price correction:** The vehicle flyby source's `launch_cost_usd` is launch-only, not a complete mission commitment. The final comparison uses recovered-combined full flyby quotes where available, instead of silently treating a launch-only proxy as the total. The earlier WIP flyby run that reported 90 unpriced bodies is superseded by the corrected 54-unpriced result. Full individual UNPRICED reasons are in each case JSON.

## Traced non-Ceres chain

**ITOKAWA**, Australian Space Agency sponsor, Toyota executor, reviewed-positive A1 study receipt `tx-000633`. In the rendezvous case the project starts in 2037, with mission-price transfer `tx-001094`, project investment `tx-001095`, financing disbursement `tx-001096`, construction payments in 2037 and 2038, commissioning in 2038, sales `tx-001365` (2039) and `tx-001437` (2040), three recorded return events totaling 0.08000 model units, and reported completion in 2042. Two later appropriation events are recorded in 2042 and 2043. This is a test-only synthetic economic chain, not a demonstrated extraction opportunity. The zero-conversion case instead starts AMUN.

## Verification and provenance

- **Selection tripwire:** clean allowlisted record accepted; deliberately injected hidden-world field rejected; leak removed. This protects the selector's explicit input projection only. It is *not* equivalent to the Box 3 boundary admission firewall.
- **Kernel:** project financing, construction, operations, sales, and distributions use existing kernel operations and annual `assert_invariants()`. The annual callback checks total money conservation against the post-Route1-inflow starting total. Route1 annual Earth inflows are explicit external boundary funding. Independent audit reconciles annual project starts, completions, sale counts and return-event counts with project records; it is not an independent replay of every kernel transfer.
- **Route 1 control:** exact PASS, `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430`.
- **Ceres equivalence:** previously exact PASS, 8,798 ordered transactions and 290 events, zero tolerance. Not rerun because no kernel or Ceres lifecycle implementation changed; this run changes only the selection adapter and quote source choice.
- **Database SHA-256 before and after:** `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.

## REAL / PLACEHOLDER evidence

| Classification | Count | Interpretation |
|---|---:|---|
| REAL | 0 | No physical deposit or commercial result established |
| PLACEHOLDER | 90 | Generic authored extraction-family proxy for every body, not observed geology |
| TEST_ONLY_STUDY | 249 | Synthetic reviewed study records, not real discoveries |

**Interpretation limit:** The low start count is a genuine output of these particular authored prices, sponsor/buyer funding, and reviewed-study receipts, not evidence that other bodies lack resources. The selection rule does not read hidden-world resource fields. No new geological truth or macroeconomic forecasting capability is established. The model currently reports project completion in 2042 while allowing a 2043 appropriation; completion therefore means the configured operating milestone, not final financial closure. No kernel file or other pre-existing file was edited.

## Annual evidence

The three `*_annual.csv` files each contain all 201 years and the requested project starts, completions, sales, money returned, and budget-related columns. Corresponding `*_report.json` files preserve the full project chain, prices, UNPRICED reasons, tie groups, per-year rows, and source identities. `independent_case_audit_report.json` documents the independent count and eligibility checks. All artifacts are TEST_ONLY and NON-CANON.
