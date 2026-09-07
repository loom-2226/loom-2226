# LOOM 2226 — Governance Baseline v1.0

**Status:** DRAFT GOVERNANCE CONSTITUTION — becomes governing only when PR #24 is approved and merged  
**Branch during adoption:** `governance/repository-control-baseline-v1`  
**Adoption baseline:** `36c21d1d13bcb441316bdb8b6f944b8a1cc2cba7`  
**Purpose:** define authority, promotion, freeze, dependency, assurance, exception and session-governance rules for the whole LOOM repository.

---

# 1. Constitutional principles

## 1.1 Repository authority

> **GitHub outranks the chat.**

Chat history, Project memory, user recollection, local files and LLM context may explain intent/history. They do not establish current repository authority.

Current Git refs, governing manifests, approved change records, hashes, tests and explicit promotion records determine what is active, frozen, governing, released or superseded.

## 1.2 Memory rule

> **Memory explains context. It never establishes authority.**

If remembered state conflicts with verified GitHub state, verified GitHub state controls.

## 1.3 Epistemic rule

> **Ideas may move freely; evidentiary status may not.**

Research, analogy, anomaly, simulation, fiction ancestry and generated model output may inspire questions. They may not silently upgrade themselves into established evidence or canon authority.

## 1.4 Focus rule

> **The map can be huge. The active lane cannot.**

WIP limits are governance rules, not suggestions.

## 1.5 Stability rule

> **Do not break the damn game while installing project-management machinery.**

Governance adoption does not retroactively reorganize grandfathered functional workstreams.

---

# 2. Project roles

## 2.1 Kevin — Project Intent Authority

Kevin decides what LOOM is trying to become, which strategic tradeoffs to accept, which workstream to prioritize, and whether advisory governance risk is accepted where overrides are permitted.

Kevin's intent does not silently rewrite:

- evidence;
- experiment history;
- Git state;
- test outcomes;
- external facts;
- previously frozen data;
- canon without the required change mechanism.

## 2.2 Sol / OpenAI agents — Integrator / Architect / Implementer

Sol and delegated OpenAI agents may research, analyze, draft, implement, test, inspect and operate the repository within the authority class and mutation scope of the active work item.

They may not treat remembered context or their own prior output as governing authority.

## 2.3 WALTER — Autonomous Continuous Assurance Agent

WALTER is LOOM's bounded autonomous `#LOOMSAFE` assurance function.

Formal specification:

`governance/agents/WALTER_AUTONOMOUS_ASSURANCE_AGENT_v1.0.md`

Personality/role contract:

`governance/roles/WALTER_CONTINUOUS_ASSURANCE_ROLE_v1.0.md`

WALTER may autonomously activate, inspect and flag. He may represent deterministic hard gates only where this governance baseline or an approved descendant rule explicitly defines them.

WALTER does not own project intent and cannot create evidence or canon by judgment.

---

# 3. Authority chain

LOOM uses one integrated authoritative trunk: `main`.

Authority normally flows downward through deliberate promotion:

```text
EXTERNAL ESTABLISHED KNOWLEDGE
            |
            v
RESEARCH / SIMULATION / DERIVATION
            |
            | may propose
            v
CANON CHANGE REQUEST (CCR)
            |
            v
CANON
            |
            v
ENGINEERING INTERPRETATION / CLOSURE
            |
            v
RUNTIME / DATA / 3D / MEDIA
            |
            v
RELEASE
```

Findings may travel upward.

Authority does not travel upward automatically.

A runtime, simulation or geometry result may challenge canon but cannot silently rewrite it.

---

# 4. Authority classes

## 4.1 Current canon

`canon/current/**` contains governing fictional truth only where recognized by the active canon baseline/authority register or an approved scoped governing amendment.

## 4.2 Research

`research/**` is non-canon unless explicitly promoted through a CCR/canon change.

## 4.3 Engineering

`engineering/**` provides normative technical interpretation, closure and delivery guidance subordinate to canon.

Engineering may raise a canon inconsistency finding.

