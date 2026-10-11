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

## Pricing correction and two 2026 affordability maps (2026-10-11; supersedes earlier factor sensitivity)

**Design report only. No runtime or pricing-code change.** The earlier NASA-anchored factor `200/3` in this report describes the **unchanged existing ESA experiment**, not the recommended next Route 1 pricing assumption. Earth investment-proxy units are normalized at `1e9` per `MODEL_CURRENCY`; thus one network unit has a **$1B constant-2015-USD-scale proxy display equivalence**. The separate `mobilization_m_max=.001` caps how much national investment is mobilized; it does **not** turn one currency unit into $1T. Mobilized cash `M=(I/1e9)*.001`, and the network trial offers `s*M` to **all 20** weighted Sponsor participants before selecting the 11 BUILD/LAND entries. Neither conversion implies observed financing or contemporary purchasing power.

**Proposed, not implemented:** re-anchor one *screened-delivery executor unit* at **$50M** proxy-equivalent, hence `EXECUTOR_TO_NETWORK_FACTOR=20`, `BUILD=1.70/20=.085` network units ($85M), and `LAND=3.00/20=.150` ($150M). The $50M unit is an **authored scenario convention**, not empirical mission pricing. Existing explicit network-unit quotes, such as Airbus .024 and Thales .027, remain explicit and **do not convert** with this factor; comparing those legacy quotes to the new defaults requires an explicit repricing decision rather than silently mixing regimes.

**Map A: original authored ceilings, unchanged.** Columns report the **names that pass cash-versus-ceiling**, not actual approvals. For these already network-denominated ceilings, the new factor is irrelevant. The original ceilings are NASA .045, CNSA .045, ISRO .015, JAXA .030, ESA .030, CNES .015, DLR .015, Australian Space Agency .015, UAE Space Agency .045, ispace .045, Interlune .090. Note the existing roster defines **UAE Space Agency as BUILD**, not LAND. With new default supplier prices, **none** of these ceilings buys a whole BUILD (.085) or LAND (.150) service: a cash-pass in this map is **not executable procurement**.

| Share of mobilized national pool offered to all 20 Sponsors | Cash-affordable at authored ceiling (11-Sponsor names) | Count |
|---|---|---:|
| 1% | CNSA | 1/11 |
| 2% (network-trial baseline) | CNSA, ISRO, ESA | 3/11 |
| 4% | NASA, CNSA, ISRO, ESA, Australian Space Agency | 5/11 |
| 10% | NASA, CNSA, ISRO, JAXA, ESA, CNES, DLR, Australian Space Agency | 8/11 |
| 25% | NASA, CNSA, ISRO, JAXA, ESA, CNES, DLR, Australian Space Agency, ispace | 9/11 |
| 50% | NASA, CNSA, ISRO, JAXA, ESA, CNES, DLR, Australian Space Agency, UAE Space Agency, ispace, Interlune | 11/11 |

**Map B: raised mission-scale ceilings, authored illustration.** Set each BUILD ceiling to **.200 ($200M)** and each LAND ceiling to **.300 ($300M)**. These are *not* sourced mission estimates; they are test parameters deliberately above the default service prices. Cash-affordability now means Sponsor budget reaches its raised ceiling, a **conservative full-ceiling-financing test**. Actual funding need may be lower if the financier underwrites a priced service rather than the entire ceiling.

| Share of mobilized national pool offered to all 20 Sponsors | Cash-affordable at raised ceiling (11-Sponsor names) | Count |
|---|---|---:|
| 1% | None | 0/11 |
| 2% | None | 0/11 |
| 4% | None | 0/11 |
| 10% | CNSA, ESA | 2/11 |
| 25% | NASA, CNSA, ISRO, ESA | 4/11 |
| 50% | NASA, CNSA, ISRO, JAXA, ESA, Australian Space Agency | 6/11 |

**Price-versus-ceiling cross-check:** At the proposed `f=20` and original **2%** Sponsor allocation, **0/11** can afford even the $85M BUILD / $150M LAND default; at 4%, CNSA and ESA can afford one default service, even though Map B's full raised ceilings are still unaffordable. At 10%, NASA, CNSA, ISRO and ESA clear their respective default *service prices*, while only CNSA and ESA clear the *raised programme ceilings*. This separation is essential: **budget >= supplier price** is a possible single-service financing gate; **budget >= project ceiling** is a stronger full-programme-financing gate. Neither implies an actual financier approval, readiness or executor slot.

