# Phase 3B Scheduled Execution Gate Decision 001

**Status:** ACCEPTED DESIGN DECISION / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Scope:** Build 4-derived Offworld MVP execution boundary

## 1. Decision

A real MVP simulation run shall execute state-changing transitions only through the sealed deterministic scheduler runtime.

Low-level kernel mutation methods remain callable before runtime seal for initialization and remain directly callable in unsealed deterministic unit/validation fixtures. They are **not** a supported simulation-run execution path after seal.

## 2. Execution lifecycle

The supported lifecycle is:

`initialize -> register systems/couplings/events -> register runtime handlers -> seal -> scheduled run -> immutable run result`.

At seal:

- the initial methodology fingerprint is pinned;
- the scheduler plan fingerprint is pinned;
- the kernel enters strict scheduled-execution mode;
- a private runtime execution token is created.

After seal:

- guarded state-mutating kernel methods reject direct calls;
- scheduled mutation context requires the runtime token;
- raw state changes before run are detected by initial-fingerprint comparison;
- scheduler-plan changes before or during run invalidate the run;
- the runtime is single-use;
- the kernel remains strict after completion.

## 3. Initialization boundary

Direct state construction before seal is initialization, not simulated elapsed-world behavior.

Initialization must still obey schema/invariant rules and preserve input/scenario lineage. This decision does not authorize arbitrary empirical defaults.

## 4. Scheduler handlers

Handlers are deterministic process adapters bound to registered SYSTEM/AGGREGATE scheduler process IDs.

A handler may call admitted kernel transitions only while executing inside its scheduled event context.

This does not make the handler an autonomous Agent policy. Autonomous decision-policy authority remains gated.

## 5. Validation fixtures

Legacy Build 2–4 unit fixtures may continue to call low-level methods directly when the kernel is unsealed. Those calls are component verification, not supported full-run execution.

Integrated MVP fixtures intended to represent a run shall use `ScheduledSimulationRuntime`.

## 6. Run standing

A successful scheduled run emits:

- run mode `SCHEDULED_MVP`;
- scheduler contract version;
- pinned plan fingerprint;
- pinned initial fingerprint;
- final fingerprint;
- ordered execution log;
- event results;
- verification status;
- validation status;
- result fingerprint.

The current validation status remains `NOT_EMPIRICALLY_VALIDATED`.

## 7. Non-claims

This gate does not:

- authorize autonomous policies;
- empirically validate behavior;
- prevent deliberate private-attribute tampering by hostile Python code;
- make Python memory immutable;
- replace conservation or causal-lineage checks.

It defines and enforces the supported execution API and causes unauthorized/direct mutation paths to fail in sealed-run mode.
