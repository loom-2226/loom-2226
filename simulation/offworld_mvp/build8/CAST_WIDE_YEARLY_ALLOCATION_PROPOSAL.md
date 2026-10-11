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
