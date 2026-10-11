# Route 1: finite country-pool funding for 11 BUILD/LAND Sponsors

**Class:** DESIGN / SIZING ONLY; RESEARCH; NON-CANON; NON-RUNTIME; NON-QUALIFICATION. **No implementation authorization.** Proposed for draft PR #388; no merge.

## Objective and boundary

Connect the 11 BUILD/LAND project entries in `sponsor_executor_network_trial.PROJECTS` (NASA, CNSA, ISRO, JAXA, ESA, CNES, DLR, Australian Space Agency, UAE Space Agency, ispace, Interlune) to **one finite set of country-scoped balances in one persistent kernel**. Sponsor requests, financier policy decisions, commitments, disbursements, and eventual executor payments must draw from that same conserved money. Insufficient funding causes WAIT or rejection, not an exact-quote top-up. Keep LAUNCH/RUN out of this first exercise; do not assert that all 11 are funded or physically delivered. Preserve existing `run_yearly()` legacy BUILD→LAND as the default and the three frozen replay fingerprints, snapshots, and transaction/parent graphs.

## Smallest causal path

1. Use `build_country_opening()` and the existing country mobilization ledger. Select and record one **authored fraction** `s` of each mobilized country balance available to the 11-project experiment. The network trial uses `s=.02` while `all_sponsors_country_trial` reserves `s=.5` of country mobilization for all eligible Sponsors: these are **different trial assumptions**, not interchangeable budgets. Never add the two pools.
2. Reuse `PUBLIC`/`PRIVATE` participation and `PREFERENCES` to allocate each country's finite selected amount to eligible Sponsor accounts. For multinational ESA, credit distinct country-origin contributions into one ESA budget with ledger lineage. Reserve funds for nonselected Sponsors or leave them in country pools; **do not reweight all 20 recipients onto the 11** without labeling a changed assumption. The same country balance must never be allocated twice.
3. Each Sponsor chooses whether to request financing using existing Sponsor policy and **admissible information**, not hidden truth. Its request carries the selected BUILD or LAND project and a quoted cost. Reuse `build_financing_request` and `run_financier_policy` from the screened driver for a financier's approve/wait/reject decision. Financier must see finite available cash and already-committed exposure; deterministic order or existing order-independent clearing must resolve simultaneous requests without creating money. Record a reason for every idle/rejected Sponsor.
4. On approval, record a financier commitment and then a distinct disbursement into the project's persistent cash account through existing kernel transitions. Only later, if there is an authorized plan and readiness permits, schedule delivery and pay the selected executor; `AWARDED_PENDING_PLAN` is not a procurement award, delivery, or revenue. No automatically sized financier top-up. Track opening Sponsor balance, available/uncommitted financier balance, committed amount, pre-payment project cash, and paid amount **separately**.
5. Carry the same accounts, commitments, project state, pending work and events into the next simulated year. A second-year replay must start from the first-year closing state, not rebuild a fresh 2026 opening. Replay determinism and transaction conservation are hard invariants.

## Reuse vs new work

| Reuse directly or narrowly adapt | New for Route 1 |
|---|---|
| `all_sponsors_country_trial.py` / `country_sponsor_allocation_trial.py`: finite country mobilization, authored weights, conserved transfers | One shared **persistent** allocation+financing+project run for the 11 selected Sponsors; preserve excluded shares |
| `sponsor_executor_network_trial.py`: roster, project category/ceilings, executor eligibility, award-pending distinction | Feed actual Sponsor request and financier decision results into this roster; separate ceiling from selected supplier price |
| `screened_yearly.py`: `run_sponsor_prospecting_policy`, `build_financing_request`, `run_financier_policy`, kernel commitment/disbursement | Adapt policy inputs for public/private identities and 11 individual projects; no hard-coded two-sponsor/one-country financing assumption |
| `esa_build_trial.py`: explicit lowest-feasible BUILD quote, removal/fallback price switch, named `EXECUTOR_TO_NETWORK_FACTOR`, authored readiness draw | Per-project quote/eligibility selection for other BUILD/LAND projects; no invented real bids; absent explicit quotes use labeled authored defaults or stop |
| `scripts/plot_esa_build_results.py`: record kernel events to JSON, plot only recorded outcomes | Generalize input to 11 Sponsors and year-by-year funding outcomes; do **not** create a new reporting subsystem |

The existing network trial currently uses an opening-balance >= project-cost test and commits/disburses directly, **not** a financier underwriting decision. The ESA helper bypasses the original yearly policy path and sizes financing exactly to its winning quote. Neither is already Route 1.

## Joint sensitivity: pool fraction AND quote conversion

For Sponsor `i`, let `M_c` be actually mobilized cash in country `c`, `w_ic` its fixed authored allocation weight, and `W_c` the sum of weights of **all** eligible Sponsors (including excluded LAUNCH/RUN participants). Then the illustrative allocation is

