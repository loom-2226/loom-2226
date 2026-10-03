# LOOM AUTHORITY AND STATE CONTRACT v1
## Phase 2 — Claim and Authority Model

**Document:** `03_PHASE2_CLAIM_AUTHORITY_MODEL.md`  
**Status:** PRE-CONTRACT / PHASE 2 IN PROGRESS / SINGLE-AUTHORITY  
**Date opened:** 2026-10-03  
**Owner:** @kT  
**Authority basis:** Phase 0 D0.1–D0.20; closed Phase 1 archaeology; Phase 1 review addendum and D0.20 Option B  
**Purpose:** Define the conceptual model by which LOOM identifies claims, represents their epistemic standing, records warrant and authorization, propagates dependency limitations, and distinguishes unknown, conflict, reference, projection, scenario and simulation.  
**Non-purpose:** This document does not select a database schema, qualify existing holdings, define the full state model, define the runtime snapshot format, or adopt historical CIVPROP architecture.

## 1. Phase 2 entry condition

Phase 2 is authorized to proceed under `PRE-CONTRACT / SINGLE-AUTHORITY`.

This permits candidate ontology and governance design. It does not satisfy any future requirement for independent authorization and does not grant v1 qualification to any existing holding.

The Phase 1 review liens are inputs to this phase, not optional cleanup.

## 2. Design constraints inherited from Phase 0

The Claim and Authority Model must preserve these already-decided principles:

1. authority ultimately attaches to claims;
2. storage, computation, automation, AI origin and repeated use do not create authority;
3. unknown remains distinct from zero, false, empty, absence and omission;
4. unknown blocks dependent use unless an explicitly authorized bridge applies;
5. computed standing cannot silently exceed the standing and scope of necessary dependencies;
6. simulation does not become evidence by inheritance;
7. projection and scenario assumption are distinct;
8. conflicts remain visible unless an authorized resolution rule applies;
9. reference and realized state remain distinguishable;
10. known uncertainty survives transformation and uncharacterized uncertainty is not zero uncertainty;
11. qualification is scoped, graduated and versioned;
12. human authorization is the root of governance acts unless a later approved delegation mechanism applies;
13. authorization, provenance, authority, qualification, standing and truth are distinct concepts;
14. replay and causal audit are distinct;
15. governed status requires epistemic, reproducibility/audit and causal integrity;
16. authority-root types remain extensible pending Phase 2 adjudication.

## 3. Phase 1 evidence constraints

Phase 2 must be capable of representing at least the following archaeological realities:

- empirical/source claims;
- derived claims;
- future projections;
- scenario assumptions;
- model parameters, including fitted, inherited, synthetic and uncalibrated parameters;
- explicit unknowns with bounded search scope;
- stale observations distinct from missing observations;
- candidate and historically promoted claims;
- conflicting claims;
- uncertainty and uncharacterized uncertainty;
- simulated state and simulation events;
- reference trajectories;
- physical/mathematical calculations;
- identity and crosswalk assertions;
- institutional/canon/governance assertions;
- human authorization records;
- bounded delegated technical-agent authority;
- qualification and promotion records;
- transformations and compiled interfaces;
- claims with unknown temporal extent or unknown knowledge time.

The model must not assume that every current holding already exposes all required metadata.

## 4. Core conceptual separation

Phase 2 begins from a five-part separation:

### 4.1 Claim

A **Claim** is an identifiable assertion about a subject within some scope.

A claim is not defined by its storage representation. One claim may occupy a row, cell, JSON object, document statement or derived result. One artifact may contain many claims.

A claim has content. Its warrant and governance are represented separately.

### 4.2 Provenance

**Provenance** records origin and transformation history.

It answers questions such as:

- where did this assertion come from?
- what source artifact or prior claim supplied it?
- what transformation produced it?
- which code/model/version participated?
- when was the relevant source or transformation available?

Provenance does not by itself authorize use.

### 4.3 Epistemic character

**Epistemic character** describes what kind of assertion the claim is and what relationship it purports to have to reality or a stipulated world.

It must not be inferred from storage location or source prestige.

The final taxonomy is not yet adopted. Candidate classes are developed in §7.

### 4.4 Authority / warrant

**Authority** is the warrant under which LOOM may rely on a claim for a specified scope and use.

Authority is relational rather than an intrinsic quality score:

`AUTHORITY = warrant to rely on CLAIM for USE within SCOPE under GOVERNANCE`

A claim may therefore be usable for one purpose and unusable for another without contradiction.

### 4.5 Standing

**Standing** is the effective governed condition of a claim for a particular use after considering epistemic character, warrant, scope, temporal extent, knowledge time, uncertainty, dependencies, qualification, conflicts, limitations and applicable authorization.

Standing is not reducible to a single ordinal confidence score.

## 5. Claim identity

A claim must be distinguishable from another claim when a material difference exists in any of the following:

- subject;
- predicate/quantity;
- asserted value or state;
- applicable spatial/entity scope;
- applicable temporal scope;
- scenario/reference context where semantically necessary.

Two identical numeric values can therefore represent different claims if their subject, scope or scenario differs.

A new source asserting the same proposition does not automatically create a new proposition, but it creates distinct provenance/evidentiary support that must remain representable.

The eventual identity/key implementation is deferred.

## 6. Scope model

Scope is not optional decoration. It constrains what a claim says.

Candidate scope dimensions, included where applicable, are:

