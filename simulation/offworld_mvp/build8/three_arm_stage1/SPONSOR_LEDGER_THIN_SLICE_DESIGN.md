# Stage 1 thin slice: sponsor to ledger

**DESIGN ONLY.** Draft PR #427; TEST_ONLY, NON-CANON, NON-RUNTIME. No implementation, simulation run, study, or change to frozen paths. Approval gate before code.

## Objective and boundary

Exercise one sponsor decision and one existing executor outcome against a previously committed vehicle/mission quote. Use a scenario file, a single small runner in the PR #427 area, and a report. Do not change geometry, pricing, frozen executor, or PRs #423–#426. First inspect the existing executor's callable contract read-only. **If this slice requires editing a frozen executor or other frozen path, stop and report instead of implementing a replacement.**

## Authored scenario inputs

A scenario JSON file contains a list of at least two cases. Each case authors: `case_id`, `sponsor_id`, `initial_budget_usd`, `target_body_id`, `year`, `mission_type_id`, `vehicle_class_id`, `decision_rule`, and `outcome_rule`. The scenario also pins the exact pair-quote CSV by SHA-256 and its quote-run identity. All choices, including any executor selection and any transaction treatment, must be authored here, not inferred from actor/body names or silently defaulted in code.

Decision rule, expressed in ordinary terms and recorded as authored data: **reject** if the exact selected quote is absent, not `PRICED_TEST_ONLY`, or exceeds available budget; **accept** when the quote is `PRICED_TEST_ONLY` and the sponsor can pay; **defer** only when the scenario explicitly authors a deferral condition, otherwise never defer. An explicit reject decision is also allowed. No alternate quotes or invented funding. Quote is always labeled **TEST ONLY / UNCALIBRATED PRICE PROXY**; it is not a real cash cost.

Outcome rule is explicit in scenario data. For a deterministic demonstration, author `SUCCESS` or `FAILURE` as the outcome, subject to the existing executor's supported input/output contract. If the existing executor requires a probability draw, author the probability, seed, draw derivation, and threshold comparison in the scenario; capture the derived draw in the report. Never use ambient randomness. A rejected or deferred mission is **NOT_EXECUTED**, not a failed flight. If the existing executor cannot accept this authored outcome policy without frozen changes, stop.

## Flow

1. Read and hash the exact scenario bytes, quote CSV bytes, and pinned quote-run identity. Run identity also includes the selected executor version/pin and any other authored data read to decide or execute. Fail closed on missing/mismatched inputs.
2. Lookup exactly one row by (year, body, vehicle class, mission type); do not recompute geometry or prices.
3. Apply the authored decision rule to the quote and budget. Record ACCEPT, DEFER or REJECT and the reason.
4. Only for ACCEPT, invoke the existing executor without changing it. Record its actual outcome and provenance; do not fabricate an executor result.
5. Post the authored financial treatment and verify the conservation equation after **each** posting. Report the full decision, quote classification, outcome and ledger.

## Minimal ledger

Start with an authored budget as the only inflow. Track `spent_usd` and `balance_usd` in exact decimal units; never floating-point dollars. Every state transition must satisfy:

`initial_budget_usd = cumulative_spent_usd + current_balance_usd`

Reject/defer spends zero. On acceptance, debit the quoted amount exactly once at the authored commitment/execution point. Failure does not silently refund or charge again. No loans, transfers, income generation, or second account. A test must deliberately corrupt one posting and assert failure of the conservation check.

## Cases and replay acceptance

- **Affordable:** an authored target/pair with a pinned `PRICED_TEST_ONLY` quote and an authored budget at least that quote. Expect ACCEPT, one real executor outcome, one debit, and conserved ledger.
- **Unaffordable:** an authored target/pair with a pinned `PRICED_TEST_ONLY` quote and an authored budget below that quote. Expect REJECT, NOT_EXECUTED, zero debit, and unchanged balance.

Run **each case twice** from fresh state. Compare complete canonical result bytes (including decision, outcome, ledger, provenance and identity), excluding nondeterministic wall-clock metadata. Both runs must match exactly. Changing any scenario input, decision rule, outcome seed/value, quote pin, or selected pair must change run identity. No calibration claims.

## Stop condition

One short scenario file, one thin runner, and proportional tests within PR #427 only, **after separate approval**. Stop immediately on a frozen-executor edit requirement, unpinned input, unsupported executor outcome contract, non-test quote, nonconserved ledger, or replay mismatch. No B/C/D.

## Approved amendment: deterministic outcome resolver and third case

The frozen executor's `simulate` consumes explicitly authored `DELIVERED`/`FAILED` outcomes, not a seeded chance. Do not edit it or pretend it resolved an outcome. A new PR #427-local **TEST ONLY** `outcome_resolver.py` derives SHA-256 from authored seed and case ID, interprets its first 64 bits as a draw in [0,1), and compares that draw to a chance derived from the **existing authored executor beliefs** `success/(success+failure)` in the pinned executor cast. This is a **test-only outcome resolution**, not a full executor run or an empirically calibrated reliability. Report this distinction explicitly. The scenario authors the executor identity and cast pin; the resolver code hash and scenario/quote/cast bytes enter the run identity.

A third authored case selects an `INFEASIBLE` pinned quote and must REJECT, NOT_EXECUTED, and debit zero. Every ledger entry carries the selected quote's `best_departure_date` and `best_flight_days` verbatim; infeasible rows may carry blank values. No new clock or synthetic date. Run all three cases twice and compare canonical bytes. Deliberately corrupt a ledger balance and require the conservation assertion to fail. No geometry, B/C/D, or frozen edits.
