# Phase 3B Decision Snapshot / Policy Firewall Decision 001

**Status:** ACCEPTED DESIGN DECISION / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Scope:** Offworld MVP DECISION_WINDOW interface
**Autonomous-policy authority:** NOT GRANTED

## 1. Decision

A policy executing in a DECISION_WINDOW shall not receive the simulation kernel, world state, scheduler, scenario-resource registry, run identity, universe identity, world seed, or hidden state.

It receives only an immutable value snapshot plus an opaque deterministic decision key:

`DecisionSnapshot -> PolicyContext -> policy result`.

The snapshot is constructed world-side from explicitly admitted agent-visible state before runtime seal.

## 2. DecisionSnapshot

The current snapshot surface contains only copied values:

- agent identity/type and current node;
- period/effective time;
- the agent account balance;
- capabilities and objectives;
- information references already held by the agent;
- agent-local beliefs;
- agent-held asset references;
- agent-held resource and claim holdings;
- explicitly admitted facts.

It contains no live references to AgentState, Account, ResourceState, KernelState, scheduler, run identity, scenario universe, hidden resource state or RNG seed.

Snapshot collections are tuples of copied scalar/value objects. Snapshot, fact and policy-context dataclasses are frozen and slotted.

## 3. Fact states

Admitted facts distinguish:

- KNOWN(value);
- UNKNOWN(no value);
- BLOCKED(no value).

UNKNOWN and BLOCKED may not carry a value. KNOWN requires one.

This prevents the snapshot layer itself from coercing missing knowledge to zero.

## 4. PolicyContext

A policy receives:

- immutable DecisionSnapshot;
- pinned snapshot reference;
- declared deterministic decision key.

If policy-local deterministic variability is needed for validation, `PolicyContext.deterministic_draw(label)` derives a keyed value from only the decision key, snapshot fingerprint and label.

No world seed or scenario universe identifier is supplied.

## 5. Runtime enforcement

A generic kernel-bearing runtime handler may not be registered for a DECISION_WINDOW process.

DECISION_WINDOW events require an event-specific policy binding.

At binding time the runtime verifies:

1. event is a DECISION_WINDOW event;
2. agent exists;
3. snapshot agent matches;
4. snapshot exactly matches the currently admitted agent-visible state;
5. scheduler has pinned the snapshot fingerprint for the period;
6. event snapshot reference matches that fingerprint;
7. snapshot effective time matches the scheduled event.

During dispatch the policy is called with only PolicyContext and executes outside the token-bearing kernel mutation context.

## 6. Hostile API test

The validation policy deliberately attempts to read:

- kernel;
- world/world_module;
- seed/master_seed;
- hidden_state;
- resources;
- run_identity;
- universe_id/version;
- scheduler;
- raw state.

Those fields are absent from PolicyContext.

Equivalent hidden-world fields are also absent from DecisionSnapshot.

The fixture includes a hidden resource with quantities 999/900/800/777 and universe identity RICH-HIDDEN/v9. None appears in the snapshot representation.

The test also confirms UNKNOWN remains UNKNOWN with no value.

## 7. Security boundary

This is an **API and causal-information firewall**, not a hostile-code sandbox.

Arbitrary Python executing in the same interpreter can potentially use language/runtime introspection or import unrelated modules. If future policy code is untrusted rather than governed LOOM code, process/container isolation would be a separate security requirement.

The present requirement is that admitted policy code cannot receive hidden world state through the supported policy interface.

## 8. Relationship to autonomous policy gate

This decision implements the policy-input firewall and hostile interface test only.

It does not authorize autonomous underwriting, investment, migration or other decision policies. Request schemas, UNKNOWN reason codes, authored economic tables, calibration/validation and policy behavior remain later gates.
