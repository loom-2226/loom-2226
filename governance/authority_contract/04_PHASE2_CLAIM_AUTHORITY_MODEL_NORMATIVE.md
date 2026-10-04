# LOOM Authority and State Contract v1
## Phase 2 — Claim and Authority Model — Consolidated Normative Candidate

**Status:** PRE-CONTRACT / OWNER-ADOPTED PHASE 2 CANDIDATE / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Scope:** Phase 2 semantics only
**Implementation authority:** NONE
**Qualification effect:** NONE

## 1. Purpose and precedence

This document consolidates the owner-adopted Phase 2 model after D2.1-D2.10, the internal hostile-review repairs, Hostile Review Repair Package A, and the three worked encodings.

It is the normative Phase 2 candidate for review. The historical development record remains in `03_PHASE2_CLAIM_AUTHORITY_MODEL.md`.

**Precedence rule:** for Phase 2 semantics, this consolidated candidate supersedes conflicting candidate, mechanical-pass, repair-draft and pre-amendment language in the historical Phase 2 development record. It does not amend Phase 0, qualify existing LOOM holdings, release Contract v1, or authorize implementation.

## 2. Core objects

### 2.1 Proposition
A **PROPOSITION** is semantic content capable of being asserted within stated scope and context.

### 2.2 Assertion
An **ASSERTION** is an identifiable occurrence by which a source, actor, process or governance act asserts a proposition.

Multiple assertions may support or contradict one proposition. A new source does not create a new proposition merely because it creates a new assertion.

### 2.3 Governed claim
A **GOVERNED CLAIM** is LOOM's governed representation linking a proposition to its assertions/support, scope, lineage and governance relations.

For v1 interpretation of Phase 0 D0.4, evidentiary/support warrant attaches to identifiable assertions and their lineage; standing is evaluated for the governed proposition/claim for a specified use. Contract v1 must preserve this interpretation explicitly rather than silently redefining Phase 0.

**Invariant:** CLAIM CONTENT != CLAIM SUPPORT.

## 3. Required semantic dimensions

A governed claim may require representation of:

1. proposition kind;
2. epistemic mode;
3. knowledge/value state;
4. derivation lineage;
5. scope;
6. time and clock;
7. world-context;
8. epistemic perspective / information domain;
9. warrant and root path;
10. governance roles/status axes;
11. uncertainty/variability;
12. support, contradiction and conflict relations;
13. dependencies;
14. use admissibility;
15. qualification outcome where applicable.

These dimensions are not a universal scalar authority score.

## 4. Proposition kinds

Candidate proposition kinds include:

- `STATE_VALUE`
- `EVENT`
- `IDENTITY`
- `RELATIONSHIP`
- `RULE_NORM`
- `PARAMETER`
- `MODEL_RELATION`
- `AUTHORIZATION`
- `QUALIFICATION_ASSERTION`

Exact serialization tokens may be frozen later. Semantic distinctions may not be collapsed merely for storage convenience.

## 5. Epistemic mode

Candidate epistemic modes include:

- `EMPIRICAL`
- `PROJECTION`
- `SCENARIO_STIPULATION`
- `SIMULATED`
- `NORMATIVE`
- `FORMAL`

`DERIVED` is not an epistemic mode. `MODEL_PARAMETER` is principally a proposition/functional role. `UNKNOWN` is not an epistemic mode.

## 6. Knowledge/value state and UNKNOWN

Knowledge/value state includes at minimum `ASSERTED`, `UNKNOWN`, and `NOT_APPLICABLE`. `QUARANTINED` is not a value state; it belongs to admission/disposition governance.

UNKNOWN is evaluated as:

`UNKNOWN(proposition, assertion_set, scope)`

Named assertion sets include at minimum:

- `ALL_RECORDED`: all recorded assertions relevant to the proposition/scope regardless of admission disposition;
- `ADMITTED`: assertions admitted for the governed context/use under applicable admission rules.

