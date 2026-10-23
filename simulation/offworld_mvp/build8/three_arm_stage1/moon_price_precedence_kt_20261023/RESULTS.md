# PR427: complete-cost-layer source precedence, no clamp

TEST_ONLY / NON-CANON. All 90 bodies, 20 sponsors, 2026–2226, share 1, material price x1, four-sale cap, high buyer budget, rendezvous.

## Selection and invariant

- Prefer priced `rendezvous_v2_90.price_fields.total_usd` (complete cost layer) over `recovered_combined_59.lowest_price_usd`. Where no complete V2 quote exists, retain completed moon/giant quotes; preserve other source rows.
- `price_rows.csv` prints every winning source, field, unit and model-unit value. No clamp, no rewritten quote price.
- Floor is a strict 0.7-model-unit check before the run, not a pricing operation.
- **667** priced source-year/mission rows checked; **205** below floor, all **flyby** and unused by this rendezvous case. Every row is listed in `floor_audit.json` with body, mission type, year, source and value.
- **0** below-floor rows used by this 2026 rendezvous campaign. Any such row raises an exception and stops the run.
- Three unpriced: DACTYL, SELAM, HYPERION.

## Comparison with clamped case

| Measure | Clamped | Source precedence |
|---|---:|---:|
| Starts | 57 | 57 |
| Last start year | 2140 | 2138 |
| Committed | 124.2581766338780427472 | 119.4807108013423935 |
| Gross returned | 9.12000 | 9.12000 |
| Treasury refilled | 7.98000 | 7.98000 |

`per_body_commitment_delta.csv` prints all 57 old/new start years, sponsors, commitments and exact differences.

- Bodies with changed commitment: 33.
- Bodies with changed start year: 18.
- Aggregate commitment delta: -4.7774658325356492472.

## Funnel

| Studied | Positive | Priced | Candidate | Started |
|---:|---:|---:|---:|---:|
| 90 | 90 | 87 | 87 | 57 |

`body_funnel.json` prints each of the 90 bodies.

## Controls

- Route 1 control: `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430` PASS.
- Ceres equivalence: PASS.
- Merged price SHA-256: `49fbd0f1015268d24e931b9e1d7083cb8a0cd3f6c02a4942a130d0885695922f`.
- Database before: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- Database after: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- No existing files edited. Draft PR #427 only.
