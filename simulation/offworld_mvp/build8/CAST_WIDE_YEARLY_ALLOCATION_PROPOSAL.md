# Proposal only: cast-network to yearly allocation

Status: DRAFT / NONCANON / NONRUNTIME / NOT BASELINE 0. No implementation authorized by this document.

## Existing foundation

Start with `sponsor_executor_network_trial.py`: 20 authored sponsors (12 public, 8 private), 16 selected executors, national participation, country-weighted investment envelopes, project motives/categories/costs, capability eligibility and preferred executor relationships. The network trial currently expects 3 `AWARDED_PENDING_PLAN` and 17 `WAIT`; awards retain project cash and do **not** produce supplier revenue or imply physical delivery. Its preferences, projects and costs are authored, not real institutional intentions. The cast has 91 actors and 75 capability entries, not 91 autonomous participants. The 80-country capital boundary is distinct from the 25 cast home-country codes.

Reuse `master_cast_candidate.json` and `master_cast.py` for identity/role/capability checks; `sponsor_executor_network_trial.py` for the initial sponsor/project/executor pool and country routing; `sponsor_development.py` for authorized development; `opening.py` for country capital; `screened_yearly.py` for existing policy/financing, staged BUILD/LAND scheduling, accounting, knowledge and internal-delivery audit; `capacity_options.py` and its separate JSON inputs for opt-in metadata/fallbacks. These are **pieces to connect**, not an already integrated cast-wide annual campaign. Existing `yearly_selections.py` supplies two named two-sponsor scenarios, not an automatic allocation engine.

## Smallest first executable slice (future work, not in this PR)

1. Use exactly the network trial's authored 20 sponsor projects and 16 eligible executors, not every cast actor as a fictitious sponsor. For each year, carry forward project status, remaining budgets, committed cash, executor occupancy, completed work, and observation provenance in the same kernel world. Unrepresented actors are listed as `NO_AUTHORED_PROJECT`, `NOT_IN_EXECUTOR_SELECTION`, `NO_ELIGIBLE_CATEGORY`, or another specific reason. Do not invent activity for idle actors. Preserve the network trial's funding-envelope provenance and do not count a sponsor's multi-country participation as separate legal actors.
2. Sponsors propose their one authored project/category when their motivation and known evidence permit; existing sponsor/financier policy decides whether to proceed. If policy inputs needed by a sponsor are absent, report `POLICY_INPUT_MISSING` rather than fabricate a real-world belief. `WAIT` is a meaningful outcome. A proposed project is not an award; an award is not a delivery.
3. For each authorized project, consider only the 16 selected executors that have cast-supported category capability. Reject infeasible bids first (missing comparable quote, incompatible category, insufficient project funds, no available slot). Rank remaining bids by lowest comparable total authored quote, then existing authored preferred relationship, then stable actor ID. This is a *proposed* transparent procurement rule, not existing behavior or evidence of how these organizations actually bid. One supplier may win multiple contracts only if available slots allow it. Preserve sponsor/executor same-owner audit without treating it as consolidated revenue.
4. Use existing authored project quotes wherever they actually define comparable deliverables. Do not conflate the network trial's sponsor project `cost` with a supplier's category-specific price without an explicit mapping; otherwise report `UNPRICED_PROJECT` and stop that award. Keep BUILD/LAND staged fulfillment where the yearly driver supports it. LAUNCH/RUN/TRANSPORT/EXTRACT cannot be automatically delivered or priced by this slice without demonstrated compatible service definitions; leave them pending/unpriced and report them.
5. Deterministic seed experiment: introduce a *single explicitly authored uncertainty*, e.g. a bounded project-readiness draw per sponsor/year **after** deterministic eligibility and financing. Derive draws from `(seed, year, project_id)` so traversal order does not alter outcomes. Log each draw and its authored probability; seed must not change identity, prices, capital, hidden truth or existing frozen cases. Compare at least five fixed seeds with a common scenario. Do not imply random draws measure actual industrial reliability.

## Independent switch semantics

