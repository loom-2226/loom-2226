# Phase 3B executable state kernel

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY

Implementation is authorized only within the scoped state-kernel and methodology-hardening boundaries of:

- `PHASE3B_IMPLEMENTATION_AUTHORIZATION_001.md`;
- `PHASE3B_IMPLEMENTATION_AUTHORIZATION_002_METHODOLOGY_HARDENING.md`.

Full autonomous-agent implementation remains gated.

## Frozen Build 4

The historical Build 4 executable baseline is frozen at:

- branch: `offworld-mvp-build4-freeze-2026-10-04`;
- commit: `8574e71810ef7cc520e160aede6ddf5379f12040`.

The active development branch extended that baseline with methodology hardening. The frozen branch was not rewritten.

The first methodology-hardened baseline is preserved at:

- branch: `offworld-mvp-build4-mvp-r1-2026-10-04`;
- commit: `82e31aaa218b36bbd1ba7ce75313fdccd0169c1a`.

The scheduler-enforced baseline is now frozen at:

- branch: `offworld-mvp-build4-mvp-r2-scheduled-2026-10-04`;
- commit: `edae7053081db20e96a00e77b752ca4c4bcecebb`.

Its validation record is `PHASE3B_KERNEL_VALIDATION_RECORD_006_SCHEDULED_RUNTIME.md`.

## Active Build 4-derived methodology baseline

The active kernel adds, without opening autonomous-policy authority:

- deterministic multi-phase / multi-rate scheduling;
- explicit coupling ownership/read/write contracts;
- SYSTEM / AGGREGATE / AGENT / ENTITY_ASSET runtime classes;
- deterministic AGGREGATE -> AGENT state reconciliation;
- an explicit MVP accounting boundary;
- verification-versus-validation standing manifests;
- deterministic scenario/parameter/uncertainty ensemble infrastructure;
- ODD-aligned model documentation and updated FRD requirements.

Existing financing, WIP/FCF, ownership, exploration, resource, population, information-firewall and deterministic replay mechanics remain under regression test.

## Run tests

From this directory:

`python3 -m unittest discover -s tests -v`

Fixtures remain scripted deterministic validation drivers. They are not autonomous agents, forecasts, empirical calibration, or evidence that the resulting civilization trajectories are scientifically validated.

## Scheduled run gate

Integrated MVP simulation runs must use `offworld_kernel.runtime.ScheduledSimulationRuntime`.

Lifecycle:

`initialize -> register scheduler couplings/events -> register runtime handlers -> seal -> run`.

Once sealed, guarded state-changing kernel methods reject direct calls. The runtime pins the initial state and scheduler plan, executes handlers only inside token-bearing scheduler contexts, rejects pre-run tampering, rejects plan mutation, and is single-use. Direct low-level calls on an unsealed kernel remain unit/fixture mechanisms only.