If `ALL_RECORDED` contains one or more relevant assertions but the evaluated assertion set (including `ADMITTED`) is empty because admission, quarantine, qualification, staleness or other use-admissibility/disposition rules excluded those assertions, the evaluation MUST return `BLOCKED` with the applicable reason and MUST NOT return `UNKNOWN`. `UNKNOWN` is permitted only when the evaluated knowledge question has no asserted value in the relevant assertion set for reasons that are not themselves a governance/admissibility exclusion. Implementations evaluating a restricted assertion set MUST inspect the corresponding `ALL_RECORDED` set sufficiently to distinguish epistemic absence from governance exclusion.

UNKNOWN is not false, zero, empty, confirmed absence, stale, conflict, rejected, quarantined or not-applicable. Confirmed absence is an asserted negative proposition with evidence and scope. An empty collection is asserted empty only where completeness is established.

Unknownness is dimension-local. A known adjacent dimension does not fill an unknown one.

Search/assessment state is separate from value state. A bounded negative search records its search scope. Evidence discovery and admission disposition are represented separately.

## 7. Scope

Scope may include:

- entity;
- spatial domain;
- temporal validity;
- knowledge time;
- scenario/reference context;
- population/cohort;
- measurement/sample;
- intended use;
- search/assessment scope.

Scope never widens implicitly. Unknown scope remains unknown.

## 8. World-context

World-context identifies which world/state a proposition is about:

- `REAL`
- `SCENARIO(id)`
- `REALIZED(run_id)`

No consumer may cross world-contexts implicitly. Any permitted cross-context dependency must be explicit in lineage and authorized where required.

## 9. Epistemic perspective / information domain

Perspective identifies where and for whom information is represented:

- `GOVERNANCE`
- `WORLD_SIM`
- `AGENT(actor_id)`

Information possession/availability is distinct from permission to use it. For agents, permission cannot create information that the agent does not possess.

Concrete knowledge-state representation belongs to Phase 3. Runtime enforcement belongs to Phase 4.

## 10. Evidence plane

For Phase 2 semantics, the **evidence plane** is world-context `REAL` with evidentiary lineage containing no scenario-world value, simulated state or authorized substitution/bridge as an evidentiary input.

A bridge may create a dependent for a named use/context but cannot convert a non-evidentiary input into evidence-plane warrant.

## 11. Derivation lineage

Candidate derivation families include:

- `DIRECT_REPORTED`
- `DIRECT_SAMPLE`
- `IN_SITU_DIRECT`
- `IN_SITU_REMOTE`
- `EARTH_REMOTE`
- `INFERRED`, with subtype where material;
- `PHYSICAL_MODEL`
- `THEORETICAL_EXPECTATION`
- `DETERMINISTIC_DERIVATION`
- `FITTED_OR_CALIBRATED`
- `IMPUTED_OR_SUBSTITUTED`
- `SIMULATED_TRANSITION`

A transformation/model is itself a necessary dependency with identity, version and standing. Correct execution proves consequence from declared inputs/rules, not empirical truth of those inputs.

Retrodiction from a fitted model remains model-derived rather than observation. Defined-by-convention constants/units may have formal or normative standing rather than measured empirical standing.

## 12. Primitive authority roots and warrant

Phase 2 adjudicates two primitive roots:

1. **EVIDENTIARY ROOT**: reliance ultimately grounded in admitted evidence/source material under an explicit root-recognition governance act.
2. **AUTHORIZATION ROOT**: reliance ultimately grounded in explicit human authorization or valid bounded delegation derived from human authorization.

Every warrant-family instance must carry a traversable derivation path to at least one primitive root. No path means no governed warrant.

Warrant families/sources may include evidentiary, explicit authorization, formal, institutional/normative and canon warrant, subject to these rules:

- canon warrant derives through authorization;
- institutional/normative warrant requires authorization-root recognition of the institution's competence/jurisdiction plus the relevant institutional assertion;
- formal warrant establishes entailment under premises/definitions but does not establish empirical applicability of premises;
- deterministic computation is derivative, not a primitive root.