- **entity scope** — the object, actor, institution, body, country, facility or other subject;
- **spatial scope** — global, national, regional, local, sampled site, sampled material, etc.;
- **temporal validity scope** — when the asserted condition applies;
- **knowledge-time scope** — when LOOM/source could legitimately know the information;
- **scenario/reference scope** — which stipulated/reference world the assertion belongs to;
- **population/cohort scope** — where a claim concerns a subset;
- **measurement/sample scope** — what was actually measured or sampled;
- **intended-use scope** — uses for which authority/qualification applies.

Unknown scope is not widened by convenience.

### 6.1 Unknown time

Temporal validity and knowledge time may themselves be unknown.

Missing date metadata does not imply timeless validity, current validity, start-of-simulation knowledge, or permission to back-propagate the claim.

### 6.2 Search scope for unknowns

An unknown produced by investigation must preserve the scope of that investigation.

At minimum, LOOM must be able to distinguish:

- no search/assessment established;
- bounded search/assessment performed;
- defined source/endpoint searched but relevant evidence not located;
- evidence exists but is quarantined/unusable;
- question is not applicable.

The exact vocabulary remains a Phase 2 decision.

`UNKNOWN_AFTER_SEARCH` without its search scope is insufficient standing information.

## 7. Candidate epistemic taxonomy

This section is a candidate model, not yet an owner-adopted Phase 2 decision.

### 7.1 OBSERVATION

An assertion grounded in an observation, measurement, record or report purporting to describe an empirical state.

Observation does not imply correctness, precision, completeness, current validity or universal scope.

### 7.2 DERIVED

An assertion computed or logically derived from other claims through an identified transformation.

Its standing depends on both the transformation and necessary inputs.

A derived claim does not become observational merely because all inputs are observations.

### 7.3 PROJECTION

An evidence/model-derived estimate of an unknown future state.

This definition is inherited from D0.7.

A future ephemeris state generated from a fitted ephemeris solution is therefore a candidate example of projection rather than automatically a physical-law fact.

### 7.4 SCENARIO_ASSUMPTION

A condition explicitly stipulated as true within a scenario without claiming to be an empirical forecast.

This definition is inherited from D0.7.

### 7.5 MODEL_PARAMETER

A value governing model behavior rather than directly asserting an empirical state of the modeled world.

Parameter substanding may need to distinguish sourced, fitted, calibrated, inherited, authored, synthetic/test, and uncalibrated values. Whether these are subclasses or metadata is undecided.

### 7.6 SIMULATED

A state/event/result produced by simulation.

Simulated state may parent later simulated state but does not become evidence through inheritance.

### 7.7 UNKNOWN

An explicit representation that LOOM lacks an authorized asserted value/state for the relevant question and scope.

UNKNOWN is not a weak observation and is not a numeric value.

Unknown reason/search state is represented separately from the fact of unknownness.

### 7.8 Candidate additional classes

Phase 1 exposes material that may not fit cleanly into the seven classes above:

- normative/institutional rule;
- identity assertion;
- canon declaration;
- mathematical/physical relationship;
- verified deterministic computation;
- reference/adopted baseline.

Phase 2 must decide whether these are epistemic classes, authority-root/warrant types, contextual roles, or combinations. They are not promoted to classes merely because archaeology found them.

## 8. Claim condition dimensions that must not be collapsed into epistemic class

The following are orthogonal or potentially orthogonal to epistemic class and should not be encoded by proliferating class labels unless later evidence requires it:

- candidate vs promoted/adopted;
- qualified vs unqualified;
- current vs stale;
- known vs conflicted;
- uncertainty characterized vs uncharacterized;
- source accepted vs quarantined;
- direct vs inherited metadata;
- human-authored vs AI-assisted vs automated;
- fitted/outcome-conditioned status;
- reference vs realized role;
- replay status;
- authorization status.

This prevents labels such as `QUALIFIED_OBSERVATION_PROMOTED_CURRENT` from becoming a substitute for an actual model.

## 9. Candidate authority-root question

D0.18 deliberately left authority roots extensible. Phase 1 found evidence requiring adjudication of at least:

1. **Evidentiary warrant** — reliance grounded in an empirical source/observation and its accepted provenance.
2. **Explicit human authorization** — governance authority for assumptions, parameters, classifications, qualification, promotion and resolution rules.
3. **Physical/mathematical relationship** — established law, mathematical identity or formal relationship used to derive a claim.
4. **Standard/institutional authority** — an external institution or standard is itself authoritative for the proposition at issue, such as an official identifier or legally effective rule.
5. **Canon authority** — an authorized fictional/worldbuilding declaration governing a stipulated LOOM scenario/world.
6. **Verified deterministic computation** — a computation whose warrant may derive from accepted inputs plus an accepted transformation rather than from a new empirical source.

These are **candidates**. Phase 2 must test whether items 3–6 are genuine authority roots or instead derive their authority from other roots plus transformations/authorization.

No root may be created merely because a model needs a value.

## 10. Dependency model

A claim may depend on:

- source claims;
- prior simulated state;
- parameters;
- scenario assumptions;
- transformations;
- physical/mathematical relationships;
- identity/crosswalk claims;
- authorization decisions;
- conflict-resolution rules.

Necessary dependencies must remain traversable.

### 10.1 Computed standing

For a dependent claim:

- scope cannot silently widen beyond necessary dependencies;
- permitted use cannot silently widen;
- unknown necessary input blocks unless an authorized bridge applies;
- conflict cannot silently resolve;
- uncertainty cannot silently disappear;
- simulation ancestry remains visible;
- a fitted/outcome-conditioned dependency remains visible;
- qualification does not propagate merely because a parent is qualified.

The phrase "weakest input wins" is insufficient where dimensions are non-ordinal. Standing must compose dimension by dimension.

## 11. Authorized bridges

