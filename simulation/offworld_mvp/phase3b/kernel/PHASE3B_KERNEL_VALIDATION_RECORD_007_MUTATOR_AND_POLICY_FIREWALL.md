# Phase 3B Kernel Validation Record 007 — Exhaustive Scheduler Mutator Gate and Decision Snapshot Firewall

**Status:** PASS FOR ITEMS 1–2 OF AUTONOMOUS-POLICY PRE-GATE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Development branch:** `offworld-mvp-phase3`
**Validated branch head before this record:** `785a98d1cbdbf7a57b3252c5a6fe14c85f87035d`
**Predecessor scheduler baseline:** `offworld-mvp-build4-mvp-r2-scheduled-2026-10-04` @ `edae7053081db20e96a00e77b752ca4c4bcecebb`

## 1. Purpose

Close the first two blockers identified before autonomous policy work:

1. prove every inherited public kernel mutator is scheduler-gated after seal, not merely representative mutation methods;
2. create and hostile-test an immutable DECISION_WINDOW policy input boundary that does not expose kernel/world/seed/hidden state.

This record does not open the autonomous-agent gate.

## 2. Test result

Executed on `quantifactus` from a fresh Git archive of `origin/offworld-mvp-phase3`.

`python3 -m unittest discover -s tests -v`

**60 tests executed; 60 passed.**

## 3. Exhaustive public execution-surface classification

The Build 4-derived methodology kernel currently exposes **61 public methods** across:

- Kernel;
- MVPKernel;
- Build3Kernel;
- Build4Kernel;
- MethodologyHardenedBuild4Kernel.

They are explicitly and exhaustively classified as:

- **45 state mutators**;
- **14 read-only/query/verification methods**;
- **2 execution-control methods**.

The regression test introspects the live class surface and requires:

`public_methods == mutators U readonly U control`.

Therefore a future public method added to the inheritance chain without an explicit execution classification causes the test to fail.

This converts the mutation gate from a manually sampled assertion into a drift-detecting execution-surface contract.

## 4. Every mutator direct-call test

After sealing an otherwise minimal `ScheduledSimulationRuntime`, the test iterates all 45 declared mutators and directly invokes each outside scheduler context.

Every call must fail with:

`InvariantError: direct mutation blocked in scheduled-run mode: <method>`.

Because the scheduler gate intercepts the method before its ordinary argument/body validation, the test can exercise the entire inherited mutation surface uniformly.

The guarded set currently includes:

`add_account, add_agent, add_aggregate, add_commitment, add_entity_asset_ref, add_node, add_project, add_resource, add_system, add_wip_expenditure, amortize_knowledge, audit, boundary_purchase, capitalize, commission_wip, consume_market_resource, consume_supply, create_carry_reservation, create_wip, decide_finance, depreciate, disburse, dispose_surplus, distribute_vehicle_to_owners, event, explore_paid, expose_agent_from_aggregate, extract, extract_bounded, lapse_carry_reservation, lapse_commitment, migrate, observe, register_vehicle_ownership, request_finance, reserve_earth_supply, resolve_exploration, sell, sell_to_market, set_resource_constraint, set_supply_capacity, spend_capex, spend_carry_reservation, spend_reserved_capex, transfer`.

This closes the scheduler-enforcement evidence gap identified in review.

## 5. Immutable DecisionSnapshot

New module:

`offworld_kernel/policy.py`.

A `DecisionSnapshot` is a frozen/slotted copied-value object containing only:

- agent id/type and node;
- period/effective time;
- the agent's own account balance;
- capabilities/objectives;
- already-held information references;
- agent-local beliefs;
- agent-held asset references;
- agent-held resource holdings;
- agent-held claim holdings;
- explicitly admitted facts.

It contains no reference to:

- Kernel or KernelState;
- ScenarioResource registry;
- scheduler;
- RunIdentity;
- universe id/version;
- world seed/master seed;
- hidden scenario state.

Collections are converted to immutable tuples and Decimal/string values.

## 6. Explicit fact knowledge state

Snapshot facts use:

- `KNOWN(value)`;
- `UNKNOWN(no value)`;
- `BLOCKED(no value)`.

Construction rejects:

- UNKNOWN/BLOCKED with a value;
- KNOWN without a value.

The hostile fixture confirms an UNKNOWN fact arrives at policy code as `state=UNKNOWN, value=None`, not zero.

