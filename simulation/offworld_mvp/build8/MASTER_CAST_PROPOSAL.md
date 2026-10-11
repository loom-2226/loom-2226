# Build 8 master cast: proposal for review

**Status:** PROPOSAL ONLY · NON-CANON · NO RUNTIME CHANGE · NOT APPROVED. **Base:** live `main` at `b64995c9` (PR #381 merge `96261fcf`, PR #380 merge `b64995c9`). No experiment moved in this PR.

## The choice

Give each real organization **one stable actor ID and home country**, with any combination of sponsor and executor roles. Put **experiment-specific prices, capacities, weights, budgets, and motives in named selections**, not into a supposedly universal truth about the company. A quote is an offer for a *service and scenario*, not a permanent property of a corporation. Countries are actors too; multinational agency participation and commercial funding routes remain separate relationships, not multiple home countries.

| Cast part | Minimum record | Example / rule |
|---|---|---|
| Country | ID, display name | `USA`, `CHN`, `FRA`; ISO3 identity; no new country Agent |
| Organization | stable ID, name, home ISO3, roles, source/status | `spacex`, SpaceX, USA, `private_sponsor + executor`; one identity in both roles |
| Sponsor role | `private / agency / defense`; optional participating/funding countries | NASA = agency/USA; CNSA = agency/CHN; US Space Command and PLA Aerospace Force = defense; ESA has multiple participating countries but one identity |
| Executor capability | actor ID, one or more of BUILD, LAUNCH, LAND, TRANSPORT, EXTRACT, RUN; evidence status | Multiple named companies per category; capability is not proof of an available quote |
| Offer / capacity assumption | actor ID + service, price/cost, markup, duration, slots, provenance | Explicitly `AUTHORED` unless supported by a source; scenario may override without redefining actor |
| Experiment selection | named ID, selected actor IDs, service offers, sponsor routes, dials, seed, cast revision | A run writes selected IDs, effective offers/dials and revision to its record; old scenarios can pin old assumptions |

**Competition:** an experiment asks for eligible actors for a service, filters by actual shared free slots and permitted legal-entity relationships, and compares **offers**. BUILD can have Northrop Grumman, CASC, Thales Alenia Space and others; LAUNCH can have SpaceX, Blue Origin, CASC, Isar Aerospace and others; LAND can have Firefly Aerospace, Astrobotic, ispace, Blue Origin and others. TRANSPORT, EXTRACT and RUN require verified candidates or clearly marked authored capabilities; do **not** rename today's fictional placeholders as real providers without evidence. A subcontract draws from this **same executor pool** and slot ledger as direct work, never a second pool. A sponsor that is also an executor retains its single legal identity, so self-awards/subcontracts cannot evade capacity or payment rules. Actual competitive selection is a later experiment, not part of the first cast change.

## Migration, without changing outcomes

| Current experiment / source | Migration | Difficulty / result risk |
|---|---|---|
| `sponsor_executor_network_trial.py`: 16 executors, public/private sponsors, country preferences | Seed organization IDs and roles from roster; leave sponsor-country preferences in named network selection | **Medium**: agency participation and multi-country routes must not be mistaken for domicile; preserve award order and values |
| `deliverable_chain.py`: six category operators, four placeholders | Keep existing single choice per category as `legacy_chain` selection; add alternative actors later | **Easy** for identity lookup; **hard** to make genuine competing offers; old chain must remain byte-for-byte equivalent in results |
| `executor_quotes.py`: Northrop/Firefly quoted candidates | Reuse their IDs; retain authored prices, capacity, duration and evidence descriptions as `pi01_quotes` selection | **Easy**; no re-pricing or historical claims |
| `competitive_delivery.py` and `screened_delivery.py`: two sponsors, shared slots, subcontract | Select Axiom/Interlune and the existing BUILD/LAND pair; preserve original scheduling and holdback | **Medium**: ordering, capacity collisions and subcontract identity must reproduce exactly |
| `sponsor_trial_setup.py` and Episode A: four private sponsors, sponsor-executor mapping | Select four sponsor IDs and current paired executor IDs; keep tier rankings and amounts in Episode A selection | **Easy–medium**; Blue Origin/SpaceX are both sponsor and executor, never duplicate entities |
| `named_sponsor_trial.py`: NASA/CNSA/ESA etc. | Select shared agency/private IDs; keep authored country weights and motives as routing dials | **Medium**: multinational routes are not corporate home countries |
| Defense draw / future four-sponsor USA–China race | Reuse country and agency IDs; add defense sponsor identities to selection; pressure/crisis dials stay in their existing authored table | **Easy identity work**; race behavior and procurement are separate later steps, not already implemented |

## Where, size, and ownership

**First step (one later PR):** `build8/master_cast.json` (~100–200 lines for current named organizations and country IDs), `build8/cast_selection.py` (~40–70 lines for simple read/select/validate), and one pinned example selection in `build8/cast_selections.json` (~30–60 lines). No new framework, schema package, database, government Agent, or global scheduler. Keep provenance as a short source/status field on each capability/offer. A named Build 8 experiment owner edits the catalogue and its selection together in an ordinary reviewed PR; sourced claims need a traceable reference, authored assumptions need an explicit label. Existing experiments remain unchanged until individually switched over.

**Later, in small pieces:** (1) migrate `executor_quotes` and the chain with identical output assertions; (2) migrate network sponsors/executors and Episode A without changing routes or award order; (3) migrate screened delivery/subcontracts using the shared identity and capacity; (4) only then let one experiment choose among multiple eligible bids. Each step stops if it changes an existing outcome unexpectedly. Record effective cast revision, selection, offers, dials, seed and code version per run, not merely the selection name.

## Uncertainties and decisions requested

- **Your researched list of 59 real executors:** use it as a candidate import, not as 59 ready-to-bid firms. Reconcile company names/aliases and home countries with existing IDs; preserve `type, company, home country, status, source`. Mark missing service capabilities, prices and slots **unknown** until independently supported or explicitly authored. Do not automatically admit every company to every service it might plausibly perform.
- **Actor identity:** use organization-level identity first; corporate subsidiaries, joint ventures and national operating arms need distinct IDs only if their contracts or capacity materially differ. ESA's member-country participation is not its home country; propose a single administrative home and separate participation edges, subject to your preference.
- **Biggest risk:** a central cast that accidentally rewrites historical experiment assumptions or collapses separate national funding routes. Pin old offers and routes; compare exact results before moving each experiment.
- **User decision:** confirm whether the 59-executor research list should be the initial catalogue authority for *candidate identity/provenance only*. My default is yes, with no invented capacity or pricing. No decision is needed now on competitive bidding rules.

**Stopping condition:** approve or revise this proposal before creating cast data or migrating code. Nothing in this PR changes runtime behavior.
