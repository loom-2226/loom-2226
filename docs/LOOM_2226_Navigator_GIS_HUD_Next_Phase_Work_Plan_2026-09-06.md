# LOOM 2226 — Navigator / GIS / HUD Next-Phase Work Plan

Date: 2026-09-06  
Status: **Governing forward work plan — planning branch**  
Baseline source branch: `release/runtime-devops-gis-baseline-2026-09-06`  
Baseline commit: `43fc7cd92a71e0460e551bcc2d6a717ccac796ca`  
Planning branch: `planning/navigator-gis-hud-next-phase-2026-09-06`

## 0. Purpose

This document defines the next implementation program for LOOM Navigator, GIS, HUD, campaign persistence, temporal/spatial runtime, travel visualization, Loom translation, platform parity, and runtime/DevOps support.

It is intentionally downstream of the accepted runtime/GIS freeze and does **not** reopen completed migration or authority work casually.

Governing baseline documents:

- `docs/LOOM_2226_Runtime_DevOps_Status_2026-09-06.md`
- `docs/LOOM_2226_GIS_Navigator_Status_2026-09-06.md`
- `docs/seeds/LOOM_2226_Navigator_GIS_Next_Thread_Seed_2026-09-06.md`

The accepted Phase-6 flight loop remains the preservation baseline:

1. GIS selection
2. Navigator endpoint resolution
3. route discovery
4. route comparison/presentation
5. preview
6. planning commit without campaign write
7. explicit execute
8. arrival computation
9. exactly one canonical campaign transition
10. historical overlay
11. GIS rebind

Mars → Ceres physically passed this loop on the migrated Pixel at campaign revision 8 → 9.

The next phase is therefore not a migration project. It is an application architecture and product implementation program.

---

## 1. Product target

LOOM should evolve into one spatial-temporal simulation/application with multiple presentation surfaces rather than a collection of loosely coupled tools.

Primary surfaces:

- **GIS** — world, infrastructure, history, discovery, context, selection, spatial/temporal exploration
- **Navigator** — route generation, comparison, trajectory qualification, travel planning, execution intent
- **HUD** — operational cockpit, live flight state, instrumentation, tactical view, playback, conversational control
- **ChatGPT / LLM surface** — reasoning, GM interaction, explanation, tool-mediated inspection and command support

These surfaces must share canonical application state rather than owning separate truths.

### 1.1 New architectural rule

> **No UX surface owns campaign state, game time, physics, ephemeris truth, or conversation/session truth.**

ChatGPT, GIS, Navigator, and HUD are clients of LOOM application services.

### 1.2 High-level target architecture

```text
                         LOOM SESSION
                              │
                     CAMPAIGN AUTHORITY
                     revision + game time
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
      WORLD STATE        NAVIGATOR           KNOWLEDGE
   canon / CIVSTATE     physics / routing    player / NPC
          │                   │                   │
          └──────────── SPATIAL-TEMPORAL ─────────┘
                          RUNTIME
                  position / velocity @ t
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
           GIS            NAVIGATOR            HUD
        world view         planning          cockpit
            │                 │                 │
            └────────── conversation / LLM ────┘
                              │
                    ChatGPT or HUD client
```

---

## 2. Preservation constraints

The following remain frozen unless a later phase explicitly replaces them through a designed and physically qualified migration:

- split-root runtime ownership
- updater boundaries
- campaign protection from updater writes
- current Phase-6 planning/execute authority chain
- Navigator endpoint/route calculation authority
- GIS map/presentation authority
- explicit distinction between planning commit and execution
- rollback retention of `/storage/emulated/0/Download/LOOM_TEST`
- current JSON/history campaign authority until campaign-SQL promotion is formally approved

Shadow campaign SQL remains diagnostic/best-effort only at the start of this plan.

---

## 3. Cross-cutting design principles

### 3.1 Campaign authority and persistence are separate concerns

The rest of LOOM should talk to a Campaign Authority service, not directly to JSON files or SQLite tables.

This allows persistence to migrate from JSON/history to campaign SQLite without rewriting Navigator, GIS, HUD, or LLM tooling.

### 3.2 Time is first-class

Every authoritative spatial, ephemeris, trajectory, world-state, and playback query must be anchored to a declared game epoch.

No gameplay component may silently use real-world wall-clock time as the universe time.

### 3.3 3D physics is authoritative; 2D is a projection

Navigator trajectories and world positions become true 3D spatial objects. Existing 2D GIS remains useful, but it must become a projection of the underlying spatial state rather than the authoritative representation of flight geometry.

