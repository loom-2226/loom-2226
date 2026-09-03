# LOOM 2226 — Navigator Phase 2 Extraction Map v1.0

**Status:** COMPLETE — Gate A PASS  
**Governing plan:** `LOOM_2226_GIS_Navigator_Convergence_Architecture_and_Work_Plan_v1.0.md`  
**Branch:** `feature/gis-navigator-convergence`  
**Qualification head:** `e74a5c1bdd94c89c6f9a704fb559d17024e4d6d7`  
**Date:** 2026-09-03

## 1. Objective

Phase 2 extracted a stable navigation-domain boundary without changing authoritative Navigator physics or campaign authority.

The frozen `src/loom_navigator_core.py` and its embedded Sequence-H implementation remain the authoritative numerical implementation. The new `src/loom/navigation/` package adapts, validates, types and exposes that implementation; it does not reproduce the physics.

**Gate A is closed.** The extracted service path reproduces a frozen completed flight's canonical runtime hash and exact post-flight campaign state, while the frozen MVP, K1 and CIVSTATE regression suites remain PASS.

## 2. Resulting decomposition

### DOMAIN LOGIC

Authoritative navigation behavior remains in the frozen implementation:

- Sequence-H loading through `_load_core(...)`, including its embedded integrity check;
- mission validation / normalization through `validate_and_normalize_mission(...)`;
- canonical dependency and route-row processing;
- route candidate generation through outer-core `_candidate_plans(...)`;
- final deterministic flight solving through `target_determinism_gate(...)`;
- underlying physics and ephemeris calculations.

The extraction layer delegates to these functions rather than recreating them.

### STATE / PERSISTENCE

Campaign persistence remains outside the navigation domain service in Phase 2.

The outer Navigator still owns:

- campaign state files and backups;
- `HistoryLedger` records and replay history;
- atomic persistence;
- job/cargo/reward lifecycle;
- committed campaign epoch and location authority.

`execute_flight(...)` is now extracted only as a **pure authoritative arrival-state result**. It performs no state-file write and no ledger append. The returned result explicitly identifies persistence ownership as `CAMPAIGN`. Integration of that result into the authoritative campaign transaction belongs to Phase 6.

### PRESENTATION / USER INTERACTION

Legacy browser HTML, terminal formatting, prompts, candidate selection and commit confirmation remain in the legacy application during Phase 2. They are not navigation-domain authority and are intentionally not copied into the service package.

## 3. Canonical navigation boundary

`src/loom/navigation/` now contains:

- `contracts.py` — canonical typed contracts;
- `service.py` — `LegacyNavigationService` facade;
- `ephemeris.py` — read-only Sequence-H canonical ephemeris/dependency adapter;
- `execution.py` — non-persisting authoritative arrival-state adapter.

### Canonical contracts

The Phase-2 boundary exposes:

- `NavigationRequest`
- `NavigationContext`
- `RouteCandidate`
- `FlightPlan`
- `FlightExecutionResult`
- `EphemerisSnapshot`
- `TrajectorySegment`
- `ArrivalState`

Stable fields are promoted and validated while the complete legacy data remains available in opaque `payload` fields during the transition. No unknown physics-bearing legacy data is silently discarded.

### Service operations

`LegacyNavigationService` now implements the required Phase-2 interface:

- `discover_routes(...)` → frozen `_candidate_plans(...)`;
- `plan_flight(...)` → discovery plus deterministic compilation;
- `compile_flight(...)` → frozen Sequence-H `target_determinism_gate(...)`;
- `execute_flight(...)` → pure arrival-state transition using frozen state helpers, with no persistence;
- `get_ephemeris(...)` → Sequence-H `build_canonical_dependency_index(...)`, with no independent provider/physics implementation;
- `get_flight_geometry(...)` → authoritative compiled runtime geometry without recalculation.

`src/loom_navigator.py` exposes `load_navigation_service()` while preserving existing CLI and self-test behavior.

## 4. Ephemeris qualification architecture

Because the ChatGPT execution environment is not the production ephemeris acquisition host, GitHub Actions now provides an independent internet-connected qualification path.

`LOOM Ephemeris Provider Qualification` reaches NASA/JPL Horizons and normalizes fixed-epoch provider data without becoming runtime authority.

Qualified fixed epoch: `2226-08-22 00:00`

Qualified targets include:

- Ceres (`1;`);
- Mars (`499`);
- Neptune system barycenter (`8`).

