# LOOM 2226 — Simulation Physical Authority Work-Plan Amendment

Date: 2026-09-08  
Status: **Governing amendment to the Navigator / GIS / HUD Next-Phase Work Plan — planning branch**  
Parent plan: `docs/LOOM_2226_Navigator_GIS_HUD_Next_Phase_Work_Plan_2026-09-06.md`

## 0. Authority and source rule

This amendment extends the governing Navigator / GIS / HUD work plan toward the explicit target of a telemetry-grade physical simulator.

**Documentary authority rule:** any LOOM document, schema note, canon file, status document, work plan, refinement, implementation note, or code artifact used to justify implementation must be fetched from live GitHub authority before it is relied upon. Chat history and model memory may identify what to look for, but they are not documentary authority. If GitHub and chat differ, GitHub wins.

This amendment does not promote chat conclusions into canon by itself. New physical constants, station orbits, surface coordinates, traffic rules, or endpoint geometry must be introduced through governed repository changes with provenance and qualification.

## 1. Simulator target

LOOM should evolve from a game application that displays calculated values into a simulation in which gameplay emerges from a physical state model.

The target chain is:

```text
WORLD / PHYSICAL AUTHORITY
        ↓
TRUE PHYSICAL STATE @ t
        ↓
SENSORS / MEASUREMENTS
        ↓
ESTIMATED NAVIGATION STATE
        ↓
GUIDANCE
        ↓
CONTROL / ACTUATORS
        ↓
VEHICLE DYNAMICS
        ↓
NEW TRUE PHYSICAL STATE
        ↓
TELEMETRY / HUD / GIS / NAVIGATOR
```

HUD values must therefore be derived from runtime physical, estimated-navigation, propulsion, power, thermal, metric, traffic, and mission state rather than decorative numbers.

Ordinary-space physics should use real celestial mechanics and navigation practice wherever practical. Torch operation should use LOOM's qualified torch engineering model inside the same state/dynamics architecture. Metric operation remains speculative physics and must remain explicitly segregated from empirically validated ordinary-space dynamics while still exposing rigorous engineering state, constraints, accounting, uncertainty, and telemetry.

## 2. Immediate physical-authority audit

Before adding richer HUD presentation, broad station placement, or decorative 3D assets, perform an explicit data and authority audit of the live GitHub repository.

Audit at minimum:

1. `data/LOOM_2226.sqlite3` — world/spatial/ephemeris/infrastructure physical authority;
2. `data/LOOM_2226_CIVSTATE.sqlite3` — civil/institutional/traffic context and any fields that must remain separate from physical navigation authority;
3. current campaign JSON/history authority — mutable campaign revision, epoch, vehicle location/state, execution history and transition semantics;
4. any current shadow/candidate campaign SQL implementation — only if actually present in Git/runtime authority;
5. current Navigator trajectory and endpoint contracts;
6. current spatial-runtime and ephemeris providers;
7. current infrastructure/orbit/placement models;
8. current ship engineering state and telemetry sources.

For every audited field or table, classify it as one of:

- `AUTHORITATIVE_NAVIGATION_GRADE`
- `AUTHORITATIVE_NON_NAVIGATION_GRADE`
- `DERIVED_QUALIFIED`
- `APPROXIMATE_PRESENTATION_ONLY`
- `SEMANTIC_LOCATION_ONLY`
- `MISSING`
- `DEPRECATED_OR_SHADOW`

Do not silently upgrade display/semantic placement into physical truth.

## 3. Core physical state rule

The shared spatial runtime must converge on the query:

```text
state(entity_id, epoch) -> position + velocity + orientation/state + frame + provenance + uncertainty/quality
```

where applicable.

All time-dependent entities must resolve against an explicit campaign, query, or playback epoch. Real-world wall-clock time must never silently become game-universe time.

The same epoch must drive:

- celestial bodies;
- barycenters and relevant local frames;
- orbital stations and moving infrastructure;
- surface-site transforms from body-fixed to inertial coordinates;
- Wayfarer and other vehicle state;
- trajectory playback;
- rendezvous/approach transition points;
- HUD relative geometry and telemetry.

## 4. Celestial-body physical authority

Each navigable celestial body requires a governed physical model appropriate to its fidelity tier.