Source acceptance/root recognition is an authorization governance act distinct from later qualification for a use.

Storage location, database choice, Git merge, automation, AI origin, repeated use, model need and computation do not create primitive warrant.

## 13. Governance axes

Admission/disposition, adoption/reference, qualification, conflict and authorization remain independent governance axes and are not collapsed into one lifecycle.

Candidate admission/disposition states include `CANDIDATE`, `ADMITTED`, `HOLD`, `REJECTED`, `QUARANTINED`.

Reference/adoption is a governed role, not an epistemic mode. Adoption does not erase projection, scenario or simulation ancestry.

Qualification is a governed assessment against an identified contract/use, not an epistemic truth label.

## 14. Standing and qualification

### 14.1 Pre-qualification standing
Pre-qualification standing is evaluated from proposition semantics, scope/time/context, warrant, dependencies, authorization, conflict and uncertainty without using the qualification decision being sought.

### 14.2 Qualification
Qualification separately assesses an identified object/interface against an identified contract/use.

### 14.3 Effective standing for use
Effective standing for use may incorporate the qualification result.

A qualification decision may not depend on an effective-standing result that already depends on that same qualification decision. Phase 5 must require the dependency/qualification graph to be acyclic.

Standing is always evaluated for a declared consumer/use, applicable time/clock, world-context and perspective. A request declaring none receives no governed standing.

## 15. Standing composition

Minimum composition rules:

- necessary dependencies compose conjunctively;
- scope, applicable time and permitted use intersect and never widen by composition;
- required UNKNOWN dimensions block unless an authorized bridge creates a dependent substitute;
- unresolved conflict propagates; indeterminate conflict propagates as indeterminate unless a governed rule permits otherwise;
- uncertainty propagates according to the transformation; uncharacterized uncertainty cannot silently become zero or characterized;
- warrant preserves root paths/families and never collapses into scalar confidence;
- qualification and authorization do not automatically propagate from dependencies to outputs;
- the transformation/model is a necessary dependency;
- alternative supports are not automatically combined, best-picked or worst-picked; aggregation/resolution requires an explicit governed D0.9 rule;
- evidence profile is determined from traversable lineage, not merely the final mode field.

## 16. Semantic legality

Combinations of epistemic mode, warrant path and derivation must be legal for the requested use.

An empirical/evidence-plane result cannot be supported solely by an authorization-root scenario stipulation unless represented as a bridge-dependent non-evidence claim.

The legality matrix is represented in Phase 3 and enforced in Phase 4.

## 17. Authorization and delegation

Authorization must distinguish authorization of:

- propositions/stipulations;
- models/transformations;
- governance/adoption acts;
- world/agent actions.

Human authorization is the root unless a bounded delegation has been explicitly established. Delegation is scoped, versioned and non-self-expanding.

Outcome-conditioned or post-hoc authorization creates new lineage and cannot retroactively validate outputs used to select the authorization.

A bridge rule may be prospectively authorized for a bounded class. Each application records rule/version, trigger, inputs, output and scope.

## 18. Bridges

An authorized bridge never mutates the blocked, unknown or conflicted source proposition.

It creates a distinct lineage-bearing dependent claim/state for the authorized use. Bridge context is part of the dependent's identity/lineage. Original assertions remain unchanged.

## 19. Conflict

Conflict evaluation has at least:

- `NO_CONFLICT`
- `CONFLICT`
- `INDETERMINATE_CONFLICT`

Conflict requires:

1. compatible normalized subject/predicate;
2. overlapping applicable scope, world-context, time and semantic role;
3. asserted contents purporting to answer the same question;
4. incompatibility after considering characterized uncertainty.

Where available uncertainty is insufficient to decide compatibility, the result is `INDETERMINATE_CONFLICT`, not silent no-conflict.

