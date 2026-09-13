# LOOM 2226 — Local Intelligence Runtime Functional Requirements v0.1

**Date:** 2026-09-13  
**Primary change class:** `class:engineering`  
**Status:** PROPOSED REQUIREMENTS BASELINE — DOCUMENTATION ONLY  
**Authority:** non-canon engineering planning; no runtime authority  
**Promotion target:** `main` as an engineering requirements/work-package baseline  

## 1. Purpose

Define functional requirements for a LOOM Local Intelligence Runtime (LIR) capable of executing bounded AI tasks on local hardware, initially the Pixel-class Android target, while retaining OpenAI as an audited external provider for tasks that materially benefit from stronger hosted models.

The objective is not to reproduce a frontier model locally and not to train a proprietary LOOM foundation model. The objective is to make AI a replaceable provider behind a governed LOOM interface, route suitable work to local inference, measure the residual value of hosted inference, and preserve authoritative LOOM state outside model weights.

This baseline converts the 2026-09-13 architecture discussion into functional requirements. It does **not** activate a fifth engineering execution lane and does not authorize implementation while current WIP limits are saturated.

## 2. Governing principles

1. **LOOM data remains authoritative; model weights do not.** Canon, engineering authority, runtime state, SQLite databases, belief graphs, provenance records, and governed research artifacts remain external to the model.
2. **Local-first where bounded and adequate; hosted when justified.** Routing is based on measured task fitness, not ideology or provider preference.
3. **One AI contract, multiple providers.** LOOM callers should not contain provider-specific assumptions.
4. **Tool use beats memorization.** The local model should retrieve and call governed LOOM functions rather than be expected to memorize mutable world state.
5. **No silent escalation of authority.** Model output is interpretation, proposal, classification, or presentation unless a separate governed deterministic process promotes it.
6. **Offline capability is a design goal.** A useful subset of Navigator/LOOM intelligence must continue without network access.
7. **OpenAI remains under active audit during migration.** Hosted calls continue only where quality, latency, engineering effort, or reliability justifies them.
8. **Provider portability is mandatory.** Switching among local models, desktop-local models, OpenAI, or future providers must not require rewriting LOOM feature code.

## 3. Target architecture

```text
LOOM feature / Navigator / tool
            |
            v
      AI service contract
            |
            v
      policy + task router
        /        |        \
       v         v         v
 Pixel local   Desktop    Hosted
 inference     local      provider
       |          |          |
       +----------+----------+
                  |
          structured result
                  |
      validation / provenance
```

The preferred boundary is a provider-neutral service interface. Local execution may initially be hosted by a localhost Android service, embedded runtime, or another implementation that satisfies the interface. The architecture must not depend on one inference engine.

## 4. Functional requirements

### FR-001 — Provider-neutral AI service contract

LOOM shall expose a single typed AI request/response contract to callers.

Minimum request fields:

- task identifier/type;
- input/context payload;
- required response schema where applicable;
- maximum latency or execution class where applicable;
- authority/evidence constraints;
- allowed tools/functions;
- offline-required flag;
- privacy/data-egress classification;
- preferred provider only as an optional routing hint, not a hard-coded caller dependency.

Minimum response fields:

- provider used;
- model/runtime identifier;
- structured result or text result;
- validation state;
- tool calls performed;
- source/provenance references supplied to the model;
- latency;
- token or equivalent usage where measurable;
- estimated/actual external cost where applicable;
- fallback/escalation reason where applicable.

### FR-002 — Task-class routing

The runtime shall route requests by declared task class and measured provider fitness.

Initial candidate local-first task classes:

- classification and tagging;
- entity/field extraction;
- structured transformation;
- database-result summarization;
- bounded explanation of authoritative LOOM data;
- tool/function selection;
- short-form NPC or Navigator presentation grounded in supplied facts;
- belief/provenance graph formatting;
- HUD/GIS natural-language interpretation of already-computed state;
- low-consequence drafting and flavor generation.

