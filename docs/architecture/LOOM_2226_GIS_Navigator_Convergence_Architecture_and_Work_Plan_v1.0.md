# LOOM 2226 — GIS / Navigator Convergence Architecture and Work Plan v1.0

**Status:** Governing implementation reference for the GIS/Navigator convergence workstream.  
**Repository:** `loom-2226/loom-2226`  
**Date:** 2026-09-03  

## 1. Executive decision

LOOM 2226 will converge the existing Solar GIS and Navigator into a single operational application surface.

**GIS becomes the sole visual application. Navigator becomes the navigation / flight domain engine behind it.**

The existing SVG/HTML Navigator renderer is retained only as a temporary qualification oracle until GIS achieves feature and behavioral parity. It is then retired.

This is not a direct merger of two monolithic Python applications. Navigator domain logic is to be extracted into reusable services/modules with explicit contracts. GIS will call those services and remain responsible only for visualization, interaction, selection, and presentation.

## 2. Target architecture

```text
                         LOOM 2226
                            |
                    +-------v--------+
                    |   GIS / HUD UI |
                    | sole visual app|
                    +-------+--------+
                            |
              canonical typed contracts
                            |
          +-----------------+------------------+
          |                 |                  |
   World / CIVSTATE     Navigation         Campaign
       services           services          services
          |                 |                  |
          |        +--------+--------+         |
          |        | flight planner |         |
          |        | route solver   |         |
          |        | ephemeris      |         |
          |        | execution      |         |
          |        +--------+--------+         |
          |                 |                  |
          +-----------------+------------------+
                            |
                      persistence
                            |
         +------------------+-----------------+
         |                  |                 |
   LOOM_2226.sqlite3   CIVSTATE.sqlite3   campaign state
                                           / history
```

### Governing architectural rules

1. GIS is the only user-facing visual application.
2. Navigation physics, route planning, execution, and ephemeris remain authoritative domain services.
3. GIS has **zero physics authority**. It renders authoritative outputs; it does not calculate flight truth.
4. LLMs retain zero calculation authority and zero state authority.
5. There is one canonical campaign-state authority.
6. Runtime consumers must use canonical typed/validated contracts and adapters/accessors rather than hard-coded payload field names or mode strings.
7. Python, SQL, JavaScript, HTML, schemas, manifests, migrations, tests, and documentation are versioned in Git.
8. Production SQLite datasets are controlled runtime artifacts; schema evolution is versioned through numbered SQL migrations and release manifests.

## 3. Target repository structure

```text
src/
    loom/
        app/
            gis.py
        navigation/
            planner.py
            execution.py
            ephemeris.py
            strategies.py
            contracts.py
        world/
            repository.py
            civstate.py
            graph.py
        campaign/
            state.py
            history.py
        presentation/
            route_layers.py
            flight_layers.py
            selection.py

deploy/
    android/
        launch_loom.py
    windows/
        launch_loom.py

sql/
    schema/
        baseline.sql
    migrations/
        001_...
        002_...
    views/
    seeds/

tests/
    unit/
    integration/
    regression/
    fixtures/

manifests/
    release_manifest.json
    database_manifest.json

docs/
    architecture/
    contracts/
```

This is the destination, not a requirement to reorganize all files immediately.

## 4. Work plan

### Phase 0 — Freeze the known-good pre-convergence state

Before architectural changes:

- freeze the current qualified runtime;
- create a Git tag/release such as `navigator-gis-premerge-v1.0`;
- record the current Git commit SHA;
- record GIS, Navigator core, Sequence H, database, CIVSTATE, and B1 asset hashes;
- record schema versions and campaign-state compatibility;
- preserve the current Android runtime structure;
- preserve the current qualification outputs.

**Gate 0:** fresh Pixel qualification passes from the frozen source.

### Phase 1 — Repository hygiene and versioning model

Normalize the repository around stable production filenames rather than version-heavy filenames.

Examples:

```text
loom_solar_gis.py
loom_navigator_core.py
```

Version history is carried by Git commits, tags, release manifests, and compatibility metadata rather than filename archaeology.

Repository rules:

- Python/JS/HTML/SQL -> Git;
- production SQLite data -> controlled snapshots/release artifacts;
- schema changes -> numbered migrations;
- every release -> hashes, schema version, compatibility declaration.

### Phase 2 — Extract Navigator domain logic

Inspect the current Navigator core, Sequence H, launchers, and related runtime code. Classify functions as:

```text
DOMAIN LOGIC
STATE/PERSISTENCE
PRESENTATION
USER INTERACTION
QUALIFICATION/TEST
LEGACY
```

Extract authoritative navigation functionality without changing behavior.

Initial canonical domain objects should include:

```text
NavigationRequest
NavigationContext
RouteCandidate
FlightPlan
FlightExecutionResult
EphemerisSnapshot
TrajectorySegment
ArrivalState
```

Initial service interface should include operations such as:

```text
discover_routes(...)
plan_flight(...)
compile_flight(...)
execute_flight(...)
get_ephemeris(...)
get_flight_geometry(...)
```

GIS and other consumers must use these contracts rather than direct dictionary-key coupling.

**Gate A — Engine extraction:** existing Navigator regression tests pass against the extracted services with identical authoritative results.

### Phase 3 — Establish the GIS navigation-layer contract

Define a versioned GIS-facing route contract, initially `LOOM_ROUTE_LAYER_V1`.

Minimum content:

```text
route_id
flight_id
origin
destination
departure_epoch
arrival_epoch
strategy
status

segments[]
    type
    start_epoch
    end_epoch
    start_position
    end_position
    geometry
    velocity
    acceleration
    phase

waypoints[]
bodies[]
maneuvers[]
current_vehicle_state
arrival_state
```

The contract contains physics truth and semantic route state, **not display instructions**.

GIS owns symbology and presentation for:

- torch phases;
- metric phases;
- coasts;
- gravity assists;
- precision collapse;
- arrival acquisition;
- planned routes;
- executed routes;
- historical routes.

### Phase 4 — Render Navigator routes in GIS

Implement route visualization incrementally.

**Route Layer 1**
- selected planned route;
- origin and destination;
- trajectory;
- current ship position;
- departure and arrival markers.

**Route Layer 2**
- phase-specific geometry;
- torch;
- metric;
- coast/collapse/acquisition.

**Route Layer 3**
- alternate candidates.

**Route Layer 4**
- executed and historical trajectories.

Initial GIS navigation controls should expose:

```text
NAVIGATION
 |- Active route
 |- Alternate routes
 |- Flight phases
 |- Maneuvers
 |- Historical tracks
 `- Traffic / CIVSTATE
```

Selecting ships, routes, waypoints, or destinations should use the GIS intelligence panel rather than opening a separate Navigator surface.

### Phase 5 — Move flight planning interaction into GIS

After route rendering is stable, migrate the planning workflow.

Target interaction:

```text
PLAN FLIGHT

Origin:      CERES
Destination: MARS
Priority:    BALANCED

DISCOVER ROUTES
```

Candidate routes appear spatially on the GIS and may also be shown in a compact comparison table.

The user can inspect a candidate and then:

```text
PLAN DETAILS
COMMIT
CANCEL
```

All planning and flight calculations continue to come from Navigator services.

**Invariant:** GIS performs no flight math.

### Phase 6 — Integrate campaign execution

GIS becomes the operational console for the campaign.

Target integrated workflow:

```text
Take job
Load cargo
Plan route
Inspect route
Commit flight
Execute
Arrive
Unload
Refuel
Service
Advance time
Inspect world
Inspect relationships
Inspect traffic
Inspect history
```

Navigation execution updates the canonical campaign state. GIS automatically reflects the updated ship location, epoch, world state, and applicable history.

There must never be separate authoritative locations or epochs in GIS and Navigator.

**Gate C — Operational convergence:** GIS can initiate, inspect, commit, execute, and display an authoritative flight using canonical campaign state.

### Phase 7 — SQL migration discipline

Establish numbered schema migrations.

Example:

```text
sql/migrations/
    001_baseline_schema.sql
    002_route_geometry.sql
    003_event_layer.sql
    004_knowledge_graph.sql
    005_campaign_location_indexes.sql
