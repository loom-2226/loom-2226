# Experience One — Neptune current execution finding v0.1

## Verified

- Protected `main` now governs the v1.2 Ceres → Neptune closure target.
- Navigator already contains the authoritative `FLIGHT_COMMITTED` → phase history → `FLIGHT_ARRIVED` path, atomic state persistence, restart recovery, and replay requirement.
- E1.0 Spike B empirically exercised that exact path to `NEPTUNE_SYSTEM` from a disposable MARS campaign and proved restart/replay while preserving the live campaign bit-for-bit.
- Navigator's own `_new_state(...)` constructor starts a fresh Wayfarer campaign at `CERES / READY_HOLD`.

## Narrow remaining proof

Run the same tested continuity path against a disposable campaign seeded by Navigator's own Ceres baseline. This is now a qualification-input problem, not a flight-authority or persistence architecture problem.

## Known boundary

Navigator's governed fresh-campaign epoch is currently 2027-06-15. Until a separate authority change reconciles that with the 2226 world layer, the first Ceres → Neptune run qualifies the deterministic flight/state/persistence seam only. It must not be represented as a 2226 campaign execution.

## Disposition

`MECHANICS_PATH_PRESENT / CERES_ORIGIN_EMPIRICAL_PROOF_PENDING`

No Ceres feature work is reopened.