An **authorized bridge** is a governed decision/rule that permits an operation to proceed where ordinary dependency semantics would block or where one epistemic role is intentionally substituted for another.

Examples may include:

- an authorized imputation for missing empirical input;
- a scenario assumption replacing an unknown for a named scenario;
- an adopted projection used as a reference trajectory;
- a governed conflict-resolution rule;
- a qualified crosswalk resolving identity between systems.

A bridge must preserve:

- what condition it bridges;
- authorizer and authorization basis;
- scope and intended use;
- effective version/time;
- replacement/substitution method;
- resulting limitations;
- provenance to the original blocked/unknown/conflicting condition.

A bridge does not rewrite the original claim.

## 12. Conflict model

Conflict exists when claims that purport to apply to the same relevant proposition/scope cannot simultaneously hold under their semantics.

Potentially different conditions include:

- two empirical observations disagreeing;
- an observation and projection disagreeing for overlapping time;
- two projections disagreeing;
- scenario assumption deliberately diverging from projection;
- identity mappings disagreeing;
- institutional authorities disagreeing or changing over time.

Phase 2 must define conflict detection and resolution semantics without treating all disagreement as the same phenomenon.

## 13. Uncertainty model

Uncertainty is not identical to epistemic class or confidence.

The model must preserve:

- characterized quantitative uncertainty where supplied;
- qualitative/source uncertainty where supplied;
- uncharacterized uncertainty as uncharacterized;
- projection uncertainty as conditional on model/input assumptions;
- simulation variability separately from epistemic uncertainty;
- scope uncertainty where relevant;
- uncertainty introduced by transformation.

No uncertainty field may default to zero merely because no estimate exists.

## 14. Authorization and delegation

Governance acts require human authorization unless an approved delegation rule explicitly permits otherwise.

An authorization must ultimately identify:

- human authority;
- date/time;
- subject/action authorized;
- scope and permitted use;
- relevant version/scenario;
- basis;
- whether authorization is prospective or post-hoc;
- independence status where required.

Delegation is bounded authority to perform specified governance actions under specified deterministic rules. It is not a transfer of epistemic judgment to an AI.

The existing WALTER registry/creation-review mechanism is Phase 2 evidence for bounded delegation but is not automatically adopted as the v1 mechanism.

## 15. Reference, adoption and simulation

`REFERENCE`, `REALIZED`, `SIMULATED`, `PROJECTION` and `SCENARIO_ASSUMPTION` answer different questions.

A reference is a role played by a versioned state/trajectory used for comparison or initialization. It is not necessarily an epistemic class.

A projection can be adopted as a reference while remaining a projection.

A scenario assumption can define a reference scenario while remaining a scenario assumption.

A simulated result can become an adopted reference only through an explicit governance event; adoption does not erase simulation ancestry.

This separation is a candidate Phase 2 principle to be tested before adoption.

## 16. Physical and mathematical standing problem

Phase 1 and its review establish that "physical authority" is too coarse.

Phase 2 must distinguish at least:

1. measured/source quantities;
2. accepted physical constants or empirical model parameters;
3. mathematical identities and formal relationships;
4. fitted physical solutions/models such as an ephemeris solution;
5. deterministic evaluation of such a model at an epoch;
6. future extrapolated state produced by that model;
7. engineering/transport calculations using physical inputs and additional assumptions.

A future state does not become an observation merely because the computation producing it is deterministic.

This section records the problem; it does not yet adjudicate root authority.

## 17. Qualification boundary

Qualification is not an epistemic class and not an intrinsic truth label.

Phase 2's claim model must make it possible for later qualification machinery to state:

- what claim/collection/interface/process was qualified;
- under which contract/version;
- for which use and scope;
- against which requirements;
- by whom;
- with what evidence;
- with what limitations and coverage;
- with what replay/audit status.

The qualification framework itself belongs to a later phase.

## 18. Phase 2 decision register

No Phase 2 design decision is treated as owner-adopted merely because it appears in this working document.

### D2.1 — Core decomposition
**Status:** CANDIDATE  
Question: Should v1 adopt the separation `Claim / Provenance / Epistemic Character / Authority-Warrant / Standing`, with qualification and authorization represented as governance relationships/events rather than properties that redefine the claim?

### D2.2 — Epistemic taxonomy
**Status:** OPEN  
Question: Which of the candidate classes in §7 are first-class epistemic classes, and which concepts belong in orthogonal dimensions?

### D2.3 — Unknown semantics
**Status:** OPEN  
Question: What minimum unknown/search-state vocabulary is required, given the Phase 1 M4-B evidence and D0.3?

### D2.4 — Authority roots
**Status:** OPEN  
Question: Which candidate warrants in §9 are genuine roots, which are derivative, and what makes each legitimate?

### D2.5 — Reference role
**Status:** OPEN  
Question: Is REFERENCE a role/context rather than an epistemic class?

### D2.6 — Dependency standing
**Status:** OPEN  
Question: What exact dimension-by-dimension composition rules govern derived claims?

### D2.7 — Authorization/delegation
**Status:** OPEN  
Question: What governance acts require direct human authorization, which may be delegated, and what independence requirements apply?

### D2.8 — Conflict
**Status:** OPEN  
Question: What constitutes conflict across epistemic classes and contexts, and what resolution mechanisms are permitted?

### D2.9 — Uncertainty
**Status:** OPEN  
Question: What uncertainty dimensions are mandatory or optional, and how does unknown uncertainty propagate?

### D2.10 — Physical/mathematical standing
**Status:** OPEN  
Question: How should physical law, fitted models, deterministic computation and future extrapolation receive and propagate warrant?

## 19. Mechanical work before owner decisions

