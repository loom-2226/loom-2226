# Phase 3B Build 4 MVP R2 Scheduled Baseline Record

**Status:** FROZEN SCHEDULER-ENFORCED BASELINE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Baseline branch:** `offworld-mvp-build4-mvp-r2-scheduled-2026-10-04`
**Baseline commit:** `edae7053081db20e96a00e77b752ca4c4bcecebb`
**Predecessor baseline:** `offworld-mvp-build4-mvp-r1-2026-10-04` @ `82e31aaa218b36bbd1ba7ce75313fdccd0169c1a`

## Decision

The scheduler-bypass lien from Validation Record 005 is closed for integrated MVP runs.

Build 4 MVP R2 preserves the R1 methodology/accounting baseline and adds an enforced sealed runtime boundary:

- initialization is completed before seal;
- scheduler couplings/events and runtime handlers are registered before seal;
- initial-state and scheduler-plan fingerprints are pinned;
- the kernel enters strict scheduled-execution mode;
- guarded state-changing methods reject direct calls after seal;
- only token-bearing scheduler-dispatched handler contexts may mutate state;
- raw state or plan tampering invalidates the run;
- the runtime is single-use;
- the kernel remains strict after completion.

## Validation

The governing validation record is:

`PHASE3B_KERNEL_VALIDATION_RECORD_006_SCHEDULED_RUNTIME.md`.

At validation:

- 53 tests passed from a fresh Git archive on `quantifactus`;
- the integrated aggregate-resolution fixture executed through `ScheduledSimulationRuntime`;
- a direct post-run transfer was rejected;
- the scheduled result remained `NOT_EMPIRICALLY_VALIDATED`.

## Meaning

This baseline establishes the supported execution path for integrated MVP simulation runs.

It does not authorize autonomous decision policies and does not constitute empirical validation of civilization behavior.

Legacy unsealed low-level kernel calls remain legitimate only for initialization and bounded component/unit validation.

Future Phase 3B work continues on `offworld-mvp-phase3` and must identify whether it preserves, supersedes or invalidates R2 behavior.
