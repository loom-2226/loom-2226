# CIVPROP Propagation Method Lab V1

Status: engineering test scaffold; synthetic; non-canon; non-production.

## Purpose

Freeze one deliberately small Earth-Orbit-Luna/cislunar world so multiple
propagation techniques can be tested against identical inputs and emit the same
result shape.

This lab does not select an engine and does not attempt to reproduce the 2226 Atlas.

## Frozen world

Horizon: 2026-2036, annual inspection.

Locations:

- EARTH_SURFACE
- EARTH_ORBIT
- LUNA_SURFACE
- CISLUNAR_FREE_SPACE

Synthetic actors:

- LAB_PUBLIC
- LAB_COMMERCIAL

The fixture includes:

- explicit initial population, capital and capacity state;
- a technology frontier separate from actor capability and access;
- time-varying synthetic accessibility with explicit UNKNOWN periods;
- generic project archetypes rather than destination-specific scripted projects;
- exogenous demand signals;
- one actor-visible lunar-water prior;
- a separate evaluator-only resource-truth file.

All numeric values are scenario fixtures chosen to exercise mechanisms. They are not
empirical claims, canon, calibrated economics or forecasts.

## Candidate-engine boundary

Each candidate implements the small PropagationEngine protocol in contracts.py:

    engine_id
    engine_version
    run(bundle, seed) -> LabResult

Every candidate receives the same LabBundle and emits
CIVPROP_METHOD_LAB_RESULT_V1.

No candidate may write production databases or treat the evaluator truth file as
actor knowledge.

## Intentionally undecided

The lab does not decide:

- master propagation technique;
- utility or choice equation;
- system-dynamics equations;
- actor decision architecture;
- migration equation;
- opportunity-generation algorithm;
- economic closure;
- exact internal timestep;
- persistence schema.

Those are subjects of the prototype and method-fit steps.

## Common output

The shared result contract records:

- run, engine and input identity;
- annual location states;
- generated facilities;
- decisions;
- causal events;
- explicit flows.

This is narrower than final Atlas output. It is the common denominator required to
compare propagation architectures.

## Reproduce contract tests

From repository root:

    python3 -m unittest engineering.civprop.method_lab.test_contracts -v

The tests validate pinned fixture hashes, truth separation, timeline/access
separation, UNKNOWN preservation, generic project archetypes, reference integrity,
construction lag and deterministic serialization.