Before asking the owner to resolve D2.1–D2.10, Phase 2 should mechanically stress-test this candidate model against concrete archaeological exemplars:

1. M4-B supported material lane;
2. M4-B bounded unknown lane;
3. Earth pooled-median imputation;
4. Earth late-horizon projected state;
5. Moderate technology scenario milestone;
6. actor empirical capability/access claim;
7. actor unknown budget/access claim;
8. SPICE/ephemeris future state;
9. Lambert/transport derived result;
10. simulated CIVPROP state/event;
11. identity/crosswalk claim;
12. WALTER delegated-governance record.

The purpose is to expose missing dimensions and category errors before freezing vocabulary.

## 20. Phase 2 exit condition

Phase 2 may close only when:

- the claim/authority conceptual model is owner-adopted;
- authority roots are adjudicated;
- unknown/search-scope semantics are adopted;
- temporal/knowledge-time semantics are adopted;
- dependency standing rules are defined;
- authorization/delegation semantics are defined;
- conflict and uncertainty semantics are defined sufficiently for the later State Model and Runtime Boundary;
- Phase 1 review liens assigned to Phase 2 are resolved or explicitly carried forward;
- hostile review is completed with limitations recorded;
- SINGLE-AUTHORITY status is either accepted for closure under an explicit rule or replaced by the required independent mechanism.

Until then:

`PHASE 2: IN PROGRESS / PRE-CONTRACT / SINGLE-AUTHORITY`


## 21. D2.1 — Core Decomposition

**Status:** OWNER-ADOPTED  
**Decision date:** 2026-10-03  
**Authority status:** PRE-CONTRACT / SINGLE-AUTHORITY

Following mechanical stress testing against Phase 1 archaeological exemplars, the owner selected **Option A: dimensional claim model**.

LOOM v1 shall model a claim as an identifiable **proposition with scope/context**. The following remain separately representable rather than being collapsed into one universal epistemic-class label:

- provenance;
- epistemic mode;
- derivation mode;
- warrant;
- governance status/role;
- uncertainty;
- dependencies and lineage.

Effective **standing** is evaluated for a specified use, time and governing contract. It is not a universal scalar quality attached to the proposition.

Qualification and authorization remain governance acts/relationships. They do not redefine claim content merely by occurring.

### D2.1 mapping consequence

The initial Phase 2 candidate labels are provisionally remapped for subsequent design:

- `OBSERVATION` → epistemic mode;
- `PROJECTION` → epistemic mode;
- `SCENARIO_ASSUMPTION` → epistemic mode;
- `SIMULATED` → epistemic mode;
- `DERIVED` → derivation mode;
- `MODEL_PARAMETER` → proposition/functional role whose own epistemic and derivation metadata remain separately representable;
- `UNKNOWN` → explicit knowledge/value state whose reason and search/assessment scope remain separately representable.

This mapping does not by itself close D2.2. It constrains D2.2 by rejecting a single mutually-exclusive `epistemic_class` enum as the governing conceptual model.

### Claim content versus claim support

D2.1 also adopts the distinction:

`CLAIM CONTENT ≠ CLAIM SUPPORT`

Multiple source assertions may support, contradict, constrain or otherwise bear on one proposition. Evidence records, coverage statements and normalized propositions must remain conceptually distinguishable even where an implementation later chooses to colocate them.

### Non-decisions

D2.1 does not select:

- a database schema;
- serialization format;
- identifier/key design;
- final epistemic-mode vocabulary;
- final derivation-mode vocabulary;
- authority roots;
- qualification mechanics;
- conflict-resolution mechanics;
- uncertainty schema;
- runtime representation.

Those remain later Phase 2 or subsequent-phase decisions.

## 22. Next mechanical pass

With D2.1 adopted, the next Phase 2 task is to derive the minimum candidate vocabularies for:

1. proposition kind;
2. epistemic mode;
3. derivation mode;
4. knowledge/unknown state and search scope;
5. governance status/role.

That pass shall test whether each distinction changes standing or permitted use before asking the owner to adopt D2.2/D2.3 vocabulary.


## 23. Mechanical Vocabulary Pass — Minimum Dimensions

**Status:** MECHANICAL ANALYSIS / NO NEW OWNER DECISION

This pass tests the D2.1 dimensional model against current-main vocabulary already present in Solar, Earth, timeline, actor, simulation and governance holdings. Historical labels are evidence, not automatically adopted v1 vocabulary.

### 23.1 Proposition kind

A proposition kind answers **what is being asserted**, not why it is believed.

The minimum candidate kinds forced by current holdings are:

- **STATE_VALUE** — a value/state/property of an entity or system;
- **EVENT** — an occurrence or state transition;
- **IDENTITY** — an assertion that identifiers/entities correspond or do not correspond;
- **RELATIONSHIP** — a relation among entities not reducible to identity;
- **RULE_NORM** — a legal, institutional, governance, canon or other normative/stipulative rule;
- **PARAMETER** — a value used to govern model/process behavior;
- **MODEL_RELATION** — a mathematical/physical/model relationship used to transform inputs;
- **AUTHORIZATION** — a governance act permitting a defined action/use;
- **QUALIFICATION_ASSERTION** — an assertion about satisfaction of a governed qualification regime.

This list is deliberately semantic rather than storage-shaped. Coverage, source artifact, provenance record and evidence packet are not proposition kinds merely because tables exist for them.

**Pressure:** `AUTHORIZATION` and `QUALIFICATION_ASSERTION` may ultimately be modeled as governance events rather than ordinary claim kinds. They remain candidates until the State Model clarifies event semantics.

### 23.2 Epistemic mode

Epistemic mode answers **what relationship the proposition purports to have to reality or a stipulated world**.

