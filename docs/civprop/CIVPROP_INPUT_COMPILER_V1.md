# CIVPROP Input Compiler V1

Date: 2026-10-01
Class: `class:engineering`
Status: GAP-001 through GAP-006 closed / production-facing input compilation with explicit downstream assumptions

## Decision

GAP-001 is closed by introducing one deterministic compiler that freezes promoted
LOOM authority into the locked CIVPROP Engine V1 runtime envelope.

Compiler:

```text
engineering/civprop/compile_inputs_v1.py
```

Default compiled package:

```text
engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/
```

The CIVPROP runner remains:

```text
engineering/civprop/run_civprop_v1.py
```

Runner V1.6 defaults to the compiled package rather than the original synthetic
Method Lab package and carries the closed Actor State, Accessibility,
Demand/Pressure, Project Economics and Mission/Knowledge boundaries.

## What GAP-001 closed means

The following sources are now captured read-only, frozen with hashes, and compiled
deterministically into one CIVPROP-compatible input package:

- `loom_earth`;
- `loom_solar`;
- `loom_timeline`;
- qualified lunar resource evidence;
- promoted actor/access evidence.

The compiler does not silently solve later gaps.

Where the selected engine still requires a value owned by GAP-002 or later, the
existing Method Lab placeholder is retained explicitly and registered with its owning
gap.

Therefore:

```text
real authority
+ explicit unresolved assumptions
        ->
frozen reproducible runtime input
```

is now the boundary.

GAP-001 closed does **not** mean all CIVPROP inputs are production-calibrated.

## Capture command

From repository root:

```bash
python3 engineering/civprop/compile_inputs_v1.py --capture-live
```

This performs:

```text
PostgreSQL
  BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY
        +
promoted repository evidence
        ->
authority_capture_v1.json
        ->
deterministic compile
        ->
compiled input package
```

The capture code never runs migrations or database writes.

## Frozen authority capture

Path:

```text
engineering/civprop/inputs/authority_capture_v1.json
```

Format:

```text
CIVPROP_AUTHORITY_CAPTURE_V1
```

Capture ID:

```text
EARTH_LUNA_AUTHORITY_CAPTURE_V1_2026_2036
```

Source-basis commit:

```text
f70476fb6aeead4e495d1e234b5f351f4688f954
```

The capture records hashes for all SQL queries and promoted source files used.

## Earth authority

Pinned snapshot:

```text
earth-v0-1-9934d0ac-20260925
state = VALIDATED
```

Captured Earth material includes:

- Australia area identity;
- Australia annual demographic rows, 2026 through 2036;
- Australia annual economic rows, 2026 through 2036;
- global 2026 biological population;
- global 2026 legacy employment;
- global 2026 economic value added;
- global 2026 gross output;
- global 2026 investment;
- global 2026 economic capital.

The 2026 global values captured from promoted Earth authority are:

```text
biological population   8,266,245,291
legacy employment       2,656,643,452
economic value added    97,972,106,141,060.23
gross output             211,514,276,597,700.8
investment               25,103,965,105,580.805
capital                  432,469,075,509,846.3
```

Only values whose semantics align with the current engine are mapped directly into
engine state.

Current direct mappings:

```text
global biological_population
    -> EARTH_SURFACE biological_population

global legacy_employment
    -> EARTH_SURFACE workforce
```

The real global economic capital value is **not** copied into the engine's current
location `capital` field. That field remains a compatibility bookkeeping quantity
rather than observed national capital.

Project Economics V1 separately defines project capital in USD_2026_billion. The two
are not equated.

This is deliberate semantic firewalling.

## Earth habitat boundary rule

The compiled input sets:

```text
EARTH_SURFACE habitat capacity
=
compiled 2026 Earth biological population
```

This is a compatibility floor allowing inherited terrestrial population to exist
inside the current habitat-constrained engine.

It is explicitly **not** a terrestrial housing/bed inventory.

Owning gap:

```text
GAP-014 DEMOGRAPHIC_DEPTH
```

## Solar authority

Captured bodies:

```text
EARTH
MOON
```

Captured identity includes active body identifiers.

Pinned ephemeris source:

```text
DE440
provider = JPL/NAIF
status = QUALIFIED
navigation_grade = true
```

