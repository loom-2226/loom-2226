# Build 8 multi-organization / 80-economy checkpoint

**Experimental, non-canon. Reviewed source hash df9c257. Economic tests need external Earth v4 data. Not a qualification baseline.**

Status: active Build 8 development baseline, **not canon or qualification**. Do not regress to Build 7's three representative Agents (`PUB`, `FIN`, `SPN`) as the Build 8 population.

## Retained implementation

- `opening.py` admits 80 national 2026-2035 investment-capacity envelopes into a disposable Build 8 opening. Country investment is a bounded financing input, not an actor budget or free cash.
- `sponsor_executor_network_trial.py` represents 20 named public/private Sponsors and 16 executor roles, with overlapping organizations counted once. Awards remain pending physical plans; awards are not deliveries or earned executor revenue.
- `country_sponsor_allocation_trial.py` exercises bounded national-to-Sponsor allocation and conservation.
- `all_agents_country_trial.py` exercises all 80 economy envelopes and the existing 20-Sponsor/16-executor authored network. It is a trial of organization participation and account allocations, **not** evidence that 32 independent kernel Agents made decisions. Do not silently promote its roster, country preferences, or appetite to canonical world identity or policy.
- `all_agents_controls_trial.py` checks appetite extremes, equal allocation weights, competing commitments, and non-interference when a Sponsor is removed.

## Reproduced observations (2026-10-11, quantifactus)

With `PYTHONPATH=src:simulation/offworld_mvp/phase3b/kernel:.`:

- `python3 -m simulation.offworld_mvp.build8.all_agents_country_trial`: PASS and deterministic replay; 80 economies, 20 Sponsors, 16 executor roles, 32 unique organizations, 41 allocations, 57 economies without eligible Sponsors. Mobilized 25.10396510558080532339 and allocated 10.55502917702657340999999999 fictional capital units.
- `python3 -m simulation.offworld_mvp.build8.all_agents_controls_trial`: PASS; 0%/100% appetite, equal weights, competing commitment rejection without mutation, and unchanged allocations in 79 economies when Interlune is excluded.

These results validate the narrow experimental behavior only, not autonomous decision-making or a full-world epoch.

## Known gaps and next executable objective

The Build 8 opening currently inherits the three generic Build 7 Agents from `_build_kernel`; the network trial registers organization accounts and allocates money but does not make each named organization an independent Agent with information-bounded policy decisions. World Authority records actor references, snapshots, beliefs and decisions, but an exhaustive world-to-Offworld Agent population path has not been demonstrated. Preserve the 80-economy and multi-organization baseline while connecting actual existing Offworld Agent decisions to capital and project consequences. Do not introduce a CIVPROP dependency or another actor registry to achieve this.

Next: exercise one Build 8 epoch with the existing multi-organization economy and capability-limited Agent decisions, preserving identity, observation access, financial conservation, and replay. Stop and report any actual missing world/Agent authority rather than inventing actors, revenues, capabilities or physical deliveries.

This checkpoint does not authorize promotion to canon, qualification, or merging to main.

## Reproduction boundary and preservation (2026-10-11)

All 16 formerly untracked Build 8 scripts are preserved as **disposable, noncanon experiments** on this work branch, not promoted into runtime authority. The 80-economy experiment imports `ROOT` from `two_economy_source_finance_trial.py`; that file must accompany it.

**A fresh clone alone is not enough to execute these experiments.** Several scripts assume an external Earth v4 baseline at `/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24`, which is not stored in this repository. Fresh-clone import verification and execution with separately supplied baseline inputs are distinct checks. Do not describe the branch as fully self-contained or portable until that input is supplied.

The country trial currently uses an authored opportunity gate of 1 and authored capital appetite/preferences. Its allocations carry the mobilization transaction as lineage, not an admitted Sponsor decision authority. The control now gives both competitors positive, unequal allocations from the same finite pool, with project cost strictly between their allocations; it tests share-level scarcity, not a full endogenous market.

Reporting rule: preserve and commit scripts before reporting them as retained; verify import from a clean clone; separately state which external inputs are needed to run them. Never equate a successful import with reproducible execution.

## Safeguards

Earth v4 root is configured once in `opening.py`: `LOOM_EARTH_V4_ROOT`, falling back to the existing quantifactus location. Supply an accessible Earth v4 baseline separately. This removes embedded paths from 13 Build 8 modules but does **not** bundle the data.

