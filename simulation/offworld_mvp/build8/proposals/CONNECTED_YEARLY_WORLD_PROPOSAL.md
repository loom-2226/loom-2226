# Build 8: one connected yearly world (proposal only)

**Standing:** PROPOSAL · NON-CANON · NON-RUNTIME · NO IMPLEMENTATION AUTHORIZATION. Based on `main` at `e20ad340` (PR #385). Do not treat current independent experiments as an integrated simulation. Earth v4 input files remain external, and many actor preferences, evidence, prices, and capacities remain authored.

## The world and its clock

Use **one existing Build 8 opening and one existing kernel instance**, advancing 2026, 2027, ... in calendar-year order. Reuse the master cast for identity and capabilities, existing kernel Agents/policies for actual decisions, country investment input, delivery and subcontract transitions, knowledge receipts, and optional defense draw. A small year driver would order existing calls and retain their state. It must not duplicate cast records, invent a new ledger, or present every named sponsor as an autonomous Agent before it actually has a policy-backed decision.

| Annual order | What happens in year Y | What persists into Y+1 |
|---|---|---|
| 1. Admit inputs | Read pinned Earth v4 country-year investment assertions; expose authored scenario pressure/crisis and observations available **by** Y. No future information. | Input/source hashes, scenario pressure history, observed vs hidden truth boundary. |
| 2. Mobilize | Draw each eligible country-year capital **once** into its finite spendable country pool; optionally make the separate defense draw under its own recorded envelope. | Account balances, transactions, boundary net, defense balances and draw receipts. |
| 3. Observe and decide | Publish only authorized evidence; existing sponsor and financier policies evaluate named requests and available funds. | Beliefs, recipient-specific knowledge, decisions, rejected/deferred requests, commitments. |
| 4. Allocate and contract | Clear finite financing and explicitly selected cast-eligible executors/subs against shared category/year slots. Do not activate quote ranking unless selected by scenario. | Project cash, contractor obligations, reserved future slots, contracts and holdback terms. |
| 5. Work and settle | Advance already-contracted BUILD/LAND/etc. work; complete, fail, re-source, withhold/pay and hand off deliverable tokens only when earned. | Physical deliverables, project status, receivables/payment ledger, failure consequences, free/occupied future slots. |
| 6. Close and advance | Reconcile boundary inflow, spendable money, payments and capacity; record snapshot/fingerprint and roll **the same state** to Y+1. | All of the above; no annual reset of money, projects, capacity, knowledge or pressure history. |

**Timing rule:** A commitment in Y cannot consume capacity in an earlier year; a completed stage cannot deliver before its prerequisite; a late-year observation cannot retroactively change an earlier award. Keep the existing deterministic priority and seeded tie-break only where the named scenario opts in. Pressure is a declared yearly input plus crisis state, **not** a newly invented feedback formula. It persists as history; the next year's effective pressure is recomputed from that year's declared inputs, not blindly accumulated.

## Existing experiments become named setups

| Named setup on the same loop | Existing mechanism and intended result | What is *not* silently inferred |
|---|---|---|
| `network_2026` | Twenty cast-backed sponsors, country-weighted capital, executor capability matching; three awards pending plan, seventeen waits in the current snapshot. | Award is not delivery or executor revenue; network's budget checks are not twenty autonomous policies. |
| `named_sponsors_2026` | Six named sponsors route public/private capital and commit 0.05 each. | No construction or realized return. |
| `screen_default`, `screen_sub`, `screen_sub_failure_recovery` | Interlune/Axiom policy and financier screens, BUILD/LAND, shared slots, one-level subcontract, private knowledge, holdback, re-source. | No contractor-specific market calibration; original scheduling and outcomes must match before any combined-world interactions are enabled. |
| `quotes_only` | Existing Northrop/Firefly authored offer/refusal evaluation. | A quote alone is not an award or payment. |
| `defense_off`, `defense_on`, `defense_crisis`, `defense_sweep` | Existing USA/CHN defense draw and authored crisis/scale dials, recorded independently of civilian draw. | No military spending, war, procurement, or automatic strategic competition. |
| `usa_china_race` **(later opt-in combination)** | One world with USA and CHN country pools, CNSA and eligible USA sponsors, named executors, declared 2027–2029 crisis pressure, shared year slots, optional defense draw and existing information boundaries. Observe who waits, who wins a slot, what is delivered, and how money shifts. | Defense funds do not automatically buy civilian work; crisis pressure does not change financier return ranking unless an existing policy actually uses it. No fabricated military or political decisions. |

Setups choose **initial actors, authored dials, enabled existing mechanisms, observations, and run horizon**. They do not construct separate ledgers or independently reset the world each year. For comparison, each setup starts from a fresh *identical* opening and its own deterministic run identity; within a run there is only one state.

## One money scale, without laundering scenario assumptions

**Proposed common denomination: `MODEL_CURRENCY` (MC), the existing kernel's model currency.** All accounts, transfers, commitments, quoted prices, capital and defense draws use MC; Earth v4 `investment` remains an **investment proxy**, converted using the existing `investment_proxy_units_per_model_currency` parameter. Never call a 0.05 commitment, a 0.625 delivery payment and a 4.46 defense draw dollars or compare them as measured national budgets.

| Existing experiment | Current magnitudes (MC) | Mapping into a single yearly world |
|---|---|---|
| Network | Typical sponsor budgets ~0.01–0.1; project costs ~0.015–0.045. | **Keep numbers unchanged for isolated replay.** Its country funding is an authored 2% slice of the derived mobilization; in a combined world, allocate that slice **from the one country pool**, not from a separately minted boundary account. |
| Named sponsors | 0.05 commitment per sponsor; opening budgets ~0.10–0.77. | **Keep numbers for replay.** Its separate 10%-investment-proxy public/private slices are a scenario-specific funding rule, not extra independent national investment when combined. Route from the shared pool under an explicitly chosen allocation rule. |
| Screened delivery | USA mobilization 4.958 (2026); financier reserves 2.00, or 4.00 counterfactual; BUILD payment 0.625 and LAND 0.900 per project; sub price 0.200. | **Keep prices, commitments and duration unchanged for replay.** The 2.00/4.00 is an authored *suballocation* of the same USA pool; no second mobilization when joined with network. Screened BUILD/LAND payments must not be counted again as national inflow. |
| Quotes | BUILD 2.500, LAND 3.600, two-year durations. | Preserve as authored **full-size offers**, not automatically equivalent to screened 0.625/0.900 payments: screened uses `SCALE=0.25`. Applying the same 0.25 quantity/scale to these quotes gives 0.625/0.900, but that is a scenario quantity assumption, not a currency conversion. |
| Defense | USA ~4.46 and CHN ~6.92 in 2026 at pressure 0.3; crisis-year draws can reach ~25/39. | **Already MC** via the same investment-unit normalization. Keep separate defense funds and a distinct boundary receipt. Existing formula has a 1% investment cap vs civilian `m_max=0.001` (0.1%); at pressure 0.3 defense is ~90% of civilian draw. It is **additive** by design, not a subtraction from the civilian pool. |

**What changes upon actual integration:** not the denomination or legacy experiment outputs, but **funding source and competition**. A combined scenario must choose which slices share the finite civilian country pool, and whether defense remains an additional independently admitted investment-linked envelope or competes for that same finite total. Otherwise simply summing network + named + screened + defense double-counts capacity and creates a misleading economy. Do not normalize by arbitrarily multiplying small budgets until they resemble large ones.

### Why `b8_source:USA` is about -10.0202 in screened delivery

This is an **intentional Earth-boundary accounting convention**, not a negative spendable account and not evidence of project overspending. `opening.py` creates `b8_source:USA` as an `EARTH_BOUNDARY` account with zero opening cash. Each mobilization moves newly admitted external capital *from* that source *to* spendable funds; its balance becomes negative and `boundary_net` records the offset. The Build 8 README explicitly calls negative source balances **external inflow, not national debt**. The ~-10.0202 value is the inherited opening's and scenario's resulting source-account total, not a demonstrated creditor claim. Kernel invariants pass. **Retain and label** this convention; in reporting, separate (a) external boundary net, (b) spendable funds and (c) obligations. Investigate only if the source's negative balance does not reconcile to authorized boundary inflows, or if a normal funds/project account overspends. Do not silently zero it or add a compensating transfer.

## Build 7 boundary: off by default

Build 8 already uses the Build 7 kernel and some policy/financier routines. The **off-by-default switch** is for *additional Build 7 campaign/world integration*, not for disabling the kernel currently used by Build 8. Default: isolated in-memory Build 8 opening with pinned Earth v4 inputs and synthetic/authored evidence. Opt-in later: admit a Build 7-generated physical world and reproducible observations through the existing World Authority boundary, invoke existing financier/governance policy and persistence contracts, and advance with ordered year/epoch receipts. Never re-author an already hashed Build 7 genesis or expose sealed truth to Sponsors. Before enabling: prove input hashes, genesis identity, per-year assertion availability, ordered persistence and replay from an independently reconstructed state. The current 2026-only non-USA scenario assertions and inherited USA Build 7 scenario assertion are a **concrete multi-year admission blocker**, not something the driver may wave away. Stop at that blocker rather than relaxing source authority.

## Smallest first slice and stopping test

**First slice:** one isolated USA world, 2026–2034, existing Interlune/Axiom screened policy, one finite USA pool, two executor categories, shared slots, existing evidence receipts, and optional subcontract/failure/recovery. A tiny year driver orders the *existing* transitions; no defense, network, all-country agents, quote auction or persistent Build 7 connection yet. This is the smallest existing trial that already exercises money, multi-year project state, capacity, knowledge and failure.

**Proof:** Run `screen_default`, `screen_sub`, and `screen_sub_failure` using the new yearly driver from identical opening, seed, inputs and authored choices. Compare **all three existing `baselines/pre_cast_migration/*.json` snapshots exactly**, including ordered events, knowledge, account balances, outcomes and kernel fingerprints, not just final delivery dates. Separately retain exact `network`, `named_sponsors` and `quotes` snapshots under their existing isolated configurations. Compare defense-on/off/crisis receipts and sweep independently because they have no corresponding pre-cast snapshots. **Stop after exact match**; do not combine the separate experiment budgets until an explicit shared-capital decision is made. If the existing trial's within-year event ordering cannot be reproduced, report the specific mismatch rather than rewrite the baseline to pass.

## Risks and decisions for review

1. **National capital sharing:** Should network, named sponsors and screened projects draw from *one* civilian country pool, with their old fractions interpreted as scenario allocation policies? **Recommend yes**, but only when explicitly combined; preserve old isolated runs unchanged.
2. **Defense source:** Keep additive, separately admitted defense capital (current semantics), or impose a shared civilian+defense ceiling? **Recommend preserve additive initially** and label it clearly; choose any cross-sector trade-off later, based on desired race behavior.
3. **Capacity arbitration:** Current category/year slots and separate seeded quote choice toy do not constitute a live cross-project market. **Recommend fixed existing priority first**; activate seeded quote/capacity choice only in an opt-in race setup after matching old scheduling.
4. **Named Agent authority:** The network's 20 sponsors are not 20 policy-backed decision-makers. **Recommend integrate only already demonstrated policy-backed actors first**; do not pretend the roster is a functioning agent population.
5. **Physical truth and Build 7 admission:** Synthetic observations and deliverable tokens are not admitted lunar geology or persistent World Authority results. **Recommend off by default**, and do not activate until the year-by-year assertion/genesis blocker is resolved.
6. **Scale and pressure:** The quoted amounts are model units and scenario sizes, not calibrated prices. Pressure does not currently endogenously drive bids, war or government decisions. **Recommend keep both authored and visible**, not retrofit speculative feedback.

**Review gate:** This document requests no code, migration, new schema, canon change, runtime activation or merge. The next action, only if approved, is the single-USA screened yearly replay slice above. Stop once the proposal branch is pushed.
