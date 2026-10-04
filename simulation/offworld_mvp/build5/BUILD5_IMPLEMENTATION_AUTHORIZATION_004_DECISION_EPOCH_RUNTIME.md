# Build 5 Implementation Authorization 004 — Governed Decision-Epoch Runtime

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “Go 1” following the FRD deployment-order assessment  
**Scope:** persistent chained decision epochs over one kernel state

## 1. Authorized purpose

Implement the smallest runtime extension needed for repeated autonomous decision cycles over one persistent simulation state while preserving the existing immutable DecisionSnapshot firewall and sealed scheduled-execution boundary.

The authorized pattern is:

`persistent state -> begin epoch -> configure fresh scheduler plan -> freeze decision snapshot(s) -> seal -> decisions/actions/world transitions -> verified epoch result -> close epoch -> persistent state -> next epoch`.

## 2. Required semantics

A decision epoch shall:

- use a fresh scheduler plan and fresh DecisionSnapshot references;
- preserve one persistent kernel/world state across epochs;
- cryptographically link each completed epoch to the prior epoch result;
- retain exact plan, initial-state, final-state, execution and result fingerprints;
- release the scheduler seal only through verified successful epoch completion;
- keep governed world mutators blocked between epochs once an epoch chain has started;
- detect raw state tampering between epochs and between epoch-open and seal;
- allow scheduler-plan construction between epoch-open and seal without treating plan construction as world-state mutation.

## 3. Existing firewall remains normative

This authorization does not permit:

- mutable policy views of live kernel state;
- kernel-bearing DECISION_WINDOW handlers;
- policies querying hidden scenario truth;
- policies seeing scheduler/world/random-state internals;
- mutation of world state from policy execution;
- changing an already frozen DecisionSnapshot;
- bypassing scheduler validation.

Each policy invocation continues to receive only an immutable DecisionSnapshot and opaque deterministic decision key.

## 4. Persistent chain identity

The runtime shall record a stable decision-epoch chain identity.

Each completed epoch record shall include at minimum:

- chain identity;
- epoch identity and ordinal;
- parent epoch result fingerprint, except for the root epoch;
- scheduler plan fingerprint;
- epoch initial fingerprint;
- epoch final fingerprint;
- execution fingerprint;
- result fingerprint.

Duplicate epoch identities are prohibited.

## 5. Boundary integrity

After the first epoch begins, direct governed world mutation outside scheduled-event context shall remain blocked, including between completed epochs.

A persistent-state fingerprint excluding scheduler-plan state shall be used to distinguish:

- legitimate scheduler configuration; from
- illegitimate world-state mutation.

The next epoch may begin only if the persistent state still matches the verified prior epoch boundary.

The epoch may seal only if persistent state still matches the state captured when that epoch opened.

## 6. Failure behavior

A failed or tampered epoch shall not be recorded as successfully completed and shall not silently release the execution seal.

A successful epoch may release the seal only after:

- scheduler plan identity remains unchanged;
- methodology invariants pass;
- final state fingerprint is computed;
- immutable scheduled result is constructed;
- epoch-chain linkage is recorded.

## 7. Structural test target

The implementation shall demonstrate on one persistent kernel that:

1. Epoch 1 executes a public publication decision and publication transition;
2. the financier state changes only through that legitimate publication;
3. Epoch 1 closes and records its hashes;
4. Epoch 2 opens from that persistent post-publication state;
5. a fresh financier DecisionSnapshot contains the newly admitted information/belief;
6. Epoch 2 executes the autonomous financier decision and its governed financing consequence;
7. Epoch 2 parent linkage equals Epoch 1 result fingerprint;
8. stale pre-publication snapshots are rejected;
9. direct method mutation between epochs is rejected;
10. raw-state tampering between epochs is detected;
11. raw-state tampering after epoch-open but before seal is detected;
12. repeating the same epoch chain produces the same chain records and final state.

## 8. Explicitly outside scope

This authorization does not add:

- sponsor/operator autonomy;
- surface prospecting;
- new economic or observation parameters;
- a continuous mutable event loop;
- asynchronous policies;
- runtime LLM agents;
- concurrency;
- rollback/recovery after failed epochs;
- dynamic Agent creation;
- production forecasting.

## 9. Standing

This is runtime-mechanics authorization only.

Passing Test 004 establishes repeated governed decision-cycle capability. It does not empirically validate any Agent policy or economic/scientific parameter.