`test_source_closure.py` imports tracked Build 8 modules from a fresh `git archive HEAD` checkout; untracked local files cannot satisfy imports. The test intentionally runs against committed HEAD, so newly staged work must be committed before checking its closure. The lunar continuation module additionally requires the optional `psycopg` Python package and a configured PostgreSQL `runtime` service for execution. If `psycopg` is absent, the test reports that optional dependency rather than treating it as a missing repository file.

## October 11 guard follow-up

The source closure test reports the number and identity of optional module skips, allowing only the `lunar_2027_continuation_trial` module when `psycopg` is absent. It verifies committed `HEAD`, **not** uncommitted working-tree edits. Missing Earth v4 directory raises an actionable error pointing to `LOOM_EARTH_V4_ROOT`. `test_sponsor_evidence_gate.py` exercises existing scripted policy outcomes (positive, economic decline, low-belief decline, funding wait) with synthetic observations; it is **not** observation-driven world evidence or autonomous multi-Agent behavior.

## Synthetic lunar observation access control

`test_three_sponsor_observation.py` tests whether three private-kind RETURN Sponsors diverge from observation access alone. Existing Build 7 `explore_paid` generates deterministic noisy signals from **authored synthetic** lunar truth; `publish_observation` applies recipient likelihoods and information access; existing Sponsor prospecting policy decides. A/C receive identical public observations, B also receives a private observation. Negative private evidence yields A/C INITIATE_PROJECT and B DECLINE; positive private evidence changes B to INITIATE_PROJECT without changing A/C. Sharing the negative private evidence makes all three DECLINE. Deterministic replay is asserted. The private-signal flip is implemented by changing authored hidden truth between synthetic scenarios, **not** by altering a recorded signal in the same world. The private water-bearing observation's relevance to volatile prospecting is a trial-only authored assumption. This is not live World Authority admission, a recorded lunar run, an autonomous Agent policy, or canonical physics. No banking machinery.

### Deferred database fixture (parked)

Later, when explicitly reactivated, use the approved read-only World Authority connection to export **only admitted lunar observation records and their receipts** for run `SOLAR_MATERIAL_1cd519072074d72fe42bb2f9:44f9a944ba26d099`. Exclude sealed truth and hidden state. Record run ID, source commit, export date, exact query and per-record SHA-256; label the frozen copy **snapshot, not live admission**. Re-read live records and verify hashes and fixture-versus-live Sponsor decisions. This is a later task, not a prerequisite for the in-memory three-Sponsor test. No database connection is attempted by that test.

### Bounded Sponsor consequences (noncanon synthetic campaign)

`test_three_sponsor_consequences.py` advances the same fixed-seed in-memory lunar information-access trial to existing kernel transfers and Sponsor project status transitions. Each Sponsor begins with 1.00 synthetic capital units and an independent PROPOSED project. An `INITIATE_PROJECT` policy result causes a 0.25 transfer from the Sponsor to its project cash and a PROPOSED→DEVELOPMENT transition; `DECLINE` causes PROPOSED→ABANDONED without investment. Negative B-private evidence: A/C invest (0.50 total), B declines; positive B-private evidence: all three invest (0.75 total). A/C are invariant across the private-evidence change; deterministic replay and kernel invariants are asserted. This is a scripted decision-to-consequence adapter in a test, not an autonomous campaign, construction spending, real-world lunar admission, or canonical economics. The World Authority fixture remains parked.

### Build 8 answered questions (noncanon trials)

- **Country capital drawn once?** Yes, one bounded country mobilization source feeds allocations; no duplicate creation in the tested opening.
- **Appetite changes allocations?** Yes, authored appetite/preferences change finite Sponsor shares; these are not autonomous preferences.
- **Scarcity binds?** Yes, competing commitments cannot both spend the same finite pool.
- **Observation access changes decisions?** Yes, A=C on public evidence; B declines on negative private evidence and initiates when its private evidence is positive.
- **Decisions change capital balances?** Yes, policy-driven transfers change project cash and Sponsor balances (0.50 versus 0.75 invested).

**Question:** Can observation-dependent Sponsor decisions produce different capital and project consequences?
**Control:** Same seed, public observations, priors and capital; A=C, while only B's synthetic private evidence varies.
**Outcome:** Negative B evidence: A/C develop and invest 0.25 each, B abandons; positive B evidence: all three develop and invest 0.25 each.
**Limits:** Scripted synthetic one-period test, authored evidence relevance, no World Authority admission, autonomous policy, realized returns or construction; database fixture deferred.

Shared setup now lives in `sponsor_evidence_setup.py` (three-Sponsor tests) and `sponsor_trial_setup.py` (existing authored episode trials). No decision or economic behavior intentionally changed.