Minimum target fields/model references:

- authoritative identifier and hierarchy;
- gravitational parameter / central-body model;
- reference radius and shape semantics;
- body orientation / pole / prime-meridian model;
- body-fixed reference frame;
- inertial-frame transform support;
- ephemeris/state source and validity interval;
- atmosphere classification and, where operationally relevant, atmosphere-model reference;
- terrain/shape/elevation-model reference where local surface operations require it;
- perturbation/gravity-field fidelity tier;
- uncertainty/provenance/navigation grade.

Higher-fidelity bodies may additionally require flattening, J2/higher harmonics, third-body perturbations, atmospheric drag, solar-radiation pressure, non-spherical shape models, terrain and weather/environment models.

Do not impose the same fidelity on every minor body. Fidelity must be operationally driven and explicitly declared.

## 5. Surface infrastructure must be physically locatable

Every surface infrastructure node intended for GIS, navigation, landing, logistics, traffic, or local operations must ultimately have an authoritative body-fixed spatial definition.

Minimum target contract:

- infrastructure entity/node ID;
- parent celestial body;
- body-fixed reference frame;
- latitude / longitude or equivalent body-fixed coordinates;
- elevation/altitude relative to an explicit datum or shape model;
- physical footprint / facility extent where relevant;
- landing/runway/pad geometry where relevant;
- provenance and quality/navigation grade.

Surface position in inertial 3D space must be derived from the body's authoritative orientation model at epoch, not stored as a timeless heliocentric XYZ shortcut.

Everything remains fundamentally 3D. A 2D map is a projection of this authority.

## 6. Orbital infrastructure and authorized orbit standards

Every orbital station or facility intended for navigation, rendezvous, docking, traffic control, or local 3D rendering must have a time-resolvable orbital definition.

Minimum station/orbital-object contract:

- entity/station ID;
- parent body/central object;
- authoritative orbit/state source;
- propagation/model type;
- state or orbital definition with epoch;
- reference frame;
- validity interval;
- provenance/navigation grade;
- station/local frame definition;
- docking/rendezvous metadata.

### 6.1 Body-specific authorized orbit regimes

Each celestial body with meaningful traffic should publish a governed orbital traffic regime rather than allowing ad hoc arbitrary parking orbits.

Potential authorized classes include:

- `LOW_CIRCULAR`
- `HIGH_CIRCULAR`
- `EQUATORIAL_CIRCULAR`
- `POLAR_CIRCULAR`
- `PHASING`
- `TRANSFER`
- `STATION_SERVICE`
- `STATION_MATCH`
- `ARRIVAL_HOLD`
- `DEPARTURE_STAGING`
- body-specific protected/science/military/commercial classes where canon and governance justify them.

Each class is a permission/intent definition, not an actual position. A spatial/orbit resolver must derive the actual 6D state at the requested epoch from the governed physical parameters.

### 6.2 Orbital traffic-law model

Traffic authority may define:

- permitted altitude/radius bands;
- inclination or plane corridors;
- station/service orbit reservations;
- phasing and arrival/departure lanes;
- keep-out and collision-avoidance zones;
- protected station shells;
- no-burn zones/windows;
- deorbit/entry corridors;
- vehicle-class restrictions;
- right-of-way/emergency precedence;
- transponder/ephemeris-publication requirements;
- clearance/authorization requirements.

Civil/institutional authority may live in CIVSTATE, while numerical orbit/geometry authority must remain in the physical/spatial layer. Do not collapse governance and orbital mechanics into one table merely for convenience.

## 7. NASA / JPL / IDSS-derived operational practice

For ordinary-space orbital dynamics, rendezvous, proximity operations, docking, reference frames, navigation, and landing operations, LOOM should use established NASA/JPL/NAIF/IDSS practice where an applicable real standard or operational convention exists.

Rules:

1. use real standards/conventions where they actually exist;
2. do not invent a universal "NASA standard orbit" where NASA practice is mission/body-specific;
3. derive transition states using real orbital mechanics/GN&C principles;
4. clearly distinguish real external standards from LOOM-governed future traffic law;
5. retain external-source provenance for adopted standards or algorithms.