Initial hosted-preferred/escalation task classes:

- difficult code generation or debugging;
- scientific or mathematical reasoning;
- long-context cross-document synthesis;
- ambiguous architecture decisions;
- research synthesis requiring broad external knowledge;
- novel multi-step reasoning where local benchmark performance is inadequate;
- any task explicitly marked for higher-capability review.

Routing policy shall be configurable and testable rather than embedded as scattered `if provider == ...` logic.

### FR-003 — Local Android inference

The first local deployment target shall support Pixel-class Android hardware.

The implementation shall:

- run without internet access after model/runtime installation;
- load a quantized/open-weight model appropriate to available device memory;
- expose inference to LOOM through the provider-neutral contract;
- support structured output or constrained parsing sufficient for LOOM schemas;
- report model identity/version and runtime identity/version;
- fail cleanly when the model cannot be loaded or the device is under resource pressure;
- permit replacement of the underlying model without application-feature rewrites.

No specific model family or inference runtime is selected by this requirements baseline.

### FR-004 — Controlled tool/function calling

The runtime shall support bounded function/tool use against explicit allowlists.

A local model must be able to request governed functions such as:

- retrieve object/body/actor state;
- retrieve economic/demographic/engineering summaries;
- query belief/provenance records;
- retrieve event/incident history;
- retrieve Navigator plan/status data;
- retrieve schema-defined lookup values.

The model shall not receive unrestricted filesystem, SQL, shell, GitHub, or mutation authority by default.

Tool calls must be schema validated before execution. Mutating tools require separate explicit authority and are outside the initial scope.

### FR-005 — Authoritative retrieval before synthesis

For mutable LOOM facts, the system shall prefer retrieval/tool results over model memory.

Responses that claim current LOOM state shall carry enough provenance to identify the supplied authoritative source or tool result. A model's pretrained knowledge of LOOM-like concepts shall not be treated as LOOM evidence.

### FR-006 — Structured output validation

Where a task declares a schema, the runtime shall validate the returned object before releasing it to the caller.

Invalid output shall trigger a bounded repair attempt, provider fallback, or explicit failure according to routing policy. Silent coercion that changes semantic meaning is prohibited.

### FR-007 — Hosted-provider fallback and escalation

The runtime shall support escalation from local inference to OpenAI or another configured hosted provider.

Escalation reasons must be machine-recordable, including at minimum:

- unsupported task class;
- local model unavailable;
- local schema failure;
- local tool-selection failure;
- context window exceeded;
- quality threshold not met by benchmark policy;
- latency threshold exceeded;
- explicit operator request.

Fallback shall not expose data externally when request policy marks the data as no-egress/offline-only.

### FR-008 — OpenAI usage audit

During development and migration, every OpenAI call made through the LIR shall be auditable by task class.

The audit record should capture where available:

- timestamp/session correlation ID;
- calling LOOM component;
- task class;
- model/provider;
- prompt/input size or tokens;
- output size or tokens;
- latency;
- estimated/actual cost;
- local-provider eligibility at the time;
- reason OpenAI was selected or local execution was rejected;
- success/failure;
- schema-valid result yes/no;
- quality/acceptance result where benchmarked.

The audit objective is to answer:

1. Which OpenAI tasks are repetitive and locally replaceable?
2. Which hosted calls still produce meaningful quality advantage?
3. What is the cost per useful accepted result by task class?
4. Where does hosted latency exceed local latency or vice versa?
5. What percentage of AI workload can operate offline without material quality loss?

### FR-009 — Cost-aware routing

Hosted-provider cost shall be a first-class routing and reporting metric but shall not override correctness, safety, provenance, or explicit quality requirements.

The router should support policy such as:

- local preferred when benchmark-qualified;
- hosted preferred for designated high-reasoning classes;
- hosted budget ceiling by task/session/day where configured;
- explicit operator override.