### 3.4 Playback is not campaign mutation

Continuous flight animation, historical replay, scrubbing, and accelerated viewing must not create repeated campaign writes.

Campaign state transitions remain sparse and explicit.

### 3.5 Loom travel is not fake FTL motion

Loom translation must be represented as a relational-topology transition between local spacetime domains, not a ship icon traversing intervening light-years.

### 3.6 HUD instrumentation must reflect actual state

The HUD should expose real values from typed runtime state, not decorative sci-fi numbers.

### 3.7 Platform parity is semantic, not pixel-identical

Pixel and Windows may render differently for screen size and performance, but must consume the same contracts and produce the same numerical/campaign outcomes.

### 3.8 Diagnostics remain support infrastructure, never runtime authority

Observability must help us qualify and debug the system without becoming a dependency for gameplay.

---

## 4. Canonical contracts and service boundaries

Before major UX implementation, formalize typed, validated contracts with adapters/accessors. Avoid hard-coding runtime payload keys or route/mode strings across consumers.

### 4.1 `CampaignClockState`

Minimum fields:

- `campaign_id`
- `revision`
- `epoch_utc`
- `last_transition_id`
- `clock_schema_version`

Optional later fields:

- pause/run metadata if a real-time simulation mode is ever introduced
- user-visible display calendar options

### 4.2 `SpatialState`

Minimum fields:

- `entity_id`
- `epoch_utc`
- `reference_frame`
- `position_xyz_km`
- `velocity_xyz_km_s`
- `orientation` if available/relevant
- `source`
- `navigation_grade`
- `uncertainty`
- `provenance`

### 4.3 `TrajectorySolution`

Minimum fields:

- `trajectory_id`
- `campaign_revision`
- `solution_epoch_utc`
- `origin_endpoint`
- `destination_endpoint`
- `reference_frame`
- `departure_epoch_utc`
- `arrival_epoch_utc`
- `segments[]`
- `trajectory_samples[]` or a reference to sampled trajectory storage
- `qualification`
- `costs`
- `risk`
- `provenance`

### 4.4 `TrajectorySegment`

Minimum fields:

- `segment_type`
- `start_epoch_utc`
- `end_epoch_utc`
- `start_state`
- `end_state`
- `propulsion_mode`
- `acceleration_profile`
- `remass_delta`
- `thermal_state/reference`
- `metric_state/reference`
- `qualification`

### 4.5 `NavigationEndpoint`

Typed endpoint categories should eventually include:

- celestial body
- barycenter
- surface site
- orbital facility
- habitat/station
- Lagrange region
- free-space waypoint
- Loom staging volume

This replaces indefinite growth of name-specific endpoint exceptions.

### 4.6 `LoomRouteSolution`

Separate from metric-space trajectory representation.

Minimum fields:

- `route_id`
- `source_domain`
- `destination_domain`
- `relational_edges[]`
- `directionality`
- `solution_confidence`
- `endpoint_geometry`
- `lattice_requirement`
- `formation_time`
- `commitment_time`
- `translation_time`
- `resolution_time`
- `arrival_spatial_state`
- `ordinary_terminal_delta_v`
- `provenance`

### 4.7 `FlightPlaybackState`

Minimum fields:

- `flight_id`
- `trajectory_id`
- `authoritative_departure_epoch`
- `authoritative_arrival_epoch`
- `playback_cursor_epoch`
- `playback_rate`
- `camera_mode`
- `is_historical_replay`

### 4.8 `LoomSession`

Target durable session abstraction linking:

- campaign identity/revision
- selected entity/destination
- current application context
- conversation/event log
- model/tool events
- provenance/source references
- optional external LLM conversation identifiers

LOOM should own this durable session state so ChatGPT and a standalone HUD can both reconnect to the same semantic context.

---

## 5. Campaign SQLite promotion workstream

Campaign SQLite is explicitly part of the target architecture, but it is **not authoritative at the start of this plan**.

### 5.1 Target role

Campaign SQLite should become the persistent operational store for mutable campaign state and canonical campaign history after successful promotion.

Expected responsibility:

- campaign identity
- authoritative revision
- authoritative game epoch
- current ship/player location
- canonical transitions
- committed/executed flight references
- event/history records
- save/checkpoint metadata
- session linkage
- references to external trajectory/history products

It should **not** absorb everything.

World/canon databases, large ephemeris products, media, CIVSTATE, and potentially heavy sampled trajectory geometry should remain separate stores or artifacts.