The repository should eventually contain a controlled external-standards bibliography/provenance record for the specific NASA/JPL/NAIF/IDSS materials used by implementation.

## 8. Navigator endpoint and transition-state model

Navigator endpoints must stop at physically meaningful transition states rather than abstract body names or docking collars.

Typed endpoint intents should include body, orbit, station, surface site, Lagrange/free-space, and transition/gate concepts.

### 8.1 Orbital-station arrival handoff

Preferred flow:

```text
INTERPLANETARY NAVIGATOR
    ↓
terminal local approach / rendezvous solution
    ↓
RENDEZVOUS_GATE
    ↓
HUD / LOCAL FLIGHT
    ↓
APPROACH_HOLD
    ↓
FINAL_APPROACH_ENTRY
    ↓
proximity operations
    ↓
docking
```

Reverse departure:

```text
docked
    ↓
HUD / LOCAL FLIGHT
    ↓
undock / local maneuvering
    ↓
DEPARTURE_GATE
    ↓
NAVIGATOR
```

Each transition point must resolve to a real epoch-stamped local and absolute state, including required relative position/velocity envelopes and frame semantics.

### 8.2 Surface-landing handoff

Surface infrastructure requires an analogous chain. Candidate semantics include:

```text
authorized orbit / arrival state
    ↓
DEORBIT_GATE
    ↓
ENTRY_INTERFACE              [where atmosphere/aerodynamic entry applies]
    ↓
TERMINAL_AREA_ENTRY
    ↓
LANDING_APPROACH_GATE
    ↓
HUD / LOCAL FLIGHT
    ↓
FINAL APPROACH
    ↓
pad / runway / vertical landing site
```

For airless bodies, stages may collapse appropriately, but the resulting transition geometry must still be physically derived rather than cosmetic.

## 9. Reference-frame architecture

Shared spatial services must own transforms among at least:

- canonical inertial / existing J2000-ecliptic navigation frame;
- body-centric inertial frame;
- body-fixed frame;
- orbital/station local frame;
- rendezvous/proximity frame;
- surface local tangent frame where needed;
- ship body frame;
- ship tactical/HUD frame.

GIS, Navigator and HUD must consume these transforms rather than maintaining independent hidden frame math.

## 10. Vehicle true-state dynamics

To reach simulator-grade telemetry, LOOM requires a persistent/continuous vehicle-state model beyond route summary values.

Target true-state domains include:

- position and velocity;
- orientation and angular rate;
- mass / dry mass / payload / consumables;
- remass inventory and flow;
- center of mass / mass properties where required;
- torch/RCS/actuator state;
- thrust-vector/attitude-control limits;
- power generation/storage/load state;
- radiator/thermal state;
- metric hardware/state where applicable;
- structural/acceleration envelopes;
- docking/landing/local-motion state;
- faults/degraded modes where modelled.

The existing qualified Wayfarer torch/metric engineering remains the performance authority unless deliberately changed through governed physics work.

## 11. Sensor, navigation-estimation, guidance and control layer

The GM/world simulation may know true state. The player-facing HUD should eventually operate from estimated state.

Required architecture:

```text
TRUE STATE
  ↓
SENSOR MODELS
  ↓
MEASUREMENTS
  ↓
NAVIGATION FILTER / ESTIMATOR
  ↓
ESTIMATED STATE + COVARIANCE / QUALITY
  ↓
GUIDANCE TARGETS
  ↓
CONTROL COMMANDS
  ↓
ACTUATORS / PROPULSION
  ↓
TRUE STATE
```

Sensor models may include, as appropriate:

- inertial measurement;
- star/attitude reference;
- optical navigation;
- radar/lidar/range-rate;
- GNSS-like/local beacon systems where infrastructure supports them;
- station/proximity sensors;
- altimetry/terrain-relative navigation;
- engineering sensors for propulsion, power, thermal and structural state.

Do not require maximum sensor fidelity immediately. Start with typed measurement/estimate contracts and deterministic, qualified sensor-error models, then increase fidelity where gameplay and validation justify it.

## 12. Communications and telemetry realism

Telemetry and command paths should eventually model:

- propagation/light-time where operationally significant;
- line-of-sight/occlusion;
- antenna/network availability;
- data latency and staleness;
- command acknowledgement delay;
- bandwidth/priority at an appropriate abstraction level;
- station/local traffic-network support.