Earth and Moon DE440 coverage rows are frozen in the authority context.

Accessibility V1 now consumes qualified frozen Solar geometry when an exact
body-pair/epoch sample is available. The current compiled slice admits the qualified
2030-07-01 Earth-Moon Roo-ver reference geometry. Body-center separation remains
context only and is never treated as route length, delta-v or transfer duration.

## Timeline authority

Pinned snapshot:

```text
timeline-v0-1-0232bf23494f-20260925
state = VALIDATED
```

The compiler freezes all interpretation rules, including:

```text
CANON_COMPARATOR_NOT_DESTINATION
DATE_DOES_NOT_UNLOCK
FOUR_TECH_STATES
SITE_SPECIFIC
UNKNOWN_NOT_ZERO
```

It also freezes promoted milestones whose start year falls in the current 2026-2036
compiler horizon.

Current captured examples include:

```text
TRN-2031-LOOK
COM-MOD-LUNAR
```

The compiler does not invent a one-to-one translation from these milestones into
generic engine capability tags where no qualified mapping exists.

Current generic technology-frontier rows therefore remain compatibility assumptions,
explicitly separated from the promoted Timeline context.

## Resource authority

Promoted resource assertion:

```text
MOON_POLAR_WATER_ICE
body = MOON
abundance_semantics = PRESENT_UNQUANTIFIED
scope = POLAR_AND_SELECTED_SURFACE_FOOTPRINTS
confidence_class = MODERATE
```

The empirical assertion is frozen exactly in the authority context.

The engine still requires a numeric probability, sensitivity and false-positive
rate. The evidence does not supply those quantities.

Therefore the current:

```text
prior_probability = 0.45
observation_sensitivity = 0.80
false_positive_probability = 0.10
```

remain explicit uncalibrated Mission/Knowledge V1 scenario parameters. GAP-006
closes the mechanism and provenance boundary; it does not convert those values into
empirical measurements.

The compiled belief status is:

```text
EMPIRICAL_PRESENCE_PLUS_SCENARIO_PRIOR
```

That name is intentionally ugly because the epistemics are ugly.

## Actor authority

The first compiled actor is:

```text
AUS
```

Identity comes from promoted `loom_earth.earth_area`.

The authority context also preserves:

- Fleet Space / SPIDER provider-access evidence;
- Australian Roo-ver / CLPS CT-4 / IM-5 service envelope.

Those records remain scoped.

Fleet's SPIDER agreement does not become generic Australian state payload access.

Roo-ver's planned service does not become generic lunar transport capacity.

Unknown delivery capacity, launch vehicle, delta-v and transfer duration remain null.

## Actor State V1 boundary

GAP-002 removes the old scenario-credit budget and generic capability compatibility
rows from the default compiled actor.

The compiled actor is now `AUS` / `STATE` with a versioned
`CIVPROP_ACTOR_STATE_V1` boundary. Generic spendable allocation remains explicitly
UNKNOWN because the admitted evidence does not establish a general off-world
appropriation. The observed AUD 42 million Roo-ver commitment is preserved as a
separate scoped committed fund and cannot be spent on unrelated CIVPROP projects.

Roo-ver access, provider path, agreement, operator relationship and development
experience remain scoped facts. Fleet SPIDER evidence remains authority context and
does not become an Australian state entitlement. No generic Method Lab capability
row is relabeled as AUS.

Detailed semantics and closure evidence are in
`docs/civprop/CIVPROP_ACTOR_STATE_AND_BUDGETS_V1.md`.

## Project Economics V1 boundary

GAP-005 removes METHOD_LAB_SYNTHETIC_V1 from the default project-economics path.

The compiler captures and validates:

```text
engineering/civprop/contracts/project_economics_v1.json
```

The parameter set is:

```text
EARTH_LUNA_PROJECT_ECONOMICS_V1_2026_2036
```

It uses explicit units:

```text
project capital  USD_2026_billion
power            MW
habitat          person
transport        tonnes/year
industrial       tonnes/year
resource         tonnes/year
shipyard         tonnes/year
```

Quantities preserve low/nominal/high ranges, provenance and status. Scale behavior
and 2026/2031/2036 technology-epoch adjustments are explicit and versioned.

