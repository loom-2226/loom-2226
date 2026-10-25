# LOOM 2226 — World State and Long-Horizon Drift Control Work Plan v0.1

**Version:** v0.1  
**Date:** 14 September 2026  
**Status:** PROJECT DESIGN / DELIVERY WORK PLAN — NOT FICTION CANON  
**Priority:** WORLD STATE FIRST  
**Scope:** establish governed world-state authority first; then add campaign/story-drift protection around generative narrative.  
**Runtime/schema mutation:** NONE in this document.

---

## 1. Purpose

LOOM now has two distinct long-horizon drift problems:

1. **WORLD DRIFT** — canon, physics, engineering, lore, history, geography, institutions, economics/demography, database semantics, provenance, and world-object state.
2. **STORY / CAMPAIGN DRIFT** — cumulative narrative change across otherwise locally valid scenes: premature resolution, forgotten threads, character-motive drift, narrative gravity, specificity ratchet, cast concentration, and campaign commitments disappearing over time.

These problems require different control mechanisms.

The immediate project priority is **WORLD STATE**.

The foundational rule is:

> **Establish authoritative world state before attempting long-horizon story governance.**

LOOM must first be able to answer, reliably and programmatically:

> What is true in the world, what is uncertain, what does a field mean, what operations are licensed, and what authority is required to change persistent state?

Story continuity is layered on top of that authority; it is not a substitute for it.

---

## 2. Governing architectural distinction

### 2.1 World drift

World drift is generally a violation of an existing rule or semantic boundary.

Examples:

- proxy → literal fact;
- aggregate/place state → individual characteristic;
- influence → ownership;
- co-presence → interpersonal relationship;
- association → causation;
- relative score → absolute interpretation;
- template/materializer signature → local anomaly;
- current state → historical state;
- historical state → current state;
- NULL → absence;
- summary statistic → invented underlying distribution;
- Claim/belief → objective Event/world truth.

World drift should therefore be controlled primarily by **explicit authority, provenance, executable semantic contracts, deterministic validation, and governed mutation**.

### 2.2 Story drift

Story drift is different. It may arise from the accumulation of individually legal narrative acts.

Examples:

- an unresolved question quietly disappearing;
- each retelling adding one plausible detail until a vague entity becomes a fully invented biography;
- an interesting NPC becoming central to unrelated threads;
- open questions resolving faster than new uncertainty enters the campaign;
- dormant threads repeatedly pulled into unrelated scenes;
- conflicting beliefs collapsing into omniscient truth;
- campaign tone, emphasis, or thematic balance changing without any single invalid scene.

Story drift therefore requires **cross-session state, protected unresolved objects, budgets, clocks, commitments, and longitudinal measures** rather than simply denial-by-default permissions.

These two systems must remain separate but interoperable.

---

## 3. Target runtime architecture

```text
AUTHORITATIVE WORLD STATE
canon / physics / engineering / lore / SQL
        ↓
EXECUTABLE SEMANTIC CONTRACT
field meaning / provenance / licensed relations / assumptions
        ↓
WORLD CONTEXT PROJECTION
only governed facts required by the consumer
        ↓
CAMPAIGN CONTINUITY STATE
open questions / commitments / character state / threads
        ↓
SCENE AUTHORITY + CONTEXT
what this scene may invent, propose, touch, or resolve
        ↓
SCENE GENERATOR
performance / dialogue / description / local improvisation
        ↓
CONSEQUENCE EXTRACTION
what persistent assertions did the scene actually make?
        ↓
VALIDATION / AUDIT
        ↓
PROMOTE / REJECT / QUARANTINE
        ↓
EVENT / CLAIM / WORLD / CAMPAIGN STATE
```

The scene generator is intentionally not the authority for persistent state.

> **Generate freely. Persist conservatively.**

The transcript is not authoritative world state.

---

## 4. Phase A — establish world-state authority [HIGHEST PRIORITY]

This phase is the current priority and should precede broad story-governance implementation.

### A1. Complete executable semantic contract migration

Build from the production data-dictionary baseline already merged through PR #116.

Required structure:

```text
data/
  LOOM_2226.sqlite3
  LOOM_2226_CIVSTATE.sqlite3
  CHECKSUMS.json

docs/database_semantics/contract/
  fields.json
  relations.json
  assumptions.json
  regimes.json
  consumers.json
  CONTRACT_SCHEMA.json
  CONTRACT_VERSION.json
```