A remote controller should not receive instantaneous omniscient telemetry merely because GM truth exists.

## 13. Campaign persistence expansion target

Current campaign JSON/history authority remains authoritative until the already-governed campaign-SQL promotion gate is passed.

When campaign SQLite is designed/promoted, its target schema must support mutable simulator state without absorbing immutable/bulk world products.

Candidate campaign responsibilities include:

- campaign revision and epoch;
- current vehicle true state/reference;
- current navigation estimated state/reference;
- orientation/angular rate;
- current mass/remass/consumables;
- power/thermal/propulsion/metric operational state;
- active flight/trajectory reference;
- active guidance/control phase;
- docking/landed/orbital/local-flight state;
- traffic clearance/authorization state;
- current faults/degraded states;
- canonical transitions and event history;
- save/checkpoint/session linkage.

Bulk ephemerides, terrain/shape models, large trajectory sample sets, media and immutable world/canon authority should remain outside campaign persistence.

## 14. Telemetry contract

Telemetry must be a derived application product, not an independent truth store.

Every telemetry field should, where meaningful, carry or inherit:

- value;
- unit;
- epoch;
- reference frame/context;
- true vs measured vs estimated vs commanded semantic;
- source subsystem;
- quality/uncertainty/staleness;
- provenance/qualification version.

Example derived fields include:

- range / range rate;
- relative position / velocity;
- acceleration/load factor;
- attitude/attitude error;
- burn residual / target delta-v;
- remass flow and remaining inventory;
- power generation/load/storage;
- thermal/radiator state;
- metric state/beta/transition state where applicable;
- navigation covariance/quality;
- traffic clearance / corridor / hold-state status;
- docking/landing gate state;
- ETA and solution freshness.

## 15. Validation and known-answer qualification

Ordinary-space simulation should be tested against external known-answer sources wherever practical.

Qualification families should include:

- celestial state/ephemeris comparisons;
- reference-frame transform checks;
- two-body and selected perturbation propagation cases;
- orbit/state conversion checks;
- rendezvous/phasing/relative-motion cases;
- docking/approach geometry checks;
- surface body-fixed/inertial transform cases;
- atmospheric/entry cases where implemented;
- sensor/navigation-estimator deterministic tests;
- cross-platform numerical parity.

Torch/metric qualification must retain existing regression evidence and add subsystem/state/telemetry consistency tests without pretending speculative metric physics is empirically validated.

## 16. Revised staged implementation sequence

The existing stages remain valid, but the program is amended as follows.

### Stage F — Basic interactive 3D viewer (current)

Continue current representation work, but Stage F must remain authority-safe:

- one playback epoch for ship, bodies, stations and HUD;
- ordinary-space geometry only where physically authoritative;
- metric transit relational/non-occupancy;
- local body/station 3D prepared for authoritative endpoints;
- no fabricated station or surface positions;
- explicit Navigator→HUD handoff design;
- numerical epoch/frame consistency qualification;
- Pixel and Windows physical/usability qualification.

Stage F does **not** need to solve the entire simulator stack before it closes.

### New Stage F-PA — Physical Authority Audit

Perform before broad local infrastructure visualization or telemetry polish.

Deliver:

- Git-sourced schema/data inventory for WORLD, CIVSTATE and campaign authority;
- classification of current spatial/infrastructure/orbit fields by authority quality;
- inventory of all navigable orbital and surface infrastructure;
- list of missing surface coordinates/orbits/frames/provenance;
- audit of current ephemeris validity/coverage and frame semantics;
- audit of current Wayfarer state/telemetry sources;
- proposed world-schema migration only after audit evidence exists.

Gate:

- no guessed physical values;
- every identified gap traced to an entity/table/contract;
- documentary references fetched from GitHub authority.

### New Stage F-PB — Physical Authority Schema / Contracts

Deliver:

- typed celestial-physical model contract;
- surface-site contract;
- orbital-object/station contract;
- body traffic-regime contract;
- transition-point contract;
- docking/landing-facility geometry contract;
- expanded frame registry/transform contract;
- explicit provenance/navigation-grade semantics;
- migration design for the next WORLD schema version.

