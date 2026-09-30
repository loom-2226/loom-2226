# CIVPROP Actor State and Budgets V1

Status: **GAP-002 closure evidence**

This document records the tested Actor State V1 boundary used by the locked CIVPROP
Engine V1 path. It does not add a new propagation architecture. It replaces the two
GAP-002 compatibility placeholders in the existing compiled input and Hybrid V1 path.

Authoritative executable artifacts:

- `engineering/civprop/contracts/actor_state_v1.py`
- `engineering/civprop/compile_inputs_v1.py`
- `engineering/civprop/run_civprop_v1.py`
- `engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/`
- `engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP2_ACTOR_STATE_SEED42.json`
- `engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP2_BASELINE_MANIFEST.json`

The machine-readable gap authority remains
`engineering/civprop/gap_register_v1.json`.

## Contract semantics

Actor State V1 keeps these concepts distinct:

- identity and actor type;
- ownership and operation;
- scoped access rights and contracts;
- provider/service access;
- installed versus acquired capability;
- experience;
- spendable allocation;
- committed funds;
- owned infrastructure;
- relationships.

A fact collection can be `KNOWN_RECORDS`, `KNOWN_NONE`, or `UNKNOWN`.
Those states are not interchangeable.

Possession is not inferred from access. A provider/service path does not become
installed capability. A timeline frontier date does not grant actor capability.
Missing evidence remains UNKNOWN.

## 2026 AUS boundary

The default compiled actor is `AUS` with actor type `STATE`.

The general CIVPROP project-decision spendable allocation is explicitly:

- status: `UNKNOWN`;
- amount: null;
- unit: null;
- scope: `GENERAL_CIVPROP_PROJECT_DECISION_BUDGET`.

The observed AUD 42 million Roo-ver commitment is preserved separately as
`AUS_ROOVER_42M_COMMITMENT`, scoped to
`ROO_VER_DEVELOPMENT_BUILD_OPERATION`.

That commitment is not Australian GDP, national capital, generic government
expenditure, or a pool of scenario credits. The engine cannot use it to fund an
unrelated generic CIVPROP project.
The admitted Roo-ver evidence records a scoped Australia/NASA/CLPS/Intuitive
Machines service path. It does not grant sovereign lunar transport capability.
Fleet SPIDER evidence remains preserved in authority context but is not converted
into an Australian government entitlement.

The previous default compiled values:

- `starting_capital = 70 scenario_credit`;
- `annual_capital_inflow = 8 scenario_credit`;
- generic Method Lab capability rows relabeled as AUS;

are removed from the default compiled input.

## Replay and future change

Actor State V1 changes only through versioned events. V1 admits:

- `BUDGET_ALLOCATION_SET`;
- `CAPABILITY_SET`.

Every event carries an event ID, year, actor ID, payload, provenance class and
provenance reference. The runtime view is pure replay over the declared boundary
and events.

The runner also reconstructs actor finance from declared inputs plus committed
Hybrid V1 decisions. It emits:

- `actor_state_boundary`;
- annual `actor_states`;
- `actor_state_events`;
- replayable `actor_transactions`.

A project commitment must replay against a KNOWN spendable allocation with the
correct unit and sufficient amount or the runner fails closed.
## Seed-42 regression consequence

With the current compiled 2026 boundary, AUS has neither a known generic spendable
allocation nor generic installed/acquired Method Lab capabilities. The seed-42
regression therefore produces:

- 44 annual location states;
- 11 annual actor states;
- 11 actor decisions;
- 0 commissioned facilities;
- 0 actor transactions;
- 45 events;
- 10 migration flows.

All 11 actor decisions are `WAIT` and include
`SPENDABLE_ALLOCATION_UNKNOWN`.

This is intentional. The previous seven-facility behavior depended materially on
the GAP-002 placeholders. Removing unsupported money and capability must be allowed
to change the realization.

This remains **not a forecast**. GAP-003 through GAP-015 remain open, including
synthetic transport accessibility, demand signals, project economics and other
later mechanisms.

## Closure evidence

GAP-002 is CLOSED only in the registered V1 sense: a tested, versioned mechanism
exists for the present development boundary, with explicit UNKNOWN preservation,
provenance, replay and removal of the identified placeholders.

Closure does not claim that Australia has no future off-world budget or capability.
It means CIVPROP no longer invents either one at the 2026 boundary.
