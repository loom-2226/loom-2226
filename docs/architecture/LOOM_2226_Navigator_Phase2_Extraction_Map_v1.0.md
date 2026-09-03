# LOOM 2226 — Navigator Phase 2 Extraction Map v1.0

**Status:** Active implementation map for Phase 2 of the GIS / Navigator Convergence Architecture and Work Plan v1.0.  
**Branch:** `feature/gis-navigator-convergence`  
**Date:** 2026-09-03

## 1. Objective

Extract a stable navigation-domain boundary without changing authoritative Navigator behavior.

The frozen `src/loom_navigator_core.py` remains the authoritative implementation during this phase. New modules must delegate to it rather than reproduce physics, state transitions or deterministic flight calculations.

## 2. Observed current decomposition

### DOMAIN LOGIC

Observed authoritative navigation behavior includes:

- the embedded Sequence-H module loaded by `_load_core(...)` with an embedded SHA-256 integrity check;
- mission validation / normalization through `validate_and_normalize_mission(...)`;
- canonical dependency / route-row processing inside Sequence H;
- direct candidate generation through outer-core `_candidate_plans(...)`;
- final deterministic flight solving through `target_determinism_gate(...)`;
- physics and ephemeris calculations reached through the embedded Sequence-H implementation.

These remain authoritative and are not reimplemented in the extraction layer.

### STATE / PERSISTENCE

The outer Navigator currently owns campaign-state reconciliation, backup/state files, compressed history, flight commit/arrival records and replay support. Observed examples include `HistoryLedger`, campaign setup, state stamping, replay, mass/remass reconciliation and state advancement.

This responsibility remains in the legacy outer core during the first extraction slice.

### PRESENTATION

The legacy runtime still produces browser HTML/report artifacts and terminal-formatted candidate/flight output. These are explicitly not part of the new navigation-domain authority.

### USER INTERACTION

Interactive terminal prompts, candidate selection, commit confirmation and main-loop orchestration remain in the legacy outer core. They are not copied into domain services.

### QUALIFICATION / TEST

The frozen runtime exposes:

- `_mvp_self_test()`;
- `_k1_self_test()`;
- `_civstate_self_test(...)`.

Those remain the authoritative legacy regression oracles while new service-boundary unit tests are added under `tests/`.

### LEGACY

The monolithic outer application, embedded Sequence-H packaging and browser renderer are retained unchanged until later convergence gates. Their presence during Phase 2 is intentional.

## 3. New canonical boundary

Phase 2 now introduces `src/loom/navigation/`.

### Contracts

`contracts.py` defines the first canonical typed objects required by the governing convergence plan:

- `NavigationRequest`
- `NavigationContext`
- `RouteCandidate`
- `FlightPlan`
- `FlightExecutionResult`
- `EphemerisSnapshot`
- `TrajectorySegment`
- `ArrivalState`

During extraction each contract preserves the complete legacy result in an opaque `payload`. Stable fields are promoted and validated, but legacy payloads are not discarded or silently rewritten.

### Service facade

`LegacyNavigationService` is a behavior-preserving anti-corruption layer over the frozen core.

Implemented service operations:

- `discover_routes(...)` delegates to existing `_candidate_plans(...)`;
- `plan_flight(...)` composes discovery and deterministic compilation;
- `compile_flight(...)` delegates to existing `target_determinism_gate(...)`;
- `get_flight_geometry(...)` exposes authoritative runtime flight geometry without recalculation.

Explicitly not yet extracted:

- `execute_flight(...)` — campaign execution/persistence remains in the outer Navigator;
- `get_ephemeris(...)` — provider extraction remains pending.

Both fail closed rather than inventing duplicate authority.

`src/loom_navigator.py` now exposes `load_navigation_service()` while preserving its existing command-line and self-test behavior.

## 4. Authority invariants

1. No new module performs flight physics.
2. No new module independently changes campaign state.
3. Candidate discovery remains `_candidate_plans(...)` from the frozen core.
4. Final solving remains `target_determinism_gate(...)` from Sequence H.
5. The service layer may validate, adapt, type and expose results; it may not alter authoritative numeric outputs.
6. Legacy dictionaries are retained losslessly inside canonical contract payloads during the extraction transition.
7. Unsupported extractions fail closed.

## 5. Qualification status

Local Phase-2 unit suite executed before commit:

```text
5 tests
PASS
```

Coverage includes:

- request-to-legacy mission adaptation;
- UTC contract validation;
- route-discovery delegation;
- deterministic-plan delegation;
- fail-closed campaign execution boundary.

This does **not** replace the frozen Navigator MVP/K1/CIVSTATE regression suites.

## 6. Remaining work to Gate A

Gate A is not declared yet.

Required next slices:

1. extract the ephemeris/provider interface behind the canonical service;
2. separate campaign execution from terminal interaction without duplicating state authority;
3. add integration tests that call the real frozen core through `load_navigation_service()`;
4. compare authoritative route and final-flight outputs against frozen golden fixtures;
5. rerun MVP, K1 and CIVSTATE self-tests plus the new service integration suite;
6. declare Gate A only when service-path and legacy-path outputs are identical for qualified fixtures.

Until then, the old Navigator remains the production execution surface and qualification oracle.