Gate:

- no renderer-owned physics;
- no body-center shortcut for ships/infrastructure;
- no surface/orbital placement without explicit authority class.

### New Stage F-PC — Time-Resolved Infrastructure

Deliver:

- authoritative state resolution for orbital stations at arbitrary supported epoch;
- body-fixed→inertial resolution for surface sites;
- local station/body frames;
- 3D rendering from the same physical state consumed by Navigator/HUD;
- exact epoch/frame numerical qualification.

### New Stage F-PD — Authorized Orbits / Traffic Regimes

Deliver:

- governed body-specific orbit classes;
- traffic constraints and keep-out/corridor geometry;
- orbit resolver producing actual 6D states from authorized class + epoch;
- civil authority separated from physical dynamics authority;
- initial high-traffic-body implementations before broad system expansion.

### New Stage F-PE — Transition Dynamics / Handoff

Deliver:

- station rendezvous/departure gates;
- docking proximity-operation boundary;
- surface deorbit/entry/terminal-area/landing gates;
- Navigator terminal state → HUD local-flight contract;
- reverse HUD local departure → Navigator contract;
- ordinary-space dynamics derived at each transition.

### New Stage F-PF — Vehicle State Simulation Core

Deliver:

- continuous/stepwise true-state propagation;
- attitude/angular state where required;
- mass/remass/power/thermal/propulsion coupling;
- torch and metric subsystem state integration;
- deterministic state transitions and telemetry derivation.

### New Stage F-PG — Sensors / Navigation / GN&C

Deliver incrementally:

- measurement contracts;
- deterministic sensor models;
- navigation estimator and uncertainty/covariance semantics;
- guidance targets;
- control/actuator command contracts;
- HUD estimated-state path distinct from GM true state.

### New Stage F-PH — Telemetry / Mission Operations

Deliver:

- typed telemetry bus/view model;
- traffic-clearance state;
- docking/landing/local-flight telemetry;
- communications latency/staleness where applicable;
- HUD instruments sourced only from real simulation/runtime state.

These new physical-authority stages may overlap later pre-existing stages where appropriate, but their gates may not be bypassed by presentation work.

## 17. Immediate execution order

The next physical-simulator work should proceed in this order:

1. finish/qualify the current Stage-F representation work enough to preserve its useful 3D foundations;
2. run **Stage F-PA — Physical Authority Audit** against live GitHub authority;
3. produce an entity-by-entity infrastructure spatial-quality matrix;
4. inspect current ephemeris coverage/frames/validity and current orbit/placement semantics;
5. design the next WORLD schema/typed contracts from observed gaps rather than assumptions;
6. define governed body-specific orbit/traffic regimes;
7. populate/qualify authoritative orbital-station and surface-site spatial definitions;
8. implement shared time-resolved infrastructure/state resolution;
9. implement Navigator transition-state/handoff contracts;
10. implement vehicle true-state dynamics;
11. add estimated-navigation/GN&C and telemetry realism;
12. only then treat HUD numerical richness as a product-completion task.

## 18. Non-negotiable simulator rules

1. **Real telemetry, not decorative telemetry.**
2. **Everything spatial is fundamentally 3D.**
3. **Every moving state is evaluated at an explicit game/query/playback epoch.**
4. **Every state carries a frame or inherits one unambiguously.**
5. **Surface infrastructure has body-fixed physical coordinates before it is navigation-grade.**
6. **Orbital infrastructure has a time-resolvable orbit/state before it is navigation-grade.**
7. **Traffic law constrains legal operations; physics determines actual motion.**
8. **Navigator solves to meaningful transition states; HUD/local flight owns final local maneuvering.**
9. **NASA/JPL/NAIF/IDSS practice is used where applicable, but nonexistent universal standards are not invented.**
10. **GM true state and player estimated state are distinct concepts.**
11. **Torch engineering remains inside ordinary dynamical accounting.**
12. **Metric physics remains explicitly speculative and must never masquerade as empirically validated ordinary physics.**
13. **No UX surface owns physical truth.**
14. **No chat-memory statement is documentary authority; governing LOOM documents/code must be fetched from GitHub before reliance.**
15. **Do not break the accepted Phase-6 campaign authority chain while building the simulator.**