Minimum candidate modes:

- **EMPIRICAL** — purports to report/represent an observed or recorded empirical state/event;
- **PROJECTION** — estimates an unknown future state from evidence/model;
- **SCENARIO_STIPULATION** — declared true within a scenario without forecast claim;
- **SIMULATED** — produced within simulated realized state;
- **NORMATIVE** — purports to state an effective rule, authorization, standard, institutional act or canon stipulation rather than describe an empirical physical state;
- **FORMAL** — mathematical/logical/formal relationship whose warrant is not an observation of world state.

**Finding:** the earlier label `OBSERVATION` is too narrow as a top-level mode. Current Solar holdings distinguish direct sample, in-situ direct/remote, Earth remote, dynamical inference, physical model and theoretical expectation. These are better handled through derivation/evidence method while `EMPIRICAL` states the proposition's intended relationship to reality.

**Open pressure:** whether `NORMATIVE` and `FORMAL` are true epistemic modes or warrant/proposition dimensions remains unresolved. Do not adopt them yet.

### 23.3 Derivation/evidence mode

This dimension answers **how the asserted content was obtained**.

Current holdings force at least these candidate families:

- **DIRECT_REPORTED** — admitted directly from a source record/report;
- **DIRECT_SAMPLE**;
- **IN_SITU_DIRECT**;
- **IN_SITU_REMOTE**;
- **EARTH_REMOTE**;
- **INFERRED** — including dynamical/analog inference with subtype retained;
- **PHYSICAL_MODEL**;
- **THEORETICAL_EXPECTATION**;
- **DETERMINISTIC_DERIVATION**;
- **FITTED_OR_CALIBRATED**;
- **IMPUTED_OR_SUBSTITUTED**;
- **SIMULATED_TRANSITION**.

The exact vocabulary should not blindly copy Solar's historical `epistemic_class`; however, that schema proves that evidence/acquisition method matters independently of proposition mode.

A claim may have more than one derivation stage. Therefore derivation is likely lineage/transform history, not necessarily a single enum on the final claim.

### 23.4 Knowledge/value state

D0.3 and Phase 1 require a value-state dimension independent of epistemic mode.

Minimum candidate states:

- **ASSERTED** — an admitted value/proposition is present;
- **UNKNOWN** — no authorized asserted value is available for the question/scope;
- **NOT_APPLICABLE** — the question does not semantically apply;
- **QUARANTINED** — relevant material exists but is not admissible for the intended use pending resolution.

**Rejected as value states:** zero, false and empty. Those are possible asserted contents, not substitutes for UNKNOWN.

`SOURCE_NOT_FOUND`, `NOT_SEARCHED`, and `UNKNOWN_AFTER_SEARCH` are not proposed as peer value states. They describe investigation/search condition associated with UNKNOWN.

### 23.5 Investigation/search state

Minimum candidate search states for an UNKNOWN:

- **NOT_ASSESSED** — no governed search/assessment is established;
- **BOUNDED_ASSESSMENT_NO_ADMITTED_VALUE** — a recorded bounded scope was assessed and yielded no admissible value;
- **DEFINED_SOURCE_NOT_FOUND** — a named endpoint/archive/source expected by the search rule did not yield the relevant source/material;
- **EVIDENCE_FOUND_NOT_ADMITTED** — potentially relevant evidence was found but held/rejected/quarantined;
- **SEARCH_STATE_UNKNOWN** — historical holding is UNKNOWN but the search condition itself is not established.

Every non-`NOT_ASSESSED` search state requires a reference to its recorded search scope. This directly incorporates the Phase 1 R-01 lien.

**Important:** this vocabulary does not create a `CONFIRMED_ABSENT` state. Confirmed absence would be an asserted negative proposition with its own evidence and scope, not a flavor of UNKNOWN.

### 23.6 Governance status and role

Current holdings show that several governance concepts are independent and must not become one status enum.

Candidate axes:

**Admission/disposition**
- CANDIDATE
- ADMITTED
- HOLD
- REJECTED
- QUARANTINED

**Adoption/reference role**
- NOT_ADOPTED
- ADOPTED_REFERENCE
- GOVERNING_SCENARIO
- GOVERNING_CANON

**Qualification**
- NOT_EVALUATED
- QUALIFIED
- QUALIFIED_WITH_LIMITATIONS
- NOT_QUALIFIED

**Conflict**
- UNCONFLICTED_OR_NOT_ASSESSED
- CONFLICTED
- RESOLVED_BY_AUTHORIZED_RULE

**Authorization**
- NOT_REQUIRED
- REQUIRED_NOT_AUTHORIZED
- AUTHORIZED
- DELEGATED_AUTHORIZED
- POST_HOC_AUTHORIZED

These are candidate conceptual axes, not final tokens. Historical `PROMOTE`, `preferred_fact`, `GOVERNING_CANON`, `AUTHOR_SCENARIO_MODERATE` and qualification labels demonstrate why one status field would be lossy.

### 23.7 Temporal condition

The vocabulary pass confirms that time must be dimensional:

- validity interval may be known, bounded, open-ended or UNKNOWN;
- knowledge time may be known or UNKNOWN;
- source publication/acquisition time is provenance and is not automatically validity time;
- future validity does not itself distinguish PROJECTION from SCENARIO_STIPULATION.

### 23.8 Stress-test conclusion

No archaeological exemplar found in this pass requires returning to a single `epistemic_class`.

The smallest model that preserves current distinctions is:

`PROPOSITION KIND`
+ `EPISTEMIC MODE`
+ `VALUE/KNOWLEDGE STATE`
+ `DERIVATION LINEAGE`
+ `SCOPE/TIME`
+ `WARRANT`
+ independent `GOVERNANCE AXES`
+ `UNCERTAINTY`
+ `SUPPORT/CONFLICT RELATIONS`.

The pass also produces three constraints for the next owner decision:

1. UNKNOWN is not an epistemic mode in the same sense as EMPIRICAL/PROJECTION/SIMULATED; it is a knowledge/value state.
2. DERIVED is not an epistemic mode; derivation may be multi-stage lineage.
3. MODEL_PARAMETER is primarily proposition/functional role, not a statement about whether its value is observed, fitted, authored, projected or synthetic.

## 24. D2.2 — Dimensional vocabulary architecture

**Status:** READY FOR OWNER DECISION

**Option A — Adopt the dimensional vocabulary architecture.**

Adopt the category separation in §23 as the governing Phase 2 architecture, while keeping the individual token lists candidate until each is stress-tested further. In particular:

- proposition kind, epistemic mode, knowledge/value state, derivation lineage and governance axes are distinct;
- UNKNOWN is a knowledge/value state;
- DERIVED belongs to derivation lineage;
- MODEL_PARAMETER is a proposition/functional role;
- governance status is multi-axis rather than a single lifecycle enum.

This decides the architecture of the vocabulary without prematurely freezing every label.

**Option B — Collapse selected dimensions before proceeding.**

Require Phase 2 to combine two or more of the above dimensions into a smaller taxonomy before continuing.

**Mechanical recommendation:** Option A. The current holdings already demonstrate independent variation among these dimensions; collapsing them now would recreate the compound-label problem rejected by D2.1.


## 25. D2.2 — Dimensional Vocabulary Architecture

**Status:** OWNER-ADOPTED
**Decision date:** 2026-10-04
**Authority status:** PRE-CONTRACT / SINGLE-AUTHORITY

The owner selected Option A.

LOOM v1 shall keep these conceptually distinct: proposition kind; epistemic mode; knowledge/value state; derivation lineage; scope and temporal context; warrant; governance status/role axes; uncertainty; and support/contradiction/conflict relationships.

This decides vocabulary architecture, not the final controlled tokens.

Consequences:

- UNKNOWN is a knowledge/value state, not a peer epistemic mode.
- DERIVED belongs to derivation lineage.
- MODEL_PARAMETER is principally a proposition/functional role; how its value was obtained and warranted remains separately represented.
- admission/disposition, adoption/reference role, qualification, conflict and authorization shall not be collapsed into one universal status lifecycle.
- implementations may colocate dimensions only where semantic round-trip preserves these distinctions.

The exact controlled vocabularies remain candidate.

## 26. Next Phase 2 task

The next mechanical pass addresses D2.3, minimum UNKNOWN semantics, including unsearched questions, bounded unsuccessful searches, missing named sources, unadmitted evidence, unknown time, evidenced absence, asserted zero/false/empty, stale values, conflict and not-applicable questions. UNKNOWN must not become a miscellaneous bucket for those distinct conditions.


## 27. Mechanical UNKNOWN Semantics Pass

**Status:** MECHANICAL ANALYSIS / NO NEW OWNER DECISION

D2.3 was tested against current-main Solar, Earth, timeline and CIVPROP holdings.

### Core finding

UNKNOWN means: **for the specified proposition/question and scope, LOOM does not have an admissible asserted value available for the intended use.**

UNKNOWN does not mean false, zero, empty, absent, stale, contradicted, rejected, not applicable or not yet selected. The reason an admissible value is unavailable is separately represented.

### Tested distinctions

- No search established: UNKNOWN with NOT_ASSESSED.
- Bounded search with no admissible value: UNKNOWN with BOUNDED_ASSESSMENT_NO_ADMITTED_VALUE and recorded scope.
- Defined source/endpoint yields no relevant source: UNKNOWN with DEFINED_SOURCE_NOT_FOUND and recorded source/search scope.
- Relevant evidence exists but is held/rejected/quarantined: UNKNOWN for the intended use with EVIDENCE_FOUND_NOT_ADMITTED and links to that evidence/disposition.
- Missing temporal metadata: the value may remain asserted while the temporal dimension is UNKNOWN. This does not automatically make the whole proposition UNKNOWN.
- Supported non-detection or absence: an asserted negative/bounded proposition with evidence, not UNKNOWN.
- Numeric zero and boolean false: asserted values, not UNKNOWN.
- Empty collection: asserted empty only when domain semantics establish completeness; otherwise it cannot silently mean none exist.
- Stale/superseded value: preserve the historical assertion and mark its temporal/governance condition; do not erase it into UNKNOWN.
- Conflicting values: preserve the assertions and conflict relationship; conflict is not UNKNOWN.
- Semantically inapplicable question: NOT_APPLICABLE, not UNKNOWN.
- Source does not cover the relevant class: a source/coverage limitation, not by itself scientific absence.

M4-B explicitly states that UNKNOWN_AFTER_SEARCH is absence of sufficient admitted evidence after a bounded campaign, not zero or material absence. It separately defines SOURCE_NOT_FOUND for a defined endpoint/archive. Existing resource vocabulary also separates supported non-detection/absence.

Solar holdings separately preserve NOT_APPLICABLE, contradictory/superseding relationships and temporal metadata. Earth temporal coverage separately records SUPERSEDED_SEMANTIC and NOT_MODELED_BY_THIS_AUTHORITY. These distinctions would be lost by broad UNKNOWN coercion.

### Partial unknowns

Unknownness attaches to the dimension actually unknown. Examples include: presence known but abundance unknown; value known but validity end unknown; scoped service access known but generic access unknown; quantity known but uncertainty characterization unknown.

