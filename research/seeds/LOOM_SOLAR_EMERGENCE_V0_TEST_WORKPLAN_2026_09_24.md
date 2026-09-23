# LOOM Solar Emergence v0 — Test Workplan

**Date:** 2026-09-24  
**Primary change class:** `class:engineering`  
**Status:** EXPERIMENT / FICTIONAL / NON-CANON / NON-PRODUCTION  
**Purpose:** Test whether a very small propagation engine can generate a differentiated Solar civilization from 2026–2226 using the current Earth economic baseline, the LOOM technology timeline, and the existing Solar ephemeris/accessibility authority.

This is a machinery test, not a final CIVPROP architecture and not an attempt to reproduce existing LOOM canon.

## 1. Test question

Can:

- Earth v3 economic capacity;
- the technology timeline;
- Solar ephemeris/accessibility;
- simple body opportunity characteristics;
- probabilistic investment/location choice;
- construction lag;
- accumulated local capital;
- simple migration;

produce an emergent system of **surface and orbital facilities across the complete registered Solar System** by 2226?

The test is successful if the machinery produces coherent differentiation and path dependence without requiring hand-authored destination importance or preselected Ceres/Mars/Luna outcomes.

## 2. Explicit non-goals

Do **not**:

- calibrate to the existing Ceres facilities;
- calibrate to the 127-node Atlas;
- force Ceres, Mars, Luna, the Belt, or any outer-system body to succeed;
- treat existing LOOM facility names/classes as required outputs;
- use Mesa in v0;
- build full corporations, institutions, mergers, sanctions, ownership politics, cohort demography, full input-output economics, queues, or final CIVPROP;
- migrate the production SQLite schema;
- mutate production Atlas/CIVSTATE/WORLD data;
- create a new Earth baseline;
- rerun or modify the Earth v3 economic model;
- turn authored test priors into canon.

Ceres is only the structural example that **body → facilities → facility attributes → body aggregate** is a useful Atlas pattern.

## 3. Authorities consumed read-only

### Earth economic envelope

Resolve the current pointer, expected at the time this plan was written to be:

`EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23`

Use the current pointer rather than hard-coding paths where practical.

Earth v3 supplies annual country-level:

- population;
- value added;
- productive capital;
- investment;
- employment.

The Earth model remains authoritative for those values. Solar emergence v0 only consumes them.

### Technology opportunity scaffold

Use:

`docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md`

Technology dates are conditional opportunity anchors. A date does not cause a facility to exist. Investment, prerequisites, accessibility, construction and local state still matter.

### Solar physical authority

Use the current LOOM ephemeris/body registry and existing Navigator/route machinery where practical.

Every registered ephemeris body is eligible for evaluation.

Do not hand-select only Earth/Luna/Mars/Ceres.

If the existing route machinery is too expensive or tightly coupled for this experiment, use a clearly labeled deterministic v0 accessibility surrogate derived from the existing ephemeris rather than building a second Navigator.

## 4. Basic model

### 4.1 Body opportunity profile

Attach one minimal test profile to every registered ephemeris body.

Candidate fields:

```text
body_id
body_class
surface_possible
orbital_possible

surface_gravity
radiation_environment
thermal_environment
solar_energy_potential

water_potential
volatile_potential
bulk_material_potential
metal_potential
```

Use existing source-backed values where readily available.

Unknown remains `null`.

Where detailed resource information is unavailable, use a small documented **body-class test prior**. Do not launch a research campaign for hundreds of bodies.

There is **no universal attractiveness score**.

### 4.2 Accessibility

Accessibility is relational and time-dependent.

Minimum conceptual output:

```text
origin_body_id
destination_body_id
year
mode_or_era
travel_penalty
transport_cost_proxy
window_quality
reachable
```

Accessibility belongs to the relationship between bodies, not to a fixed body score.

Compute lazily where possible:

1. Earth → candidate bodies initially;
2. active settlement/facility bodies → candidate bodies after local civilization appears.

### 4.3 Facility as the only generated civilization object