- **All off (control):** preserve current network and yearly authored values. Compare the *unchanged existing* `legacy_usa` replay to main, and separately label any new network-to-yearly result as a new experiment, **not** an identical main run.
- **Tiers only:** descriptive tier/basis audit metadata; **no award, schedule, price, or failure change**. If it changes results, that is a bug.
- **Tiers + slots:** retain explicit authored slots. Only absent slots receive the separate flat one-slot authored default; resulting contention can move award timing or cause `WAIT`. Tier does not set slot count.
- **Tiers + slots + prices:** retain explicit authored quotes. Only absent quotes in supported BUILD/LAND categories receive authored price defaults. This may change affordability or bid ranking *only for comparable deliverables*. Track number of default-priced awards and candidates. No LAUNCH price fallback. Keep the three switches independently selectable even if the reporting sequence is cumulative.

## Required observation bundle when implemented

Per seed and configuration: proposed/awarded/waiting/blocked projects by sponsor, category and funding country; selected and losing executors and bid reasons; actor participation/idle reason; opening/closing balances, committed and spent amounts; year-by-year occupancy, delay and failure; all events, transactions, knowledge and parent provenance; internal delivery events including ispace if actually produced. Produce Gantt and actor/country/project network views from the **same** recorded state. Count distinct actors and funding countries, not just cast roster. Show per-switch deltas and unchanged results explicitly. Audit invariant: no award is reported as paid delivery.

## Deliberately excluded from first slice

No universal 91-agent policy population; no invented participation for unused cast members; no world-market clearing, bidding negotiation, dynamic quote formation, endogenous capital markets or defaults; no tier-derived slot count, tier pricing or tier failure rates; no unresearched launch reference mission; no modeled logistics or resource geography; no consolidated vertically integrated company accounts; no repair of CAST/Sierra or Chinese lander cast gaps; no baseline migration, canon changes, or frozen replay edits. Do not run Baseline 0 until a comparable multi-actor yearly path actually exists.

## Stop / go decision

Before implementation, resolve the *one concrete missing interface*: how the network trial's authored project cost/category maps to a comparable yearly executor quote and physical deliverable. If this cannot be specified narrowly for BUILD/LAND, stop and report the blocker rather than construct a general procurement framework. The first executable stopping condition is a repeatable single-world yearly run with at least two competing eligible BUILD/LAND executors, a recorded winner/loser, an explicit idle-actor inventory, and frozen legacy replays unchanged. Expand the population only after this produces a meaningful difference.

## Narrow mapping review (proposal only; no runtime admission)

The network trial's 20 projects split into **7 BUILD, 4 LAND, 6 LAUNCH, 3 RUN**. The latter **9 LAUNCH/station-operation projects are out of this slice**. Therefore a proposed Baseline 0 limited to BUILD/LAND covers **11 of 20 sponsors**, not the whole cast or the whole network. This is project *coverage*, not 11 successful awards.

The following costs are **sponsor-side authored network project costs**, not executor quotes. Proposed comparable request means *one category-specific trial service unit* for each project. That unit's technical specification, physical quantity and pricing conversion are **not established**; do not treat these 0.015–0.090 costs as a purchase of a 1.70 BUILD or 3.00 LAND deliverable.

| Sponsor | Category | Network cost (model units) | Proposed request | Capability-eligible executor count | Existing preferred executor |
|---|---|---:|---|---:|---|
| NASA | LAND | 0.045 | 1 LAND trial service unit | 4 | Astrobotic |
| CNSA | LAND | 0.045 | 1 LAND trial service unit | 4 | CASC |
| ISRO | BUILD | 0.015 | 1 BUILD trial service unit | 14 | HAL / L&T |
| JAXA | LAND | 0.030 | 1 LAND trial service unit | 4 | Mitsubishi Heavy Industries (not LAND eligible) |
| ESA | BUILD | 0.030 | 1 BUILD trial service unit | 14 | Thales Alenia Space |
| CNES | BUILD | 0.015 | 1 BUILD trial service unit | 14 | Airbus Defence and Space |
| DLR | BUILD | 0.015 | 1 BUILD trial service unit | 14 | OHB |
| Australian Space Agency | BUILD | 0.015 | 1 BUILD trial service unit | 14 | Toyota |
| UAE Space Agency | BUILD | 0.045 | 1 BUILD trial service unit | 14 | Thales Alenia Space |
| ispace | LAND | 0.045 | 1 LAND trial service unit | 4 | ispace (same-owner delivery candidate) |
| Interlune | BUILD | 0.090 | 1 BUILD trial service unit | 14 | Northrop Grumman |

