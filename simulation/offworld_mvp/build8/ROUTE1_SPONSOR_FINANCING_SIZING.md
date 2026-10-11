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