The primary emergent object is a **facility** attached to an ephemeris body.

A facility has:

```text
facility_id
parent_body_id

placement = SURFACE | ORBITAL

founded_year
commissioned_year
status

financing_origin
owner_actor

capital

resident_population
transient_population
workforce

power_capacity
resource_capacity
industrial_capacity
habitat_capacity
shipyard_capacity
transport_capacity

annual_cargo
annual_passengers
```

Not every field must be non-null in v0.

Do not force facilities into existing Ceres Atlas classes.

Facility capabilities determine what a facility became.

### 4.4 Body state is derived

Body-level civilization state is the aggregate of facilities attached to that body.

For example:

```text
body productive capital = sum(facility productive capital)
body residents          = sum(facility residents)
body power               = sum(facility power)
...
```

The ephemeris body itself is not assigned authored civilization importance.

### 4.5 Project types

Keep project choice extremely small.

Only two project actions are required:

```text
CREATE_FACILITY
EXPAND_CAPABILITY
```

Capability families:

```text
power
resource
industrial
habitat
shipyard
transport
```

Optional `science` or `communications` may be added only if implementation remains trivial.

### 4.6 Financing actors

For v0, the 80 Earth economies are **financing pools**, not rich political agents.

Each uses the same decision machinery.

A configurable test fraction of modeled annual investment may be exposed to Solar projects.

Do not invent country personalities such as "prestige preference" or tune national behavior to expected outcomes.

A minimal split into:

```text
COMMERCIAL_CAPITAL
PUBLIC_STRATEGIC_CAPITAL
```

is acceptable if useful, but not required for the first successful run.

### 4.7 Investment/location choice

For feasible project `p` at body `b` in year `t`, use a simple utility based on:

```text
economic value
resource fit
accessibility
existing complementary capital / agglomeration
demand
construction cost
transport cost
risk
```

Then choose among similar alternatives probabilistically using a softmax/discrete-choice rule rather than always selecting the exact maximum.

All authored coefficients live in one `parameters.json`.

Do not hide constants in code.

### 4.8 Path dependence

Completed facilities make later development easier where complementary capital exists.

Examples:

```text
resource capacity
    → increases value of power/industrial investment

power + resource
    → increases value of industrial investment

industry + transport demand
    → increases value of shipyard investment

habitat + jobs + accessibility
    → permits resident migration
```

This positive feedback is the core emergence mechanism.

Add congestion/diminishing returns only if needed to prevent obvious runaway concentration.

### 4.9 Population

Keep migration simple.

Facilities may initially support:

- remote work;
- transient/rotational work;
- resident population.

Resident migration requires habitat and employment opportunity.

Migration must be source-debited/conserved.

Do not build cohort demography in this test.

## 5. Targeted Codex execution plan

Use one experimental branch/worktree and one PR at the end.

Each run has a hard stop.

### Codex Run 1 — experiment shell + body opportunity layer

Create:

`experiments/solar_emergence_v0/`

Deliver:

- `README.md`
- `WORKPLAN.md` copied/referenced from this governing plan
- `parameters.json`
- `body_catalog.json`
- `body_opportunities.json`
- body/opportunity loader code
- focused tests

Requirements:

- derive the body catalog from the actual current ephemeris registry;
- every registered ephemeris body appears exactly once;
- no hand-selected body list;
- unknown inputs remain null;
- use only small documented body-class priors when necessary.

**STOP. Do not implement propagation.**

### Codex Run 2 — accessibility layer

Deliver:

- `route_accessibility.py`
- a compact annual/accessibility output or reproducible cache;
- focused tests.

Prefer a thin adapter over existing Navigator/ephemeris machinery.

If reuse is disproportionate to the experiment, implement a deterministic, clearly labeled v0 surrogate from existing ephemeris inputs.

Requirements:

- accessibility varies by origin, destination and year;
- unavailable routes do not become zero-cost;
- fixed inputs reproduce identical values;
- no separate orbital-physics authority is created.

**STOP. Do not implement facility investment.**