`B_i(s) = sum_c [s * M_c * w_ic / W_c]`.

If a project has an authored executor-unit quote `u_i` with no explicit network-unit quote, the comparison cost is `Q_i(f) = u_i / f`, where `f = EXECUTOR_TO_NETWORK_FACTOR = 200/3` (NASA LAND anchor: 3.00 executor units / 0.045 network units). With an **explicit** network-unit quote, use it unchanged instead of `u_i/f`. Basic cash affordability is `B_i(s) >= Q_i(f)`; actual award still requires a financier approval, available uncommitted funds, eligibility and a plan. When `Q_i=u_i/f`, the affordability ratio is `B_i/Q_i = s*f*[sum_c M_c*w_ic/W_c]/u_i`: pool fraction and factor multiply. This is a structural sensitivity, not a calibration.

For a *hypothetical* Sponsor whose allocation at `s=.02` is `0.0200` network units and whose BUILD default is `u=1.70`, the two-dimensional comparison is:

| Pool fraction `s` | `f=50` (quote .0340) | `f=200/3` (quote .0255) | `f=100` (quote .0170) |
|---|---|---|---|
| .01 (budget .0100) | No (0.29×) | No (0.39×) | No (0.59×) |
| .02 (budget .0200) | No (0.59×) | No (0.78×) | Yes (1.18×) |
| .04 (budget .0400) | Yes (1.18×) | Yes (1.57×) | Yes (2.35×) |

These numbers are **illustrative, not measured allocations for any of the 11 Sponsors**. Recompute the matrix from the actual 11 Sponsor allocations before drawing a real-world or in-simulation affordability conclusion. Explicit Airbus .0240 and Thales .0270 ESA quotes do not vary with `f`; their affordability changes only with `s` and competition for cash. Changing `f` can reverse the ranking of a fallback offer against an explicit offer (as in the ESA removal control). Changing `s` and `f` together can therefore change both affordability and the winning quote; report both dimensions, not a one-at-a-time sensitivity.

## Size, first stop and verification

**Estimate: ~350–600 net new/changed Python lines** for the 11-Sponsor shared allocation, request/financier decision, commitment/disbursement and one-year persistent handoff; **~120–220 test lines**, **~40–100 event-report adaptation lines**. Total **~510–920 lines** excluding this design note. This is a rough inspection-based estimate, not a measured diff. It exceeds the previous 170-line *ESA driver-only* gate because Route 1 joins previously separate experiments; do not pretend it is a small driver conditional. Avoid new agents, banking, schema or finance architecture.

**First stopping condition:** Run **one 2026 epoch for the 11 Sponsor roster** using existing policy/kernel mechanisms and a fixed, authored pool fraction. Stop immediately if the existing Sponsor/financier policy cannot represent the required public/private actors or if funds cannot be committed and disbursed from a single conserved pool **without rewriting the frozen driver or inventing a new finance subsystem**. If it runs, stop after reporting 11 requests/outcomes, country-to-Sponsor lineage, closing cash and commitments, and a deterministic replay. Do **not** start multi-year delivery, new capacity competition, or diagrams until that gate is reviewed.

**Required regression before any implementation PR review:** all three frozen yearly replays must retain their exact snapshots, transaction identities, parent graphs and fingerprints. Legacy BUILD→LAND remains the unmodified default. This report alone changes no runtime or tests.

## Pre-code 2026 affordability prediction from existing country allocations

Recomputed from the existing `build_country_opening` Earth v4 capacities, `derive_mobilization` at opportunity=1, `PUBLIC`/`PRIVATE` country participation, and `PREFERENCES` over **all 20** eligible Sponsors. Apply `s=.02`, the existing `sponsor_executor_network_trial` fraction, without reallocating non-BUILD/LAND shares. These are **predicted cash-threshold results against existing `PROJECTS` costs**, not results of financier policy, quote competition, execution or actual 11-Sponsor Route 1 code.

| Sponsor | Category | 2026 allocated cash (`s=.02`) | Existing project cost | Predicted threshold outcome |
|---|---|---:|---:|---|
| NASA | LAND | .03541447 | .045 | WAIT |
| CNSA | LAND | .10989995 | .045 | AFFORDABLE |
| ISRO | BUILD | .02340433 | .015 | AFFORDABLE |
| JAXA | LAND | .01472373 | .030 | WAIT |
| ESA | BUILD | .05229053 | .030 | AFFORDABLE |
| CNES | BUILD | .00604042 | .015 | WAIT |
| DLR | BUILD | .00499128 | .015 | WAIT |
| Australian Space Agency | BUILD | .00824577 | .015 | WAIT |
| UAE Space Agency | BUILD | .00264319 | .045 | WAIT |
| ispace | LAND | .00588949 | .045 | WAIT |
| Interlune | BUILD | .00708289 | .090 | WAIT |