```

Each migration should define:

```text
from_schema_version
to_schema_version
description
forward migration
validation queries
```

Maintain a SQLite metadata table such as:

```text
loom_schema_history
-------------------
migration_id
schema_version
applied_utc
git_commit
sha256
description
```

A production database should be able to identify the migration and Git lineage from which it was built.

### Phase 8 — Automated qualification

Every substantive change should run appropriate tests.

**Unit**
- navigation contracts;
- mass accounting;
- state transitions;
- graph queries;
- GIS adapters.

**Integration**
- GIS <-> navigation;
- navigation <-> campaign;
- GIS <-> CIVSTATE;
- migrations <-> SQLite.

**Regression**
- Navigator MVP suite;
- K1;
- CIVSTATE;
- known flight fixtures.

Full end-to-end qualification remains reserved for production-release finalization.

Maintain golden flight fixtures including at least:

```text
Ceres -> Mars
Ceres -> Neptune
inner-system route
outer-system route
moon/local-system route
precision-collapse route
```

Same authoritative inputs should continue to reproduce expected physics outputs.

### Phase 9 — Retire the old Navigator renderer

The visual Navigator is not removed until GIS reaches parity.

Once Gate B and Gate C pass, retire:

- Navigator SVG rendering;
- Navigator HTML visualizer;
- browser-specific route renderer;
- duplicate visual contracts;
- separate visual Navigator launch path.

Retain the domain engine under a namespace such as:

```text
loom.navigation
```

Create a final archival tag such as:

```text
navigator-visual-final
```

The legacy renderer then becomes historical reference only.

**Gate B — GIS parity:** GIS can visualize every meaningful authoritative flight state required from the old Navigator renderer.

### Phase 10 — One production launcher

Final runtime target:

```text
launch_loom.py
```

This launches GIS, the sole visual application.

Target Pixel runtime structure:

```text
LOOM_TEST/
    src/
    data/
    deploy/
    state/
    cache/
```

Windows should use the same logical structure with platform-specific launch and path adapters only where necessary.

The updater installs only artifacts declared by the release manifest.

## 5. Git workflow

Keep the workflow lightweight.

```text
main
  production / qualified

feature/*
  active development

release/*
  stabilization only
```

Primary convergence branch:

```text
feature/gis-navigator-convergence
```

Commits should represent meaningful architectural milestones, for example:

```text
nav: extract flight planning contracts
nav: separate execution service from CLI
gis: add route-layer contract adapter
gis: render planned trajectory
gis: add candidate route selection
db: add migration framework
runtime: unify application launcher
nav: retire legacy visual renderer
```

## 6. Release/version model

Avoid carrying history in production filenames.

Preferred production artifacts:

```text
loom_solar_gis.py
loom_navigation.py
launch_loom.py
```

Version lineage is carried by:

```text
Git tag
Git commit SHA
release manifest
schema version
contract version
```

Example release metadata:

```text
LOOM 2226 v0.13.0
GIS 0.13
NAVIGATION CONTRACT 2
DB SCHEMA 14
CIVSTATE SCHEMA 1.2
```

## 7. Delivery gates

Three major gates govern retirement of the old Navigator surface.

### Gate A — Engine extraction

Navigator calculations work independently of Navigator UI and preserve authoritative outputs.

### Gate B — GIS parity

GIS can visualize every meaningful flight state required by the old Navigator renderer.

### Gate C — Operational convergence

GIS can initiate, inspect, commit, execute, and display a flight using canonical campaign state.

Only after Gate C passes is the old Navigator renderer removed from the production runtime.

## 8. Strategic consequence

This convergence creates a single spatial-temporal operating picture for LOOM 2226.

Routes, traffic, incidents, facilities, organizations, relationships, campaign state, player knowledge, world truth, and future event/intelligence layers can all be represented through one coherent GIS/HUD environment while their underlying authorities remain properly separated.

The result is not "Navigator embedded in GIS." It is a single LOOM operational application with specialized domain engines behind it.

---

**New-chat reference phrase:** `Reference the GIS/Navigator Convergence Architecture and Work Plan v1.0 in GitHub.`