### 5.2 Promotion sequence

1. inventory current JSON/history authority semantics
2. inspect current shadow SQL schema and gaps
3. define target campaign SQLite schema
4. build persistence adapter behind Campaign Authority service
5. dual-write or mirrored diagnostic population where safe
6. perform read equivalence checks
7. perform revision/history/hash/state equivalence checks
8. test stale-state guard
9. test failed-write rollback
10. test exact one-transition execution semantics
11. run Mars → Ceres Phase-6 regression
12. run Pixel physical acceptance
13. run Windows parity acceptance
14. only then authorize campaign SQLite as canonical persistence

### 5.3 Promotion gate

Campaign SQL promotion requires explicit evidence that:

- state before and after a known flight matches expected semantics
- revision increments once
- epoch advances once
- history appends once
- failed executes are non-destructive
- rollback restores the exact prior canonical state
- JSON/history can be retained temporarily as compatibility/export during cutover if needed

Until this gate passes, the current baseline remains in force: JSON/history authoritative, campaign SQL diagnostic/best-effort only.

---

## 6. Persistent game time workstream

### 6.1 Canonical campaign clock

Create a first-class Campaign Clock service.

Conceptual API:

```text
CampaignClock.read()
CampaignClock.require_revision(revision)
CampaignClock.advance(authorized_transition)
CampaignClock.resolve(epoch)
```

### 6.2 Distinct time concepts

LOOM must explicitly distinguish:

1. **campaign time** — authoritative universe time for active gameplay
2. **query/simulation time** — arbitrary epoch used to ask what the world looked/looks like at T
3. **playback time** — UI cursor used for flight animation or historical replay

Playback/query time does not mutate campaign time.

### 6.3 Ephemeris rule

All ephemeris/spatial calls must accept or resolve a LOOM game epoch.

Conceptually:

```text
get_spatial_state(entity_id, epoch_utc)
```

not:

```text
get_spatial_state(entity_id, wall_clock_now)
```

### 6.4 Solution freshness

Every route/trajectory solution is stamped with campaign revision and solution epoch.

If campaign revision or relevant epoch changes beyond qualification limits, the solution becomes stale and must be revalidated/re-solved.

### 6.5 Gate

- campaign epoch persists across restart
- Pixel and Windows load the same epoch
- preview does not alter epoch
- planning commit does not alter epoch unless explicitly designed later
- execute advances epoch exactly once
- replay/scrub does not alter epoch
- stale solutions are detected

---

## 7. 3D spatial runtime workstream

### 7.1 Reference-frame discipline

Support explicit frames rather than anonymous coordinate arrays.

Initial practical set:

- heliocentric J2000/ecliptic or existing canonical navigation frame
- body-centric frame
- station/body-relative local frame
- ship-local tactical frame

Transforms belong in one spatial service.

Renderers must not reinvent physics transforms.

### 7.2 Scene graph

Each visible entity should resolve to a time-stamped world state including:

- parent relationship if relevant
- world position
- local position
- velocity
- orientation if relevant
- physical scale
- render scale
- epoch
- provenance/quality

### 7.3 Physical versus render scale

Maintain physical coordinates separately from render transforms.

Bodies/icons may be visually exaggerated for usability, but trajectory physics and relative geometry remain untouched.

### 7.4 Camera modes

Initial modes:

- SYSTEM
- ORIGIN
- DESTINATION
- FOLLOW SHIP
- FREE
- LOCAL / TACTICAL

Later optional modes:

- chase
- trajectory-normal
- orbital-plane
- arrival-geometry

### 7.5 Gate

Given the same epoch, Pixel and Windows must produce the same numerical spatial states before any visual-only scaling.

---

## 8. True 3D Navigator trajectory workstream

True 3D trajectories are a first-priority requirement.

### 8.1 Conventional/torch travel

Trajectory representation should expose usable time-parameterized spatial state:

- `r(t)`
- `v(t)`
- `a(t)` or equivalent segment profile

within the accepted solver model.

### 8.2 Metric travel

Metric flights should expose their actual staged structure rather than only ETA/cost totals:

- conventional departure/staging
- metric establishment
- metric transit
- collapse/stand-off geometry
- terminal conventional transfer

Different operating modes should visibly produce different path/time/cost/geometry consequences.

### 8.3 Adaptive trajectory sampling

Avoid brute-force fixed-rate sampling.

Sample densely around:

