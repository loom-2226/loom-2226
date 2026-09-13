# Experience One — Neptune qualification execution plan v0.1

Status: IMPLEMENTATION IN PROGRESS / NO PASS CLAIM

The empirically tested E1.0 Spike B demonstrated the exact campaign continuity property needed here using the existing Navigator path against disposable campaign artifacts. The production closure branch will reuse that proven harness logic rather than invent a second flight executor.

## Immediate execution

1. Bring the tested disposable-campaign harness forward unchanged as qualification support.
2. Seed a disposable qualification campaign using Navigator's own `_new_state(...)`; the current governed constructor starts Wayfarer at `CERES` in `READY_HOLD`.
3. Feed that disposable campaign to the tested continuity harness with destination `NEPTUNE_SYSTEM`.
4. Require normal Navigator direct-navigation plan selection and explicit commit authorization.
5. Capture `FLIGHT_COMMITTED`, `FLIGHT_ARRIVED`, post-restart Neptune location, plan SHA, and replay result.
6. Hard-fail if any live campaign artifact changes.

## Temporal honesty

Navigator's current `_new_state(...)` baseline epoch is `2027-06-15T02:00:00Z`. The first closure run therefore qualifies the **flight/state/persistence seam**, not a 2226 campaign epoch. We will not relabel a 2027 qualification run as 2226 world execution. The 2226 world/context seam remains separately visible and must be reconciled or explicitly bounded before the final zero-instruction Experience One claim.

## Falsifier

The flight seam is not closed if the disposable run lacks either `FLIGHT_COMMITTED` or `FLIGHT_ARRIVED`, does not restart at Neptune, fails replay, mutates the live campaign, or requires a second state/flight authority.