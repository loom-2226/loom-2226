# Sponsor treasury refill sweep (TEST_ONLY, non-canon)

90 bodies, 20 sponsors, 2026–2226. Four sale events, rendezvous, buyer inflow 1,000 model currency annually. The only new authored economic variable is the share of eligible treasury owner returns appropriated into the project sponsor budget: 0, 0.5 or 1. Prices are x1, x3, x10.

| Treasury share | Price | Projects | Sponsors / bodies | Last start | Committed | Gross returned | Sponsor refilled | Zero-balance sponsors at 2226 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | x1 | 42 | 19 / 42 | 2065 | 40.4457 | 6.7200 | 0.0000 | 0 |
| 0 | x3 | 42 | 19 / 42 | 2065 | 40.4457 | 20.1600 | 0.0000 | 0 |
| 0 | x10 | 42 | 19 / 42 | 2065 | 40.4457 | 67.2000 | 0.0000 | 0 |
| 0.5 | x1 | 42 | 19 / 42 | 2063 | 40.4457 | 6.7200 | 2.9400 | 0 |
| 0.5 | x3 | 42 | 19 / 42 | 2059 | 40.4457 | 20.1600 | 8.8200 | 0 |
| 0.5 | x10 | 42 | 19 / 42 | 2052 | 40.4457 | 67.2000 | 29.4000 | 0 |
| 1 | x1 | 42 | 19 / 42 | 2061 | 40.4457 | 6.7200 | 5.8800 | 0 |
| 1 | x3 | 42 | 19 / 42 | 2056 | 40.4457 | 20.1600 | 17.6400 | 0 |
| 1 | x10 | 42 | 19 / 42 | 2050 | 40.4457 | 67.2000 | 58.8000 | 0 |

**Starts after 2066: NO. After 2100: NO. In 2226: NO.** Every case starts exactly 42 projects, across 19 sponsors and 42 bodies. Refilling changes the timing of starts, not the eligible project population.

**Important:** Zero-balance sponsors is a literal zero-account-balance count at 2226, **not** the number unable to afford a pending project. This statistic must not be interpreted as budget sufficiency. The quote/study pipeline and one-start-per-candidate behavior constrain starts.

## Existing return routing preserved

All projects in this test have authored public-agency economic ownership, including privately classified sponsors. Owner distributions route to the corresponding home-country treasury; the existing return-routing table delays treasury appropriation by three years. Financier distributions remain in financier accounts; local reinvestment remains project-local. The new share applies only to eligible treasury owner receipts. Every receipt is handled once with its transaction ancestry and the existing appropriation operation.

The v3 copied lifecycle separates the fourth operation’s physical funding from treasury appropriation. Existing fixed two-receipt appropriations remain an optional scenario mode for legacy parity, disabled for this sweep. All four sale events are executed, with 168 owner-receipt appropriation events at positive share across 42 projects. No names or size multipliers control the share.

## Controls and provenance

- Route 1 control: PASS `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430`.
- Ceres ordered parity: PASS, 8,798 transactions per side, 290 events. The Ceres control uses its established scripted scenario, not the sweep mode.
- Selection firewall: PASS.
- Authored scenario SHA-256: `891b263658181d6bb38ed1bc1b288fd5a6a52dbe438539cd036df310123882bc`.
- Sweep identity SHA-256: `80ecaed754064e484092c8cf85d4b9ce52f16c2fe5fca83001743379b3f29341`.
- DB SHA-256 before: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- DB SHA-256 after: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- Per-case effective scenario SHA-256 and complete annual diagnostics: in case reports.
- All values are synthetic model currency; no canon promotion.