## 4.4 Runtime / source

`src/**`, runtime tools and executable behavior implement governing sources. Runtime behavior does not override canon merely because it executes.

## 4.5 Data

Repository SQLite/data, migration logic and seeds may be authoritative for runtime state within their declared domain, but they do not become canon authority by storage location.

## 4.6 Assets / media / 3D

Generated images, media libraries, browser displays, 3D models and rendered geometry are representational/derived unless explicitly designated authoritative by a governing engineering/canon source.

## 4.7 Governance

`governance/**`, `AGENTS.md`, `LOOM_START_HERE.md`, `.github/**` and machine-readable control metadata define process/authority control. Governance cannot promote substantive canon by implication.

---

# 5. Change classes

Every substantive PR declares one primary class:

- `class:research`
- `class:canon`
- `class:engineering`
- `class:runtime`
- `class:data`
- `class:asset-media`
- `class:governance`

Mixed-authority changes are exceptional.

If a change genuinely requires multiple classes, the PR must identify:

- primary class;
- secondary affected classes;
- why separation is harmful/impossible;
- promotion/validation sequence;
- affected dependencies.

A mixed PR never gains permission to cross authority boundaries merely by declaring itself mixed.

---

# 6. Canon change and amendment rules

## 6.1 Canon Change Request

Material canon change requires a numbered CCR before promotion.

A CCR identifies:

- source/reason;
- evidence/derivation status;
- claims added/modified/retired;
- affected canon sources;
- affected engineering/runtime/data/3D/media;
- superseded content;
- required revalidation;
- decision/disposition.

## 6.2 Scoped governing amendments

A governing amendment may coexist with a parent canon volume when:

- the amendment explicitly names its parent;
- the scope is explicit;
- only the declared scope is superseded/extended;
- parent content outside that scope remains governing;
- the amendment is registered in the active authority/baseline record;
- downstream dependencies reference the combined authority set.

### Existing Wayfarer v2.4a reconciliation

`canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md` declares itself a governing schematic/physical-packaging amendment to CANON II v2.4.

Governance recognizes the **declared scoped-authority relationship** for current workstream interpretation but records a baseline-management defect: the next formal canon baseline update must explicitly include/hash/register v2.4a so the machine-readable baseline and effective governing source set agree.

Governance adoption does not edit the canon file or retroactively change its content.

## 6.3 Supersession

Superseded governing sources are archived, not silently overwritten/deleted.

Supersession records must make the replacement relationship machine-readable where practical.

---

# 7. Research freeze and preregistration

A `FROZEN_SCIENTIFIC_QUALIFICATION` object has:

- exact branch/ref;
- exact SHA;
- preregistered design;
- verdict rules;
- required environment/qualification procedure where applicable;
- mutation prohibition.

After freeze:

- no rebasing;
- no merge-from-main;
- no tuning;
- no diagnostic change that affects the preregistered design;
- no verdict-rule change;
- no cleanup/refactor in the frozen object.

A worthwhile improvement becomes a successor experiment.

### PR #19

PR #19 remains frozen at:

`314efe50875630ba4be720b4097a2ca14075e620`

until executed/dispositioned under its preregistered gate.

### PR #16

PR #16 remains preregistered/on hold at:

`b60086d906f63211206502f23458be490902c2df`

until the comparator prerequisite is resolved and governance restart occurs.

---

# 8. Dependency and invalidation discipline

Material change must identify downstream dependents.

Examples:

```text
CANON II
 -> Wayfarer engineering
 -> mass / thermal / packaging closure
 -> Navigator model
 -> runtime/data fields
 -> authoritative 3D geometry
 -> media/canon browser
 -> Pixel/Windows release
```

A changed upstream authority does not automatically mutate dependents.

Instead dependents become one of:

- `UNCHANGED_COMPATIBLE`
- `REVIEW_REQUIRED`
- `REVALIDATION_REQUIRED`
- `MIGRATION_REQUIRED`
- `BLOCKED_PENDING_UPSTREAM`
- `SUPERSEDED`