Core rules:

- machine-readable contract is authoritative for consumer interpretation;
- prose documentation is generated from the contract, not independently edited;
- contract is pinned to exact production database SHA-256 values;
- contract/schema version mismatch fails loudly;
- unresolved meaning is preserved as unresolved;
- absence of a relation license means denial;
- no semantic definition is invented to achieve apparent completeness.

### A2. Exact relation licensing

License operations as fully-qualified relation triples, not generic field permissions:

```text
database
field_a
field_b
operation
license
purpose
constraint
authority
governing_assumptions
alternative
```

Examples:

- workforce / resident population ratio may be permitted as descriptive composition;
- habitable-capacity minus resident population must be forbidden because the field is itself derived from resident + transient population and utilization.

A `FORBIDDEN` relation should identify a supported alternative where one exists.

### A3. Make assumptions executable

Export governing assumptions, including `LOCKED_CANON` assumptions, into machine-readable form and map their downstream effects to relevant fields/relations.

The goal is for a rule such as the separation of resident population, throughput and strategic importance to block an invalid construction at runtime rather than merely explain the error after it occurs.

### A4. Runtime semantic client

Create a governed client for semantic interpretation.

Intended interface:

```python
contract.field(...)
contract.may(field_a, field_b, operation)
contract.read(...)
contract.context_block([...])
```

Any code deriving meaning from production database fields should progressively move behind this interface.

Raw SQLite access remains appropriate for:

- migrations;
- integrity checks;
- schema tooling;
- low-level audits;
- deterministic infrastructure that does not infer semantic meaning.

### A5. Consumer inventory

Generate a field → consumer index by scanning current production consumers.

This becomes permanent impact-analysis infrastructure for:

- migrations;
- refactoring;
- deprecation;
- field disposition;
- testing;
- future schema evolution.

### A6. Field disposition

Every field eventually receives a governed disposition:

| interpretable | used | disposition |
|---|---|---|
| yes | yes | LICENSED |
| yes | no | DORMANT |
| no | yes | RESTRICTED |
| no | no | DROP_CANDIDATE |

Important rules:

- disposition assignment is evidence-driven, not name-driven;
- automation may propose disposition, but evidence governs assignment;
- RESTRICTED means literal report / supported positional comparison only;
- DROP_CANDIDATE is quarantine metadata, not deletion authority;
- no production field is dropped before downstream E1/Canon Context consumers have been built and the consumer index regenerated.

### A7. World-state CI gates

Add tests that fail when:

- contract/database hashes diverge;
- a contract record does not resolve to a real field;
- a production field disappears from contract coverage;
- a consumer performs an unlicensed field relation;
- a RESTRICTED field is used in forbidden arithmetic/derivation;
- generated narrative documentation diverges from machine-readable contract state.

Static analysis is a migration guard, not the ultimate enforcement boundary. The long-term safety boundary is runtime access through the governed semantic interface.

---

## 5. Phase B — Canon Context / world projection [NEXT CONSUMER]

Canon Context Projection is the next consumer that should earn a semantic-contract slice.

Its job is not to load the entire world into an LLM.

Its job is to produce a compact, governed packet of only the world-state facts required for a particular task.

Required properties:

- every materially used database field has a governed contract;
- provenance and epistemic status travel with the projected fact;
- Claims never silently become Events;
- world truth and actor knowledge remain distinct;
- historical and current-state authority remain distinct;
- unresolved world-state questions remain unresolved;
- no projection may manufacture semantics from names, correlations or apparent topology.

This is the bridge between the world-state project and future game LLMs.

---

## 6. Phase C — minimal campaign-continuity primitives [AFTER WORLD BASELINE]

Do not build a monolithic AI-GM subsystem.

Start with the minimum primitives required to prevent Dragon-Mountain-style cumulative drift.

### C1. Open Question

First-class object representing a deliberately preserved hole in campaign knowledge.

Minimum fields:

```text
question_id
statement
epistemic_state
protected
world_answer_known
authority_to_resolve
opened_at_event
resolved_at_event
last_touched_session
```

Candidate epistemic states:

```text
UNRESOLVED
CONTESTED
RUMORED
MISUNDERSTOOD
DELIBERATELY_OPAQUE
RESOLVED
```

Critical distinctions:

- world knows, campaign does not;
- world does not know, campaign does not;
- campaign has legitimately resolved the question.

`UNRESOLVED` is protected state, not missing data.

### C2. Campaign Commitment

Represent what the campaign owes the player:

- setup;
- foreshadow;
- obligation;
- threat;
- arc beat.

This allows detection of resolution-by-omission and abandoned narrative promises.

### C3. Character Commitment

Persist motives, loyalties, stances, obligations and other character commitments that may not silently drift through characterization.

Each commitment must state what can legitimately change it.

### C4. Campaign Thread

Explicit state:

```text
ACTIVE
DORMANT
CLOSED
```

Dormancy must be represented explicitly rather than inferred from absence.

### C5. Scene Authority

Written before generation.

At minimum:

```text
location
present_characters
may_invent
may_propose
may_not_resolve
may_not_surface
required_uncertainties
invention_budget
```

Scene freedom should be stated positively and generously within a declared envelope.

### C6. Scene Consequence

Persistent assertions extracted from prose after generation.

State:

```text
PROPOSED
PROMOTED
REJECTED
QUARANTINED
```

Only PROMOTED consequences change persistent campaign/world state.

---

## 7. Phase D — generation / extraction / validation loop

The game loop must not allow generated prose to become persistent state automatically.

```text
scene context
   ↓
scene generation
   ↓
separate consequence extraction
   ↓
classification
   ↓
deterministic validation + independent semantic/continuity audit
   ↓
promote / reject / quarantine
```

Hard rules:

1. consequence extraction is a separate model call/process from scene generation;
2. deterministic rules govern what can be checked deterministically;
3. an independent model may audit semantic commitment conflicts but does not replace deterministic authority;
4. rejected assertions remain auditable as transcript assertions that were not promoted;
5. ambiguous assertions may be quarantined rather than prematurely resolved.

---

## 8. Phase E — long-horizon story-drift monitoring [POST-E1]

Story drift cannot be solved solely by per-scene validation.

Track longitudinal campaign health, including:

- open-question count;
- question birth/resolution rate;
- unresolved-question dormancy;
- dormant-thread age;
- cast appearance concentration;
- top-character share of scenes;
- new named-entity rate;
- thread merge/connection rate;
- specificity growth on previously vague entities;
- character-commitment changes;
- belief/claim → truth collapse;
- unresolved material pulled into unrelated scenes.

These metrics are primarily **drift indicators and budgets**, not universal per-scene hard limits.

Do not make all scenes mechanically uniform to satisfy metrics.

The campaign-level concern is distribution over time.

---

## 9. Drift test taxonomy

### Stateless / per-scene

**D1 — Data → Interpretation**  
Proxy becomes literal; aggregate becomes individual; influence becomes ownership.

**D2 — Inference → Fact**  
Possibility or hypothesis narrated as established event.

**D3 — State → Psychology**  
Environmental/place state silently becomes individual motive/personality.

**D4 — Co-presence → Relationship**  
Shared facility/workplace becomes interpersonal relationship.

**D5 — Regime → Anomaly**  
Template/materializer structure becomes an invented local crisis or mystery.

### Stateful / cross-session

**D6 — Protected Resolution**  
Model invited to explain what really happened; unresolved state must survive.

**D7 — Narrative Gravity**  
Repeated minor NPC/topic grows centrality without earned cause.

**D8 — Dormant-Thread Capture**  
Unrelated scene pulls dormant conspiracy/thread back in.

**D9 — Belief Collapse**  
Conflicting actor beliefs become narrator/world truth.

**D10 — Satisfaction Over Authority**  
Emotionally satisfying explanation exceeds established state.

**D11 — Resolution by Omission**  
Thread disappears without explicit resolution.

**D12 — Specificity Ratchet**  
Repeated retelling steadily invents unsupported detail.

**D13 — Question-Supply Exhaustion**  
Open questions decline monotonically without replacement.

Useful red-team rule:

> Closure, connection and explanation are the fingerprints of narrative drift and deserve heightened scrutiny when unsupported.

---

## 10. Relationship to existing LOOM epistemic architecture

