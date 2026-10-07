# LOOM Offworld Build 7 — Scoped Codex Instructions

This file supplements the repository-root \`AGENTS.md\` for work under:

\`simulation/offworld_mvp/build7/\`

The root operating contract and current governance on authoritative \`main\` still apply.

## Bootstrap before substantive Build 7 work

After the repository-root bootstrap, read these Build 7 documents in order:

1. \`simulation/offworld_mvp/OFFWORLD_MVP_GUIDING_FRD.md\`
2. \`simulation/offworld_mvp/build7/BUILD7_ACCEPTANCE_CRITERIA.md\`
3. \`simulation/offworld_mvp/build7/BUILD7_EMERGENCE_IMPLEMENTATION_GUIDE.md\`

Authority interpretation:

- FRD = purpose and protected invariants;
- acceptance criteria = scoped Build 7 completion obligation;
- implementation guide = approved minimum implementation route;
- current code/tests = implementation evidence, not permission to weaken the documents above.

If these documents conflict, stop and report the conflict.

## Change class

Build 7 implementation work is \`class:engineering\` unless a separately authorized change explicitly establishes another class.

Historical \`research/**\` files cited by the implementation guide are reference material only. Do not mutate them and do not treat them as active research authority.

## Inherited baseline

Preserve the targeted-consequence baseline:

\`8b19259223346ed91a7280687c4fa3dbdd765640\`

Its already-qualified body coverage, physical/epistemic invariants, downstream project machinery, World Authority persistence, and targeted regressions are assets to reuse.

Do not replace qualified machinery merely because the emergent front end requires a different orchestration path.

## Build 7 non-negotiables

- Normal emergent runtime starts with no operator-selected body/site/project target.
- No development project exists at GENESIS.
- Hidden generated site/resource truth does not enter Agent decisions.
- Actor-visible opportunities are derived from legitimate visible state.
- Exploration destination is an Agent choice, not a CLI input.
- Durable projects arise only from an authorized sponsor decision.
- Use the agreed country-level capital-to-cash abstraction in the acceptance/implementation documents for this pass.
- Reuse the existing Offworld consequence engine after project creation.
- Preserve deterministic scheduler, causal trace, conservation, and World Authority replay.
- Do not tune parameters to make preferred bodies succeed.
- Emergent geography is an output, not a target.

## Scope firewall

Do not introduce without a concrete blocker and explicit review:

- Mesa or another general ABM framework;
- runtime LLM decision authority;
- a new World Authority;
- a second persistence architecture;
- a new Navigator/routing authority;
- a country ABM;
- banks, securities markets, insurers, government balance sheets or household finance;
- all-80-country activation;
- endogenous technology development;
- full Earth macroeconomic feedback;
- universal site-level prospecting;
- generalized future-proof architecture.

If the assigned increment appears to require substantial new architecture, stop and identify the concrete blocker.

## Repository research first

The repository research cited in \`BUILD7_EMERGENCE_IMPLEMENTATION_GUIDE.md\` is the default modeling/method basis.

Do not conduct online research by default.

External research is allowed only when:

1. an acceptance requirement depends on a fact absent from cited repository material;
2. a third-party library/API has changed and current official documentation is required;
3. an observed implementation blocker cannot be resolved from repository code, tests or cited research.

Before external research, state:

- the exact missing question;
- why repository material cannot answer it;
- how the answer affects the current authorized increment.

If outside research would materially change architecture or acceptance semantics, stop for review.

## Increment discipline

Implement only the explicitly authorized increment from:

\`BUILD7_EMERGENCE_IMPLEMENTATION_GUIDE.md\`

Do not proceed automatically to the next increment.

Each increment must stop at its stated stopping condition.

Do not bundle later work merely because it is convenient while editing the same file.

## Testing

Use the test class specified by the implementation guide and the root \`AGENTS.md\`.

At minimum:

- pure derivation change -> focused unit/property/determinism tests;
- Agent policy change -> policy + firewall + replay tests;
- kernel transition -> scheduler-valid transition + accounting/conservation tests;
- persistence change -> World Authority lifecycle/reopen/replay tests;
- conductor/integration change -> bounded emergent fixture + relevant Offworld regressions;
- final qualification -> replacement Build 7 acceptance suite + preserved targeted Build 7 regressions.

Never replace a required behavioral acceptance test with a weaker unit test merely because the unit test passes.

## Completion report

At the end of every authorized Build 7 increment, report:

- acceptance criteria sections addressed;
- files changed;
- behavior added;
- existing machinery reused;
- tests run and exact results;
- preserved regressions run;
- blockers/deviations;
- exact commit SHA;
- confirmation that the next increment was not started.

Passing tests do not override acceptance semantics. State how the observed behavior satisfies the criterion.