The 14 BUILD candidates are Astrobotic, CASC, RKK Energia, HAL / L&T, Mitsubishi Heavy Industries, Thales Alenia Space, Airbus Defence and Space, OHB, MDA Space, Hanwha Aerospace, Toyota, SpaceX, Blue Origin, and Northrop Grumman. The four LAND candidates are Astrobotic, CASC, Blue Origin, and ispace. These are capability eligibility counts, **not** counts of comparable offers or free capacity. Existing network-trial preference for JAXA falls back to alphabetically first eligible LAND actor (Astrobotic); this is not a researched procurement preference.

### Specific candidate award and loser

**ESA BUILD** is the narrow proposed head-to-head: Thales Alenia Space (existing authored preference) versus Airbus Defence and Space (eligible alternative). If both submit comparable offers for the *same specified BUILD unit*, both have an available slot, and ESA has enough committed funds, one must win and the other lose that award. Under the proposed lowest-comparable-price rule, the cheaper offer wins; at equal price, Thales wins on the existing authored preference. **No winner or loser can presently be predicted from the supplied numbers**, because neither company has a comparable ESA-specific quote. This is a proposed competition case, not an observed award. It must not be counted as awarded until the missing quote/unit mapping is resolved.

### Seeded observable change (proposed, not measured)

A single keyed readiness draw `(seed, project_id, year)` after financing/eligibility, with an explicitly authored probability, would make an otherwise authorized project **READY** or **NOT_READY**. NOT_READY records a **one-year deferral**, retains unspent committed funds and releases no delivery revenue; the next year receives its own logged draw. Seed does **not** change project category, quoted price, actor identity, national envelope, tier, or hidden physical truth. Five seeds could produce different award/delivery years and occupancy contention. There is **no existing calibrated readiness probability**, so neither frequency nor numerical seed effect can be claimed now. Avoid calling this a random failure of a real company.

### Mapping decision / stop condition

**BLOCKED for executable price competition:** no defensible common BUILD/LAND deliverable specification and no conversion from sponsor-side project cost to comparable executor bid exist in these artifacts. A category label plus `quantity=1` is not enough to equate network budgets and PI01/yearly supplier quotes. The 11 rows above are an exact inventory and *candidate mapping*, not priced procurements. Do **not** manufacture per-executor offers, scale the network budgets to fit the default prices, select a winner, or run Baseline 0 on this basis. First resolve one narrow ESA BUILD service specification and two comparable authored bids, with funding consistent with the network capital boundary; if that cannot be justified, stop there. Frozen baselines remain untouched.

## Money-scale alternatives (decision requested; neither selected)

### What one network unit represents

`PROJECTS` in `sponsor_executor_network_trial.py` calls its `.015`–`.090` costs **fictional model units**. `opening.py` supplies Earth investment-proxy-derived mobilization; the network trial offers 2% of that mobilized amount to its country pool and allocates it by authored sponsor weights. **There is no documented USD-per-network-unit, purchasing-power, physical-deliverable, or network-to-executor exchange rate.** `executor_quotes.py` separately calls its prices model currency units. `competitive_delivery.py` multiplies some delivery work by `SCALE = 0.25`, which is not a documented conversion between these experiments. The network project `cost` is a sponsor-side project commitment threshold, not a supplier quote or necessarily the sponsor's available opening balance. Thus the following tables are *illustrative affordability of the authored project-cost envelope*, not evidence of cash actually available in a sponsor's ledger or a funded award.

For transparent arithmetic, both alternatives below **assume an arbitrary factor of 100**, explicitly *not* a researched or calibrated conversion. Assume exactly one homogeneous BUILD or LAND trial service unit per project; ignore markup, taxes, launch, financing and other delivery costs; assume the price defaults of BUILD 1.70 and LAND 3.00 are final all-in prices for that one unit (although the original file does not establish that); and assume the project `cost` is an available spend ceiling rather than a separate project budget or merely a commitment threshold. Existing authored supplier quotes, when present, take precedence over defaults. Neither factor nor homogeneous-unit premise is justified by the source artifacts. The choices are mathematically reciprocal and intentionally give the **same affordability classification**; selecting between them does not solve the deliverable-identity problem.

**Option A — scale executor defaults down into network project units:** divide the quoted fallback prices by 100: BUILD **0.017**, LAND **0.030** network model units. Keep each network project cost and its actual country/sponsor capital ledger unchanged. Do not divide existing cash or network costs. This is a proposed *quote conversion*, not a currency discovery.