### Second decision period: carry-forward control (noncanon)

**Question:** Do three Sponsors retain their first-period capital, information and project consequences when making another decision?
**Control:** Same fixed-seed synthetic observations and Sponsor policies, one kernel across periods 2 and 3, with separate second-period proposals and no capital reset.
**Outcome:** A/C invest another 0.25 each (remaining 0.50); B again declines under negative private evidence (remaining 1.00), or invests another 0.25 under positive evidence (remaining 0.50). Total two-period investments: 1.00 versus 1.50; replay and accounting checks pass.
**Limits:** No new observations or updated appetite; second proposals are authored, not a lifecycle continuation of the first projects. Each Sponsor uses its own funds, so no Sponsor constrains another. Scripted synthetic trial, no World Authority admission, autonomous policy, returns or construction. Shared-pool competition and the database fixture remain deferred.

### Shared finite capital pool: cross-Sponsor consequence (noncanon)

**Question:** Can B's information-driven choice prevent another Sponsor from receiving otherwise available capital?
**Control:** Same seeded public evidence and A/C beliefs, fixed B→A→C funding order, shared 0.50-unit pool, 0.25 per project; only B's authored private evidence changes across scenarios.
**Outcome:** Negative B evidence: B declines, A/C funded. Positive B evidence: B/A funded, C still chooses INITIATE_PROJECT but remains PROPOSED and unfunded. Pool ends at zero in both cases; replay and kernel invariants pass.
**Limits:** A fixed first-come queue, not bidding, prices, negotiated financing or autonomous allocation. Funding comes from a separate authored shared account rather than Sponsors' individual funds; this is a single-period causal control, not yet the two-period campaign combined with the pool. Private signal changes synthetic authored truth across scenarios; no World Authority admission. Database fixture deferred.

### Full-population activation probe (2026-10-11; stopped at demonstrated blocker)

**Question:** Can the existing full 80-economy/20-Sponsor/16-executor experiment already run as an information-dependent, persistent campaign without inventing actors or policy?
**Control:** Executed the existing 2026 all-economy capital allocation and named Sponsor/executor network with the configured Earth v4 baseline, leaving both trial mechanisms unchanged.
**Outcome:** 80 economies, 20 Sponsors, 16 executor roles (32 distinct organizations), 41 allocations and 57 economies without eligible Sponsors. The separate network trial produced 3 `AWARDED_PENDING_PLAN` and 17 `WAIT`, with zero executor revenue. Both completed with kernel invariants; the allocation trial reproduced its fingerprint.
**Concrete blocker:** The 80-economy trial distributes capital using authored appetite/weights and registers executor accounts, but does not instantiate independent decision-making Sponsor Agents. The named network trial uses authored project costs and budget checks, not recipient-specific evidence/policy decisions. These are separate trials, not a shared persistent campaign; neither establishes full-population information-bounded policy or annual state carry-forward. Do not manufacture policies or present 20 budget checks as 20 autonomous decisions. Stop here before any multi-year claim.
**Limits:** Authored roster and capital assumptions, no World Authority actor/observation admission, no project execution or revenues, no integrated cross-economy competition. No merge to main. The next narrow blocker to resolve is mapping the existing named Sponsor identities to authorized Agent capabilities and observations, without replacing the roster or adding an actor registry.

### Four named USA Sponsor Agents, one finite pool (noncanon)

**Question:** Does private information held by one named Sponsor change another named Sponsor's access to USA capital?
**Control:** Build 8 Earth-v4 opening; existing USA mobilization 4.958025335469291 model units, with an authored 0.50-unit subpool; four real kernel Agents (SpaceX, Blue Origin, Interlune, Axiom), fixed queue in that order, 0.25-unit requests, identical positive public observations. Only SpaceX receives a private synthetic water-bearing observation, negative versus positive across distinct authored-truth scenarios.
**Outcome:** Negative private evidence: SpaceX declines; Blue Origin and Interlune receive funding; Axiom unfunded. Positive: SpaceX and Blue Origin funded; Interlune and Axiom unfunded. Interlune's belief and policy choice remain unchanged. Existing kernel transfers conserve the subpool; deterministic replay passes.
**Limits:** Synthetic evidence, forced-positive public observation with zero sensor error in generation, authored inference from water-bearing to volatiles, authored priority and cost, not actual Sponsor behavior. The 0.50 subpool is a deliberately bounded slice of mobilized USA funds, not a calibrated budget. The other 79 economies and 16 Sponsors remain outside this four-Agent decision experiment; prior 80-economy allocation trial is unchanged. No World Authority observation admission, cross-country competition, autonomous policy, realized returns or construction. No merge.