Alternative scenarios, perspectives or non-overlapping epochs are not conflicts merely because values differ. A consumer MUST NOT narrow query scope below the natural scope required by its declared governed use for the purpose or effect of evading otherwise applicable conflict evaluation. Phase 5 conflict detection MUST evaluate relevant `ALL_RECORDED` assertions over the broadest intersection of the declared use scope and their applicable scopes before admission/use filtering, then separately determine which assertions are admissible for consumption. Exact detection belongs to Phase 5.

## 20. Uncertainty and variability

Preserve separately where applicable:

- empirical/epistemic uncertainty;
- projection uncertainty;
- model/parameter uncertainty;
- observation/measurement uncertainty;
- agent-belief uncertainty;
- simulation stochastic variability;
- scenario/universe variability;
- uncharacterized uncertainty.

A transformation states how relevant uncertainty propagates or declares output uncertainty uncharacterized. Uncharacterized uncertainty cannot be converted to zero or to characterized uncertainty merely by derivation, even when the transformation explicitly declares such a conversion. Such conversion requires a separate explicit AUTHORIZATION-root governance act that recognizes an identified bounding/uncertainty model for the specified use and records its assumptions, scope and lineage. The resulting characterization is bridge/model-dependent and does not erase the original uncharacterized uncertainty.

Scenario alternatives have no probability merely by existing. Weighting scenarios or treating run frequencies as epistemic probabilities requires explicit authorization and an identified basis. Scenario-seed spread is simulation/scenario variability unless separately justified as an epistemic uncertainty model.

## 21. World/agent information firewall

A parameter used on both world and agent sides must be either:

1. a separate declared agent-side parameter with its own lineage; or
2. explicitly stipulated as information known to the agent.

Equality between world truth and agent-side priors, likelihoods, detection/false-positive rates, noise models, cost distributions or analogous parameters is itself a scenario assumption where material. Such a run discloses the corresponding perfect-information/perfect-calibration assumption.

World seeds and world random streams are world-side only and are not agent information.

An agent belief proposition states that the agent holds a belief. It does not make the believed proposition LOOM evidence or scenario truth.

## 22. Reference and realized state

REFERENCE is a governed adoption/use role, not an epistemic mode.

Reference adoption is use-scoped, including comparison, initialization and forcing where applicable. Reference and realized state remain permanently distinct.

A run may not be validated against a reference adopted from that same run or an undisclosed outcome-conditioned equivalent.

Simulation output may parent later simulated state while retaining SIMULATED ancestry. It does not become evidence by inheritance.

## 23. Time and staleness

Temporal fields identify their clock where ambiguous, including real-world time and simulation/run time. Knowledge time is tied to the applicable information domain/clock.

Staleness is a use-relative admissibility condition over temporal validity/age under a recorded rule. A stale assertion remains an assertion and is not converted to UNKNOWN.

## 24. Physical, formal and computational standing

Distinguish:

- measured physical quantities;
- accepted constants and empirical parameters;
- defined-by-convention constants/units;
- mathematical identities/formal relationships;
- fitted physical models;
- deterministic evaluations;
- engineering approximations;
- future extrapolated physical states;
- retrodictions;
- scenario state;
- simulated state.

Formal correctness establishes entailment under premises. Computational correctness establishes that declared computation followed its inputs/rules. Neither alone establishes that empirical premises describe reality.

## 25. Qualification boundary

Qualification is not an epistemic class and not a universal truth label.

A later qualification framework must identify at least:

- object/interface being qualified;
- governing contract/version;
- intended use/scope;
- requirements;
- authorizer/reviewer;
- evidence and limitations;
- coverage;
- replay/audit status.

Exact qualification mechanics belong to Phase 5.

## 26. Phase-boundary ownership

**Phase 3 State Model:** representation of assertion sets, world-context, perspective, legality matrix, clocks, bridge identity and worked encodings as test seeds.

**Phase 4 Runtime Boundary:** enforcement of perspective and admissibility, declared-use consumption, world-side seeds/random streams and no-standing-on-undeclared-consumption.