Reuse what already exists.

LOOM already separates:

- objective world state;
- Events;
- Claims;
- claimant/provenance;
- confidence;
- verification state;
- player/NPC/world knowledge;
- asymmetric belief;
- persistent event history.

Do not replace these systems with campaign-continuity machinery.

The most important missing concepts are:

1. an explicit **Open Question** object;
2. a **Campaign Commitment** / future narrative obligation;
3. dependency/assumption labels sufficient to support eventual principled retraction.

ATMS-style labels may later improve Claim dependency and retraction without requiring a full truth-maintenance engine.

---

## 11. What not to build yet

Do not:

- merge campaign governance into the database semantic contract;
- build a full drama manager;
- build a full ATMS;
- build automated campaign retraction before the event/consequence shape is understood;
- build tone-drift machinery;
- execute database DROP_CANDIDATE deletions before downstream consumers exist;
- attempt to solve regime-normal relevance with another projection-engine heuristic;
- give scene generation authority over persistent world/campaign truth;
- treat larger context windows or better memory retrieval as substitutes for authoritative state.

---

## 12. Delivery priority

### PRIORITY 0 — WORLD STATE BASELINE

1. executable semantic-contract schema/version/hash pinning;
2. exhaustive fields contract;
3. exact relation licenses;
4. governing assumptions export;
5. runtime semantic client;
6. generated consumer index;
7. field disposition report — no drops;
8. CI enforcement;
9. Canon Context Projection as first governed LLM consumer.

### PRIORITY 1 — E1-compatible continuity seam

After world-state authority exists:

1. minimal Open Question representation;
2. Scene Authority object;
3. separate consequence-extraction pass;
4. log proposed consequences without automatic promotion;
5. D1–D5 stateless drift tests.

Keep E1 itself narrow. Do not allow continuity research to reopen E1's flight qualification scope unnecessarily.

### PRIORITY 2 — POST-E1 CAMPAIGN CONTINUITY

1. six-object campaign-continuity model;
2. independent commitment auditor;
3. promotion/rejection/quarantine workflow;
4. campaign health metrics;
5. D6–D13 cross-session tests;
6. ATMS-style dependency labels where useful;
7. controlled replay/retraction experiments.

### PRIORITY 3 — LONG-HORIZON VALIDATION

Build an adversarial mini-campaign test harness and compare:

- conventional memory/context generation;
- LOOM governed generation → extraction → validation → promotion.

Target 50–100 simulated sessions initially.

Measure:

- unsupported resolutions;
- relationship invention;
- question survival;
- specificity ratchet;
- cast concentration;
- dormant-thread capture;
- belief→truth collapse;
- campaign-state divergence;
- narrative quality / sterility trade-off.

This is the experiment that can establish whether LOOM has a genuine architectural advantage in long-horizon narrative stability.

---

## 13. Competitive positioning hypothesis

Current systems commonly focus on one or more of:

- larger context;
- retrieval/memory;
- persistent NPC memory;
- structured RPG mechanics;
- structured world state.

LOOM's intended differentiator is deeper:

> **Generative freedom without granting generation authority over reality or campaign continuity.**

The distinguishing chain is:

```text
world truth
→ semantic authority
→ projected context
→ campaign continuity
→ scene authority
→ generation
→ consequence extraction
→ validation
→ selective persistence
```

This remains a hypothesis until demonstrated experimentally.

Do not claim a product lead before long-horizon testing establishes it.

---

## 14. Governing principles

Freeze these principles as the working architecture baseline:

> **WORLD STATE FIRST.**

> **Generate freely. Persist conservatively.**

> **The transcript is not the state.**

> **Only promoted consequences become persistent history.**

> **Unresolved is a legitimate and protectable state.**

> **A scene may elaborate current state; it may not silently redefine world or campaign state.**

> **Narrative importance must not imply institutional/world importance.**

> **What happened outranks what it later came to mean.**

---

## 15. Success criterion

The goal is not an impressive one-session AI GM.

The goal is a system capable of sustaining a world and campaign over hundreds of sessions without either quietly becoming something else.

The immediate success criterion is narrower:

> **LOOM establishes a governed, queryable, version-pinned world-state authority that every future semantic consumer can rely upon before long-horizon campaign generation is allowed to become persistent state.**
