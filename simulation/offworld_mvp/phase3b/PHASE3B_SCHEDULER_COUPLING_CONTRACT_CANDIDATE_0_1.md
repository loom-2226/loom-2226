# Phase 3B Scheduler and Coupling Contract Candidate 0.1

**Status:** DESIGN CANDIDATE / PRE-CONTRACT / SINGLE-AUTHORITY
**Implementation scope:** Authorized deterministic state-kernel methodology hardening

## 1. Decision

Global simulation time is owned by a deterministic scheduler. No subsystem, aggregate or agent advances global time independently.

The scheduler separates:

- simulation timestamp;
- macro period;
- phase/order;
- sub-event time;
- causal parentage.

A one-year Earth economic cadence does not imply every offworld process occurs annually.

## 2. Phase ordering

Default macro-period order:

1. OPEN_PERIOD
2. EXOGENOUS_INPUTS
3. OBSERVATION
4. INFORMATION_UPDATE
5. DECISION_WINDOW
6. ACTION_VALIDATION
7. COMMITMENT_DISBURSEMENT
8. OPERATIONS
9. MARKET_CLEARING
10. DEPRECIATION_AMORTIZATION
11. ACCOUNTING_CLOSE
12. CONSERVATION_CHECK
13. SNAPSHOT_CLOSE

A phase may contain zero or more events.

## 3. Multi-rate events

Sub-period processes may be scheduled at deterministic offsets or explicit timestamps. Examples include mission arrival, observation return, payment date, construction completion and transport arrival.

A sub-period event declares:

`event_time, phase, priority, stable_key, process_id, input_refs, parent_refs`.

## 4. Tie-breaking

Events with identical effective time and phase are ordered by:

1. explicit priority;
2. stable process/object key;
3. event identity.

Insertion order is not authority and must not affect unrelated results.

## 5. Coupling contract

Each coupled process declares:

- process_id/version;
- runtime class;
- owned state;
- read set;
- write set;
- cadence/trigger;
- phase;
- units;
- world context/perspective;
- whether coupling is one-way or two-way;
- blocking preconditions;
- invariant checks;
- event outputs.

No process may write state owned by another process except through an admitted transition interface.

## 6. Agent simultaneity

Future autonomous decisions must specify whether agents observe:

- prior-period closed state;
- same-window public information;
- already executed actions in the same window.

Until separately authorized, validation fixtures use snapshot decision semantics: all scripted decisions in a decision window consume a pinned pre-decision snapshot unless an explicit causal dependency orders them.

## 7. Randomness

Random keys include semantic identities and time keys, not scheduler queue position.

Reordering independent events must not change their draws.

## 8. Accounting close

Commitment, cash, WIP, FCF, ownership, inventory and boundary ledgers are reconciled before SNAPSHOT_CLOSE.

Depreciation/amortization occurs in the declared phase, not opportunistically inside unrelated transitions.

## 9. Failure behavior

Blocked events produce no partial mutation unless the modeled process explicitly incurs pre-failure cost.

Scheduler validation failure aborts governed comparison output. Diagnostic execution may continue only under an explicit non-governed/experimental status.

## 10. Required executable tests

- deterministic phase order;
- stable same-time tie order;
- insertion-order independence;
- sub-period event before/after semantics;
- snapshot decision-window semantics;
- accounting-close before snapshot;
- keyed random independence from queue order;
- illegal cross-owner write blocked.