**Option B — scale sponsor-side project budgets up:** multiply each of the 11 authored `PROJECTS` costs by 100, leaving executor fallback prices BUILD **1.70**, LAND **3.00** unchanged. This changes the project's numeric spend ceiling but **does not generate extra mobilized cash**. To make the higher ceilings genuinely payable would also require an explicitly authorized 100× capital-source scaling or a defined accounting-unit redenomination of *all* relevant cash, commitments and transactions; either changes the trial's funding boundary and must not be smuggled in as a budget edit. The table below compares ceilings only, not actual affordability from existing cash.

| Sponsor | Category | Existing project cost | A: fallback quote in network units | A: ceiling covers quote? | B: project ceiling ×100 | B: original fallback quote | B: ceiling covers quote? |
|---|---|---:|---:|---|---:|---:|---|
| NASA | LAND | .045 | .030 | YES | 4.50 | 3.00 | YES |
| CNSA | LAND | .045 | .030 | YES | 4.50 | 3.00 | YES |
| ISRO | BUILD | .015 | .017 | NO | 1.50 | 1.70 | NO |
| JAXA | LAND | .030 | .030 | YES (exact) | 3.00 | 3.00 | YES (exact) |
| ESA | BUILD | .030 | .017 | YES | 3.00 | 1.70 | YES |
| CNES | BUILD | .015 | .017 | NO | 1.50 | 1.70 | NO |
| DLR | BUILD | .015 | .017 | NO | 1.50 | 1.70 | NO |
| Australian Space Agency | BUILD | .015 | .017 | NO | 1.50 | 1.70 | NO |
| UAE Space Agency | BUILD | .045 | .017 | YES | 4.50 | 1.70 | YES |
| ispace | LAND | .045 | .030 | YES | 4.50 | 3.00 | YES |
| Interlune | BUILD | .090 | .017 | YES | 9.00 | 1.70 | YES |

**Ceiling-only result in either option: 7 of 11 cover one assumed default-priced service unit; 4 do not (ISRO, CNES, DLR, Australian Space Agency).** This does **not** mean seven funded projects. The frozen network trial actually reports only CNSA, ISRO and ESA as funded at the original costs, with 17 `WAIT`. Under either proposed change, eligibility, real available balances, commitment policy, and service definition would need to be re-evaluated; in particular, ISRO's original funded status does not mean its hypothetical 0.017 BUILD quote is affordable from a .015 project ceiling. No baseline result is overwritten by these hypothetical classifications.

### Evidence quality of candidate executors

In the network's **14 BUILD-capable** selected executors, **6** BUILD capability entries have `evidence_basis: SOURCED` (Airbus Defence and Space, Hanwha Aerospace, MDA Space, Northrop Grumman, OHB, Thales Alenia Space) and **8** are `AUTHORED` (Astrobotic, CASC, RKK Energia, HAL / L&T, Mitsubishi Heavy Industries, Toyota, SpaceX, Blue Origin). In the **4 LAND-capable** entries, **3** are `SOURCED` (Astrobotic, Blue Origin, ispace) and **1** is `AUTHORED` (CASC). Sourced means there is a linked capability reference, **not** a verified comparable service offer, contract price, free slot or delivered outcome. Some sources concern planned or unsuccessful missions. Do not infer procurement feasibility from the evidence label.

### Decision held

Neither A nor B is recommended or activated. Factor 100 is a *visible sensitivity example*, not a defensible conversion. Before a price-clearing run, the user must select an accounting interpretation and explicitly authorize a common service unit and its quote meaning; option B additionally requires a capital accounting decision. The nine LAUNCH/RUN projects remain out of scope; proposed Baseline 0 coverage is **11 of 20 sponsors**. No code, data defaults, frozen baseline, or runtime behavior changes are authorized here.

## Selected direction: Option A with NASA LAND anchor (proposal only)

**Decision:** use Option A conceptually. Keep the network sponsor budgets, mobilization, country source accounts, transfers, and capital ledger **unchanged**. Do not use the earlier illustrative factor 100 for the selected proposal. No code/default JSON changes yet.

Define the **single named conversion parameter** `EXECUTOR_TO_NETWORK_FACTOR = LAND_EXECUTOR_DEFAULT / NASA_LAND_AUTHORED_PROJECT_COST = 3.00 / 0.045 = 200/3` (exact rational; about 66.6667). The *anchor statement* is **“NASA's authored LAND project exactly buys one default lander.”** Convert any eligible executor quote expressed in the executor-default scale to network units by **dividing** by this factor. The current fallback prices would become LAND `3.00 / (200/3) = 0.045` and BUILD `1.70 / (200/3) = 0.0255` network units. The factor is a scenario-authored *price scale*, not a physical, currency, or national-investment conversion. Preserve explicit quote priority, and do not convert network-side project costs or actual balances.