### FR-010 — Benchmark harness

Before a local model is qualified for a task class, it shall be evaluated against a representative LOOM benchmark set.

The first benchmark set should contain approximately 30–50 real or representative tasks spanning:

- extraction;
- classification;
- schema adherence;
- tool selection;
- SQLite/query-result interpretation;
- HUD/Navigator explanation;
- NPC/belief presentation;
- engineering interpretation;
- provenance-sensitive responses.

Metrics shall include:

- factual fidelity to supplied source data;
- schema validity;
- tool-selection accuracy;
- hallucination/unsupported-claim rate;
- latency;
- memory/resource use;
- thermal behavior over repeated inference;
- battery impact where practical;
- external cost;
- human acceptance for subjective presentation tasks.

A model/runtime combination qualifies per task class, not globally.

### FR-011 — Comparative provider evaluation

The benchmark harness shall allow the same test corpus to run against:

- Pixel-local candidate model/runtime combinations;
- desktop-local candidates when available;
- current OpenAI model(s) used by LOOM;
- future providers without benchmark redesign.

Results shall preserve model/runtime version so later upgrades do not invalidate historical comparisons.

### FR-012 — Resource and thermal controls

The Android implementation shall expose or infer enough runtime state to avoid pathological device behavior.

At minimum, design shall account for:

- memory pressure;
- model load/unload strategy;
- repeated inference heating;
- battery consumption;
- foreground/background Android constraints;
- concurrency limits;
- cancellation/timeouts.

The local AI service shall degrade or refuse work cleanly rather than destabilize Navigator or the device.

### FR-013 — Privacy and egress policy

Every AI request shall be classifiable for external-data egress.

Minimum policy values:

- `LOCAL_ONLY`;
- `HOSTED_ALLOWED`;
- `HOSTED_REDACTED_ONLY`;
- `OPERATOR_APPROVAL_REQUIRED`.

The router must enforce this classification before calling an external provider.

### FR-014 — Offline Navigator capability

The architecture shall support a useful Navigator intelligence mode with no network connectivity.

The offline mode should be able to:

- answer bounded questions from locally available LOOM state;
- summarize plans/status/sensor or world-state data exposed by allowed tools;
- distinguish confirmed facts from claims/beliefs when the underlying data supplies that distinction;
- state when required information is unavailable rather than fabricate it;
- produce structured tool requests and user-facing explanations.

### FR-015 — Epistemic-state preservation

When operating over LOOM belief/provenance structures, the model must not collapse objective state, character knowledge, claims, rumors, confidence, deception, and unresolved evidence into a single truth layer.

The tool contract should pass epistemic labels explicitly. Output schemas should preserve them where relevant.

### FR-016 — Logging and replay

AI executions used for qualification, defect investigation, or consequential LOOM operations shall be replayable to the practical extent allowed by nondeterministic inference.

Logs should preserve:

- normalized request;
- provider/model/runtime version;
- tools and tool outputs or durable references;
- routing decision;
- returned result;
- validation result;
- sampling/configuration parameters required for reproduction where available.

Sensitive values may be redacted according to policy, but redaction must not be represented as a complete replay artifact.

### FR-017 — Provider failure isolation

Failure or removal of OpenAI must not prevent local-qualified tasks from running. Failure of the local model must not prevent hosted-qualified tasks from running when egress policy permits.

Provider health shall be isolated behind the router.

### FR-018 — Configuration over hard-coding

Model names, provider endpoints, task-to-provider policies, context limits, timeout values, and benchmark qualification state shall be configuration/schema driven.

LOOM feature code must not depend on a particular model marketing name.

### FR-019 — Human authority and mutation boundary

Initial LIR operation is read/interpret/draft oriented.

The model shall not autonomously:

- alter canon;
- mutate governing SQLite state;
- approve scientific results;
- change engineering qualification status;
- merge GitHub changes;
- bypass `loom-gate`;
- promote a belief/claim to fact.