- departure
- burns/transitions
- closest approaches
- metric establishment/collapse
- arrival

Sample sparsely during uneventful cruise.

Interpolate deterministically for visualization.

### 8.4 Route comparison

Navigator should expose multiple qualified candidate routes simultaneously.

The UX must synchronize route cards and 3D paths: selecting a route in the comparison UI selects/highlights the corresponding trajectory in the scene.

### 8.5 Gate

Mars → Ceres must retain the accepted Phase-6 physical/campaign outcome under the enhanced trajectory representation.

This phase enhances representation; it does not silently change accepted physics.

---

## 9. Unified GIS / Navigator flight-planning UX

The player should experience one continuous spatial workflow rather than jumping between loosely connected products.

### 9.1 Target interaction

1. select destination directly on map/scene
2. inspect world context
3. choose **NAVIGATE**
4. planning drawer opens without losing spatial context
5. candidate routes appear
6. candidate trajectories render in 3D
7. select/compare strategy
8. inspect timing/remass/risk/geometry
9. preview
10. planning commit
11. explicit execute
12. animated playback or skip
13. arrival
14. GIS rebind

### 9.2 Authority boundary

GIS owns:

- selection
- spatial presentation
- map/camera interaction
- route comparison display
- explicit user actions

Navigator owns:

- endpoint validity
- route discovery
- flight compilation
- trajectory/physics
- qualification

Campaign Authority owns:

- current state
- revision
- game time
- canonical transition

### 9.3 Gate

Mars → Ceres must be executable entirely through the unified UX while preserving the accepted underlying authority chain.

---

## 10. Animated flight and FOLLOW SHIP

Animated travel should become a core map feature.

### 10.1 Execution playback

After successful execute, the renderer should deterministically play the authorized trajectory from departure epoch to arrival epoch.

At any playback time `t`, the scene resolves:

- ship state from trajectory
- body/infrastructure state from ephemeris/world state
- HUD instrumentation from the same state

### 10.2 Playback controls

Initial controls:

- pause/play
- 1×
- 10×
- 100×
- 1000× or adaptive fast-forward
- skip to arrival
- scrub where physically/UX appropriate

Playback duration is a UX choice and does not have to equal game elapsed time.

### 10.3 FOLLOW SHIP

FOLLOW SHIP should be a signature operational mode.

Camera remains attached to or centered on the spacecraft while:

- origin recedes
- destination approaches
- ephemerides advance
- velocity/acceleration states update
- instrumentation updates

### 10.4 Replay

Executed trajectories should remain referenceable for later historical replay.

### 10.5 Gate

Whether the player watches the animation, accelerates it, or skips it entirely, arrival campaign state must be semantically identical.

---

## 11. Loom travel workstream

Loom-based travel becomes a first-class Navigator regime after conventional 3D navigation is stable.

### 11.1 Two spatial concepts

LOOM must represent:

- **metric physical space** — actual astronomical 3D geometry
- **Loom relational topology** — experimentally known/predicted relational connections between domains

These are related but not interchangeable.

### 11.2 Loom graph model

Create explicit node/edge/route structures carrying:

- source/destination domain
- directionality
- route confidence
- discovery provenance
- last validation epoch
- coherence requirements
- endpoint geometry requirements
- infrastructure/lattice requirements
- operational cost/risk

A viable A → B route does not automatically imply B → A viability.

### 11.3 Mixed-mode planning

Navigator should be able to construct mixed itineraries such as:

```text
current location
   ↓ torch/metric
Loom staging region
   ↓ Loom translation
arrival domain
   ↓ torch/metric
terminal destination
```

### 11.4 Loom animation

Do not animate the ship moving through intervening light-years.

Target sequence:

1. conventional approach to departure geometry
2. lattice/formation state
3. coherence/solution establishment
4. commitment
5. physical-map transition
6. relational/topological visualization
7. resolution
8. emergence in destination local spacetime
9. local navigation reacquisition
10. terminal conventional transfer

### 11.5 Hard rule

There must never be an authoritative gameplay state corresponding to a ship “halfway” through interstellar metric space during Loom translation.

---

## 12. HUD 2.0 design

HUD becomes the operational cockpit surface and may eventually host the LLM directly if ChatGPT embedding is insufficient.

### 12.1 Design lineage

Preserve the existing HUD philosophy:

- restrained instrument-like presentation
- progressive disclosure
- touch-safe interaction
- minimal decorative noise
- alerts reserved for genuinely important states
- assurance/provenance available without dominating routine operation

