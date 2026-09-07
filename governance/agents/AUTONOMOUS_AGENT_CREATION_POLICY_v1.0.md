# LOOM 2226 — Autonomous Agent Creation Policy v1.0

**Status:** DRAFT — governing after PR #24 merge  
**Registry:** `governance/agents/AGENT_REGISTRY.yml`

## 1. Purpose

Prevent LOOM from turning every useful check, workflow or fictional personality into another autonomous LLM.

An autonomous agent is a governance and operational commitment. It receives a distinct persistent objective, trigger surface, state/evidence access, allowed actions and failure modes. Creating one therefore requires stronger justification than creating a script, workflow, module, reviewer persona or prompt.

## 2. Technical definition

A LOOM autonomous agent must be able to:

1. activate on registered events without a new human prompt;
2. observe registered state;
3. evaluate that state against a persistent bounded objective/policy;
4. select from a constrained response set;
5. take bounded registered actions or create durable findings;
6. preserve auditable identity, scope and authority boundaries.

A deterministic script is not automatically an agent. An LLM chat is not automatically an agent. A character/personality is not automatically an agent. An agent module is not another agent.

## 3. Creation gate

A new autonomous agent is justified only when **all** of the following are true:

- the objective is materially distinct from every existing agent;
- independent triggering/state is operationally useful;
- a deterministic workflow alone is insufficient;
- a module of an existing agent would create harmful coupling or weaken independent assurance;
- permitted actions and prohibited actions can be stated explicitly;
- inputs, output provenance and replay/audit path can be defined;
- vendor/LLM/cost/data-handling exposure is understood;
- shutdown/hold behavior is defined;
- Kevin explicitly approves creation through a governance-class change.

If any of these remain unclear, default to **do not create the agent**.

## 4. Preference order

Before creating a new agent, ask whether the requirement can be satisfied by:

1. deterministic validation/script;
2. a capability/module of an existing agent;
3. an autonomous agent only when distinct objective/independence genuinely requires it.

This keeps agent count small enough that accountability remains comprehensible.

## 5. Expected LOOM topology

Current active autonomous agents: **1 — WALTER**.

Near-term target maximum: **3**:

- WALTER — Continuous Assurance;
- Research Qualification — reserved, not active;
- Release Operator — reserved, not active.

Possible later fourth:

- Runtime / Simulation Steward — deferred until persistent campaign-state operation justifies it.

Five or more top-level autonomous agents is a governance smell and requires explicit architecture review rather than incremental creation.

## 6. Separation-of-duties principle

New agents should exist primarily when independence is valuable, not because personalities are fun.

Examples:

- A licensing checker belongs in `WALTER.VENDOR`, not a new Vendor Agent.
- A provenance checker belongs in `WALTER.PROVENANCE`, not another autonomous reviewer.
- A recurring frozen scientific qualification custodian may deserve a separate agent because independence from experiment authoring materially improves scientific discipline.
- A release operator may deserve a separate agent because packaging/promotion custody is distinct from assurance and project intent.

## 7. Agent activation package

An approved new agent requires at minimum:

- registry entry;
- technical objective;
- trigger list;
- allowed observations/data sources;
- allowed autonomous actions;
- prohibited actions;
- authority boundary;
- deterministic versus LLM responsibilities;
- exception/override rules;
- audit/replay method;
- cost/vendor/privacy assessment;
- tests/fixtures before enforcement;
- optional persona binding record.

An agent is not considered ACTIVE merely because a design document exists.

## 8. Walter's role in agent creation

WALTER should automatically review proposals for new autonomous agents for:

- role duplication;
- hidden vendor/LLM dependency;
- excessive permissions;
- weak shutdown/rollback semantics;
- false independence;
- cost/lock-in exposure;
- persona-driven authority creep.

WALTER cannot approve his own expansion of authority or create another agent by himself.

## 9. Agent retirement

Agents must be removable.

Retirement requires preservation of durable findings/state needed for audit, removal/revocation of autonomous triggers and permissions, and update of the registry.

An agent's prior output remains historical evidence after retirement.

## 10. Core rule

> **Create a new agent only when independence and persistent objective earn one. Personality alone never does.**