### Exhaustive USA Sponsor queue sensitivity (noncanon)

**Question:** Does the private-information effect survive all 24 fixed funding orders, or is the original Interlune displacement a queue artifact?
**Control:** Same four USA Agents, Earth-v4-backed 0.50 subpool, 0.25 per request, same authored evidence and policy; permute all 24 orders for each of negative/positive SpaceX private evidence. No funding mechanism changed.
**Observed:** Negative evidence: SpaceX declines in every ordering; Blue Origin, Interlune, Axiom each funded 16/24; three possible funded pairs, each 8/24. Positive evidence: all four request funding; each funded 12/24; six possible funded pairs, each 4/24. In matched orderings the funded set changes in 12/24 cases. The first expectation of 24/24 was falsified by the actual run and corrected to the observed 12/24. All orderings spend exactly 0.50; policy decisions are invariant to order.
**Interpretation:** Private evidence changes SpaceX's decision regardless of queue; who else loses funding is strongly order-dependent. The originally reported Interlune displacement is not universal. This does not establish a fair allocation rule.
**Reproducibility:** Economic sweep requires external Earth v4 baseline at `LOOM_EARTH_V4_ROOT` (or the configured quantifactus path); a clean clone without that data cannot execute the sweep. No merge.

### Frozen USA financier clearing (noncanon, test-only)

Four real USA Sponsor Agents use the existing sponsor prospecting policy. The existing `FINANCIER_SCREENING_V1` evaluates their submitted requests against one frozen 0.50-unit balance and its own per-project belief; no request spends while screening. The one USA fund is a deliberately authored investment fund, not the country's entire available capital. All APPROVE decisions are ranked by the existing policy's `annual_return_proxy`, with a seeded request-ID hash tie-break; complete requests are funded until the fund is exhausted. Unfunded approved requests remain in the existing kernel financing-request collection, marked for next-period reconsideration, not automatically funded in a later period. Canonically ordered ledger transfers do not determine allocation.

The policy's existing **test-only, not-authorized** manifest is used without altering its parameters: concentration cap 0.80, each 0.25 request is 0.50 of the fund; hurdle 0.20. All underwriting inputs (PRICE 1, EXPLORATION_CAPEX 0.125, DEVELOPMENT_CAPEX 0.125, OPERATING_COST 0.5, LEAD_TIME 1) and tie seed `BUILD8_USA_FINANCIER_TEST_0` are authored fixtures, not calibrated economics. Synthetic public volatiles observations are disclosed for all projects; SpaceX's private water-bearing observation is only disclosed to the financier in the disclosed-positive control. Financier beliefs are distinct per project and updated only by observations admitted to it. The financing decision snapshot records strategic pressure from mobilization, fixed at zero; no rival-driven pressure, government Agent or new policy is introduced. Earth per-economy mobilization cap remains unchanged.

**24-order checks:** all permutations have one identical outcome and fingerprint per scenario, for negative private evidence, positive withheld, and positive disclosed. Negative: Blue Origin and Axiom funded, Interlune deferred, SpaceX declines. Positive withheld: Blue Origin and Axiom funded, SpaceX and Interlune deferred. Positive disclosed: SpaceX and Axiom funded, Blue Origin and Interlune deferred. Disclosure raises SpaceX financier return proxy from 14.4 to ~16.94. These results are **not** economic findings. Earth v4 baseline is required for execution; clean clone without external data cannot run the economic test. No merge.

## Executor-to-deal research line (2026-10-11; branch review candidate)

**EXPERIMENTAL / NON-CANON / NOT A BASELINE.** The economic tests require the separately supplied **Earth v4** dataset (`LOOM_EARTH_V4_ROOT`). This is a disposable Build 8-only experiment, not a qualified or persistent offworld campaign. Earlier sections describe historical increments and must not be mistaken for current coverage.

