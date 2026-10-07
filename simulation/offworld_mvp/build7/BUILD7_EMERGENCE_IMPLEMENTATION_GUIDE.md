# LOOM Offworld Build 7 Emergence Implementation Guide

**Status:** Build 7 implementation guidance  
**Branch:** \`offworld-mvp-build7-hidden-world\`  
**Inherited targeted-consequence baseline:** \`8b19259223346ed91a7280687c4fa3dbdd765640\`  
**Governing FRD:** \`simulation/offworld_mvp/OFFWORLD_MVP_GUIDING_FRD.md\`  
**Normative Build 7 gate:** \`simulation/offworld_mvp/build7/BUILD7_ACCEPTANCE_CRITERIA.md\`

## Purpose

This document is the implementation connective tissue between the unchanged Offworld FRD and the emergent Build 7 acceptance criteria.

It exists to prevent scope drift, architectural reinvention, and regression loss while converting the already-qualified target-conditioned Build 7 consequence engine into an emergent world simulation.

It answers:

- what is already earned;
- what remains missing;
- the smallest intended implementation seam for each missing criterion;
- which existing LOOM research/code should be reused;
- how difficult each seam is likely to be;
- how development should be staged and tested;
- when Codex must stop rather than continue expanding the task.

It does **not** replace the FRD or acceptance criteria.

## Authority order

For Build 7 work, use this order:

1. \`simulation/offworld_mvp/OFFWORLD_MVP_GUIDING_FRD.md\`
2. \`simulation/offworld_mvp/build7/BUILD7_ACCEPTANCE_CRITERIA.md\`
3. this implementation guide
4. current code/tests

The FRD defines purpose and protected invariants.

The Build 7 acceptance criteria define what must pass.

This guide defines the approved minimum path for getting there.

If this guide conflicts with either higher authority, stop and report the conflict. Do not silently weaken the higher document.

---

# 1. Earned Build 7 baseline

Commit \`8b19259223346ed91a7280687c4fa3dbdd765640\` is the inherited targeted-consequence baseline.

It has already earned and must preserve:

- generated hidden WORLD integration;
- 90/90 eligible-body physical/runtime portability;
- no Cabeus/body-specific runtime dependency;
- hidden truth / actor knowledge separation;
- \`R_IN_SITU / R_ACCESSIBLE / R_RECOVERABLE\` separation;
- capability-gated recoverability;
- financing request/decision/commitment/disbursement machinery;
- multi-stage development;
- operating/extraction cycles;
- market sale;
- financier return / owner distribution / reinvestment;
- settlement infrastructure;
- passenger transport / population movement;
- enterprise review / repeated operation;
- Earth shadow accounting;
- current promoted Earth authority consumption;
- fixed 2026 technology handling;
- read-only Timeline availability;
- World Authority persistence;
- deterministic reopen/replay;
- targeted 2026-2045 Earth roll-forward;
- zero/unsuccessful/viable/deep-chain behavioral cases.

Do not redesign these systems merely because the new emergent front end exposes awkward interfaces.

The objective is to **reuse the consequence engine**, not replace it.

---

# 2. Research basis already in Git

External research is not required for ordinary Build 7 implementation. The relevant modeling/method research is already preserved in the repository.

## 2.1 Selected propagation architecture

### \`docs/civprop/CIVPROP_ENGINE_V1_SELECTION.md\`

Selected architecture:

\`annual dynamic-recursive state + system-dynamics pressures/opportunities + actor/event decisions\`

Key causal loop:

\`state(t) -> pressures/opportunities -> actor evaluation -> discrete commitments -> changed state -> state(t+1)\`

Important conclusions:

- annual state is the temporal spine;
- pressures/opportunities do not themselves create infrastructure;
- major commitments are Agent decisions;
- actors see only qualified opportunities;
- deterministic replay and hidden-truth separation are required;
- no runtime LLM authority.

## 2.2 Method Lab development practice

### \`engineering/civprop/method_lab/METHOD_LAB_V1.md\`

Key guidance:

- freeze a deliberately small world;
- hold feasibility/accounting semantics common while testing orchestration;
- keep evaluator-only truth separate;
- use a common result contract;
- do not freeze persistence/schema before method fit.

### \`engineering/civprop/method_lab/PROTOTYPES_V1.md\`

Key guidance:

- shared mechanics across candidate engines;
- dynamic-recursive annual progression;
- actor/discrete-event commitments;
- keyed deterministic stochasticity;
- construction lag;
- source-debited migration;
- small synthetic runs before production-scale runs.

## 2.3 Solar emergence research

### \`research/seeds/LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md\`

Key guidance directly relevant to Build 7:

- all eligible Solar bodies may be evaluated;
- do not hand-select Mars/Ceres/Luna outcomes;
- there is no universal attractiveness score;
- accessibility is relational and time-dependent;
- use an existing authority/adapter or a narrow deterministic surrogate rather than building another Navigator;
- keep financing pools simple;
- use simple project/investment choice;
- allow probabilistic discrete choice among similar alternatives if useful;
- authored coefficients live in explicit parameter files;
- accumulated realized capital/infrastructure creates path dependence;
- first prove the engine on a tiny 5-10 year fixture;
- only then run the full experiment;
- do not tune parameters because emergent geography looks surprising.

## 2.4 Mission / knowledge

### \`docs/civprop/CIVPROP_MISSIONS_AND_KNOWLEDGE_V1.md\`

Key guidance:

\`actor-visible knowledge -> mission opportunity -> access/capability/budget/economics/VOI -> mission decision -> mission execution -> noisy observation -> knowledge update -> later project/economic decision\`

Critical invariant:

\`HIDDEN PHYSICAL REALIZATION != ACTOR KNOWLEDGE\`

Mission selection and value-of-information calculation may not read hidden truth.

## 2.5 Pressure / opportunity

### \`docs/civprop/CIVPROP_DEMAND_PRESSURE_V1.md\`

Key guidance:

\`civilization state -> requirement -> installed capacity -> unmet demand -> decaying pressure -> opportunity qualification -> actor decision\`

Need does not imply affordability.

Pressure does not itself build infrastructure.

## 2.6 Accessibility

### \`docs/civprop/CIVPROP_TRANSPORT_ACCESSIBILITY_V1.md\`
### \`engineering/civprop/contracts/accessibility_v1.py\`

Key guidance:

- accessibility is relational;
- scope includes origin, destination, epoch, mission/service class and technology/actor state;
- preserve \`FEASIBLE / INFEASIBLE / UNKNOWN\`;
- generalized transport cost is distinct from mere geometric distance;
- UNKNOWN does not become zero cost or entitlement.

## 2.7 Offworld methodology / ODD

### \`simulation/offworld_mvp/phase3b/PHASE3B_METHODOLOGY_RESEARCH_BASIS_2026_10_04.md\`
### \`simulation/offworld_mvp/phase3b/OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md\`

Key guidance:

- selective Agent resolution;
- explicit scheduling/coupling;
- verification distinct from empirical validation;
- invariants over narrative expectations;
- state-changing actions remain scheduler/kernel governed;
- causal trace and deterministic replay are first-class.

---

# 3. Capital-to-cash abstraction is fixed for this implementation pass

Do not reopen the financing architecture during the emergence conversion.

Use the agreed reduced country-level coupling:

\[
F_{c,t},\quad X_{c,t},\quad R_{c,t},\quad S_{c,t}
\]

with:

\[
M_{c,t}=I_{c,t}\times m_{c,t}
\]

\[
m_{c,t}=f(O_{c,t},S_{c,t}),\qquad 0\le m_{c,t}\le m^{max}
\]

Interpretation for Build 7 development:

- \(F\): available cash for new Offworld financing;
- \(X\): outstanding country-origin Offworld exposure;
- \(R\): realized Offworld cash returned during the period;
- \(S\): strategic pressure.

Commercial opportunity and strategic pressure affect mobilization separately.

Actual downstream financing remains in existing Offworld financing machinery.

Commitments reserve available financing.

Actual disbursement creates Earth -> Offworld diversion and increases exposure.

Returns/losses alter later financing state.

The final Earth-side semantic refinement of this abstraction is explicitly deferred until after the emergent loop works, provided conservation, lineage and the acceptance criteria are maintained.

Do not replace this with:

- banks;
- securities markets;
- government balance sheets;
- public/private financial sectors;
- household savings;
- country ABMs.

---

# 4. Current Build 7 gap matrix

Difficulty is relative to the inherited Build 7 baseline.

| Acceptance area | Current Build 7 state | Minimum implementation | Difficulty | Primary research/code basis |
|---|---|---|---|---|
| Epistemic extension | Hidden truth protected, but selected \`GEN_SITE_1\` is exposed as an actor-visible authored opportunity/site | Remove hidden site identity from opening Agent opportunity facts. Initial candidates are body/legitimate-region level. Site becomes visible only via authorized observation/action. | MEDIUM | FRD §§3,15-17; Mission/Knowledge V1 |
| No-target GENESIS | \`_build_kernel(target)\` requires one body; creates node/resource/colony/\`EXP\`/\`P\` around it | Split scenario-level initialization from later opportunity/project materialization. GENESIS creates world, Earth, actors, capital, knowledge, capabilities only. | HIGH | FRD mission/agent/project semantics; Build 7 baseline |
| Recurrent annual loop | \`run_remote -> run_surface -> run_full_chain\`; years/stages hard-coded; then passive Earth roll-forward | Add one annual conductor over existing scheduler. Each year updates state, derives opportunities, makes bounded decisions, executes authorized events, closes/persists. | HIGH | CIVPROP Engine V1 Selection; Offworld scheduler contract |
| Opportunity generation | No Build 7 candidate set; operator already chose target | Add a pure/reconstructable function over actor-visible state producing ephemeral candidates | MEDIUM | Method Lab; Solar Emergence v0 |
| Comparable accessibility | One target-specific transport relationship | Provide deterministic provenance-bearing origin/destination/year accessibility for candidate bodies using existing authority or narrow compiled surrogate | MEDIUM | Accessibility V1; Solar Emergence v0 |
| Endogenous exploration | Explorer only authorizes/rejects a supplied preselected request | Let explorer evaluate several legitimate mission candidates and choose one/none using visible knowledge/access/capability/budget/cost/VOI | MEDIUM-HIGH | Mission/Knowledge V1; public explorer policy |
| F/X/R/S capital state | Absent | Add one country-indexed state object/ledger surface upstream of existing finance | MEDIUM | Agreed capital abstraction; Actor State V1 concepts |
| Mobilization | Earth investment constrains supply expenditure; actor cash starts as fixed fixture balances | Compute \(M=I\times m(O,S)\), bounded by \(m^{max}\), with explicit response/persistence parameters | MEDIUM | Agreed capital abstraction |
| Commercial opportunity | Persistent project exists before economics are evaluated | Compute prospective economics over ephemeral candidate using actor-visible inputs and existing underwriting values | MEDIUM | Project Economics / underwriting machinery |
| Strategic pressure | Absent | Add thin \(S\) state. Baseline may be zero; bounded visible-rival fixture proves causal seam | LOW-MEDIUM | Agreed capital abstraction; epistemic firewall |
| Cash/exposure/returns | Commitments/disbursement/returns exist, but no country exposure state | Bridge existing financial events to \(F/X/R\). Do not replace current ledger/accounting | MEDIUM | Existing kernel financing + Earth shadow |
| Earth shadow reconciliation | Diverted/returned capital already recorded | Add country/year checks tying new capital state to actual transactions | LOW | Existing EarthImpactLedger |
| Endogenous project creation | \`Kernel.add_project()\` only used during initialization | Add one governed SYSTEM transition authorized by sponsor decision to create project/account/location binding | MEDIUM | Existing Kernel.add_project; Agent request->SYSTEM transition pattern |
| Emergent prefix -> existing chain | Deep chain already works after target/project exists | Instantiate existing development/market/settlement structures when chosen project is created, then hand off to qualified downstream machinery | MEDIUM-HIGH | Current Build 7 |
| Path dependence | Exists within one selected venture, not across future candidate choice | Feed realized beliefs/capital/infrastructure/population/project history back into future candidate derivation | MEDIUM | CIVPROP Engine V1; Solar Emergence v0 |
| Ten-year temporal depth | Active fixed chain mostly completes before passive Earth advance | Run same annual conductor for 2026-2035, including no-action years | MEDIUM after conductor | CIVPROP Engine V1 |
| Country-indexed scope | USA semantic assumptions appear throughout current Build 7 | Parameterize new capital/opportunity layer by country; keep USA as only active baseline economy | MEDIUM | Earth authority; FRD country-neutral architecture |
| Emergent persistence | Persistence centered on one NamedLocationBinding | Separate run-level persistence from optional world/project-scoped materialization. Add binding only after legitimate action needs it. | HIGH / HIGHEST RISK | World Authority existing multi-world schema; current named-world adapter |
| Clean entrypoint | \`new --body ...\` required | Normal emergent \`new\` takes seed/authority only. Keep targeted runner for qualification regression. | LOW after GENESIS/persistence |
| Emergence suite | Absent | Implement acceptance tests A-I only after seams exist | HIGH TEST EFFORT / LOW NEW ARCHITECTURE |
| New parameters/randomness | Current parameters explicit; new emergence parameters absent | One versioned parameter block; keyed choice draws by stable identities if stochastic selection is used | LOW-MEDIUM | Method Lab; existing keyed RNG |

---

# 5. Implementation rules by gap

## 5.1 No-target GENESIS

This is the first implementation blocker and must be solved before opportunity logic.

Current problematic pattern:

\`operator body -> _target_from_generated -> _build_kernel(target) -> project/resource/settlement state\`

Required pattern:

\`world seed -> generated Solar WORLD -> scenario-level kernel/run state\`

GENESIS may contain:

- Earth node/context;
- actors;
- actor accounts/capital coupling state;
- actor knowledge;
- fixed technology/capabilities;
- Solar catalog identity;
- hidden generated worlds on WORLD_SIM plane;
- scheduler/persistence identity.

GENESIS may not contain a selected development location/project/settlement.

Do not solve this by inventing a fake \`SOLAR_SYSTEM\` project or dummy resource.

### Required focused proof

- normal run opens without \`--body\`;
- zero projects;
- zero settlements;
- no privileged target;
- persist;
- reopen;
- advance one empty annual period;
- exact deterministic replay.

Stop here before adding opportunity choice.

## 5.2 Opportunity derivation

Implement opportunities as immutable/reconstructable value objects or equivalent narrow records.

Avoid persisted lifecycle/state for unchosen opportunities.

Stable identity should be derived from legitimate visible inputs such as:

\`actor + year + action archetype + destination/scope\`

Initial opportunity families should remain minimal:

- remote exploration mission;
- legitimate follow-on prospecting mission;
- resource-development candidate after information makes one possible.

Do not add generic opportunity taxonomies unless required by an acceptance case.

## 5.3 Accessibility

Prefer reuse in this order:

1. existing admitted Build 7/Offworld transport/accessibility state;
2. existing CIVPROP accessibility adapter/contracts;
3. narrow compiled deterministic Solar accessibility input derived from existing authority.

Do not build a new routing engine.

Required candidate comparison fields only need to support meaningful choice, e.g.:

- status;
- cost/generalized cost;
- travel time where used;
- capability/service requirement;
- limiting constraint/provenance.

## 5.4 Exploration choice

Current public explorer policy answers:

> Is this supplied mission authorized?

The emergent layer must first answer:

> Which legitimate mission candidate, if any, should be supplied?

Keep those concerns separate.

Recommended minimal pattern:

1. derive feasible candidate missions;
2. compute bounded visible utility/VOI for each;
3. choose one/none;
4. submit existing exploration request;
5. existing public explorer policy may still perform final authorization/gating;
6. existing WORLD_SIM transition executes observation;
7. existing belief update machinery consumes observation.

Do not let candidate ranking call WORLD_SIM hidden resource state.

## 5.5 Commercial opportunity / prospective economics

A candidate can be economically evaluated without becoming a project.

Reuse current underwriting/project-economics inputs where possible.

Do not instantiate \`Project P\` merely to ask what a hypothetical project might cost.

UNKNOWN required economic inputs produce UNKNOWN/BLOCKED/DEFER semantics, not fallback scores.

## 5.6 Project creation

Add exactly one governed transition unless a concrete blocker proves more is required.

Conceptual form:

\`create_project_from_opportunity(actor_decision_ref, opportunity_ref)\`

It must:

- validate sponsor authorization;
- validate opportunity identity/scope;
- create project identity;
- create/attach required project cash account;
- materialize project location/world binding;
- preserve causal provenance;
- be replay-safe / duplicate-safe.

It shall not:

- assess hidden recoverability;
- finance itself;
- commission infrastructure;
- create settlement/population;
- create market demand.

## 5.7 Annual conductor

Do not replace the existing scheduler.

Use one annual recursive spine over the existing deterministic scheduler.

Conceptual Build 7 year:

\`\`\`text
YEAR OPEN
  admit annual Earth context
  execute/settle already-due events
  update F/X/R/S

  derive actor-visible opportunities

  PUBLIC DECISION WINDOW
    choose exploration mission or WAIT

  SPONSOR DECISION WINDOW
    evaluate legitimate project opportunities
    INITIATE / WAIT / DECLINE / BLOCKED_UNKNOWN

  FINANCING DECISION WINDOW
    existing financing machinery for requests that exist

  execute authorized due actions
  generate legitimate observations
  update beliefs
  execute due development / operation / market / transport

  accounting + conservation
  snapshot
  persist
YEAR CLOSE
\`\`\`

Do not create multiple within-year decision windows unless an observed behavior requires them.

An observation produced after an Agent's current decision window should affect the next legitimate decision window, not retroactively alter earlier decisions.

## 5.8 Path dependence

Do not create a special "path dependence engine."

Path dependence is simply future opportunity derivation consuming persisted realized state.

At minimum it may consume:

- current beliefs;
- remaining financing cash;
- exposure/returns;
- existing infrastructure/capacity;
- existing projects;
- population/settlement;
- accessibility relationships;
- demand/pressure if already modeled.

A successful project may change future opportunities because state changed.

A failed project may change later decisions because financing state changed.

That is enough.

---

# 6. Development DevOps: hard-stop increments

Continue on the existing Build 7 branch and PR #370.

Do not create a new Build 8 branch.

Each increment has a hard stop. Codex must not begin the next increment unless explicitly authorized.

## Increment 0 - authority/docs
### Objective

Establish the authoritative guidance set.

### Required artifacts

- unchanged FRD;
- replacement Build 7 acceptance criteria;
- this implementation guide;
- root \`AGENTS.md\` router.

### Runtime changes

None.

### Stop

Commit/push guidance only.

---

## Increment 1 - no-target GENESIS + persistence
### Objective

Normal Build 7 run opens without body/project target and survives World Authority persist/reopen.

### Minimum changes

- scenario-level Build 7 initialization;
- run identity no longer depends on selected body;
- zero project/settlement initialization;
- run-level persistence path that works without one named target;
- one empty annual epoch.

### Tests

- no \`--body\` required;
- zero project;
- zero settlement;
- no actor-visible hidden site;
- complete generated hidden WORLD exists;
- persist COMMITTED;
- replay ALREADY_MATCHED;
- inherited targeted regression still runnable.

### Stop condition

A no-target run opens, commits, reopens and advances one empty year deterministically.

Do not implement opportunity generation yet.

---

## Increment 2 - opportunity + accessibility derivation
### Objective

Produce legitimate actor-visible candidate missions without executing them.

### Fixture

Use a tiny 3-body or similarly small bounded test fixture first.

### Minimum changes

- immutable candidate representation;
- pure candidate derivation;
- comparable accessibility input/adapter;
- visible information only.

### Tests

- hidden truth absent from candidate payload;
- UNKNOWN preserved;
- stable candidate IDs;
- candidate enumeration order does not affect identity/result;
- visible accessibility differences affect candidate qualification;
- hidden physical differences alone do not.

### Stop condition

Deterministic candidate sets are produced from actor-visible state only.

Do not add Agent selection yet.

---

## Increment 3 - endogenous exploration choice
### Objective

Public actor chooses one legitimate mission or none and existing observation machinery executes it.

### Minimum changes

- bounded candidate ranking/VOI;
- deterministic choice rule;
- handoff to existing exploration request/policy;
- existing WORLD_SIM observation;
- existing belief update.

### Tests

- zero candidates -> WAIT;
- one viable candidate -> correct bounded choice;
- multiple candidates -> deterministic selected candidate;
- hidden-truth twin -> same pre-observation choice;
- visible-information twin -> choice may legitimately change;
- unchosen bodies untouched;
- replay exact.

### Stop condition

One mission choice can emerge from state, execute, and update knowledge.

Do not create development projects yet.

---

## Increment 4 - capital coupling + prospective economics + project creation
### Objective

Convert Earth economic capacity into finite Offworld cash using the agreed abstraction, then allow sponsor to create a durable project from an actor-visible candidate.

### Fixture

Use a tiny 5-10 year synthetic/controlled fixture first.

### Minimum changes

- F/X/R/S;
- \(M=I\times m(O,S)\);
- prospective commercial opportunity;
- thin strategic-pressure seam;
- sponsor project-initiation decision;
- one governed project-creation SYSTEM transition.

### Tests

- zero \(O,S\) bounded result;
- commercial-only mobilization;
- strategic-only mobilization;
- \(m^{max}\) respected;
- cash/exposure non-negative;
- opportunity may exist without project;
- WAIT creates nothing;
- INITIATE creates exactly one project;
- duplicate replay impossible;
- hidden truth absent from sponsor decision;
- project finance still uses existing machinery.

### Stop condition

An endogenous opportunity can mobilize finite financing and cause exactly one sponsor-authorized project to come into existence.

Do not yet refactor the entire downstream chain.

---

## Increment 5 - annual conductor + downstream handoff
### Objective

A created project enters the existing qualified financing/development/operation machinery under the recurrent annual loop.

### Minimum changes

- annual conductor;
- dynamic project-specific instantiation of existing development/market/settlement structures only when needed;
- state feedback into next year's candidate derivation.

### Tests

- 3-5 year integration fixture first;
- no fixed stage-by-year assumptions;
- no-action year valid;
- project financing/development works;
- failure persists;
- success changes later opportunity;
- accounting/conservation;
- persistence/resume at internal checkpoint.

### Stop condition

The same annual loop can create a project, advance it through existing machinery, persist, reopen, and make a later decision from changed state.

---

## Increment 6 - ten-year emergent qualification
### Objective

Run 2026-2035 from no-target GENESIS.

### Required acceptance cases

Acceptance criteria §25 A-I.

### Additional regressions

- inherited 90/90 targeted breadth;
- inherited zero/unsuccessful/viable/deep-chain cases;
- inherited targeted 2045 Earth temporal regression;
- affected kernel/World Authority tests;
- \`git diff --check\`.

### Stop condition

All replacement acceptance criteria pass on the exact tested commit.

Then stop engineering Build 7.

---

# 7. Test strategy

Testing should be proportional to the changed seam.

## Pure derivation changes

Run:

- focused unit tests;
- property/invariant tests;
- deterministic serialization/identity tests.

## Agent policy changes

Run:

- focused policy tests;
- decision-snapshot firewall tests;
- deterministic replay;
- hidden-truth twin tests.

## Kernel transition changes

Run:

- focused unit tests;
- scheduler-valid transition tests;
- accounting/conservation property tests;
- causal lineage tests.

## Persistence changes

Run:

- focused World Authority lifecycle tests;
- Build 7 persist/reopen/replay;
- inherited targeted persistence regressions.

## Annual conductor changes

Run:

- tiny emergent integration fixture;
- relevant Offworld regressions;
- resume from at least one internal checkpoint.

## Final qualification

Run:

- full replacement Build 7 acceptance suite;
- all preserved Build 7 targeted qualification;
- broader affected Offworld regressions;
- exact code/tree linkage as applicable;
- clean working tree/diff review.

---

# 8. Properties to test, not preferred histories

Do not test that Mars/Ceres/Moon/Bennu "should" win.

Test invariants and causal properties.

Examples:

\[
0\le m\le m^{max}
\]

\[
F\ge0,\qquad X\ge0
\]

- no project without an initiating sponsor decision;
- no selected mission outside the actor-visible candidate set;
- no hidden-world property in an Agent decision snapshot;
- same actor-visible state + same decision key -> same decision;
- hidden-world changes alone do not change pre-observation behavior;
- legitimate visible-information changes may change behavior;
- candidate ordering does not alter stable identity or unrelated random draws;
- no money from nothing;
- no population from nothing;
- no resource conservation violation;
- commitments and disbursements remain distinct;
- project replay creates no duplicate project;
- no body importance is authored as an outcome target.

Emergent geography is an output, not a test oracle.

---

# 9. Randomness

Stochastic choice is optional.

If used:

- use stable keyed randomness;
- keys should include stable semantic identities such as run seed, year, actor, decision class and opportunity ID;
- never use one mutable global RNG stream for cross-domain behavior;
- candidate enumeration order must not alter unrelated draws;
- unrelated opportunity insertion must not perturb unrelated stochastic processes.

A deterministic bounded choice rule is acceptable for Build 7 if it still chooses from current state rather than operator-selected targets.

---

# 10. Online research policy for Codex

Do **not** conduct online research as part of ordinary Build 7 implementation.

The repository research listed in §2 is the default modeling/method authority.

External research is permitted only when one of these concrete conditions exists:

1. an acceptance criterion requires a fact not covered by cited repository authority;
2. a third-party library/API behavior has materially changed and current official documentation is necessary;
3. an observed implementation blocker cannot be resolved from repository code, tests or cited research.

Before external research, Codex must identify:

- the exact missing question;
- why repository authority/code cannot answer it;
- how the answer would affect the current increment.

Do not perform broad "modern ABM research" or redesign the method during implementation.

If external research would materially change architecture or acceptance semantics, stop and request review rather than proceeding.

---

# 11. Explicit anti-drift rules

Codex shall not:

- weaken the FRD;
- weaken or rewrite acceptance criteria to match current code;
- redefine emergence as body portability;
- make \`--body\` part of the normal world-run interface;
- pre-create development projects at GENESIS;
- expose hidden generated site/resource truth to Agent decisions;
- create a universal destination-attractiveness score;
- tune parameters to make a preferred body succeed;
- replace the agreed capital-to-cash abstraction during this implementation pass;
- introduce Mesa or another general ABM framework;
- introduce runtime LLM decisions;
- build a new World Authority;
- build another general persistence architecture;
- build another Navigator;
- activate all countries merely because authority data exists;
- create banks/markets/government simulators;
- add architecture for hypothetical future needs;
- proceed beyond the assigned increment.

If a narrow increment appears to require substantial new architecture, stop and report the concrete blocker before authorizing expansion.

---

# 12. Codex completion report for every increment

At the end of an authorized increment, report:

- acceptance criterion IDs/sections addressed;
- files changed;
- behavior added;
- existing machinery reused;
- tests run and exact results;
- preserved regressions run;
- any observed blocker/deviation;
- exact commit SHA;
- explicit statement that the next increment was **not** started.

A passing test suite is not by itself evidence that the acceptance criterion was satisfied. The completion report must state how the observed behavior satisfies the criterion.

---

# 13. Build 7 final development principle

The intended conversion is:

\[
\boxed{
\text{no-target WORLD}
\rightarrow
\text{actor-visible opportunity}
\rightarrow
\text{exploration choice}
\rightarrow
\text{knowledge}
\rightarrow
\text{capital mobilization}
\rightarrow
\text{sponsor project creation}
\rightarrow
\text{existing Build 7 consequence engine}
}
\]

Do not expand the problem beyond that unless actual execution exposes a concrete missing causal requirement.

Research broadly has already been done.

Model narrowly.

Use the world early.

Complexity must earn its existence.