Any future mutation capability requires a separate governed work item and explicit permissions.

### FR-020 — Graceful no-AI behavior

Where practical, LOOM features shall retain deterministic/read-only fallback behavior when neither local nor hosted AI is available.

AI should enhance interpretation and interaction; it should not become an unnecessary single point of failure for basic navigation, database access, or core simulation operation.

## 5. Non-functional requirements

### NFR-001 — Portability

Provider implementations must be replaceable without feature-level rewrites.

### NFR-002 — Security

Local inference endpoints shall bind only to an appropriate local interface by default. No unauthenticated LAN exposure is required by this baseline.

### NFR-003 — Observability

Routing, latency, errors, schema failures, fallbacks, and hosted cost shall be measurable.

### NFR-004 — Maintainability

Schemas and adapters are preferred over hard-coded provider fields. The provider-neutral contract should be versioned.

### NFR-005 — Performance

Performance thresholds shall be established empirically per task class rather than guessed in this document.

### NFR-006 — Compatibility

The design must preserve Pixel and Windows LOOM workflows. A future desktop-local provider should satisfy the same service contract as the Pixel provider.

### NFR-007 — Provenance

AI-generated interpretation must remain distinguishable from authoritative source data and deterministic computed results.

## 6. Initial provider policy hypothesis

This is a testable starting hypothesis, not an authoritative model selection:

| Task | Initial routing hypothesis |
|---|---|
| classification/tagging | local-first |
| structured extraction | local-first |
| schema transformation | local-first |
| bounded tool selection | local-first after qualification |
| summary of supplied SQL/tool results | local-first |
| short NPC/Navigator presentation | local-first |
| offline shipboard/Navigator assistance | local-required |
| difficult code/debugging | hosted-preferred |
| scientific/mathematical reasoning | hosted-preferred |
| long-context research synthesis | hosted-preferred |
| ambiguous architecture/governance advice | hosted-preferred + human decision |
| authority-changing actions | human/governed deterministic process; not model-owned |

## 7. OpenAI audit requirements during transition

OpenAI shall remain available while the local runtime is built and benchmarked. The migration policy is **audit before replacement**, not arbitrary API elimination.

For each recurring OpenAI task class, the work package shall eventually produce one of four dispositions:

- `LOCAL_QUALIFIED` — local execution meets acceptance threshold and becomes default;
- `HOSTED_JUSTIFIED` — hosted quality/reliability materially exceeds local and remains default;
- `HYBRID_ROUTE` — local handles routine cases with measurable escalation criteria;
- `REMOVE_AI_DEPENDENCY` — deterministic code/tooling is superior to either model.

A successful program therefore may reduce OpenAI usage substantially without targeting zero hosted calls.

## 8. Acceptance gates for implementation

The implementation workstream may be considered functionally complete only when all applicable gates pass:

1. A provider-neutral contract exists and is exercised by at least one real LOOM feature or harness.
2. At least one Pixel-local model/runtime combination executes fully offline.
3. The benchmark harness compares local and OpenAI execution on the same corpus.
4. At least three bounded task classes achieve an agreed local qualification threshold.
5. OpenAI calls through the new path produce auditable usage/cost/routing records.
6. Egress policy prevents `LOCAL_ONLY` tasks from external fallback.
7. Structured-output failures are detected rather than silently accepted.
8. Tool calls are allowlisted and schema validated.
9. Provider outage tests demonstrate failure isolation.
10. Pixel repeated-inference testing records memory, thermal, latency, and battery observations.
11. Windows/local-provider compatibility is either demonstrated or explicitly deferred without provider coupling.
12. No implementation grants autonomous authority over canon, scientific qualification, protected Git operations, or governing data.

## 9. Phased work plan

This plan is deliberately dormant until admitted under current WIP controls.

### Phase 0 — Audit existing AI use