| Capability | Real and exercised | Authored inputs | Stand-in / not established |
| --- | --- | --- | --- |
| Executor quotes (`executor_quotes.py`) | Deterministic BUILD/LAND and other role quote calculations; capacity, cost, markup and scheduling controls | Executor names, role capabilities, costs, markups, durations, capacities | Not bids from real firms, procurement, or calibrated lunar prices |
| Sponsor authorization (`sponsor_development.py`) | Existing Sponsor policy decisions can gate funded project transitions | Proposed projects, budgets, opportunity and Sponsor motives | Authored proposals; not an autonomous investment committee or production authorization |
| Delivery chain (`deliverable_chain.py`) | BUILD→LAND dependencies, success/failure, blocked downstream work and ledger consequences | Stage durations, operator costs, failure injection and outcome definitions | `BUILT` / `ON_MOON` tokens, not conserved spacecraft, cargo, launch or lunar operations |
| Competing projects (`competitive_delivery.py`) | One mobilized country source, two funded projects, shared executor slots, conserved transfers, reproducible scheduling | Two project opportunities, fixed contract prices, finite funding and operator capacity | A narrow scheduler and synthetic cost books, not a real market or contractor balance sheet |
| Sponsor and financier decisions (`screened_delivery.py`) | Existing Sponsor prospecting and financier screening policies; frozen screening, ranked funding, next-year retry; pressure sourced from country mobilization and recorded separately | Interlune/Axiom objectives, underwriting fixture, capital envelope, initial scenario | Test-only financier manifest, zero pressure contribution (no pressure weighting), no endogenous lender or national allocation |
| Private evidence and funding counterfactual (`sponsor_evidence_setup.py`, `evidence_counterfactual.py`) | Existing observation/belief access, private signal flip/share, decision ranking reversal; default two BUILD slots; constrained vs immediate-funding runs show a one-year landing delay for the deferred Sponsor | Synthetic lunar truth/sensor relevance, common 1.525 project budget, 2.00 constrained versus 4.00 immediate fund | Distinct evidence kernel and economic kernel; no integrated provenance, discounting, lost production or monetary delay cost; forecast error is explicitly zero |
| Deal view (`deal_record.py`) | Read-only list of Sponsor, financier, executor roles, decisions, work and evidence routes; flip/share checks | Actor-to-fixture labels and synthetic deal terms | Reconstructed *after* execution, not an event-time custody ledger; posterior disclosure is not disclosure of raw private evidence; no single-world source of truth |

**Contract comparison:** `screened_delivery.py` compares full payment on failed work with a 10% acceptance holdback. Executor cost still occurs; failure suppresses the delivered token. This is an authored contract experiment, not an established industry rule. In the default two-slot negative-private-evidence scenario, Interlune lands in 2030 and deferred Axiom in 2031; with positive private evidence Axiom lands in 2030 and deferred Interlune in 2031. In the immediate-funding control both land in 2030. The older one-slot scenario can hide the financing delay behind executor capacity. Do not quote it as the default.

**Decision integrity:** Sponsor-specific costs and name-typed beliefs are not the ranking mechanism in the latest trial. A common project cost basis supplies financing requests, financier development-capital input and executor payment budget. Different synthetic evidence access changes the financier's belief and reverses ranking. The existing private/public evidence fixture remains a separate kernel; its raw observation is not automatically disclosed to the financier. `deal_record.py` is a presentation of fixture receipts plus the economic result, not authoritative provenance. The two kernels must be joined or event-time receipts added before claiming every actor's actual knowledge is traceable in one world.

**Regression command (requires Earth v4):** `PYTHONPATH=src:simulation/offworld_mvp/phase3b/kernel:. python3 -m unittest discover -s simulation/offworld_mvp/build8 -t . -p 'test_*.py' -q` (or enumerate test modules by dotted package name). `test_source_closure.py` checks committed HEAD, so rerun after the checkpoint commit. No merge or promotion is implied by a passing test or loom-gate.

### Job 2: event-time evidence and deal-party receipts (experimental)

The screened Interlune/Axiom trial now creates public and private synthetic observations **inside its economic kernel**, using the existing `explore_paid` and `publish_observation` transitions. The private positive/negative flip changes authored synthetic truth; sharing is an explicit publication to Interlune. Each receipt is recorded when observation, publication, financier-belief disclosure, financing or executor contract occurs (`BUILD8_KNOWLEDGE` audit and `build8_knowledge` list). `who_knows` lists actors and routes per fact; `deal_records` reads that list rather than regenerating a second evidence fixture. Only actual financing parties see financing terms; only the Sponsor and stage executor see each stage contract. The financier receives an explicitly disclosed **posterior**, not the private raw observation. The Sponsor prospecting decision happens on public evidence before private observation; private evidence affects the later financier screening, not that earlier Sponsor decision.

This is one **disposable trial world** for the screened experiment, not a conversion of every older Build 8 fixture or World Authority provenance. Receipts are plain trial audit records, not a canonical knowledge ontology. Synthetic truth, likelihoods and the inference from water-bearing to volatiles remain authored. No shared kernel modification.