Neptune system barycenter is intentionally used for the outer-system qualification semantics rather than forcing Neptune body center.

Provider identification: `NASA/JPL Horizons API`, version `1.2`.

Normalized provider-probe artifact SHA-256:

`7b9192f8f515d56459de8fcf8f98686a0f3beec531e9b6e96e21e92b1f9f6d57`

This provider workflow is a qualification/acquisition facility only. Runtime navigation continues to consume its authoritative local content-addressed ephemeris cache.

## 5. Gate A qualification evidence

Gate A is implemented by `.github/workflows/phase2-gate-a.yml` and `tools/phase2_gate_a_qualify.py`.

The workflow downloads the frozen Pixel pre-clean runtime from release `v0.1.0-runtime-baseline`. Because that archive contains duplicate historical copies of some artifacts, the qualifier binds history, Sequence-H cache and the locked B1 package as one **coherent runtime bundle** from the same runtime root. It never mixes identically named files from separate archived copies.

Qualified coherent bundle:

`LOOM_TEST/`

Frozen replay:

- flight ID: `F000001`;
- route: `CERES -> MARS`;
- all 34 Sequence-H ephemeris dependencies: `CACHE_HIT`;
- ephemeris mode: `FROZEN_OFFLINE_ONLY`;
- provider-filled entries: `0`.

The extracted service reproduced the frozen deterministic runtime exactly:

`c834998cc9b8016dcbf5f0e200db781cb1d2f5dc9245c091a8f205dea280107b`

The extracted `execute_flight(...)` result also reproduced the exact frozen `FLIGHT_ARRIVED.state_after_snapshot`, whose state SHA-256 is:

`31b3b27f887b2d55ecb46e58411a987cec4168a84e5179e766282947a5a7b7b0`

The same Gate A run passed the frozen legacy regression oracles:

- MVP state transactions — PASS;
- MVP job loop — PASS;
- MVP mass accounting — PASS;
- MVP save/reload — PASS;
- MVP history chain — PASS;
- MVP menu parser — PASS;
- MVP preflight job guard — PASS;
- MVP cargo cap gate — PASS;
- MVP recovery unload — PASS;
- MVP reward sanity cap — PASS;
- MVP history atomic write — PASS;
- MVP history backup recovery — PASS;
- MVP invalid guards — PASS;
- K1 J-provider contract — PASS;
- K1 live-binding guard — PASS;
- K1 execution guard — PASS;
- CIVSTATE locked hash — PASS;
- CIVSTATE schema `1.2-runtime` — PASS;
- CIVSTATE token bindings — PASS;
- CIVSTATE place context — PASS;
- CIVSTATE route context — PASS;
- CIVSTATE read-only behavior — PASS.

At qualification head `e74a5c1bdd94c89c6f9a704fb559d17024e4d6d7`, all three branch workflows completed successfully:

1. `LOOM Python Regression` — PASS;
2. `LOOM Ephemeris Provider Qualification` — PASS;
3. `LOOM Phase 2 Gate A` — PASS.

## 6. Authority invariants after Phase 2

1. No extracted module independently performs flight physics.
2. Candidate discovery remains the frozen `_candidate_plans(...)` implementation.
3. Final solving remains frozen Sequence-H `target_determinism_gate(...)`.
4. Ephemeris exposure remains a read-only adapter over Sequence-H canonical dependency truth.
5. Navigation execution can return the authoritative arrival transition, but cannot persist it.
6. Campaign state files, history, jobs, rewards and committed epoch/location remain campaign authority until Phase 6.
7. Presentation remains outside navigation-domain authority.
8. The frozen Navigator core remains retained as the numerical implementation and regression oracle through later convergence gates.

## 7. Gate A verdict

**PASS — Phase 2 complete.**

The Navigator brain now has a stable reusable service boundary with typed contracts, route discovery, deterministic planning, ephemeris exposure, geometry exposure and non-persisting execution. Frozen legacy behavior has been reproduced at both the deterministic runtime and exact post-flight state levels.

No legacy renderer or campaign persistence path is retired by this gate.

## 8. Next phase

Proceed to **Phase 3 — define the GIS ↔ Navigation data contract**.

The next governing deliverable is `LOOM_ROUTE_LAYER_V1`, which must carry navigation truth into GIS without leaking rendering instructions or duplicating physics. Phase 3 should formalize route identity, trajectory segments, positions/epochs, maneuver markers, vehicle state and arrival state while preserving the authority boundary proven by Gate A.