- inventory current and planned OpenAI use in LOOM;
- define task classes;
- identify deterministic alternatives;
- add cost/latency/quality measurement at the provider boundary where one exists;
- build the initial benchmark corpus from real LOOM tasks.

**Deliverable:** AI workload inventory + benchmark corpus + baseline OpenAI measurements.

### Phase 1 — Local proof of concept

- select 2–4 candidate small open-weight models and suitable Android runtimes;
- run the same benchmark corpus on-device;
- measure correctness, schema adherence, latency, memory, thermal and battery behavior;
- do not integrate the winner into production LOOM yet.

**Deliverable:** evidence-based model/runtime selection per task class.

### Phase 2 — Provider-neutral service and router

- implement versioned request/response schemas;
- implement local provider adapter;
- implement OpenAI provider adapter;
- implement policy router and egress enforcement;
- implement structured validation and fallback reasons.

**Deliverable:** interchangeable local/hosted execution through one LOOM contract.

### Phase 3 — Controlled LOOM tool integration

- expose a small read-only allowlist of LOOM retrieval functions;
- validate tool arguments and responses;
- add provenance to synthesized answers;
- test epistemic-state preservation.

**Deliverable:** local model answers grounded in authoritative LOOM state rather than memorized fiction.

### Phase 4 — First production consumers

Candidate order:

1. benchmark/diagnostic console;
2. HUD/Navigator state summarization;
3. bounded query-to-tool routing;
4. NPC/belief presentation;
5. additional local-qualified use cases.

**Deliverable:** measurable hosted-call displacement without degrading core LOOM behavior.

### Phase 5 — Continuous provider audit

- periodically rerun benchmark corpus after local or OpenAI model upgrades;
- review cost per accepted result;
- move task classes among local/hosted/hybrid/deterministic dispositions;
- retain historical benchmark records to identify regressions.

**Deliverable:** provider choice remains an evidence-based engineering decision.

## 10. Explicit non-scope of this PR

This requirements baseline does **not**:

- add an AI runtime;
- download or select a model;
- add Python/Android dependencies;
- change Navigator behavior;
- change SQLite schema or bytes;
- alter Pixel or Windows launch/update behavior;
- modify canon;
- mutate a frozen/preregistered scientific object;
- create a new autonomous LOOM agent;
- authorize unrestricted SQL, shell, filesystem, GitHub, network, or write-capable tools for a model;
- activate a fifth substantive engineering stream.

## 11. Dependencies and compatibility classification

Upstream authorities checked for this requirements baseline:

- `LOOM_START_HERE.md`;
- root `AGENTS.md`;
- `governance/current/LOOM_CURRENT_WORKSTATE.yml`;
- `governance/current/LOOM_PROJECT_STATUS_2026-09-12.yml`;
- `governance/current/LOOM_CHANGE_CONTROL_v1.0.md`.

Current downstream components are `UNCHANGED_COMPATIBLE` because this PR adds documentation only. Any future runtime implementation must re-evaluate Navigator/HUD, runtime/devops, Pixel/Windows deployment, data access, security, compatibility manifests, and dependency mapping at implementation time.

## 12. Testing / qualification for this PR

Documentation-only engineering change. No functional test is required by the current root agent contract.

Future implementation phases require unit and relevant functional tests; production promotion requires the applicable end-to-end regression class.

## 13. Recovery / rollback

Rollback is deletion or reversion of this requirements document. No runtime, schema, canon, release, or data state is changed by this PR.

## 14. WALTER / #LOOMSAFE assurance note

This topic inherently touches external AI/vendor cost, data egress, opaque-model behavior, lock-in and fallback. Those concerns are therefore designed into the requirements rather than deferred:

- provider neutrality;
- local offline fallback;
- OpenAI usage/cost audit;
- explicit egress policy;
- provenance and schema validation;
- benchmark qualification by task class;
- no autonomous authority expansion.

No claim that a specific local model is adequate is promoted by this document. Model fitness must be demonstrated empirically before routing policy changes.