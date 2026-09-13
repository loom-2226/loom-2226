# Experience One — typed interaction seam port note v0.1

## Disposition

`BOUNDED_PORT / PR99_PATTERN_REUSED / PR99_EXECUTOR_NOT_PORTED`

## Source

The useful pattern was recovered from PR #99 (`HUD_LOCAL_FLIGHT`):

- caller origin does not alter execution authority;
- staged review is nonexecuting;
- explicit authorization is a separate boundary;
- deterministic server/flight authority remains responsible for stateful execution.

## What was ported

`engineering/experience_one/e1_flight_interaction_contract.py`

Provider-neutral E1 contracts now cover:

1. flight intent (`destination`, `priority`, origin/provenance);
2. review of deterministic Navigator candidate references;
3. explicit human authorization bound to the exact review hash, plan number, and plan SHA;
4. generation of a Navigator execution **request** only.

The contract preserves:

- Mara/LLM calculation authority: `ZERO`;
- Mara/LLM state authority: `ZERO`;
- caller execution authority: `ZERO` until explicit authorization, then still request-only;
- planner authority: `NAVIGATOR`;
- execution authority: `NAVIGATOR_ONLY`;
- mandatory Navigator revalidation before mutation.

## What was deliberately not ported

The following PR #99 elements remain outside this seam:

- local Earth-orbital qualification session state;
- inertial burn-vector construction;
- qualification-only maneuver executor;
- browser physics/state authority;
- stale campaign assumptions;
- any direct state mutation path.

Those are not required to expose the already-qualified Ceres → Neptune Navigator path.

## Next integration step

Bind the provider-neutral contract to the existing E1/Navigator candidate-plan path so that:

`typed intent → Navigator candidates → typed review → explicit authorization → Navigator revalidation/execution`

can be proven without changing Navigator's calculation, campaign, ephemeris, clock, or execution authority.

Only after that deterministic seam is proven should the audited Mara/OpenAI adapter be inserted as one possible producer/interpreter of `FlightIntent` and review explanation.
