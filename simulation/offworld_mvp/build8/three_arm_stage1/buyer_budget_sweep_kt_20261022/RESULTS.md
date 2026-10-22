# Buyer budget sweep results

**Status:** executed TEST_ONLY, non-canon sensitivity run.  
**Clock:** 2026–2226 inclusive (201 annual inflow records per case).  
**Coverage:** 90 bodies and 20 sponsors in every campaign. The annual Earth
inflow is the same for every buyer, body, sponsor, and year. No governor or
body-size factor is used.

The annual budgets are 10, 100, and 1,000 model currency units. The existing
synthetic buyer endowment is 100 units per project, making these 0.1×, 1×,
and 10× reference levels. They are sensitivity points, not empirical values.

| Case | Earth inflow/year | Total inflow | Projects started | Distinct bodies / sponsors | Buyer endowment deferrals | Sponsor has no affordable candidate | No-quote pairs | Sales | Money returned | Ties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Low | 10 | 2,010 | 21 | 21 / 11 | 2,885 | 891 | 24 | 40 | 1.60000 | 0 |
| Medium | 100 | 20,100 | 42 | 42 / 19 | 196 | 2,905 | 24 | 84 | 3.36000 | 0 |
| High | 1,000 | 201,000 | 42 | 42 / 19 | 0 | 3,049 | 24 | 84 | 3.36000 | 0 |
| Zero-conversion control | 100 | 20,100 | 66 | 66 / 20 | 799 | 0 | 24 | 132 | 5.28000 | 862 |

The medium and high cases start the same number of projects. At the high level,
buyer-endowment deferrals disappear; sponsor affordability then limits further
starts. The growing sponsor-deferral count reflects repeated annual retries of
pending candidates when no sponsor has enough uncommitted capital. The low
case remains buyer-limited.

The zero-conversion control sets mission price conversion to zero. It does
not set extraction or sales to zero: construction, lifecycle, and sales remain
active. It starts 66 projects and records 132 sales. Its extra starts relative
to the medium rendezvous case result from removing the converted mission-price
component from sponsor commitment. The 862 ties are equal-commitment candidate
groups under that zero-price condition.

Across the three priced cases, the campaign recorded 90 positive A1 reviews,
66 quote-eligible candidate pairs, and 24 no-quote pairs. The existing
campaign’s candidate pipeline therefore instantiated 66 quote-eligible
project pairs in this run; these results do not establish outcomes for a
7,601-project portfolio. In years with no pending eligible candidate, the
annual diagnostics say whether there was no annual callback, no reviewed-
positive quote-eligible pair, a missing quote, buyer endowment shortfall, or
sponsor affordability shortfall. The first clock year (2026) has no annual
policy callback in the parent runner; its inflow was entered at the first
callback (2027) with effective transaction year 2026 and is identified that
way in the funding ledger.

## Verification

- World SQLite SHA-256 matched the supplied baseline:
  e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde.
- Route 1 exact control passed:
  4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430.
- Ceres lifecycle parity passed with 8,798 transactions, 290 events, and
  zero ordered-projection mismatch.
- Selection firewall tripwire passed: clean allowlisted input accepted and a
  deliberate hidden-world field rejected.
- All annual funding records used a new Earth boundary account and a kernel
  transfer into earth_market. The raw high-precision callback money residual
  was zero in the recorded annual diagnostics.
- Evidence table in every case: REAL 0, PLACEHOLDER 90,
  TEST_ONLY_STUDY 249.

The JSON case reports contain complete annual diagnostics, funding transaction
IDs, candidate dispositions, starts, project chains, sales, returns, sponsor
decisions, body roster, and sponsor roster. input_identity.json binds each
scenario level and case into the run identity.
