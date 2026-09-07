# LOOM 2226 — Stage F-PA-4 Campaign True-State Audit

Date: 2026-09-08  
Status: **Audit evidence — feature branch / NON-CANON until governed merge**

## Authority

This audit is grounded in the live GitHub feature branch. The source-defined canonical state fixture is produced by `src/loom_navigator_core.py::_new_state`; persistent flight commits are governed by `src/loom/campaign/execution.py`; coverage is classified by `src/loom/campaign_true_state_audit.py` and tested by `tests/test_campaign_true_state_audit.py`.

GitHub documentary authority applies. Chat/model memory is not a source of record.

The actual current player campaign JSON is runtime-local/preserved state and is **not claimed here to be Git-tracked**. This document audits the governed state contract/schema and persistence behavior, not the player's current instance values.

## CI evidence

GitHub Actions run `34158549628` at commit `8fa5ca20d69b16751e99957ed3eec7fe90fb2877` passed the unit regression suite, including the F-PA-4 source-defined-state audit.

## What the canonical campaign state already persists

The source-defined RC6/Sequence-H state persists:

- campaign identity and ship identity;
- `state_id`, state hash and monotonic `revision`;
- authoritative `epoch_utc`;
- semantic `location_token` and campaign status;
- fixed non-remass mass, variable cargo, remass capacity, current remass and wet mass;
- fusion-fuel model status, with quantity currently open/null;
- thermal model status and last declared action, but no quantitative thermal state;
- configuration identity/hash;
- placeholder ship condition / destroyed flag;
- a semantic `kinematic_boundary` such as `BODY_RENDEZVOUS`;
- `last_flight` and `last_reconciliation` provenance/history pointers;
- explicit Python state authority declaration.

`src/loom/campaign/execution.py` validates stale-state protection, exact one-step revision advance, non-backward campaign time, flight provenance hashes and atomic state/history persistence. It does not add navigation physics.

## Simulator true-state gap matrix

### Persisted now

- campaign clock: **PERSISTED**;
- semantic location / high-level hold state: **PERSISTED, BUT NOT A 6D PHYSICAL STATE**;
- mass/remass/cargo accounting: **PERSISTED**;
- campaign transition/history provenance: **PERSISTED**.

### Open or partial models

- fusion-fuel quantity: **OPEN MODEL / NULL**;
- thermal: **STATUS/ACTION ONLY**, no temperature, stored heat energy or heat-load state;
- ship condition: **PLACEHOLDER**, not a general fault/damage dynamics model;
- kinematic boundary: **SEMANTIC**, not position/velocity/orientation authority.

### Missing from canonical campaign true state

- physical position + velocity + reference frame;
- attitude/orientation + angular rate;
- center of mass / inertia tensor / time-varying mass properties;
- propulsion and actuator state, including thrust vector and RCS state;
- quantitative electrical power generation/load/storage state;
- quantitative thermal state;
- explicit mutable metric-drive state;
- active trajectory/solution binding;
- guidance state and control-command state;
- docking/proximity/landing/local-flight state;
- sensor measurements;
- estimated navigation state and covariance;
- traffic clearance state;
- structured general fault state.

## Critical boundary

`location_token`, `status`, `kinematic_boundary`, `last_flight` and history records **must not be used to reconstruct or invent current 6D vehicle state**.

The live vehicle currently has semantic campaign location authority, not full simulator-grade translational/attitude state authority. Historical trajectory samples are likewise not a substitute for a mutable current state unless a governed transition explicitly writes the resulting physical state.

This preserves the architecture:

```text
WORLD qualified physical environment
        ↓
CAMPAIGN mutable TRUE vehicle state
        ↓
SENSORS / ESTIMATED NAVIGATION
        ↓
GUIDANCE / CONTROL
        ↓
VEHICLE DYNAMICS
        ↓
new CAMPAIGN TRUE state
```

The current campaign layer implements the clock/history/accounting skeleton but not yet the full middle of that loop.

## Persistence boundary remains unchanged

F-PA-4 does **not** promote campaign SQLite. The existing canonical JSON + history chain remains authority under the current governed architecture. `LOOM_CAMPAIGN_DEV.sqlite3` remains a non-authoritative shadow/reconciliation surface.

A later campaign-schema promotion must preserve:

- exact revision/epoch monotonicity;
- stale-plan rejection;
- one canonical transition per executed flight/state event;
- atomic save/history behavior;
- provenance/hash continuity;
- Pixel split-root semantics;
- rollback/recovery behavior.

## F-PA-4 decision

The campaign system is adequate as a **canonical state-transition and accounting authority**, but it is **not yet adequate as telemetry-grade vehicle true-state authority**.

The next schema phase must add the missing true physical state explicitly rather than deriving it from location labels, rendered geometry or flight history.

No campaign value, physics constant or player state was changed by this audit.