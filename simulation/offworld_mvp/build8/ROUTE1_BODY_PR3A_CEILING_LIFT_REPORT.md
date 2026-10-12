# PR 3A — Separate counterfactual report: sponsor ceilings only

**REPORT ONLY / TEST_ONLY / NON-CANON.** These are two independently run **201-year** Route 1 Phobos+Europa campaigns. The effective named setting registers differ in **exactly one key**: `SPONSOR_REQUEST_CEILINGS_ENABLED`, True in the control and False in the counterfactual. The underlying 20 sponsors, 16 executors, two bodies, ordering, yearly stage cap, study prices, A1 seed/50% outcome rule, financing policy, national annual allocations, and original 2026–2035 behavior are identical.

## Paired-run results

| Measure | Existing ceilings | Ceilings disabled | Difference |
|---|---:|---:|---:|
| Bodies receiving funded A1 | **2** | **2** | **0** |
| Distinct sponsor/body projects funded | **2** | **2** | **0** |
| A2 studies funded | **1** | **1** | **0** |
| Total supplier-paid new study stages | **3** | **3** | **0** |
| Request attempts | **5** | **5** | **0** |
| Primary-blocked requests | **2** | **2** | **0** |
| TEST_ONLY new supplier payments | **0.045** | **0.045** | **0** |
| 2226 closing sponsor cash | **≈1,662.358631** | **≈1,662.358631** | **0** |

In both runs the financed A1 body claimants are **Europa → Australian Space Agency** and **Phobos → Axiom**. Phobos A2 is funded in 2037 after the accepted A1 review. Europa A2 is blocked once because its synthetic review is insufficient.

## Named primary blockers, by decade

Each attempt has exactly one primary blocker when not funded. These are not results from physical 90-body orbital mission quotes.

| Years | Normal attempts | Normal funded | Normal `MAX_NEW_STAGES_PER_SPONSOR_YEAR` | Normal `A1_REVIEW_INSUFFICIENT` | Lifted attempts | Lifted funded | Lifted stage limit | Lifted insufficient A1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2036–2045 | 5 | 3 | 1 | 1 | 5 | 3 | 1 | 1 |
| 2046–2055 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2056–2065 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2066–2075 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2076–2085 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2086–2095 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2096–2105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2106–2115 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2116–2125 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2126–2135 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2136–2145 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2146–2155 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2156–2165 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2166–2175 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2176–2185 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2186–2195 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2196–2205 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2206–2215 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2216–2225 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2226–2226 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

All **other named primary blockers are zero** in every decade in both cases, as shown individually in the full limit-by-limit matrix in `ROUTE1_BODY_PR3A_REVIEW.md`. Overall, **5 attempts = 3 funded + 2 primary blockers** in each run; all twenty decade buckets reconcile separately.

## Which rule binds next?

Removing the sponsor ceiling adds **zero body projects** because the existing per-request ceilings already exceed the TEST_ONLY 0.015 analytical service quotes for each actually funded request. The next observed blockers are:

- **One** otherwise-affordable Phobos A1 request stopped in 2036 by the **SOL-PROPOSED TEST_ONLY one-new-stage-per-sponsor/year restriction**; the next sponsor can still fund it. This is not a demonstrated physical or organizational limit.
- **One** Europa A2 request stopped in 2037 by the synthetic A1 **INSUFFICIENT/HOLD** review outcome.

A **separate** sensitivity increasing only the stage-per-sponsor-year setting from 1 to 2 allows the Australian Space Agency to fund both Europa and Phobos initial studies. Total new financed stages remain three; the artificial governor changes claimant identity rather than the count of bodies reached. This sensitivity is **not mixed into the ceilings-only experiment**.

**Scope warning:** These are abstract RUN/BUILD study-work tokens, not priced orbital reconnaissance or landing missions. Build 7 physical mission prices and 2036–2226 trajectory affordability are outside PR 3A. Do not generalize two cheaply funded study projects into 90 spacecraft missions.

**Proof:** The new `test_ceiling_lift_changes_one_setting_only_and_fundability_is_measured` asserts exactly one differing effective setting, identical paid stages, body claimants, financier receipts, closing balances, and actual transactions. The exact 67/67 PASS sequential regression command and its 18 verified module counts are in `ROUTE1_BODY_PR3A_REVIEW.md`.

No runtime code or parameter change is introduced by this separate report.