**Phase 5 Qualification:** acyclic dependency/qualification graph, conflict detection with uncertainty, failing mutation tests, circular-validation checks and mechanical NULL/default audit.

**Qualified-input work:** current Earth lineage and pooled-median bridge, staleness application, delegation-registry classification and producer-consumer graph.

**Independent review:** changed Phase 2 areas and the carried four-domain independence lien where required.

## 27. Carried liens

The following remain open and are not resolved by ontology alone:

- current Earth version lineage and whether historical pooled-median imputation survives in the promoted reference;
- mechanical NULL/default audit;
- concrete parameter authorization and fit/validation lineage;
- AI provenance where material;
- concrete human approval records;
- delegation-registry classification;
- producer-consumer graph;
- reproducibility of negative-search procedures;
- independent confirmation of findings requiring independence.

## 28. Worked encoding A — Earth imputation bridge

Historical empirical observations remain REAL/GOVERNANCE empirical assertions with their actual temporal scope. If a required current value is absent in the declared assertion set, the empirical question may be UNKNOWN and dependent use BLOCKED.

An authorized pooled-imputation bridge creates a distinct dependent with `IMPUTED_OR_SUBSTITUTED` lineage and authorization-root path. If adopted as a reference-model input, it remains bridge-derived and is usable only within adoption/bridge scope.

Required behavior:

- empirical-observation query returns historical observations, never the imputed value as observation;
- current empirical query returns UNKNOWN/BLOCKED according to assertion set and admissibility rule;
- authorized reference-input query may return the bridge dependent with lineage;
- bridge output is never described as recovered observation.

Whether the historical pooled-median bridge survives in current promoted Earth is an open qualified-input question.

## 29. Worked encoding B — Solar UNKNOWN, hidden deposit, observation, belief

A bounded M4-B empirical resource-quantity question may be UNKNOWN in `REAL/GOVERNANCE`.

A planted deposit may exist in `SCENARIO(S17)/WORLD_SIM` under authorization-root scenario lineage. It does not repair the REAL empirical UNKNOWN.

A simulated prospecting observation may enter `AGENT(A12)` through the declared observation channel. A12 may update a belief using agent-side priors/likelihoods. The belief proposition asserts A12's belief, not the hidden deposit as LOOM fact.

Extraction produces `REALIZED(R17)` simulated state and does not alter the REAL evidence plane.

Required behavior:

- REAL empirical query excludes S17 hidden truth;
- A12 before observation cannot access hidden truth or world seed;
- A12 after observation receives only permitted observation/belief state;
- shared world/agent model equality requires separate representation or explicit knowledge stipulation;
- extraction changes REALIZED(R17), never REAL evidence.

## 30. Worked encoding C — projection reference and realized run

A future BAU economic trajectory may be a `PROJECTION` in `REAL/GOVERNANCE` and simultaneously carry an `ADOPTED_REFERENCE` role for a declared comparison/initialization use.

A scenario forcing remains `SCENARIO_STIPULATION` in its scenario context. A realized trajectory remains `SIMULATED` in `REALIZED(run_id)`.

A comparison may consume reference and realized states only through an explicit cross-context comparison operation. It mutates neither parent.

Required behavior:

- reference query returns the adopted projection while preserving PROJECTION ancestry;
- realized-state query returns the run state, not the reference;
- comparison is explicit and lineage-bearing;
- a run cannot validate itself against a reference adopted from that same run or an outcome-conditioned equivalent.

## 31. Phase 2 invariants