A known adjacent dimension cannot fill an unknown one.

### Minimum candidate search states

1. NOT_ASSESSED
2. BOUNDED_ASSESSMENT_NO_ADMITTED_VALUE
3. DEFINED_SOURCE_NOT_FOUND
4. EVIDENCE_FOUND_NOT_ADMITTED
5. SEARCH_STATE_UNKNOWN

States 2 through 4 require references to the assessment/search/evidence scope. State 5 covers historical holdings where the reason for UNKNOWN cannot itself be established. Token names remain candidate.

### Blocking

UNKNOWN blocks an operation only when that operation requires the unknown dimension. An authorized substitution may bridge it only through governed substitution/assumption machinery. The substitute never becomes a recovered observation and the original UNKNOWN remains in lineage.

## 28. D2.3 — UNKNOWN Semantics

**Status:** READY FOR OWNER DECISION

**Option A:** adopt the scoped UNKNOWN semantics in §27.

**Option B:** permit stale, conflicted, temporally incomplete or otherwise unusable values to collapse into a broader UNKNOWN state for consumers.

**Mechanical recommendation:** Option A. Current holdings already preserve the distinctions that Option B would destroy, and A is consistent with Phase 0 local-blocking, claim-scope, conflict and uncertainty rules.


## 29. Owner Disposition — D2.3 through D2.10

**Status:** OWNER-ADOPTED
**Decision date:** 2026-10-04
**Authority status:** PRE-CONTRACT / SINGLE-AUTHORITY

The owner adopted the remaining Phase 2 choice slate as an integrated package. The offworld capital/resource/colony/agent proposal remains mutable, non-canon and non-implementing; it is a stress case and gains no authority through this adoption.

- **D2.3 Scoped UNKNOWN:** adopt Option A. UNKNOWN is scoped and dimension-local. Its search/reason state is separate. Scenario state cannot silently satisfy evidence-plane UNKNOWN.
- **D2.4 Warrant roots:** adopt plural, use-relative warrant. Candidate root families are evidentiary warrant, explicit authorization, formal warrant, institutional/normative warrant and canon warrant. Deterministic computation is derivative rather than an independent truth root. Storage, AI, automation, repetition and model need are not roots.
- **D2.5 Reference:** REFERENCE is a governed adoption/use role, not an epistemic mode. Adoption does not erase projection, scenario or simulation ancestry. Reference and realized state remain distinct.
- **D2.6 Dependency standing and admissibility:** standing is evaluated for consumer, intended use, time and context and composes across relevant dimensions. Epistemic perspective/admissibility is explicit. Agent belief does not assert the believed proposition as LOOM fact.
- **D2.7 Authorization/delegation:** distinguish authorization of propositions/stipulations, models/transformations, governance/adoption acts and world/agent actions. Delegation is explicit, bounded and non-self-expanding. Outcome-conditioned changes create new lineage and do not retroactively validate outputs used to choose them.
- **D2.8 Conflict:** conflict requires proposition-level incompatibility after relevant scope/time/scenario/context alignment. Mere difference is not conflict. Resolution preserves provenance and displaced assertions.
- **D2.9 Uncertainty/variability:** preserve empirical/epistemic, projection, model/parameter, observation/measurement, agent-belief, simulation-stochastic, scenario/universe and uncharacterized uncertainty/variability as distinct concepts. Scenario-seed variation is not automatically epistemic uncertainty; generator distributions are not agent priors.
- **D2.10 Physical/formal/computational standing:** distinguish formal relationships, empirical physical quantities/laws, fitted models, engineering approximations, deterministic evaluations, future extrapolations, scenario state and simulated state. Correct computation establishes consequence from declared inputs/rules; it does not establish that those inputs describe reality.

### Integrated Phase 2 architecture

The adopted conceptual decomposition is:

PROPOSITION + KIND + EPISTEMIC MODE + VALUE/KNOWLEDGE STATE + DERIVATION LINEAGE + SCOPE/TIME/SCENARIO + EPISTEMIC PERSPECTIVE/ADMISSIBILITY + WARRANT + GOVERNANCE AXES + UNCERTAINTY/VARIABILITY + SUPPORT/CONFLICT + DEPENDENCIES.

Effective standing is use-relative, not a universal scalar attached to a row.

Authored hidden-scenario starting values may be scenario stipulations; values produced by an authorized generator are derived scenario-world state; later values changed by simulation transitions are realized simulated state. These categories must not be collapsed.

### Phase 2 status after this disposition

The owner-decision portion of Phase 2 is complete. Phase 2 is **not yet closed**. Remaining closure work is mechanical/review work: integrate the adopted model, map or carry Phase 1 liens, run the integrated archaeological and offworld adversarial stress tests, obtain hostile review, disposition findings, and record final owner closure including PRE-CONTRACT / SINGLE-AUTHORITY limitations.


## 30. Phase 1 Lien Mapping After Owner Decisions

**Status:** MECHANICAL DISPOSITION / NOT PHASE 2 CLOSURE