**Anchor caveat:** NASA's `.045` is a fictional sponsor project-cost threshold, **not evidence of its actual cash balance, a procurement quote, or a technically specified lander**. `LAND` category eligibility does not prove all four selected executors can provide the same complete lander/launch/service package. The earlier PI01 LAND scenario explicitly bundled launch and landing, whereas this network trial only labels the category LAND. Calling it “one default lander” is an authored homogeneous-unit assumption. Using NASA to calibrate LAND and applying the *same factor* to BUILD is an additional cross-category price-scale assumption, not a demonstrated equivalence. If `.045` does not represent spendable project ceiling, the anchor does not establish affordability. No real-world NASA price is implied.

### Sensitivity: minimum factor for each authored project-cost ceiling

For one assumed service unit, ceiling covers default price when `factor >= category_executor_default / authored_project_cost`. This is a **ceiling-only** comparison; it does not demonstrate sponsor opening balance, funded award, slot availability, or an executable bid. The factor is global and positive. At the selected NASA anchor (`200/3`), the results are:

| Sponsor | Category | Authored ceiling | Minimum factor (exact) | Minimum factor (approx.) | At NASA anchor? |
|---|---|---:|---:|---:|---|
| NASA | LAND | .045 | 200/3 | 66.6667 | YES (exact) |
| CNSA | LAND | .045 | 200/3 | 66.6667 | YES (exact) |
| ISRO | BUILD | .015 | 340/3 | 113.3333 | NO |
| JAXA | LAND | .030 | 100 | 100.0000 | NO |
| ESA | BUILD | .030 | 170/3 | 56.6667 | YES |
| CNES | BUILD | .015 | 340/3 | 113.3333 | NO |
| DLR | BUILD | .015 | 340/3 | 113.3333 | NO |
| Australian Space Agency | BUILD | .015 | 340/3 | 113.3333 | NO |
| UAE Space Agency | BUILD | .045 | 340/9 | 37.7778 | YES |
| ispace | LAND | .045 | 200/3 | 66.6667 | YES (exact) |
| Interlune | BUILD | .090 | 170/9 | 18.8889 | YES |

At this anchor **6/11** project ceilings cover the category default (NASA, CNSA, ESA, UAE Space Agency, ispace, Interlune); **5/11** do not (ISRO, JAXA, CNES, DLR, Australian Space Agency). This revises the *hypothetical ceiling comparison* from the prior 100-factor sensitivity, not the frozen network trial's 3 awards / 17 waits. In particular, NASA being exactly at its ceiling does not mean NASA has enough money in its actual account.

### First honest price competition: ESA BUILD

With the flat fallback BUILD price `0.0255` for all missing quotes, **Thales Alenia Space and Airbus Defence and Space tie on price**. Assuming both eligible, funded and free, the *existing authored preferred-relationship tiebreak* selects **Thales**, and **Airbus loses**. This is a preference-driven result, **not** evidence of price competition.

Smallest meaningful next test: author **exactly two independent, explicitly fictional, final all-in BUILD service-unit quotes** for ESA's one identically specified BUILD trial unit, one from Thales and one from Airbus. Keep the NASA-derived factor fixed, all other suppliers' fallback pricing unchanged, and ESA's `.030` network ceiling and actual ledger untouched. A minimal illustrative pair **in network units** is Thales `0.0270`, Airbus `0.0240`; both are under ESA's `.030` authored ceiling. These are *proposed scenario test inputs*, **not offers, sourced prices, or implemented defaults**. If both have an available slot and ESA has spendable cash, Airbus wins by lower price and Thales loses despite the preference. A reversed-price counterfactual would show the rule is responsive to price rather than preference; neither should be treated as historical evidence. Before executing, define the shared BUILD unit explicitly and check real available cash. Do not alter frozen baseline quotes or the original network trial.

**Boundary:** the six LAUNCH and three RUN/station projects remain excluded; first-slice coverage is 11/20 sponsors. Capability eligibility remains 6 sourced / 8 authored BUILD and 3 sourced / 1 authored LAND entries, with no sourced comparable bids. This is documentation and proposed sensitivity only; no runtime activation, tests, merge or baseline changes.