1. Need never creates authority.
2. Storage never creates authority.
3. Computation never creates empirical truth.
4. Scenario truth never repairs empirical UNKNOWN.
5. Agent belief never becomes LOOM endorsement of the belief-object.
6. Reference adoption never erases epistemic ancestry.
7. Simulation never becomes evidence by inheritance.
8. UNKNOWN never silently becomes zero, absence, empty or not-applicable.
9. Permission never creates information availability.
10. World truth never leaks to an agent except through explicit information/observation lineage.
11. Bridge outputs are new dependents, not rewrites.
12. No warrant exists without a path to a primitive root.
13. No governed standing exists without declared consumption context.
14. Conflict is not inferred merely from differing worlds, perspectives or times.
15. Scenario frequencies are not epistemic probabilities without explicit authorization and basis.
16. Qualification cannot recursively establish the standing it consumes.
17. Transformation/model standing is a necessary dependency of derived results.
18. Governance/admissibility exclusion cannot be represented as epistemic UNKNOWN when relevant recorded assertions exist.
19. Query-scope narrowing cannot be used to evade conflict evaluation for the natural scope of the declared governed use.

## 32. Phase 2 status

Owner decisions D2.1-D2.10, including the adopted amendments to D2.3, D2.4, D2.6, D2.8 and D2.9, are consolidated here.

The model remains **PRE-CONTRACT / SINGLE-AUTHORITY**. It does not qualify existing LOOM holdings and does not release `LOOM_AUTHORITY_AND_STATE_CONTRACT_v1`.

Phase 2 is **NOT CLOSED** until the changed areas receive the required independent hostile review and review findings are dispositioned. Final closure must explicitly preserve PRE-CONTRACT/SINGLE-AUTHORITY limits and carried liens.


## 33. Independent Hostile Review Disposition

**Reviewer independence statement:** the reviewer declared no prior involvement in authoring or materially shaping Phase 0, Phase 1, the Phase 2 development record, the offworld stress proposal, or the hostile reviews that produced Repair Package A.

**Review verdict:** REPAIR REQUIRED.

The reviewer identified three findings. No finding reopens an owner ontology decision.

### 33.1 FND-PH2-001 — ACCEPTED AND REPAIRED

The empty-`ADMITTED` ambiguity is closed in §6. When relevant `ALL_RECORDED` assertions exist but the evaluated set is empty because governance/admissibility/disposition excluded them, the result is `BLOCKED`, never `UNKNOWN`. Restricted-set evaluation must inspect `ALL_RECORDED` sufficiently to distinguish epistemic absence from governance exclusion.

### 33.2 FND-PH2-002 — ACCEPTED AND REPAIRED

The uncertainty rule in §20 is strengthened. Explicit declaration by a deterministic transformation cannot convert uncharacterized uncertainty to zero or characterized uncertainty. Such characterization requires a separate AUTHORIZATION-root governance act recognizing an identified bounding/uncertainty model. The original uncharacterized uncertainty remains in lineage.

### 33.3 FND-PH2-003 — ACCEPTED AND REPAIRED / ENFORCEMENT CARRIED TO PHASE 5

The conflict rule in §19 and invariant set in §31 now prohibit query-scope narrowing that evades conflict evaluation for the natural scope of the declared governed use. Phase 5 owns executable detection and must evaluate relevant `ALL_RECORDED` assertions over the broadest intersection of declared use scope and applicable assertion scopes before admission/use filtering.

### 33.4 Worked-encoding ambiguities

The review also identified two encoding clarifications that do not alter the adopted ontology:

- A simulated observation and resulting agent-belief state retain their full derivation lineage, including scenario/simulation dependencies and applicable authorization-root paths. Authorization does not replace SIMULATED ancestry.
- A cross-context comparison output is a derived proposition whose epistemic mode is determined by what the proposition asserts and its context; `DERIVED` remains a derivation mode, never an epistemic mode. A deterministic comparison does not automatically become `NORMATIVE` or `FORMAL`.

These clarifications are binding Phase 2 semantics and must be represented consistently in Phase 3.

### 33.5 Review disposition

All three independent-review findings are accepted. FND-PH2-001 and FND-PH2-002 are repaired at the Phase 2 semantic level. FND-PH2-003 is repaired at the Phase 2 invariant level with executable conflict detection correctly carried to Phase 5.

The review's stated condition is therefore met at the conceptual-model level: Phase 2 may close after disposition of these findings, while preserving PRE-CONTRACT / SINGLE-AUTHORITY limitations and all carried liens.
