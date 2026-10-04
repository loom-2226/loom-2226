# Phase 3B Kernel Validation Record 006 — Sealed Scheduler-Only MVP Runtime

**Status:** PASS FOR SCHEDULER-ENFORCED BUILD-4-DERIVED MVP BASELINE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Development branch:** `offworld-mvp-phase3`
**Validated branch head before this record:** `3bc783a9dd7d9ca9f409160da519ad9743233dc7`
**Predecessor methodology baseline:** `offworld-mvp-build4-mvp-r1-2026-10-04` @ `82e31aaa218b36bbd1ba7ce75313fdccd0169c1a`

## 1. Purpose

Close the remaining execution-boundary lien from Validation Record 005:

> inherited Build 2–4 low-level methods remained directly callable even though the integrated methodology fixture used the deterministic scheduler.

The supported integrated MVP execution path is now a sealed `ScheduledSimulationRuntime`.

## 2. Test result

Executed on `quantifactus` from a fresh Git archive of `origin/offworld-mvp-phase3`.

`python3 -m unittest discover -s tests -v`

**53 tests executed; 53 passed.**

All Build 2–4 regression tests and methodology tests remain green.

## 3. Supported run lifecycle

The integrated run lifecycle is now:

`initialize -> register scheduler couplings/events -> register runtime handlers -> seal -> scheduled run -> immutable run result`.

Before seal, direct low-level state construction remains permitted for initialization and bounded unit/validation fixtures.

At seal:

- the methodology-state fingerprint is pinned;
- the scheduler-plan fingerprint is pinned;
- strict scheduled-execution mode is enabled;
- a private runtime execution token is created.

After seal, guarded state-changing methods reject direct invocation unless the call executes inside a scheduler-dispatched event context carrying that token.

## 4. Guarded mutation surface

The strict gate covers the Build 4-derived state-changing surface, including:

- node/account/project/commitment construction;
- transfers, disbursement, spending and capitalization;
- Agent/resource registration;
- observation, financing request/decision, extraction, sale and migration;
- Earth resource constraints/reservations;
- paid exploration and exploration resolution;
- surplus disposition;
- ownership registration/distribution;
- supply-capacity consumption;
- WIP creation/addition/commissioning;
- depreciation/amortization;
- carried reservations and commitment lapse;
- boundary purchases/resource consumption;
- SYSTEM/AGGREGATE/ENTITY registration;
- AGGREGATE -> AGENT resolution.

Read-only fingerprints, invariant checks and deterministic keyed draws remain callable.

## 5. Runtime token

A scheduled event context requires the private token issued at runtime seal.

Calling `scheduled_event_context(...)` without that token fails.

This prevents ordinary callers from manufacturing a valid scheduled mutation context merely by naming an event.

The private token is an execution-API guard, not a claim that hostile Python introspection is impossible.

## 6. Direct scheduler bypass blocked

After seal, invoking `kernel.scheduler.run(...)` directly with a handler that attempts kernel mutation fails because that handler does not possess the runtime execution token/context.

Only `ScheduledSimulationRuntime.run()` dispatches handlers within the admitted context.

## 7. Tamper detection

The runtime checks the sealed initial methodology fingerprint immediately before execution.

A raw state mutation after seal and before run causes the run to abort.

The runtime also pins the scheduler plan fingerprint. Adding or changing scheduled events after seal causes the run to abort before execution. A plan change during execution is detected before a valid result is returned.

## 8. Single-use result boundary

The scheduled runtime is single-use.

After completion:

- the kernel remains in strict scheduled-execution mode;
- direct guarded mutation remains blocked;
- a second `run()` call fails;
- the returned run result pins the execution log and fingerprints.

The run result carries:

- `run_mode = SCHEDULED_MVP`;
- scheduler contract version;
- plan fingerprint;
- initial fingerprint;
- final fingerprint;
- execution log;
- event results;
- verification status;
- validation status;
- result fingerprint.

## 9. Integrated methodology fixture

The prior aggregate-resolution methodology fixture now runs through `ScheduledSimulationRuntime`, not by calling `scheduler.run()` directly.

Observed execution order:

`resolve -> check -> snapshot`.

Observed strict-run fingerprints:

- plan: `d12fe280aaef5571254e02945c97fc5ce04b0c2fdb8c33cd228555dd9f11f6c4`;
- initial: `fd9d8d3286eaf76ea61cabb8511c39617fc86d6e7e389a8963155038f592acf4`;
- final methodology: `2505bffe4b29e444ef0621ffdb9ced9774618cf2275b8879113c9c8b9ab1503d`;
- scheduled result: `b9de6b23e95ecf08088eb4b04fa2617aa6e1ea0c3858981e1bea97df6979599a`.

A post-run direct transfer fails with:

`InvariantError: direct mutation blocked in scheduled-run mode: transfer`.

## 10. Regression compatibility

Legacy Build 2–4 unit tests continue to use unsealed kernels where appropriate.

This is intentional. Direct low-level invocation remains useful for local component verification.

Such an unsealed fixture is not a supported integrated simulation run and cannot produce the scheduler-enforced run standing described above.

## 11. Verification / validation standing

The runtime emits:

`verification_status = SCHEDULED_EXECUTION_VERIFIED`.

It continues to emit:

`validation_status = NOT_EMPIRICALLY_VALIDATED`.

Scheduler enforcement improves causal/replay integrity. It does not empirically validate financing, migration, settlement, production, resource economics or long-horizon civilization behavior.

## 12. Remaining liens

This pass closes the specific scheduler-bypass lien from Record 005, but Phase 3B remains open.

Important remaining work before autonomous policies includes:

1. defining the first bounded autonomous-policy contract and its validation targets;
2. determining how future DECISION_WINDOW handlers consume pinned snapshots without hidden-state leakage;
3. expanding scheduler ownership enforcement from declared read/write contracts toward state-diff enforcement where practical;
4. preserving causality when dynamically scheduling future sub-period events;
5. empirical calibration/validation design for whichever behavioral policy is introduced first.

## 13. Result

For an integrated MVP run, the scheduler is no longer merely present or conventional.

**After initialization is sealed, the supported world-mutation path is scheduler-dispatched execution through `ScheduledSimulationRuntime`.**

Direct low-level methods remain available only on unsealed kernels for initialization and bounded component validation.
