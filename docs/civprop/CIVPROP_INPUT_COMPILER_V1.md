# CIVPROP Input Compiler V1

Date: 2026-09-30
Class: `class:engineering`
Status: GAP-001 closed / production-facing input compilation with explicit downstream assumptions

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

Runner V1.1 defaults to the compiled package rather than the original synthetic
Method Lab package.

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
99dadcfb4276471c29aa3bf52650d0584ef03038
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
`capital` field because that field still uses synthetic `scenario_credit`
semantics under GAP-002/GAP-005.

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

The current Hybrid engine does not yet consume ephemeris geometry directly.
Transport/accessibility remains GAP-003.

The Solar capture is nevertheless part of the runtime input hash so future adapters
can consume it without changing provenance history.

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

remain explicit Method Lab assumptions owned by GAP-006.

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

## Actor runtime placeholders

The current Hybrid engine requires actor budget and generic capability rows that are
not yet production-resolved.

Therefore:

```text
AUS starting_capital = 70 scenario_credit
AUS annual_capital_inflow = 8 scenario_credit
```

remain explicit GAP-002 placeholders copied from the original public-financier
Method Lab actor.

Generic capability rows are likewise compatibility placeholders and do not claim
that the real Australian state owns those capabilities.

## Remaining assumption register

Every compiled scenario carries an `assumption_register`.

Current explicit entries include:

```text
ASSUME-GAP002-AUS-BUDGET
ASSUME-GAP002-AUS-CAPABILITIES
ASSUME-GAP003-ACCESSIBILITY
ASSUME-GAP004-DEMAND
ASSUME-GAP005-PROJECT-ECONOMICS
ASSUME-GAP006-RESOURCE-PRIOR
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

It remains synthetic and is not consumed by HYBRID_V1.

Its continued presence does not close GAP-006 or GAP-008.

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

## Runner V1.1

The single simulation entrypoint remains:

```text
engineering/civprop/run_civprop_v1.py
```

Runner version:

```text
1.1.0
```

Output contract:

```text
1.1.0
```

The default input directory is now the GAP-001 compiled package.

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
GAP-002 OPEN
...
GAP-015 OPEN
```

Closing GAP-001 does not auto-close any downstream gap.

## Current executable behavior

With compiled input and seed 42, the current baseline produces:

```text
44 annual states
7 commissioned facilities
11 actor decisions
87 events
10 migration flows
```

Current generated facility geography:

```text
EARTH_ORBIT
CISLUNAR_FREE_SPACE
```

This is **not** a forecast.

The result still depends materially on unresolved GAP-002 through GAP-005
placeholders.

Its purpose is to prove that real promoted authority now reaches the same locked
engine and output path.

## Golden GAP-001 baseline

Output:

```text
engineering/civprop/baselines/
CIVPROP_ENGINE_V1_GAP1_COMPILED_SEED42.json
```

Manifest:

```text
engineering/civprop/baselines/
CIVPROP_ENGINE_V1_GAP1_BASELINE_MANIFEST.json
```

The previous synthetic V1.0 baseline remains in the repository as historical
evidence. It is not overwritten.

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
- GAP-001 is CLOSED in current output;
- evaluator-only truth remains prohibited from runtime decisions;
- current golden output reproduces exactly.

## Program continuation

The authoritative current gap register and the post-gap handoff plan are:

    engineering/civprop/gap_register_v1.json
    docs/civprop/CIVPROP_GAP_REGISTER_AND_POST_GAP_PLAN_V1.md

GAP-001 closure should be interpreted using that register's closure semantics. The
next engineering target is GAP-002 ACTOR_STATE_AND_BUDGETS.

## Boundary after GAP-001

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

The next gap can now replace one assumption family without redesigning this path.