**Prediction: 3 affordable (CNSA, ISRO, ESA); 8 waiting** under existing costs and 2% allocations. The source code's `network` trial is a budget threshold followed by commitment, **not financier underwriting**. A real financier could still decline an affordable request. A fallback-priced quote may differ from `PROJECTS` cost, so the 3/8 count is **not invariant across the factor map below**. ESA's .05229053 is the sum of eligible contributions from 12 country pools; no single DEU-only allocation is substituted.

**Information gain criterion for Gate 1:** If the new one-epoch run merely produces 3 funded / 8 waiting with no new policy-driven distinctions, its substantive result is *only* that the existing allocation and cash constraints have been correctly joined to persistent Sponsor commitments. Record that as a successful integration check, **not a discovered economic result**. Report actual policy outcomes separately from the predicted cash test, including any differences and why.

## Two-parameter affordability map (11 Sponsors, not an invented baseline)

For the **existing** `PROJECTS` network-unit costs (which are explicit and therefore independent of `f`), the count of Sponsors clearing the budget test changes with pool fraction `s` but is constant across conversion-factor columns:

| Pool fraction `s` | `f=50` | `f=200/3` (NASA anchor) | `f=100` |
|---|---:|---:|---:|
| 1% | 1/11 | 1/11 | 1/11 |
| 2% | 3/11 | 3/11 | 3/11 |
| 4% | 5/11 | 5/11 | 5/11 |

**This flat factor sensitivity is intentional:** multiplying/dividing existing explicit network-unit costs by `f` would double-convert them. The map is a source-backed **current-cost control**, not a fallback-quote simulation. The companion **fallback-quote sensitivity** uses `Q_BUILD=1.70/f` and `Q_LAND=3.00/f` for all 11 as an explicitly different, hypothetical cost convention; it must not be silently mixed with current project costs:

| Pool fraction `s` | `f=50` | `f=200/3` | `f=100` |
|---|---:|---:|---:|
| 1% | 0/11 | 2/11 | 2/11 |
| 2% | 2/11 | 2/11 | 4/11 |
| 4% | 4/11 | 4/11 | 4/11 |

Each cell is a **cash-affordable Sponsor count**, not a funded count or a forecast. The first table tests pool scale against existing authored project costs; the second exposes joint `s,f` sensitivity under a clearly labeled counterfactual quote convention. If actual explicit executor quotes are supplied, preserve them and vary only fallback quotes with `f`. No assertion that the second table's hypothetical defaults are quotes from real firms.

## Gate 2: 2027–2029 carry-forward and executor contention (separate authorization)

**Prerequisite:** Gate 1 has conserved 2026 accounts, genuine Sponsor/financier decisions, committed/disbursed cash, project status and deterministic replay. Gate 2 is **not authorized for implementation by this report**.

Resume the **same persistent kernel state** for 2027, 2028 and 2029. Admit each year's country mobilization once, retain unspent country and Sponsor balances and already-committed exposure, and allow 2026 WAIT Sponsors to resubmit under existing policy using information available by that year. Funding is contingent: do **not** promise all eight WAIT Sponsors eventually fund. Carry any uncommitted remainder, rejected request, or expired/lapsed commitment explicitly, without double spending. Select BUILD/LAND executor offers using the established quote/fallback switch and eligible cast; apply **finite per-year slots**, record bids lost to unavailable slots, and advance incomplete work to the next year rather than treating award as instant delivery. Readiness draws and scheduling must remain deterministic and actor-visible only when properly disclosed. A later funding approval may change the executor or start year; preserve the lineage.

**Gate 2 output:** annual table for all 11 Sponsors (WAIT, policy-rejected, committed, disbursed, scheduled, deferred, delivered), country-pool opening/inflows/closing, Sponsor/project cash and unpaid commitments, executor utilization by BUILD/LAND and year, queue age, actual delivery/payment years and event-derived timeline. Compare identical seeds under (a) no executor contention and (b) finite slots, holding funding inputs constant. **New information exists only if** carried-forward balances, policy choices or finite slots produce a different funded set, queue, delay, payment, or year-end state than static annual affordability alone predicts. If no such difference appears, report the null result and stop, rather than adding machinery to force emergence.

**Gate 2 stop:** after 2029 close and deterministic replay of the 2026–2029 state/event history, or earlier at the first demonstrated missing invariant/actor-policy capability. No unbounded campaign, banking, market-clearing system, new scheduler framework or canon promotion. The old two-stage driver remains the default, and the frozen three yearly replays must stay unchanged. The earlier 510–920-line estimate is for the Gate 1 integration only; Gate 2's incremental code size is **not yet defensibly estimable** until Gate 1 reveals what persistence/slots machinery already suffices.