## 7. DECISION_WINDOW runtime firewall

A generic runtime handler that receives `(kernel, event)` is now prohibited for any DECISION_WINDOW coupling.

Decision events instead require an event-specific policy binding containing:

- agent id;
- immutable DecisionSnapshot;
- pinned snapshot reference;
- deterministic decision key;
- policy callable.

At registration the runtime verifies:

- the event exists and is DECISION_WINDOW;
- the agent exists;
- snapshot agent identity matches;
- rebuilding admitted agent-visible state yields the identical snapshot fingerprint;
- the scheduler has pinned that fingerprint for the decision period;
- event snapshot reference matches it;
- effective time matches the scheduled event.

During dispatch, policy code receives only:

`PolicyContext(snapshot, snapshot_ref, decision_key)`.

It does **not** execute inside the token-bearing kernel mutation context.

## 8. Hostile policy test

The hostile test universe deliberately contains hidden values:

- universe id: `RICH-HIDDEN`;
- universe version: `v9`;
- hidden resource id: `RES-HIDDEN`;
- hidden resource quantities: `999 / 900 / 800 / 777`.

The policy deliberately probes PolicyContext for:

- kernel;
- world;
- world_module;
- seed;
- master_seed;
- hidden_state;
- resources;
- run_identity;
- universe_id;
- universe_version;
- scheduler;
- raw state.

Every probe is blocked by absence of the attribute.

It repeats corresponding probes against DecisionSnapshot. Those also fail.

The snapshot representation is explicitly checked not to contain the hidden universe/resource identifiers or quantities.

The test policy completes through the scheduled runtime and returns a result without receiving any hidden-world object.

## 9. Snapshot immutability and copy isolation

DecisionSnapshot, SnapshotFact and PolicyContext are frozen/slotted dataclasses.

Tests establish:

- field assignment raises `FrozenInstanceError`;
- no mutable `__dict__` is exposed;
- changing live agent beliefs after snapshot construction does not alter the snapshot;
- changing the live account after snapshot construction does not alter the snapshot;
- a stale snapshot cannot be registered if current admitted agent-visible state has changed.

## 10. Policy-local deterministic draw

PolicyContext exposes an optional deterministic draw helper based only on:

- declared decision key;
- snapshot fingerprint;
- caller label.

It does not use or expose the world seed/universe seed.

Identical snapshot + key + label replays identically; changing the label changes the keyed draw.

This is validation infrastructure, not autonomous-policy authority.

## 11. Security boundary

The firewall is an **execution/API information boundary**, not a security sandbox for arbitrary malicious Python.

Code executing in the same interpreter may be capable of Python introspection/import tricks outside the supported policy API.

If future policy implementations are untrusted code rather than governed LOOM modules, process/container isolation must be considered separately.

The present verified claim is narrower and deliberate:

> Policy code invoked through the supported DECISION_WINDOW interface is not passed kernel/world/seed/hidden-state references and receives only a pinned immutable admitted snapshot.

## 12. Documentation updates

Updated:

- `OFFWORLD_MVP_GUIDING_FRD.md`;
- `PHASE3B_SCHEDULER_COUPLING_CONTRACT_CANDIDATE_0_1.md`;
- `OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md`.

Added:

- `PHASE3B_DECISION_SNAPSHOT_POLICY_FIREWALL_DECISION_001.md`.

## 13. Remaining autonomous-policy blockers

Items 1 and 2 from the review are now closed at the stated verification level.

Still open before autonomous policy authorization:

1. resolution invariance with aggregate-only versus exposed-agent equivalent behavior;
2. governed exposure/allocation rule for how an aggregate member/share is selected;
3. ensemble reporting guardrails for probabilities/weighted summaries and variability terminology;
4. authored underwriting tables for price/revenue basis, capex, operating cost and lead time;
5. scheduler-valid property/generative coverage of all required identities;
6. boundary-position mirror reconciliation;
7. held-out/out-of-sample validation disclosure;
8. full code/Git hash in replay manifest;
9. genuine multi-rate synchronization fixture beyond timestamp ordering;
10. true multi-year staged WIP expenditure before commissioning.

## 14. Result

The scheduler gate is now exhaustively tested against its full current inherited public mutation surface, and the decision-window interface no longer hands future policy code the kernel.

**Autonomous policy authority remains closed.**
