# Sponsor candidate selection by expected surplus

**DESIGN ONLY · TEST_ONLY · NON-CANON · NON-RUNTIME.** Draft PR #427. This proposes the next small decision layer; it does not change the existing four-case sponsor-to-ledger runner, frozen executor, pricing, geometry, or PRs #423–#426. No study or B/C/D.

## Objective

A sponsor chooses **at most one** mission from an **authored list** of candidates. Each candidate identifies `candidate_id`, `target_body_id`, `mission_type_id`, `vehicle_class_id`, and `year`. The sponsor and its available budget are authored, as are the candidate list, a deterministic tie-break rule, a minimum acceptable surplus, and any explicit deferral condition. No sponsor, body, year, or vehicle is special-cased in code.

For **each sponsor–candidate pair**, author two separate values in USD-equivalent decision utility: `value_if_delivered` and `value_if_failed`. These express that sponsor's assessment of the outcomes, not transferable funds, receipts, or physical resource production. Different sponsors may assign different values to the same mission. No global value constant or implicit zero for failure.

## Probability and quote

**Today**, the same success chance applies to every candidate evaluated with the same selected executor: `p = executor.beliefs.success / (executor.beliefs.success + executor.beliefs.failure)`, from the existing pinned authored executor cast. It is a TEST_ONLY belief, not an empirical mission reliability model. No target-, mission-, or vehicle-dependent probability is currently supported; **do not invent one**. A later per-mission chance, if justified, belongs in authored scenario data keyed by `(executor_id, candidate_id)` with explicit provenance, and must be hashed in the run identity. This is a future option, not a field to populate now.

Look up each candidate's pinned quote using its year, target, mission type, and vehicle class. Only `PRICED_TEST_ONLY` rows with numeric quotes are eligible for consideration. Infeasible, unpriced, missing, or mismatched rows are excluded with explicit reasons; they do not become zero-price opportunities. The quote remains labeled **TEST ONLY / UNCALIBRATED PRICE PROXY**.

## Decision rule

For each eligible candidate, derive using exact decimal arithmetic:

`expected_value = p × value_if_delivered + (1 − p) × value_if_failed`

`expected_surplus = expected_value − quoted_price`

First exclude candidates whose quoted price exceeds the sponsor's authored available budget. Of the remaining eligible and affordable candidates, select the **highest expected surplus**. On an exact surplus tie, apply the **authored deterministic tie-break rule**, such as ascending authored candidate priority then candidate ID; do not use accidental input or dictionary order. If there are no eligible affordable candidates, REJECT (or DEFER only if an explicitly authored deferral condition applies). If the best expected surplus is **below** the authored minimum threshold, REJECT; equality passes. An explicitly authored deferral condition may instead produce DEFER, with a recorded reason and no expenditure. Otherwise ACCEPT exactly one selected candidate. Record each candidate's quote status, affordability, derived expected value/surplus, exclusion reason, tie-break, and final selection.

No speculative search, new price model, second mission, or additional actor subsystem. All scenario inputs, values, thresholds, tie-break rule, quote/cast pins, and implementation bytes must affect the run identity. Preserve deterministic replay.

## Ledger boundary

**Sponsor value never enters the ledger.** Neither expected value nor expected surplus is an inflow, balance increase, refund, or transaction. The ledger starts with authored budget; ACCEPT debits only the selected quote once, regardless of DELIVERED or FAILED; REJECT and DEFER debit nothing. Every posting retains the quote's best departure date and flight days and checks `initial_budget = cumulative_spent + balance`. No new clock.

## Planned proportional tests (not executed)

- Two or more authored candidates with distinct outcome values: choose the **highest expected surplus among affordable eligible candidates**, not the cheapest or highest gross value. Verify sponsor-specific values can reverse a ranking.
- Tie: use the authored rule deterministically; reorder candidate input and obtain the same winner.
- Below-threshold best surplus: REJECT; exactly at threshold: ACCEPT. Explicit DEFER only under authored condition.
- Unaffordable, INFEASIBLE, UNPRICED and missing quotes: never selected, with explicit reasons. No acceptable candidate: no debit.
- Same pinned executor beliefs yield the **same p** for all current candidates. No mission-specific chance is silently derived.
- **Value isolation:** change only authored outcome values; selection may change, but no value or expected surplus is posted to the ledger. For a fixed selected quote, budget and debit must be identical despite changes in valuations. Deliberately inject value into a ledger balance and require conservation to fail.
- Accepted FAILED and DELIVERED outcomes both debit the exact selected quote once; ledger remains conserved. Run each authored scenario twice, compare canonical outputs exactly, and verify identity sensitivity to candidate lists, values, thresholds, tie-break, and pins.

**Stop condition:** document approved before any implementation. No code or run is authorized by this document.
