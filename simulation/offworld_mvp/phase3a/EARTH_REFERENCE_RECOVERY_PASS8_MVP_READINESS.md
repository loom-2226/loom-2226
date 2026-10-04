# Phase 3A Earth Reference Recovery - Pass 8

Status: PRE-CONTRACT / RECOVERY EVIDENCE / NO REPAIR

## Result

Pass 8 completes the broad Earth-reference archaeology needed before drafting the narrow Offworld MVP Earth Reference Contract.

## Full hierarchy verification

All available promoted/selected country, sector and sector-asset artifacts were reconciled.

| Regime | Country rows | Sector rows | Asset rows | Max tested relative residual |
|---|---:|---:|---:|---:|
| v4 2026-2031 bridge | 480 | 4,800 | 19,200 | 8.09e-16 |
| v4 2031-2060 structural | 2,400 | 24,000 | 96,000 | 8.89e-16 |
| v4 2060-2226 successor artifact | 13,360 | 133,600 | 534,400 | 1.03e-15 |
| selected biosynthetic 2100-2226 replay | 10,160 | 101,600 | 406,400 | 9.98e-16 |

Every country-year has 10 sectors and 40 sector-assets. Sector value added, investment, capital and gross output reconcile to country totals where represented. Asset investment and capital reconcile to country totals. There were zero failures at relative tolerance 1e-10.

The selected biosynthetic report also records zero capital stock-flow residual, zero production-equation residual, and sub-1e-15 hierarchy reconciliation residuals.

## Biosynthetic gross output

Biosynthetic sector rows carry gross output and reconcile internally, but the detailed biosynthetic country NDJSON does not directly expose country gross output while PostgreSQL does.

Disposition: NON-MVP. Gross output is excluded from the first Earth Reference Contract. It can be recovered separately if a later simulation requirement needs it.

## Monetary / price basis

Recovered v4 documentation states that all monetary outputs are inherited constant-2015-USD-scale model proxy units, not physical capacity or literal 2226 purchasing-power USD.

The 2026 macro envelope is anchored as `gdp_2026_constant_2015_usd` using `WDI_CONSTANT_2015_USD_LEVEL_PLUS_WEO_REAL_GROWTH`.

For the narrow contract:

- value added is a real-output model proxy on the inherited constant-2015-USD scale;
- investment is economy-wide modeled GFCF/investment flow on that inherited real scale;
- capital is reconstructed/model real capital stock on the inherited accounting scale;
- long-run values are not literal future nominal USD;
- they are not future purchasing-power claims;
- they are not physical productive capacity;
- investment is not actor cash;
- capital is not a liquid financial balance sheet.

This is sufficient for reference-scale use. It does not authorize financial spending.

## MVP use distinction

Cleared for narrow reference use:

- country identity;
- year;
- biological population;
- value-added real proxy;
- investment real proxy;
- capital-stock real proxy;
- temporal derivation identity;
- provenance and exception flags.

Not cleared for direct financial use:

`actor_budget = f * national_investment`

The accessible fraction or allocation rule is a separate scenario/model authorization bridge. Earth may supply the reference investment assertion; the simulation must separately create governed spendable capital and preserve its accounting counterparty.

## Remaining liens

MVP-BLOCKING before Earth Reference Contract freeze:

1. define typed field concepts and unit/basis strings;
2. define exact temporal resolver so v4 cannot be silently used after 2100;
3. expose population specifically as BIOLOGICAL_POPULATION;
4. carry fallback/exception metadata;
5. define BLOCKED behavior outside admitted fields/regimes;
6. preserve the unresolved Phase0 D0.18 versus Phase2 two-root contradiction as a blocker before Phase3 implementation encodes warrant roots.

MVP-BLOCKING before financial coupling, but not reference freeze:

7. authorize Earth-reference-to-actor-capital bridge;
8. define accessible-capital allocation parameter/mechanism;
9. define accounting counterparty/clearing treatment.

NON-MVP / deferred:

10. country gross-output provenance for biosynthetic 2101-2226;
11. primitive replay of every country-year;
12. complete contracts for labor, employment, TFP, trade and diagnostic fields;
13. future purchasing-power conversion;
14. firm/national financial balance sheets;
15. treating reconstructed capital as liquid financing;
16. requalifying historical labels under unreleased Authority Contract v1.

## Recovery sufficiency

For the narrow Offworld MVP purpose, Phase 3A recovery is **SUFFICIENT TO DRAFT A CONTRACT CANDIDATE**.

This is not Authority Contract v1 qualification. V1 is unreleased. It means the evidence is adequate to specify a narrow read-only interface without guessing.

## Candidate admitted fields

The first candidate should admit only:

- `BIOLOGICAL_POPULATION`
- `VALUE_ADDED_REAL_PROXY`
- `INVESTMENT_REAL_PROXY`
- `CAPITAL_STOCK_REAL_PROXY`

plus identity, year, trajectory/derivation, provenance, exception state and replay status.

## Required temporal resolver

- 2026-2030 -> `V4_2026_2030`
- 2031-2059 -> `V4_2031_2059`
- 2060-2100 -> `V4_2060_2100`
- 2101-2226 -> `BIOSYNTHETIC_2101_2226`

The resolver is semantic, not merely a storage convenience.

## Phase 3A conclusion

Broad recovery stops here. Further archaeology should be driven by a concrete contract requirement.

Next deliverable: **EARTH_REFERENCE_CONTRACT_CANDIDATE_v0**.

It remains PRE-CONTRACT / SINGLE-AUTHORITY, grants no CIVPROP implementation authority, and does not claim v1 qualification.