### Codex Run 3 — minimal emergence engine

Deliver:

- project generation;
- simple investment/location choice;
- construction lag;
- facility creation;
- capability expansion;
- body aggregation;
- minimal migration;
- focused unit tests.

Do **not** execute 2026–2226 yet.

First prove the engine using a tiny synthetic 5–10 year fixture.

Mechanical requirements:

- no actor spends more than its available test budget;
- capital cannot teleport;
- facilities cannot commission before construction completion;
- unavailable technology cannot be used;
- body state reconciles exactly to facility state;
- migration is source-debited;
- fixed random seed is deterministic.

**STOP after fixture passes.**

### Codex Run 4 — full Solar experiment

Run:

```text
2026 → 2226
all registered ephemeris bodies
primary seed = 42
```

After seed 42 completes mechanically, run two comparison seeds such as:

```text
11
97
```

Do not tune parameters because a resulting geography looks odd or fails to resemble canon.

Debug mechanical defects only.

Core outputs:

```text
facility.ndjson
facility_state_year.ndjson
body_state_year.ndjson
investment_flow_year.ndjson
migration_flow_year.ndjson
route_accessibility_year.ndjson
run_summary.json
```

The summary should report selected years:

```text
2035
2050
2060
2090
2120
2165
2180
2205
2226
```

and include:

- facility count by body;
- surface/orbital counts;
- capital;
- residents/transients/workforce;
- capability totals;
- financing origins;
- untouched bodies.

**STOP. Do not interpret against canon or change parameters.**

### Codex Run 5 — inspection adapter + test PR

Add a tiny read-only adapter such as:

```python
body_state(body_id, year)
facilities(body_id, year)
```

Produce:

- compact `RESULTS.md`;
- an Atlas-friendly SQLite/JSON artifact or reproducible builder;
- exact reproduction command for quantifactus;
- fixed-seed reproducibility result.

Open **one test PR** containing:

- experiment code;
- parameters;
- workplan;
- compact result summaries;
- small seed-42 result artifacts if reasonable;
- tests.

Do not integrate into production Atlas/CIVSTATE.

Do not merge until human review of the generated Solar geography.

## 6. Acceptance criteria

The test passes mechanically when:

1. 2026→2226 completes.
2. Every registered ephemeris body was eligible for evaluation.
3. Bodies are allowed to remain completely untouched.
4. Surface/orbital placement respects basic feasibility.
5. Facilities cannot precede required technology.
6. Investment is bounded by available test capital.
7. Capital does not appear or relocate without an investment/construction path.
8. Resident migration is source-debited and habitat constrained.
9. Body totals reconcile exactly to attached facilities.
10. Fixed seed reproduces exactly.
11. Alternate seeds produce at least some historical variation.
12. Atlas-style queries work by existing `body_id + year`.

## 7. What we are looking for

A useful result might look conceptually like:

```text
MARS
    multiple surface/orbital facilities
    substantial habitat / industry / transport

CERES
    several facilities
    resource / industrial / shipyard accumulation

VESTA
    smaller resource-oriented presence

CALLISTO
    outer-system cluster

PALLAS
    possibly no facilities

many minor bodies
    untouched
```

These examples are **not targets**.

A surprising but mechanically coherent geography is a successful experiment.

## 8. Decision after v0

Only after inspecting v0 decide whether the next experiment should add:

- better project economics;
- explicit orbit/Lagrange-point economic places;
- richer trade;
- corporations/ownership;
- Mesa organizational agents;
- institutional behavior;
- richer migration/demography;
- direct Atlas playback.

Mesa, if tested later, should replace only the decision interface:

```text
DevelopmentChoiceEngine
    ├── DiscreteChoiceEngine   # v0
    └── MesaActorEngine        # later experiment
```

The physical/economic state engine should not depend on Mesa.

## 9. Working rule for this experiment

**Keep it small enough that a strange outcome makes us inspect the mechanism, not spend a week maintaining the framework.**

This is fictional simulation machinery. The purpose is to learn whether the mechanism is promising.