### 12.2 Major change

The 3D scene becomes the primary visual surface.

The HUD should not become a wall of panels surrounding a small map.

### 12.3 Primary mobile layout

Default Pixel portrait surface should prioritize:

- current ship / route / campaign revision
- campaign game time
- large 3D operational view
- range
- relative velocity
- ETA
- propulsion/acceleration state
- remass/power/thermal/metric status as relevant
- FOLLOW / PLAN / CHAT / MORE actions

### 12.4 Progressive disclosure layers

Suggested modes:

**NAV**
- trajectory
- intercept
- ETA
- vectors
- route phases

**SHIP**
- propulsion
- remass
- power
- thermal
- metric/Loom hardware state

**TACTICAL**
- contacts
- uncertainty
- LOS
- threat/intent if available

**MISSION**
- destination
- route
- objectives
- current transition state

**ASSURANCE**
- solution validity
- navigation grade
- provenance
- qualification state

**HISTORY**
- prior flights/events
- replay

### 12.5 Alerts

Reserve high-attention states for matters such as:

- trajectory invalid/stale
- collision/clearance hazard
- insufficient remass
- drive/array limit
- thermal danger
- stale or low-confidence Loom solution
- uncertain arrival state
- campaign persistence failure

Routine information should remain visually quiet.

---

## 13. HUD implementation architecture

### 13.1 Web-first client

Keep the HUD web-based initially to maximize:

- Pixel support
- Windows support
- one renderer/client codebase
- local runtime integration
- future ChatGPT embedding opportunity

### 13.2 Separate client from Python server

Gradually retire the pattern of embedding an increasingly large HTML/JS application inside Python strings.

Target structure:

```text
hud/
  app/
  components/
  scene3d/
  instruments/
  planner/
  chat/
  replay/

runtime/
  contracts/
  campaign/
  clock/
  spatial/
  trajectory/
  loom/
  diagnostics/
```

Python/runtime services expose typed application state; the web client renders and interacts with it.

### 13.3 Rendering technology decision

Evaluate a WebGL-capable stack suitable for:

- true 3D trajectories
- large dynamic scale ranges
- mobile GPU constraints
- touch orbit/pan/zoom
- label/icon overlays
- animation/playback

Implementation choice should be made through a small proof-of-capability rather than a full rewrite.

---

## 14. Conversational cockpit / LLM integration

### 14.1 Goal

The LLM should operate on the same typed application state as the human, not scrape the HUD visually or rely on free-form prose state dumps.

Potential tools:

- `get_campaign_state`
- `get_campaign_time`
- `get_current_ship_state`
- `get_selected_destination`
- `compare_routes`
- `explain_route`
- `show_trajectory`
- `set_camera_target`
- `inspect_contact`
- `query_history`
- `get_world_context`

### 14.2 Surface strategy

Three possible product surfaces remain valid:

1. ChatGPT-first if interactive HUD/app embedding is sufficient on Android
2. standalone HUD with embedded LLM
3. hybrid ChatGPT + HUD using the same LOOM session

The architecture must not depend on only one option.

### 14.3 Conversation persistence

LOOM should own durable semantic conversation/session state.

A standalone HUD may use an external LLM conversation/session identifier, but LOOM must retain the campaign-linked session/event history needed for continuity.

Literal mirroring of one consumer ChatGPT thread into an external HUD should not be assumed unless a supported mechanism is explicitly verified.

---

## 15. Historical flight and temporal GIS

Once 3D playback exists, historical visualization should reuse the same spatial runtime.

### 15.1 Historical replay

Selecting a historical flight should:

- load its departure epoch into query/playback time
- reconstruct ephemeris/world state for that time
- load the retained trajectory
- play the flight
- leave active campaign time unchanged

### 15.2 Later overlays

Potential overlays:

- prior routes
- infrastructure changes
- traffic
- incidents
- discoveries
- political/economic state
- sensor observations

This creates the foundation for genuine spatial-temporal GIS rather than static “current world + history lines.”

---

## 16. Minor-body and infrastructure endpoint expansion

After core trajectory/playback UX is stable, expand endpoint coverage.

Priority includes currently deferred bodies such as Vesta and Psyche plus infrastructure destinations.

Do this through typed endpoint classes and registry data, not one-off UI aliases.

Endpoint expansion should support:

- body centers
- orbit targets
- stations/habitats
- ports
- free-space locations
- staging regions
- Loom staging volumes

---

## 17. Spatial-temporal simulation workstream