The current 40-kW-class POWER_PLANT base output is the only qualified physical
component in the first parameter set, sourced from the existing NASA Fission Surface
Power reference preserved by the technology timeline. Its cost, lag, prerequisites
and learning schedule remain scenario assumptions.

Dorrington-Olsen is preserved as an asteroid-mining mission/economic boundary and is
explicitly not applied to Earth-Luna facility costs.

The default scenario carries a start-year resolved project view for compatibility,
while Hybrid resolves project economics again at the actual opportunity year.

## Mission / Knowledge V1 boundary

GAP-006 adds:

```text
engineering/civprop/contracts/mission_knowledge_v1.json
```

The compiler captures and validates the package as:

```text
CIVPROP_MISSION_KNOWLEDGE_V1
EARTH_LUNA_MISSION_KNOWLEDGE_V1_2026_2036
```

The first admitted mission is LUNAR_RESOURCE_PROSPECTING_SURVEY. It references the
PROSPECTING_SURVEY economics row but is removed from runtime project_archetypes so a
mission action cannot masquerade as commissioned infrastructure.

The first actor-visible question is MOON_POLAR_WATER_PRESENT with a 0.45 scenario
prior. The first observation model is binary detection with sensitivity 0.80 and
false-positive probability 0.10. These are versioned uncalibrated scenario-model
parameters, not empirical instrument calibration.

The follow-on RESOURCE_PLANT success value remains UNKNOWN. This causes the default
AUS mission decision to WAIT rather than inventing resource-development value.

Evaluator truth remains a separate file. Mission/Knowledge V1 permits only the
observation runtime to read the hidden present/absent realization when an admitted
mission executes. Actor decisions and project scoring consume actor-visible
knowledge, never the hidden realization.

## Remaining assumption register

Every compiled scenario carries an `assumption_register`.

Current explicit entries include:

```text
ASSUME-GAP012-OFFWORLD-INITIAL-STATE
ASSUME-GAP014-EARTH-HABITAT-FLOOR
```

Each assumption records:

- assumption ID;
- owning gap;
- status;
- semantic meaning.

No placeholder is allowed to masquerade as promoted authority.

## Compatibility envelope

The compiled scenario currently retains:

```text
format = CIVPROP_METHOD_LAB_SCENARIO_V1
```

This is intentional.

The locked Hybrid V1 parser already understands this envelope, and changing the
envelope solely for naming aesthetics would create needless engine churn.

The package classification and manifest authority distinguish it from the synthetic
Method Lab fixture:

```text
fixture_id =
EARTH_LUNA_COMPILED_AUTHORITY_V1_2026_2036

classification =
COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1

authority =
COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1
```

A later semantic input-contract change can version the envelope deliberately.

## Compiled package files

```text
scenario_v1.json
truth_v1.json
manifest_v1.json
compiler_manifest_v1.json
```

### scenario_v1.json

Runtime actor-visible input.

Contains:

- engine-compatible fields;
- frozen authority context;
- explicit assumption register.

### truth_v1.json

Evaluator-only compatibility realization.

It remains synthetic. Actor decisions cannot consume it. Mission/Knowledge V1 allows
the observation runtime to read only the scoped hidden resource realization when an
admitted mission actually executes, in order to generate a keyed noisy observation.
The current seed-42 baseline executes no mission and therefore does not consume it.

Its continued presence does not close GAP-008 or promote the synthetic realization
to Solar/resource authority.

### manifest_v1.json

Locked-runner package manifest.

Pins scenario/truth hashes and bundle hash.

### compiler_manifest_v1.json

Machine-readable provenance for the compiler.

Contains:

- compiler identity/version;
- authority-capture identity/hash;
- Earth and Timeline snapshot rows;
- Solar ephemeris authority;
- source-file hashes;
- SQL-query hashes;
- package hashes;
- gap-resolution map;
- full assumption register;
- explicit meaning of GAP-001 closure.

## Determinism

Compilation from a frozen authority capture is deterministic.

Tests compare byte-for-byte regeneration of:

```text
scenario_v1.json
truth_v1.json
manifest_v1.json
compiler_manifest_v1.json
```

Live recapture may legitimately produce a new capture hash if promoted authority
changes.

That requires:

```text
new authority capture
-> new compiled runtime-input hash
-> new executable golden baseline
```