The dependency map created in Step 6 will machine-encode these relationships.

---

# 9. Testing and qualification classes

## 9.1 Documentation / governance only

No functional tests required unless the change modifies executable governance automation.

## 9.2 Python/code release

Run unit regression before releasing any new Python source to the user/runtime branch.

## 9.3 Substantive functional change

Run unit regression + relevant functional tests.

## 9.4 Production release/finalization

Run full end-to-end regression immediately before production promotion, not on every development change.

## 9.5 Scientific qualification

Run the preregistered scientific procedure exactly. Expensive scientific runs are not replaced by generic CI.

CI validates code/contracts; designated qualification machines execute frozen scientific experiments.

---

# 10. WIP / preemption

The Foundations & Consequences research program may have at most:

1. one T0 scientific execution/qualification;
2. one T1 science/discovery stream;
3. one T1 fiction/world/simulation stream;
4. one bounded enabler.

A fifth substantive stream requires explicit displacement, completed release, or approved convergence-hotspot preemption under the portfolio model.

New curiosity goes to backlog by default.

---

# 11. Session bootstrap

Every substantive LOOM ChatGPT/Codex session must recover current authority before authoritative mutation.

Required bootstrap sequence:

1. read `LOOM_START_HERE.md` once created;
2. read current governance/workstate;
3. verify relevant branch/PR state;
4. identify requested change class;
5. identify mutation scope;
6. identify frozen/dependency constraints;
7. only then mutate.

If GitHub authority cannot be verified, discussion may continue but authoritative mutation waits.

---

# 12. WALTER assurance integration

WALTER should be deterministic-first and LLM-second.

Deterministic checks may hard-block when an explicit rule fails.

LLM interpretation may flag/recommend but does not create a hard factual block without a deterministic policy basis.

WALTER finding classes:

- `PASS`
- `WATCH`
- `REVIEW_REQUIRED`
- `HOLD`
- `BLOCK`

One WALTER agent may use multiple assurance modules; modules are not independent votes.

---

# 13. Exceptions and overrides

## 13.1 No silent override

No material governance exception exists merely because Kevin or Sol says 'just this once' in chat.

## 13.2 Exception record

A permitted exception records:

- exception ID;
- finding/rule;
- requester/decision authority;
- rationale;
- risk accepted;
- affected components;
- time/scope limit;
- required recovery/monitoring;
- closure/disposition.

## 13.3 Non-overridable history

An exception may permit a future action.

It may not rewrite history:

- failed tests stay failed;
- old hashes stay old hashes;
- frozen SHAs remain the recorded frozen SHAs;
- scientific results are not relabeled;
- provenance records are not erased.

---

# 14. Grandfathered workstreams during adoption

Exact recovery points are recorded in:

`governance/adoption/IN_FLIGHT_BRANCH_REGISTER_2026-09-07.yml`

Navigator/GIS/HUD, runtime/devops, media, Pixel release state and Wayfarer 3D remain paused and grandfathered until restart.

Governance adapts to their legitimate architecture. They are not forced into retroactive path cleanup or rebasing merely to satisfy a new aesthetic.

---

# 15. Release and baseline principles

A release should be reconstructable from:

- source commit/ref;
- manifests;
- required data/artifact hashes;
- schema/compatibility state;
- required test/qualification evidence;
- release assets;
- rollback/recovery point.

Generated/release artifacts must not be confused with governing source simply because they are large or convenient.

---

# 16. Governance adoption exit

Governance Baseline v1.0 is not complete until:

- Step-1 recovery points remain intact;
- no game/physics/canon/data/asset behavior was accidentally changed;
- OpenAI/Codex bootstrap files exist;
- PR/issue templates exist;
- dependency/compatibility metadata exists;
- CCR mechanism exists;
- WALTER/loom-gate runs in advisory mode and passes historical fixture validation;
- `main` receives minimal protection;
- active workstreams receive non-functional governance sync;
- a fresh LOOM ChatGPT Project chat successfully reloads Git authority and respects frozen state.

Until then, development and physics execution remain paused.