1. **Unknown search scope:** RESOLVED AT CONCEPTUAL-MODEL LEVEL by D2.3. Search/assessment state is separate and bounded-search states require scope. Implementation enforcement remains downstream.
2. **Unknown temporal extent/knowledge time:** RESOLVED AT CONCEPTUAL-MODEL LEVEL by D2.3 plus the dimensional time model. Missing time metadata remains unknown rather than inferred.
3. **Current Earth lineage / pooled-median bridge:** CARRIED TO QUALIFIED INPUTS. Phase 2 establishes how imputation/substitution is represented but does not establish whether that historical bridge survives in the current Earth reference.
4. **Mechanical NULL/default audit:** CARRIED TO QUALIFICATION / QUALIFIED INPUT COMPILATION. D2.3 supplies the semantics the audit must protect.
5. **Parameter authorization, producer-consumer, fit/validation, AI provenance, human approval:** PARTLY RESOLVED CONCEPTUALLY by D2.4, D2.6, D2.7 and D2.10; concrete holdings still require later qualification and lineage checks.
6. **Existing delegation instruments:** RESOLVED AT CLASSIFICATION LEVEL by D2.7. Existing WALTER material is evidence of bounded delegation but gains no v1 authority automatically.
7. **Physical/mathematical standing:** RESOLVED AT CONCEPTUAL-MODEL LEVEL by D2.10.
8. **Independent check of four-domain finding:** CARRIED AS INDEPENDENCE LIEN. It is not necessary to pretend the shorthand is independently disproven in order to use the richer model; any future claim requiring independent confirmation must obtain it.
9. **Reproducible negative searches:** CARRIED TO QUALIFICATION/ARCHAEOLOGY METHOD. Phase 2 requires search scope semantics; rerunnable mechanics belong to the later framework.

No carried lien is silently treated as resolved by ontology alone.


## 31. Integrated Adversarial Stress Test

**Status:** MECHANICAL PASS / NO NEW OWNER DECISION

The adopted D2.1-D2.10 model was re-tested against current-main archaeological exemplars and the mutable offworld proposal.

### Results

1. **M4-B supported material lane — PASS.** Evidence-bearing assertions remain empirical propositions with acquisition/derivation lineage and bounded scope. Coverage status does not become the proposition's epistemic mode.
2. **M4-B UNKNOWN_AFTER_SEARCH — PASS.** Current-main explicitly preserves 343 bounded unknown lanes, distinguishes supported non-detection/absence, SOURCE_NOT_FOUND and NOT_APPLICABLE, and states that unsupported lanes are not zero or scientific absence. D2.3 preserves these distinctions.
3. **Earth imputation exemplar — PASS WITH CARRIED LINEAGE LIEN.** An imputed value can be represented as a parameter/state proposition with IMPUTED_OR_SUBSTITUTED derivation and bridge lineage without becoming observation. Whether the historical pooled-median bridge survives in the current promoted reference remains downstream evidence work.
4. **Earth late-horizon projection/reference — PASS.** Projection and ADOPTED_REFERENCE can coexist without laundering projection into observation. Reference and realized scenario state remain separate.
5. **Moderate technology milestone — PASS.** Current-main marks the threshold authority as AUTHOR_SCENARIO_MODERATE and the period as MODERATE_SCENARIO_ANCHOR. D2.5 permits governing-scenario/reference roles without changing epistemic ancestry.
6. **Actor empirical capability/access — PASS.** Empirical access propositions can remain evidence-plane claims with actor/time/scope limitations and can be consumed only where standing permits.
7. **Actor unknown budget/access — PASS.** Unknown amount/access blocks only dependent actions; adjacent known actor attributes do not fill it.
8. **Future ephemeris/model state — PASS.** D2.10 distinguishes deterministic model evaluation from observation and from formal truth.
9. **Transport/engineering derivation — PASS.** A deterministic or engineering result inherits bounded standing from inputs/model and does not manufacture empirical warrant.
10. **CIVPROP simulated event/state — PASS.** Current-main CIVPROP0 explicitly labels events SIMULATION_EVENT. D2.1/D2.10 preserve simulated ancestry rather than promoting it to evidence.
11. **Identity/crosswalk — PASS.** Identity propositions and their match basis remain distinct from source evidence, admission and conflict/disposition.
12. **WALTER delegation — PASS WITH GOVERNANCE LIMIT.** Current-main identifies WALTER as a bounded autonomous assurance agent with an agent-creation review. D2.7 can classify this as delegation evidence without treating historical delegation as automatic v1 authorization.

### Offworld adversarial case

The model can represent simultaneously:

- empirical Solar UNKNOWN;
- a hidden scenario-world value for the same property;
- a simulated noisy observation generated from that hidden state;
- an agent-relative belief updated from the observation;
- an agent decision that may consume only admissible information;
- a realized extraction/state transition;
- and an immutable adopted BAU reference used for comparison.

No contradiction is created because evidence scope, scenario context, epistemic perspective, derivation and governance role remain separate. No scenario value repairs the empirical UNKNOWN. No agent belief becomes evidence. No simulated observation becomes a real-world observation by inheritance. No realized state overwrites reference state.

### Adversarial mutations

The candidate model rejects the following semantic mutations:

- treating hidden scenario quantity as Solar evidence;
- allowing agent code to consume hidden state merely because it exists in the same store;
- converting UNKNOWN to zero;
- treating a negative bounded search as confirmed absence;
- treating a generator distribution as an agent prior;
- treating scenario-seed spread as measured epistemic uncertainty;
- treating deterministic computation as an independent authority root;
- treating reference adoption as reclassification to empirical truth;
- treating differing scenario universes as conflicts;
- treating an agent belief as LOOM endorsement of its object;
- treating a post-output parameter/universe change as retroactive validation.

### Mechanical verdict

**PASS WITH CARRIED LIENS.** No tested exemplar forces reopening D2.1-D2.10. The remaining liens concern concrete qualification, lineage, reproducible search/audit mechanics and independence rather than a missing conceptual dimension.

## 32. Phase 2 Review Readiness

The candidate Claim and Authority Model is mechanically ready for hostile review. It remains PRE-CONTRACT / SINGLE-AUTHORITY and does not qualify any underlying holding.
