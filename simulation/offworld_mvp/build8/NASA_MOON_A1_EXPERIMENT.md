# NASA → Moon A1, Route 1 / 6C funding handoff

**EXPERIMENTAL / NON-CANON / NON-RUNTIME-DEFAULT.** Stacked on draft #391. No frozen 6C file modified.

Currency: `AUTHORED_6C_CURRENCY_INTERPRETATION_10M_USD_PER_UNIT`.

The opt-in Route 1 Gate 1 variant changes **only NASA's 2026 requested amount**, from LAND's 0.150 network units to Moon A1's 0.350 network units. All other requests and the financier policy are unchanged. The legacy LAND category/executor metadata is not a claim that an executor delivered the lunar study. The opt-in handoff reads the actual NASA disbursement and represents that same cash in a separate 6C ledger at 100 native units per $1B network unit. The 6C SPN alias means NASA's funded cash; the canonical SPN 220-unit opening is not instantiated. This is a reconciled model boundary, not a live cross-kernel transfer transaction.

## One-page timeline and reconciliation

| Date | Route 1 (USD) | Moon 6C (native units) | State |
|---|---:|---:|---|
| 2026 | NASA opening $442,680,833.524... | 0 | Country-origin investment allocation available |
| 2026 | NASA disburses **$350M**, retains **$92,680,833.524...** | SPN alias opens **35** | Same funded value, two ledger denominations; no 220-unit SPN |
| 2026.25 | No further disbursement | A1 authorized; 35 reserved | Moon-only activity |
| 2027.50 | No further disbursement | 35 spent, supplier receives 35 | A1 starts in authored window; NASA-funded balance 0 |
| 2029.00 | No further disbursement | A1 result completes | Authored SUPPORTS_ADVANCE |
| 2029.01–2029.02 | No further disbursement | Result admitted; study review advances maturity | A2 not registered and no A2 request |
| 2030 | Route 1 ordinary allocations continue outside this single-year funding variant | No further study spending | No automatic replenishment or repeat purchase |

Conservation: Route 1 NASA opening minus closing = **0.350** network units; 6C opening alias = **35** native units; 35 × $10M = **$350M**; 6C study expense = **35**, supplier receipt = **35**, closing alias = **0**. Both ledgers independently satisfy invariants; matching disbursement amount and provenance identify the boundary. The source account in Route 1 and destination opening balance in 6C are not claimed to be one database transaction.

The separate kernel registers only `SOL:MOON`, `PROJ:MOON:POLAR_VOLATILES` and `MOON-A1-SURFACE`. No Mars, Bennu or Ceres project/activity exists to receive money. A2 is intentionally absent. This does not establish an executor mission or empirical lunar prospecting outcome.