This is a later phase built on the canonical game clock and state-at-time architecture.

Potential evolving state includes:

- infrastructure construction
- population/demographic changes
- traffic/shipping
- port throughput
- economic flows
- political/institutional events
- outages
- incidents
- route discovery
- information propagation

The architectural query becomes:

```text
state(entity, epoch)
```

CIVSTATE remains contextual authority for civil/economic/infrastructure state and should not be collapsed into the navigation physics engine.

---

## 18. Runtime / DevOps / diagnostics support workstream

The runtime baseline is accepted, but the next application phase will significantly increase the number of moving parts. Diagnostics therefore becomes an active support lane without reopening the migration architecture.

### 18.1 Existing accepted diagnostic foundation

Retain and extend:

- `loom_doctor.py`
- runtime diagnostics manifest/audit
- deployment identity reporting
- runtime trace JSONL
- localhost-only no-write diagnostics endpoint
- campaign revision/state/history/shadow-SQL diagnostics
- split-root Navigator cache diagnostics
- `loom_debug_bundle.py`

### 18.2 Diagnostic schema expansion

Add structured diagnostic events for:

- campaign clock reads/advances
- campaign revision transitions
- campaign-SQL mirror/promotion checks
- route discovery
- trajectory solve IDs
- trajectory qualification results
- frame/ephemeris resolution failures
- playback start/stop/skip
- FOLLOW SHIP state
- HUD websocket/HTTP/session state if used
- Loom route validation/translation events
- LLM tool calls at metadata level where appropriate

Diagnostics should store identifiers and safe state summaries, not secrets or uncontrolled transcript dumps.

### 18.3 Correlation IDs

Introduce stable correlation identifiers across one user flight operation:

- session ID
- plan ID
- trajectory ID
- flight ID
- campaign transition ID
- diagnostic correlation ID

This should allow a debug bundle to reconstruct one failed operation end-to-end across GIS, Navigator, campaign, HUD, and runtime traces.

### 18.4 Health checks

Expand read-only health checks to cover:

- root resolution
- installed version/commit identity
- campaign authority reachability
- campaign clock readability
- campaign revision consistency
- campaign SQL authority mode (`shadow`, `dual-check`, `canonical`)
- database readability/schema version
- ephemeris/cache availability
- Navigator contract/schema version
- HUD static bundle/client version
- platform adapter identity

### 18.5 Debug bundles

Extend `loom_debug_bundle.py` to optionally include allowlisted summaries for the new architecture:

- runtime identity
- root topology
- campaign revision/epoch
- current authority mode
- latest route/trajectory identifiers
- recent safe diagnostic events
- relevant schema versions
- recent qualification results
- cache/provider status
- platform/runtime versions

Do **not** include arbitrary filesystem content, credentials, API tokens, full unrelated chats, or personal files.

### 18.6 Automatic sanitized diagnostic publishing — future enhancement

The previously deferred concept remains valid and should be retained as a later DevOps phase after the expanded runtime has been exercised.

Target triggers may include:

- explicit user “publish diagnostics” action
- post-deployment qualification failure
- fatal/unhandled runtime error
- explicit health capture
- possibly low-frequency opt-in heartbeat during development

Required safeguards:

- local spool when offline
- retry with bounded retention
- dedicated diagnostics branch/artifact location, not normal source history
- allowlist-only bundle contents
- token/credential stripping
- no gameplay dependency on successful upload
- user-visible indication when a bundle is created/published

Automatic publishing is useful support infrastructure but remains non-blocking and must never become part of campaign authority.

### 18.7 Runtime trace/session concurrency hardening

The frozen status explicitly leaves deeper concurrency hardening deferred. This should be addressed before the HUD/LLM introduces more simultaneous requests.

Focus areas:

- trace writer safety
- HTTP request correlation
- campaign write serialization
- session state synchronization
- playback read load versus campaign writes
- SQLite connection/transaction discipline

### 18.8 World database mutability follow-up

Do not enforce immutable live WORLD database byte hashes.

Later separate:

- immutable canonical seed/baseline data
- mutable derived/runtime state

This is not a blocker for the first 3D Navigator milestone but should remain in the architecture backlog.

---

## 19. Deployment and update support

### 19.1 Preserve split-root contract

Updater responsibilities remain:

- install/update APP runtime assets
- install/update approved canonical DATA artifacts
- never overwrite CAMPAIGN authority

### 19.2 Client asset deployment

When HUD becomes a separate web client bundle:

- version client assets
- pin them in release manifest
- include client/runtime compatibility version
- provide atomic deployment and rollback
- expose client version in diagnostics

### 19.3 Database migrations

Campaign SQLite promotion and future schema upgrades must use explicit migration tooling with:

- preflight validation
- backup
- migration version
- post-migration validation
- rollback/recovery path

Do not hide schema mutation inside ordinary application startup.

### 19.4 Pixel and Windows launcher parity

Both platforms should launch the same logical services and contracts with platform-specific path/runtime adapters only.

---

## 20. Qualification ladder

Every significant release should move through a defined ladder.

### Q0 — Contract/schema tests

- typed payloads
- adapters/accessors
- schema version compatibility

### Q1 — Unit tests

- clock
- transforms
- trajectory interpolation/sampling
- endpoint resolution
- campaign adapter
- diagnostic event generation

### Q2 — Physics regression

Known route calculations against accepted expected outcomes.

### Q3 — Phase-6 preservation gate

Mars → Ceres baseline semantics preserved.

### Q4 — Campaign persistence gate

JSON/current authority and SQL candidate produce equivalent semantics when campaign-SQL promotion work is active.

### Q5 — Cross-platform numerical parity

Same inputs on Pixel and Windows produce the same campaign/trajectory/spatial outputs within declared numerical tolerance.

### Q6 — Functional UX

Select → plan → compare → preview → commit → execute → playback/rebind.

### Q7 — Visual/device qualification

Physical inspection on Pixel and Windows.

### Q8 — Full end-to-end regression

Reserved for promotion/finalization before production use, consistent with existing LOOM release practice.

---

## 21. Staged implementation program

### Stage A — Architecture/contracts freeze

Deliver:

- typed campaign/spatial/trajectory/playback/Loom/session contracts
- service ownership diagram
- adapter plan over current Phase-6 payloads
- explicit schema/version rules

Gate:

- no behavior change
- current tests pass

### Stage B — Persistent campaign clock

Deliver:

- authoritative clock service
- persisted epoch
- epoch-stamped ephemeris/spatial requests
- stale-solution detection
- diagnostics

Gate:

- restart persistence
- no preview/commit mutation
- one execute advance

### Stage C — Campaign SQLite candidate architecture

Deliver:

- target schema
- persistence adapter
- mirror/dual-check mode
- diagnostic equivalence reporting
- migration/rollback tooling

Gate:

- do not promote yet unless all campaign equivalence tests pass

### Stage D — 3D spatial runtime

Deliver:

- reference-frame service
- 3D entity state
- scene graph
- render/physical scale separation
- basic camera framework

Gate:

- Pixel/Windows numerical parity

### Stage E — True 3D trajectory packets

Deliver:

- time-parameterized conventional/torch/metric representation
- adaptive samples
- segment metadata
- qualification/provenance

Gate:

- accepted Mars → Ceres physics unchanged

### Stage F — Basic interactive 3D viewer

Deliver:

- WebGL-capable scene
- solar-system/body rendering
- trajectory rendering
- orbit/pan/zoom
- destination/origin camera modes

Gate:

- usable on Pixel and Windows

### Stage G — Route comparison

Deliver:

- multiple candidate trajectories visible
- synchronized comparison cards
- selected trajectory emphasis
- route costs/timing/risk display

### Stage H — Unified GIS → Navigator planning UX

Deliver:

- map-native destination selection
- unified planning drawer
- preview/commit/execute within one experience

Gate:

- full Phase-6 authority loop preserved

### Stage I — Animated flight

Deliver:

- trajectory playback
- ephemeris motion during playback
- time controls
- skip to arrival

Gate:

- watched/accelerated/skipped arrival state identical

### Stage J — FOLLOW SHIP and camera suite

Deliver:

- FOLLOW SHIP
- system/origin/destination/free/local camera modes
- smooth camera transitions where practical

### Stage K — HUD 2.0 shell

Deliver:

- mobile-first cockpit layout
- 3D scene dominant
- NAV/SHIP/TACTICAL/MISSION/ASSURANCE/HISTORY layers
- responsive Windows layout

### Stage L — Live instrumentation

Deliver:

- range
- range rate/relative velocity
- ETA
- propulsion state
- remass
- power/thermal where authoritative
- metric/Loom state when applicable
- qualification/staleness indicators

### Stage M — Campaign SQLite promotion

Only after sustained dual-check success.

Deliver:

- canonical SQL persistence cutover
- compatibility/export path if needed
- revised diagnostics authority mode