**Interpretation / stopping decision:** At 2% the proposed $50M executor-unit anchor creates a **0-funded-by-price** first epoch for these 11 Sponsors unless another independently authorized financing source or altered allocation fraction exists. Do not hide that by handing each financier the exact winning quote. Gate 1 should explicitly report this null result and stop if no new policy information is produced. Gate 2 (2027–2029) remains separately authorized, and would be meaningful only if carried-forward funding and executor competition change the queue/delivery path. Do not call the $200M/$300M ceiling values “realistic” as an empirical claim; they are illustrative mission-scale assumptions. Existing frozen replays and old two-stage default remain unchanged.

**Reproduction:** Each Sponsor's 2%-share opening balance is tabulated above. For a map row with pool fraction `s`, compare `B_i(s)=B_i(.02)*(s/.02)` against the applicable authored or raised ceiling. Names and categories come from the existing `PROJECTS` roster. This is report arithmetic, not a new simulation.

## Public-budget calibration review: choose the Sponsor share, not the Earth mobilization cap (2026-10-11)

**RESEARCH / REPORT ONLY.** This section proposes **10%–25% of already-mobilized capital** as the 2026 *network-wide allocation fraction* `s`, **not 10%–25% separately for each of the 11 Sponsors**. The fraction is split among all 20 eligible Sponsor participants under existing national weights; non-BUILD/LAND shares remain reserved. Preserve `mobilization_m_max=.001` and `investment_proxy_units_per_model_currency=1e9`. `MODEL_CURRENCY` is $1B **proxy-scale equivalent** per unit, not an empirical 2026 USD purchasing-power assertion.

### Public comparators and limitations

| Route 1 Sponsor (origin) | Public real-world comparator | Evidence reliability and comparability | LOOM 2026 mobilized origin |
|---|---|---|---|
| NASA (USA) | NASA FY2026 **exploration request $8.313B** (2025 enacted $7.666B); includes major Artemis/human-exploration systems, not one LAND service | **High** for published NASA request; **low** as a single LAND budget | USA **$4.958B** |
| CNSA (CHN) | Estimated Chinese **total civil + defence government space spending ~$14–20B/year** (2023–24/2026 estimates), not published CNSA lunar appropriation | **Low** for CNSA lunar budget; third-party aggregate estimates with opaque breakdown | CHN **$7.693B** |
| ISRO (IND) | India Department of Space FY2026–27 allocation **₹13,705.63 crore**; whole department, not lunar-only | **High** for parliamentary budget, **low** for lunar attribution | IND **$1.170B** |
| JAXA (JPN) | JAXA FY2026 agency budget roughly **¥154.8B**, excluding separate Space Strategy Fund; JAXA lists multi-year project costs independently | **Medium** (published official chart, numerical secondary transcription); **low** for lunar-only share | JPN **$1.325B** |
| ESA (12 origins) | ESA CM25 subscriptions **€22.3B multi-year** across all activities; German exploration contribution **€885M multi-year** (not ESA annual budget) | **High** for announced commitments; **low** if treated as annual or attributed to one country | Multinational weighted allocations; do not compare with a single DEU pool |
| CNES (FRA) | CNES 2024 **€2.370B total budget**, including **€1.092B ESA contribution** | **High** official budget; **low** for lunar-only; do not add CNES ESA contribution twice | FRA **$0.604B** |
| DLR (DEU) | Germany 2025 space investment **€1.954B**, including **€1.168B ESA programmes**, €324M DLR research/operations, €350M national space | **High** DLR figures; **low** for DLR-only lunar expenditure; ESA overlap | DEU **$0.749B** |
| Australian Space Agency (AUS) | Australian **A$50M Trailblazer lunar rover** within **A$150M Moon to Mars** initiative, **multi-year**, not annual | **High** official mission-programme commitment; not an annual agency exploration budget | AUS pool not independently verified in this review |
| UAE Space Agency (ARE) | UAE Ministry of Finance reports **AED63M federal budget** for its multi-year asteroid-belt exploration mission; **not lunar** | **High** for the stated government mission allocation, **low** for a lunar annual proxy | ARE pool not independently verified in this review |
| ispace (JPN) | FY ended March 2026 **¥5.890B project revenue**, **¥3.307B net sales**, **¥8.152B net loss**; raised ~¥18B in financing during fiscal year | **High** corporate reporting; **low** as a spendable lunar mission budget; company financing is not national public spending | JPN **$1.325B**, shared with JAXA and other recipients |
| Interlune (USA) | **$18M seed financing (2024)**; 2025 **$1.25M** federal R&D award and 2026 **$6.9M** NASA award (distinct instruments) | **High** announcements/award records; **low** as annual capital expenditure or total mission budget | USA **$4.958B**, shared with NASA and other recipients |