No silent replacement.

## Runner V1.6

The single simulation entrypoint remains:

```text
engineering/civprop/run_civprop_v1.py
```

Runner version:

```text
1.6.0
```

Output contract:

```text
1.6.0
```

Compiler version:

```text
1.5.0
```

The default input directory is now the GAP-001 through GAP-006 compiled package.

Default command:

```bash
python3 engineering/civprop/run_civprop_v1.py   --seed 42   --output /tmp/civprop_v1.json
```

No `--input-dir` is required for the current promoted baseline.

## Gap-state output

The runner reads the compiler manifest when present.

For the default compiled package:

```text
GAP-001 CLOSED
GAP-002 CLOSED
GAP-003 CLOSED
GAP-004 CLOSED
GAP-005 CLOSED
GAP-006 CLOSED
GAP-007 OPEN
...
GAP-015 OPEN
```

GAP-006 closure is independent of later pressure-observability,
resource/production/power, fleet and materialization gaps.

## Current executable behavior

With compiled input and seed 42, the current GAP-006 baseline produces:

```text
44 annual location states
11 annual actor states
0 commissioned facilities
11 project decisions
11 mission decisions
1 actor-visible knowledge state
0 missions
0 observations
0 actor transactions
46 events
0 migration flows
```

The current realization commissions no facility because AUS generic spendable
allocation remains UNKNOWN and no generic project path satisfies the closed
actor/accessibility boundaries. Demand still exists internally: 2026 Earth orbit has
150 persons of unmet habitat requirement and 200 tonnes/year of unmet resource
requirement. That behavior is intentional and is not a forecast.

This is **not** a forecast.

The result still depends materially on GAP-007 and later open mechanisms. Demand,
mission-observation and project-economics scenario coefficients remain explicit
uncalibrated model parameters where marked, not empirical forecasts.

Its purpose is to prove that real promoted authority now reaches the same locked
engine and output path.

## Golden GAP-006 baseline

Output:

```text
engineering/civprop/baselines/
CIVPROP_ENGINE_V1_GAP6_MISSIONS_KNOWLEDGE_SEED42.json
```

Manifest:

```text
engineering/civprop/baselines/
CIVPROP_ENGINE_V1_GAP6_BASELINE_MANIFEST.json
```

The GAP-001 compiled baseline and previous synthetic V1.0 baseline remain in the
repository as historical evidence. They are not overwritten.

## Tests

Unit/functional coverage proves:

- promoted Earth/Timeline snapshots are pinned and validated;
- DE440 is qualified and navigation-grade;
- real Earth population/employment map only where semantics align;
- real Earth economic series are preserved without being miscast as scenario credit;
- actor evidence scope is preserved;
- resource presence is separated from synthetic probability;
- unresolved gaps remain explicit assumptions;
- compilation from frozen capture is byte deterministic;
- the locked runner accepts the compiled package;
- the default runner now uses the compiled package;
- GAP-001 through GAP-006 are CLOSED in current output;
- UNKNOWN actor budget does not become zero, national capital or scenario credit;
- scoped provider/service evidence does not become generic actor capability;
- future actor budget/capability changes require replayable events;
- evaluator-only truth remains prohibited from runtime decisions;
- current golden output reproduces exactly.

## Program continuation

The authoritative current gap register and the post-gap handoff plan are:

    engineering/civprop/gap_register_v1.json
    docs/civprop/CIVPROP_GAP_REGISTER_AND_POST_GAP_PLAN_V1.md

GAP-001 through GAP-006 closure should be interpreted using that register's closure
semantics. The next engineering target is GAP-007 PRESSURE_OBSERVABILITY.

## Boundary after GAP-006

The executable pipeline is now:

```text
PROMOTED LOOM AUTHORITY
        |
        v
CIVPROP_INPUT_COMPILER_V1
        |
        +-- explicit unresolved gap assumptions
        |
        v
FROZEN COMPILED INPUT PACKAGE
        |
        v
run_civprop_v1.py
        |
        v
HYBRID_V1
        |
        v
CIVPROP_ENGINE_V1_OUTPUT
```

GAP-007 can now expose pressure state and qualification provenance without
redesigning this path or weakening the closed actor, accessibility, demand/pressure,
project-economics or mission/knowledge boundaries.