Gate:

- explicit promotion decision
- Pixel physical acceptance
- Windows parity
- rollback verified

### Stage N — Loom relational graph and solver

Deliver:

- Loom node/edge model
- route knowledge/confidence/directionality
- endpoint admissibility
- solution qualification

### Stage O — Mixed-mode Loom flight planning

Deliver:

- conventional → Loom → conventional itinerary planning
- timing/cost/risk integration
- destination-local emergence state

### Stage P — Loom visualization

Deliver:

- departure geometry animation
- relational/topology transition visualization
- emergence/reacquisition
- no fake intervening metric path

### Stage Q — Historical replay / temporal GIS

Deliver:

- replay executed flights
- arbitrary historical query time
- no active campaign mutation

### Stage R — Minor-body/infrastructure endpoint expansion

Deliver:

- Vesta/Psyche coverage
- infrastructure/station/free-space endpoint types
- registry-driven expansion

### Stage S — Conversational HUD

Deliver:

- typed LLM tool surface
- contextual chat panel
- model can inspect/explain routes and current state
- model actions remain mediated by explicit application tools

### Stage T — ChatGPT/HUD session bridge

Deliver:

- LOOM-owned durable session state
- reconnectable HUD conversation
- ChatGPT integration where supported
- no dependency on literal consumer-thread mirroring

### Stage U — Diagnostic publishing automation

After runtime maturity.

Deliver:

- opt-in sanitized bundle generation/publishing
- offline spool
- dedicated diagnostics surface
- bounded retention and failure handling

### Stage V — Spatial-temporal world simulation

Deliver incrementally:

- state-at-time world processes
- infrastructure evolution
- traffic/economic/event layers
- knowledge propagation integration

---

## 22. Immediate milestone: Phase-7 3D Qualification

The first implementation milestone should remain deliberately narrow.

### Objective

> **Mars → Ceres Phase-7 3D Qualification**

### Required demonstration

- persistent canonical campaign game time
- Mars and Ceres resolved at that epoch
- current accepted route calculation preserved
- trajectory emitted as true XYZ + time
- interactive 3D scene
- destination/body motion according to ephemeris
- route visible in 3D space
- preview/commit/execute authority unchanged
- animated departure → arrival
- FOLLOW SHIP
- campaign ends at exactly the expected arrival epoch/revision
- Pixel pass
- Windows numerical parity pass
- debug bundle can capture the operation using correlation IDs

### Explicitly out of scope for this first milestone

- Loom travel
- LLM cockpit
- campaign SQL promotion unless required solely as a shadow/dual-check dependency
- broad minor-body expansion
- spatial-temporal civilization simulation
- automatic GitHub diagnostics publishing

The point is to make the new 3D/time foundation boringly reliable before layering on the more ambitious product features.

---

## 23. Development/release discipline

For LOOM code releases:

- run unit regression tests before sending any new Python file
- when changes are substantively functional, run unit + functional tests
- reserve full end-to-end regression for finalization immediately before a production run
- do not hard-code payload field names/mode strings across consumers
- use canonical typed/validated schemas with adapters/accessors
- preserve accepted authority boundaries unless a deliberate migration is being qualified

When a stage is physically accepted:

1. record acceptance evidence
2. update the governing status/work-plan documents
3. commit exact state
4. run exact-head CI
5. freeze or tag/branch the accepted milestone as appropriate

---

## 24. Decision log / current conclusions

As of 2026-09-06:

- runtime migration/convergence is complete and should not be reopened casually
- Phase-6 Mars → Ceres is the preservation baseline
- true 3D trajectories are mandatory
- persistent canonical game time is mandatory
- animated travel is a core feature
- FOLLOW SHIP is a core feature
- Loom travel must be first-class and relational-topology-correct
- HUD remains a major product surface and should be implemented web-first
- HUD should host the LLM if ChatGPT embedding is insufficient
- LOOM should own durable session context rather than depending on a consumer-chat transcript as game authority
- campaign SQLite is the target mutable campaign persistence layer, but promotion requires an explicit qualification gate
- runtime diagnostics/support must evolve alongside the new application layers
- automatic sanitized diagnostic publishing remains deferred until the expanded runtime has been exercised

---

## 25. Next action

Begin **Stage A — Architecture/contracts freeze**, immediately followed by **Stage B — Persistent campaign clock**.

Do not begin HUD polish, Loom animation, or broad endpoint expansion before the 3D/time foundations and preservation gates are in place.