**Source links:** NASA https://www.nasa.gov/wp-content/uploads/2025/05/fy-2026-budget-technical-supplement-002.pdf ; China independent estimates https://www.europarl.europa.eu/RegData/etudes/BRIE/2024/762460/EPRS_BRI%282024%29762460_EN.pdf and https://newspacetracker.com/countries/china/ ; India https://www.pib.gov.in/PressReleasePage.aspx?PRID=2245313&lang=1&reg=3 ; JAXA https://www.jaxa.jp/about/transition/ and numerical transcription https://spaceodysseyhub.com/intelligence ; ESA https://www.esa.int/About_Us/Corporate_news/ESA_Member_States_commit_to_largest_contributions_at_Ministerial ; DLR https://countdown.dlr.de/wp-content/uploads/2026/04/Countdown-43_MK_2025.pdf ; CNES https://cnes.fr/en/budget ; Australia https://www.space.gov.au/news-and-media/headed-moon-trailblazer-program-and-nasa-space-act-agreement ; UAE https://mof.gov.ae/wp-content/uploads/2025/02/Federal-General-Budget-Annual-Report-2025.pdf ; ispace https://testing.ispace-inc.com/2026/05/15/ispace-reports-full-year-financial-results-for-the-fiscal-year-ending-march-2026-2/ ; Interlune https://www.interlune.space/press-release/space-resources-startup-interlune-raises-18-million-in-seed-capital and https://www.sbir.gov/awards/216899 and https://www.interlune.space/media-center?3f045fab_page=3&49a8bc92_page=14 .

**Caveat:** public budgets are mixed years, currencies, price bases, institutional coverage, and annual versus multi-year totals. **No exchange-rate or inflation normalization is claimed.** The displayed mobilized amounts are LOOM proxy-dollar scale, not audited space budgets. NASA's $8.313B exploration request alone exceeds the modeled **entire USA $4.958B mobilization ceiling**, proving this Earth-to-Offworld proxy **cannot** represent all real national exploration expenditure. That is not a reason to quietly enlarge the cap: Route 1 only models selected BUILD/LAND purchases. ESA overlaps member budgets; ispace and Interlune cannot be counted again as separate national public expenditures.

### Re-run: 2026 allocation shares 10% and 25%

These maps use **unchanged 2026 per-Sponsor country-weighted opening balances** from the prior section, rescaled linearly from `s=.02`. Both are *threshold predictions*, **not** financier-policy approvals or deliveries.

| Share `s` | **Map A**: cash >= original authored Sponsor ceiling | Count | **Map B**: cash >= illustrative raised ceiling ($200M BUILD / $300M LAND) | Count |
|---|---|---:|---|---:|
| 10% | NASA, CNSA, ISRO, JAXA, ESA, CNES, DLR, Australian Space Agency | 8/11 | CNSA, ESA | 2/11 |
| 25% | NASA, CNSA, ISRO, JAXA, ESA, CNES, DLR, Australian Space Agency, ispace | 9/11 | NASA, CNSA, ISRO, ESA | 4/11 |

**Service-price check at `f=20`:** one default BUILD service costs **$85M**; one LAND costs **$150M**. At 10%, **NASA, CNSA, ISRO, ESA** have enough cash for one appropriate default service (4/11); at 25%, **NASA, CNSA, ISRO, JAXA, ESA, Australian Space Agency, Interlune** (7/11). Original authored ceilings are *below* both service defaults, so Map A cash-pass alone cannot authorize a whole default service. Map B requires the *full* higher project ceiling, so it is more restrictive than a one-service purchase.

**Decision:** prefer **`s=.10` for the first 2026 trial and `s=.25` as a stress/control**. The empirical comparators establish scale and warn against treating full space-agency budgets as a single project, but **do not identify a statistically calibrated universal Sponsor share**. Raising `mobilization_m_max` instead would change the entire country's offworld cash-generation rule, including unrelated financing, and obscure whether the network allocation alone causes changed outcomes. Keep `m_max=.001` as an explicit coarse authored ceiling until an observed experiment or separate Earth-finance study justifies revisiting it. Preserve all default/frozen replays, keep 2027–2029 Gate 2 separate, and stop if Gate 1 merely recapitulates the arithmetic.
