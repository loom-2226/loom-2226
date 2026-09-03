# LOOM 2226 — Integrated Runtime Architecture, Product Delivery Workflow, and Navigator Integration Plan

**Version:** v1.0  
**Date:** 25 August 2026  
**Status:** PROJECT DESIGN / DELIVERY BASELINE — NOT FICTION CANON  
**Replaces:** `LOOM_2226_Integrated_HUD_Navigator_Architecture_and_Work_Plan_v0.1`  
**Purpose:** Provide one working architecture and delivery-management baseline from the current HUD/runtime implementation through a fully playable LOOM product, including eventual integration of the existing Python Navigator map and solver without reimplementing its numerical authority.

---

## 0. How to use this document

This is the primary design and delivery guide for the LOOM interactive runtime.

It has four jobs:

1. define the **target product**;
2. define the **runtime architecture and authority boundaries**;
3. define the **delivery workflow, assurance model, and project-management artifacts**;
4. maintain a coherent **roadmap from the current implementation to a fully workable product**, including the existing Python Navigator.

This document is intentionally not fiction canon. It references canon, engineering sources, HUD standards, character sheets, and Navigator contracts, but it governs **software design and delivery**, not the fictional universe.

Where this document describes a current implementation as `ACTIVE`, `PASS`, `MVP ABSTRACTION`, `OPEN`, or `DEFERRED`, that status is a software/model status and must not be silently promoted into fiction canon.

> *Vendor-management practice note: separating product authority, architecture authority, source-of-truth ownership, and delivery evidence is useful far beyond LOOM. A vendor can be accountable for a deliverable without becoming the authority for the business requirement, target architecture, production data, or acceptance decision.*

---

# 1. Product vision

## 1.1 Product Goal

Deliver a deterministic, persistent hard-science-fiction campaign runtime in which:

- the **player commands intent**;
- **Python owns quantitative simulation and mutable campaign truth**;
- character and crew capabilities influence outcomes through a **replaceable game-mechanics boundary**;
- the LLM provides narration, character interaction, explanation, intent interpretation, and GM functions without silently becoming numerical authority;
- the HUD presents player-known state without inventing precision or leaking hidden truth;
- local flight occurs in genuine three-dimensional space;
- macro navigation uses the preserved Python Navigator, real ephemeris/provenance machinery, and its existing route/timeline work;
- game time, ship state, contact state, route state, replay, and narrative audit remain coherent across HUD, chat, local flight, Navigator, save/reload, and future host adapters;
- the default operating architecture has **zero incremental recurring cost**.

## 1.2 Fully workable product — practical definition

A product increment is considered **fully workable** when a player can complete the following loop without manual state copying, arbitrary LLM numerical invention, or a separate navigation authority:

1. load or resume a campaign;
2. see current game time, ship state, location, known contacts, and allowed actions;
3. interact through chat, character HUD, or rich SVG HUD;
4. scan and track contacts subject to knowledge/uncertainty rules;
5. command local maneuvers in real 3D space;
6. receive physically valid Flight Director options;
7. preview and commit a maneuver;
8. execute rotation, finite burns, coasts, counter-burns, and local gravity/free-space motion through authoritative Python physics;
9. apply relevant crew capabilities through the active mechanics adapter;
10. derive narration from the committed physics/mechanics/knowledge packet;
11. record replay and audit lineage;
12. transition into **NAV**;
13. request a macro route from the existing Python Navigator;
14. inspect candidate route/timeline/map state;
15. commit a route only if it is still bound to the current campaign revision;
16. execute macro travel with authoritative time, position/location, mass/remass, route phase, and provenance;
17. transition back into local flight at the destination;
18. resume tactical/local gameplay from the same campaign state;
19. save/reload and reproduce the consequential history;
20. use character/monospace HUD as a fallback if the rich host surface fails.

The product is not required to possess every eventual engineering refinement before it is playable. It **is** required to label abstractions honestly and fail closed where a required physical or knowledge mechanism is absent.

---

# 2. Executive architecture decision

The architecture eliminates “handoff” as a copy/merge problem.

HUD, LLM, local flight, sensor systems, Flight Director, replay, audit, and Navigator operate against one versioned campaign authority rather than exporting competing authoritative copies.

```text
                              LOOM SOURCE / CANON PACK
                         versions + hashes + model status
                                      |
                                      v
+------------------+        +----------------------------+        +----------------------+
| LLM / GM         |<------>| LOOM CAMPAIGN RUNTIME      |<------>| PYTHON NAVIGATOR     |
| intent           |        | PYTHON MUTATION AUTHORITY  |        | preserved solver     |
| characters       |        |                            |        | ephemeris / routes    |
| narration        |        | time / state / events      |        | map compiler          |
| explanation      |        | flight / sensors / views   |        | NAV_STATE             |
+--------+---------+        +-------------+--------------+        +----------+-----------+
         |                                |                                  |
         |                                v                                  |
         |                    +---------------------------+                    |
         +------------------->| VIEW / CONTEXT COMPILERS  |<------------------+
                              +-------------+-------------+
                                            |
                    +-----------------------+----------------------------+
                    |                       |                            |
                    v                       v                            v
              CHARACTER HUD          SVG / PWA HUD              FULL NAVIGATOR
              guaranteed fallback    portrait-first             reference/regression
```

**Governing rule:**

> Python is the only component permitted to commit mutable campaign state or advance authoritative game time. The LLM, renderer, browser, future MCP/Apps SDK host, and Navigator presentation may request, display, explain, validate, or reject state; they may not silently manufacture or mutate campaign truth.

---

# 3. Current implementation checkpoint

The original v0.1 design was written before the implementation sequence began. The project has now moved substantially beyond that proposal.

The current architecture has qualified the following capabilities.

| Capability | Current status |
|---|---|
| Single Python state/time authority | ACTIVE / qualified |
| Stale-state and idempotent action discipline | ACTIVE / qualified |
| Portrait HUD architecture | ACTIVE / evolving |
| Character HUD fallback | retained requirement |
| Genuine local 3D position `[x,y,z]` | ACTIVE |
| Genuine local 3D velocity `[vx,vy,vz]` | ACTIVE |
| Quaternion ship attitude | ACTIVE |
| Camera orientation independent of ship attitude | ACTIVE |
| Knowledge-bounded 3D contact rendering | ACTIVE |
| 3D triangular +X-forward / +Z-dorsal tactical contact glyph | ACTIVE placeholder symbology |
| Shared-time multi-object local propagation | ACTIVE |
| Gravity-well two-body propagation | ACTIVE |
| Free-space propagation | ACTIVE |
| Continuous finite-burn integration | ACTIVE |
| Propulsion mass flow / remass expenditure | ACTIVE |
| Proper acceleration / load vectors | ACTIVE |
| Certified propulsion control envelope | MVP ABSTRACTION |
| Certified attitude-control envelope | MVP ABSTRACTION |
| Character/crew capability overlay | ACTIVE |
| Game mechanics isolated behind replaceable adapter | ACTIVE |
| Player-known / GM-objective truth separation | ACTIVE |
| Narrative truth packet | ACTIVE |
| Narrative audit record | ACTIVE |
| Event-sourced flight replay ledger | ACTIVE |
| Flight event/state/contact topology | ACTIVE |
| Two-stage Flight Director optimizer architecture | ACTIVE; final finite-burn validator binding NEXT |
| INTERCEPT / MATCH candidate generation | qualification stage |
| Full commit-authoritative INTERCEPT / MATCH | NOT YET COMPLETE |
| Full Python Navigator integration | PLANNED / preserve existing work |
| Native ChatGPT Android rich widget dependency | NOT on critical path |

The following physics remain deliberately explicit rather than silently fabricated:

- full angular-velocity / rigid-body torque integration;
- dynamic centre of mass and inertia tensor;
- continuous attitude steering inside a burn;
- detailed thermal/structural strain/wear coupling;
- full sensor SNR/radiometry/EW performance model;
- multi-body gravity where required;
- final detailed actuator/node geometry underlying certified control envelopes.

These are **deferred engineering closures**, not permission for narration or UI to invent capability.

---

# 4. Non-negotiable architecture principles

## 4.1 Single mutable authority

At any instant, there is one authoritative campaign state at revision `N`.

No browser state, HUD state, chat memory, Navigator UI state, or LLM-generated object may become a second campaign authority.

## 4.2 One authoritative game clock

Game time advances only through validated committed events.

Typing time, wall-clock time, LLM response latency, screen rotation, application backgrounding, and reopening the HUD have no effect on game epoch.

## 4.3 QUERY → PLAN → COMMIT

Consequential subsystems use the same transaction grammar.

| Operation | Meaning | Mutation |
|---|---|---|
| QUERY | inspect current state / request estimate | none |
| PLAN | produce candidate bound to current state revision | none |
| COMMIT | validate base revision and execute | atomic mutation |
| REJECT | stale/invalid/physically impossible | zero mutation |

## 4.4 Physics before narrative

The causal order is:

```text
PLAYER INTENT
      ↓
INTERPRETATION
      ↓
PHYSICAL / KNOWLEDGE FEASIBILITY
      ↓
GAME MECHANICS where applicable
      ↓
COMMITTED EVENT
      ↓
NEW STATE
      ↓
NARRATIVE PACKET
      ↓
LLM NARRATION
```

Narration never creates an uncommitted physical result.

## 4.5 Knowledge before display

The renderer may not know more than the player view.

```text
OBJECTIVE TRUTH
      ↓
SENSOR / OBSERVATION PROCESS
      ↓
TRACK / UNCERTAINTY
      ↓
PLAYER VIEW
      ↓
HUD / NARRATIVE
```

A velocity track does not imply identity. Geometry does not imply hostility. A contact shape may not show attitude until attitude is actually resolved.

## 4.6 Renderer does not design the map

For the existing Navigator, Python owns projection, display coordinates, route primitives, symbology, provenance, and map semantics.

For the local 3D HUD, Python owns world state and knowledge. Presentation owns camera transforms and pixels.

## 4.7 No dangling nodes

All consequential runtime artifacts must possess causal lineage.

Examples:

- no state transition without an event;
- no maneuver solution without an objective, base state, and validator;
- no contact track without observations;
- no narrative without an event/narrative packet;
- no audit without the narrative/event it evaluates;
- no committed Navigator plan without its base state and route-plan identity.

This principle applies equally to delivery assurance later in this document.

---

# 5. Runtime authority model

## 5.1 Authority matrix

| Concern | Authority | May propose/display | Forbidden authority |
|---|---|---|---|
| Campaign time | Campaign Runtime Kernel | HUD/LLM/Navigator | wall clock, JS timer, prose |
| Mutable campaign state | Campaign Runtime Kernel | all clients may request | local widget state |
| Canon/world truth | active source manifest | LLM may interpret | chat memory override |
| Model status | runtime model registry | UI displays | renderer promotion |
| Local flight physics | Python simulation services | Flight Director requests | LLM/SVG physics |
| Contact objective truth | simulation/GM state | GM tooling | player HUD |
| Player contact knowledge | sensor/view compiler | HUD/LLM | objective truth leak |
| Character mechanics | active mechanics adapter | runtime consumes result | physics importing dice/skills |
| Navigation numerical authority | existing Python Navigator | HUD/LLM requests | JavaScript route solving |
| Navigator map geometry | Python map compiler | SVG renderer | renderer designing map |
| Mutation/commit | Campaign Runtime Kernel | user/button/model initiates | narrator self-commit |
| Campaign persistence | runtime persistence/ledger | clients request | browser local storage |
| Flight replay | replay ledger | viewers | becoming campaign authority |
| Narrative audit | audit ledger | assurance/reporting | retroactive state mutation |

---

# 6. Core runtime components

## 6.1 Canon Loader / Authority Gate

Responsibilities:

- identify active governing sources;
- verify file/version/hash requirements;
- expose model status;
- distinguish canon, provisional engineering, test fixture, working model, and deferred/open model;
- fail closed or diagnostic when a required governing dependency is missing or mismatched.

Runtime should not dump the entire archive into LLM context.

Instead, expose:

```text
CANON_RELEASE
MANIFEST_SHA256
ACTIVE_FILE_HASHES
MODEL_REGISTRY_VERSION
HUD_STANDARD_VERSION
NAV_BASELINE_VERSION
ENGINE_VERSION
```

and retrieve specific source content only when needed.

## 6.2 Campaign State Kernel

Owns:

- `campaign_id`;
- `state_id`;
- `revision`;
- authoritative epoch;
- ship instance state;
- local/macro location state;
- current route/execution state;
- known contacts/observations;
- crew assignments;
- consequential resources;
- event linkage;
- persistence pointer/history.

Only this kernel performs consequential commits.

## 6.3 Action Registry / Transaction Gate

Every executable action is registered.

Examples:

- `WAIT`
- `TRACK`
- `ACTIVE_SCAN`
- `ROTATE`
- `TRANSLATE`
- `BURN`
- `CUTOFF`
- `INTERCEPT`
- `MATCH`
- `NAV_QUERY`
- `NAV_PLAN`
- `NAV_COMMIT`

A request includes:

```text
action_id
idempotency_key
campaign_id
expected_state_id
expected_revision
expected_state_hash
actor / assigned crew where applicable
typed parameters
```

A repeated idempotency key returns the original result.

A stale expected revision returns the current state identity and causes zero mutation.

> *Vendor-management practice note: this is the software equivalent of insisting that a supplier's change be traceable to an approved baseline. “Latest” is not a control; explicit version/baseline identity is.*

## 6.4 Persistence

Initial runtime should continue using the existing robust RC5-style persistence semantics rather than introduce a database merely because databases sound more serious.

Required properties:

- atomic write;
- backup/recovery;
- stale-state protection;
- state/history consistency checking;
- replay/reconstruction;
- hash/provenance checks.

SQLite/Postgres is not a milestone. It becomes a backlog item only if an actual concurrency, query, scale, or operational requirement justifies migration.

---

# 7. Local spatial and flight architecture

## 7.1 Spatial state

Minimum physical local-space state:

```text
position_km              [x,y,z]
velocity_km_s            [vx,vy,vz]
attitude_quaternion      [w,x,y,z]
wet_mass_t
remass_t
frame_id
primary_body_id / gravity environment
```

Reserved future physical fields:

```text
angular_velocity_rad_s
center_of_mass_body_m
inertia_tensor_body
thermal_state
structural_strain_state
wear_state
configuration_state
```

The reserved fields remain explicitly `DEFERRED` until implemented.

## 7.2 Flight environments

The same physical integrator supports:

**FREE SPACE**

```text
gravity = 0
trajectory = thrust + initial state
```

**GRAVITY WELL / ORBIT**

```text
gravity = environment model
trajectory = gravity + thrust + initial state
```

Local two-body gravity is the current MVP environment.

Multi-body gravity is deferred until a scenario or accuracy requirement demands it.

## 7.3 Propulsion

The propulsion model owns engine performance and outputs:

```text
mode
thrust_N
mass_flow_kg_s
exhaust_velocity_km_s
thermal_interpretation
```

The finite-burn integrator consumes these values.

Current Wayfarer working torch cards:

| Mode | Working acceleration card | Exhaust velocity |
|---|---:|---:|
| ECON | 0.30 g | 3000 km/s |
| CRUISE | 1.00 g | 2000 km/s |
| EXPEDITE | 2.00 g | 1000 km/s |
| FAST | 3.00 g | 700 km/s |
| HARD | 5.00 g | 450 km/s |
| LIMIT | 7.50 g | 300 km/s |

These remain source-derived working engineering cards, not universal spacecraft constants.

## 7.4 Certified control envelopes

Detailed actuator geometry is deferred behind explicit **certified control envelopes**.

This is an MVP abstraction of actuator capability, not a replacement for eventual force/torque engineering.

Data may include:

```text
main propulsion +X body authority
translation sustainable/transient authority
pitch/yaw/roll max angular rate
pitch/yaw/roll max angular acceleration
settle time
mass scaling
inertia multiplier
damage authority multiplier
power authority multiplier
```

Ship identity chooses configuration data. Physics modules do not branch on a literal ship name.

## 7.5 Finite-burn integration

Finite burns integrate:

- position;
- velocity;
- gravity;
- thrust;
- changing mass/remass;
- derived acceleration/load state.

The Flight Director may use fast approximations to generate candidates, but **final validation uses the same authoritative physical engine that will execute the solution**.

## 7.6 Acceleration and load vectors

Maintain distinct internal vectors:

```text
gravity_accel_world
thrust_accel_world
proper_g_body
apparent_load_g_body
```

Important rule:

> Free-fall gravity changes trajectory but is not added to crew felt-g while the ship and crew share the same free fall.

Future crew-load projection should add:

```text
station orientation
head-foot component
chest-back component
lateral component
duration
repetition
recovery state
restraint/support class
```

The narrative compiler may use derived g/load state; it may not invent numerical exposure.

---

# 8. Attitude, NASA/GNC terminology, and visualization semantics

## 8.1 Internal coordinate language

Use body-frame and inertial/reference-frame language internally.

Canonical runtime concepts:

- BODY FRAME;
- INERTIAL FRAME;
- ATTITUDE;
- ANGULAR RATE;
- THRUST VECTOR;
- VELOCITY VECTOR;
- ACCELERATION VECTOR;
- PROPER ACCELERATION;
- RELATIVE POSITION;
- RELATIVE VELOCITY;
- RANGE;
- RANGE RATE / CLOSURE;
- LINE OF SIGHT;
- ATTITUDE COMMAND;
- BURN;
- COAST;
- CUTOFF.

Ship-operational terms such as fore/aft, port/starboard, dorsal/ventral may supplement the body-axis model in UI and narrative.

They do not replace `+X/+Y/+Z` semantics internally.

## 8.2 Visualization invariant

The HUD must preserve:

```text
ATTITUDE ≠ VELOCITY ≠ ACCELERATION ≠ CAMERA
```

Camera rotation is presentation state.

It never rotates the ship or universe.

## 8.3 Tactical craft glyph

Current placeholder tactical symbology uses a genuine 3D triangular pyramid:

- apex = `+X` forward;
- asymmetric dorsal vertex = `+Z`;
- orientation transforms with the contact's earned attitude;
- camera transforms the mesh into screen pixels.

The symbol is **tactical symbology**, not literal hull geometry.

## 8.4 Knowledge-bounded visual resolution

Example progression:

```text
DETECTION      → point / uncertainty region
COARSE         → uncertainty volume
FIRM           → resolved geometry / attitude unknown
ATTITUDE       → oriented 3D tactical glyph
CONFIGURATION  → generic craft representation
CLASS          → known class geometry
IDENTIFIED     → identified hull representation
```

The renderer cannot skip ahead because objective truth exists in the engine.

## 8.5 Tactical scale

Two explicit modes may coexist:

- `SYMBOL ENLARGED` — minimum readable tactical glyph;
- `TRUE SCALE` — physical scale even if the craft becomes microscopic.

The HUD must never visually imply that an enlarged glyph is the object's actual spatial size.

---

# 9. Sensors, observations, and contact knowledge

## 9.1 Knowledge layers

```text
OBJECTIVE CONTACT STATE
       ↓
SENSOR PROCESS
       ↓
OBSERVATION
       ↓
TRACK
       ↓
PLAYER-KNOWN CONTACT STATE
       ↓
HUD / FLIGHT DIRECTOR / LLM
```

## 9.2 Track quality

Track quality must be earned.

Final performance should eventually depend on:

- target signature;
- sensor hardware;
- observation/integration time;
- geometry/baseline;
- aspect;
- occlusion;
- ownship noise;
- EW/ECCM;
- operator effectiveness;
- environment.

Current sensor thresholds used for UI qualification remain provisional until engineering closure.

## 9.3 Flight Director knowledge boundary

A player-side maneuver solution uses estimated/observed target state and its uncertainty.

It may not use objective/GM target truth merely because the runtime possesses it.

This is essential for both gameplay and assurance.

---

# 10. Character and crew mechanics boundary

## 10.1 Governing rule

**Character skill changes execution quality and probability of good outcomes where competence matters. It does not change the laws of physics or create hardware capability.**

The physics layer does not import:

- dice;
- TN;
- Attribute;
- Skill;
- Boon/Bane;
- Specialty;
- XP.

## 10.2 PilotEffectPacket

The active mechanics adapter translates the current or future RPG mechanics into bounded execution inputs such as:

```text
timing_quality
control_precision
plan_efficiency
track_management
workload_tolerance
```

Replacing the game mechanics requires replacing/versioning the adapter, not rewriting the physical solver.

## 10.3 Causal competency overlay

Task context identifies relevant competencies.

Examples:

| Task | Primary | Support opportunities |
|---|---|---|
| Trajectory solution | Astrogation + Reasoning | Sensors + Reasoning |
| Torch execution | Pilot + Reflex | Composure |
| Degraded flight | Pilot + Reflex | Engineer + Reasoning; Composure |
| Track maintenance | Sensors + Reasoning | Pilot + Reflex |
| Engineering diagnosis | Engineer + Reasoning | relevant specialty |
| High-g exposure | Physique | Composure |
| Crisis coordination | Command + Presence | Composure |
| EVA repair | Zero-G/EVA + Reflex; Engineer + Reasoning | Composure |

Routine certified automation should normally be no-roll.

Skill matters most under uncertainty, degraded automation, time pressure, damage, contested sensing, incomplete information, difficult geometry, or consequential manual intervention.

> *Vendor-management practice note: a useful analogue is distinguishing system capability from operator/process maturity. Strong operations cannot make an unavailable interface exist; they can reduce error, detect exceptions faster, and use available capability more effectively.*

---

# 11. Flight Director

## 11.1 Role

The Flight Director converts operational intent into physically valid candidate maneuver plans.

The player can express intent such as:

- intercept K2;
- match velocity outside 20 km;
- preserve bow aspect;
- minimize signature;
- do not exceed a specified load;
- maintain sensor track;
- separate rapidly;
- brake;
- hold;
- dock/approach under certified constraints.

## 11.2 Two-stage optimizer

### Stage 1 — candidate generation

Fast/coarse analytical or simplified candidate generation.

Purpose:

- explore many horizons/options;
- reject obviously bad candidates cheaply;
- rank promising solutions.

Authority:

`NONE / CANDIDATE ONLY`

### Stage 2 — authoritative validation

The best candidates are run through:

- current state/revision;
- observed target state and uncertainty;
- certified ship control envelopes;
- attitude timing;
- continuous finite burns;
- changing mass;
- gravity environment;
- resource constraints;
- mechanics where consequential;
- acceptance constraints.

Only validated solutions may become commit-eligible.

## 11.3 Maneuver event grammar

A maneuver can compile to events such as:

```text
ROTATE
BURN
COAST
ROTATE
COUNTER_BURN
TRACK / REACQUIRE
CUTOFF
```

Each event has:

- duration;
- inputs;
- before-state;
- after-state;
- provenance;
- replay identity.

## 11.4 Objective set

Initial local Flight Director objectives:

- INTERCEPT;
- MATCH;
- SEPARATE;
- HOLD;
- BRAKE.

Future objectives may include:

- APPROACH;
- DOCK;
- SHADOW;
- SCREEN;
- EVA SUPPORT;
- LOW-SIGNATURE APPROACH.

New objectives are registered rather than invented in narration.

---

# 12. Narrative truth boundary

## 12.1 Flight Narrative Packet

The LLM should not inspect a raw campaign-state dump and infer what happened.

A read-only narrative packet exposes only relevant derived truth:

```text
event
ship_motion
load
propulsion
maneuver
crew_mechanics
observable_truth
knowledge_limits
provenance
```

Example use:

- factual flight narration;
- crew experience;
- technical explanation;
- “why did that happen?” questions;
- post-event summaries.

## 12.2 Narrator constraints

The packet explicitly forbids:

- state mutation;
- invented physics;
- invented mechanics;
- hidden-truth disclosure;
- time advancement beyond the committed checkpoint.

## 12.3 Technical explanation

A separate safe technical view may expose:

- vectors;
- g/load;
- propulsion mode;
- mass/remass;
- maneuver phase;
- mechanics result;
- model IDs/provenance.

This lets the LLM explain the physics without receiving unrelated GM secrets.

---

# 13. Narrative audit and self-evaluation

## 13.1 Audit chain

For selected/all consequential turns:

```text
ENGINE TRUTH
      ↓
OBSERVABLE TRUTH
      ↓
MECHANICS RESULT
      ↓
EXACT NARRATIVE PACKET
      ↓
LLM OUTPUT
      ↓
AUDIT
```

## 13.2 Audit dimensions

- physics fidelity;
- knowledge-boundary fidelity;
- mechanics fidelity;
- temporal fidelity;
- canon fidelity.

## 13.3 Storage

Audit is append-only JSONL or equivalent.

It is **not campaign state**.

It stores the exact packet supplied to the narrator and the output being evaluated.

## 13.4 Improvement loop

Aggregate failure codes can be used to improve:

- prompts;
- narrative compiler;
- state packet design;
- sensor disclosure rules;
- mechanics integration;
- canon retrieval;
- UI semantics.

> *Vendor-management practice note: this is continuous assurance. Evidence is generated as part of execution rather than assembled retrospectively for a gate. The equivalent in delivery governance is to make acceptance/control evidence an output of the delivery process itself.*

---

# 14. Flight replay and spatiotemporal topology

## 14.1 Three histories

Keep three concepts separate:

**Campaign ledger** — what became true.

**Flight replay ledger** — how the physical/operational encounter unfolded.

**Narrative audit** — what was said about that encounter and whether it was supportable.

## 14.2 Replay ledger

Record meaningful checkpoints/events, not every integration substep.

Example fields:

```text
campaign epoch
elapsed game seconds
state revision
event ID

own ship:
  position
  velocity
  attitude
  mass/remass
  propulsion state
  proper/load vector

contacts:
  player-observed track history
  privileged GM objective history separately

commands:
  exact raw command
  parsed intent
  assigned crew
  selected Flight Director solution

event:
  action type
  resulting state revision
```

## 14.3 Player vs GM replay

A player replay cannot expose GM contact truth.

A GM/forensic replay may include objective truth.

## 14.4 Event topology

Runtime relationships are explicit.

```text
STATE → COMMAND → SOLUTION → EVENT → STATE
                  ↑
OBSERVATION → TRACK

EVENT → NARRATIVE → AUDIT
```

No dangling nodes in committed history.

Replay records contain hashes so alteration/divergence can be detected.

---

# 15. HUD and player experience

## 15.1 Presentation hierarchy

The product supports multiple surfaces over the same state.

1. **Character/monospace HUD** — guaranteed fallback.
2. **Portrait SVG tactical HUD** — primary rich local-play target.
3. **Landscape expansion** — richer spatial presentation.
4. **Integrated NAV HUD** — compact macro navigation.
5. **Full existing Navigator** — expanded/reference/regression surface.
6. **Future ChatGPT Apps SDK/MCP adapter** — optional host integration, never required for core authority.

## 15.2 Android-first design

Portrait is the default qualification surface.

Requirements:

- touch targets ≥ 44 CSS px;
- semantic HTML buttons over/around SVG where appropriate;
- camera state disposable;
- reopen/reload reconstructs from authoritative state;
- no external CDN required;
- adaptive landscape without changing state semantics.

## 15.3 Contextual actions

Buttons are compiled from `allowed_actions`.

The UI does not invent available commands.

Examples:

```text
WAIT
TRACK
ACTIVE SCAN
POINT
ROTATE
BURN
CUTOFF
INTERCEPT
MATCH
NAV
PLAN
COMMIT
```

---

# 16. Python Navigator integration

## 16.1 Design decision

The existing Python Navigator is preserved.

The product does **not** reimplement ephemeris, map projection, route solving, or timeline physics in JavaScript or LLM prose.

The Navigator becomes:

- a solver/compiler subsystem;
- a source of `NAV_STATE`;
- an expanded/reference UI;
- a regression and scientific-validation surface.

## 16.2 Existing assets to preserve

- JPL/Horizons acquisition and provenance;
- synchronized Solar/local ephemeris tracks;
- moving-target route composition;
- current route semantics;
- torch/metric/terminal phase solving;
- wet-mass/remass accounting;
- deterministic flight timelines;
- Atlas/navigation separation;
- map contract/projection primitives;
- route/leg-inspector data;
- hash/version locks;
- replay/determinism evidence.

## 16.3 Map contract

Prime directive:

> **THE RENDERER DOES NOT DESIGN THE MAP.**

Python owns:

- projection;
- canvas/panel geometry;
- astronomical display coordinates;
- reference-orbit geometry;
- local-system display coordinates;
- body glyphs and line styles;
- selection symbology;
- Main Belt treatment;
- provenance/APPROX treatment;
- route primitive schema;
- label anchors;
- slider/frame semantics.

The integrated HUD can render these primitives in a new surface, but may not alter their astronomical semantics.

## 16.4 NAV_STATE

Freeze a versioned common interface before integration polish.

Recommended binding fields:

```text
campaign_id
ship_instance_id

base_state_id
base_state_revision
base_state_sha256

nav_plan_id
nav_plan_sha256

candidate / committed / executing status
current timeline sample ID
arrival-state binding
allowed nav actions

frame/provenance
map primitives
route primitives
timeline primitives
engineering summary
```

## 16.5 NAV transaction pattern

```text
STATE 1842
  |
  +-- NAV_QUERY -------------------------- no mutation
  |
  +-- NAV_PLAN N-0084 -------------------- no mutation
  |      base revision = 1842
  |
  +-- NAV_COMMIT N-0084
         |
         +-- verify revision 1842 still current
         +-- verify plan hash/model versions
         +-- commit route/execution once
         +-- create STATE 1843
```

Any consequential change after plan generation invalidates or requires revalidation of the candidate.

## 16.6 Local ↔ macro handoff

There is one campaign state, not two flight saves.

**LOCAL → NAV**

- campaign state provides authoritative epoch, frame/location, ship state, mass/remass, operational constraints;
- Navigator receives a query/plan request.

**NAV → MACRO EXECUTION**

- route/timeline becomes a committed campaign event set;
- Navigator does not maintain an independent hidden campaign clock.

**MACRO ARRIVAL → LOCAL**

- arrival state is bound to campaign epoch/location/velocity/resource state;
- local environment is instantiated from the arrival state;
- HUD resumes without manual import/export.

## 16.7 Navigator acceptance scenario

A required golden path:

```text
GANYMEDE LOCAL
     ↓
open NAV
     ↓
query CERES
     ↓
plan N-xxxx
     ↓
inspect map / timeline
     ↓
COMMIT
     ↓
macro execution
     ↓
arrival state
     ↓
CERES LOCAL
     ↓
resume tactical HUD
```

At every step:

- epoch agrees;
- state revision agrees;
- remass/mass agree;
- route status agrees;
- player-known information remains filtered;
- replay/audit lineage remains intact.

---

# 17. Fully integrated product flow

The complete game runtime should eventually behave as:

```text
PLAYER INTENT
     |
     v
LLM / UI INTERPRETATION
     |
     v
ACTION REGISTRY
     |
     +-----------------------+
     |                       |
     v                       v
LOCAL FLIGHT              NAVIGATOR
Flight Director           NAV query/plan
Sensors                    macro route solver
Finite physics             NAV_STATE/map
     |                       |
     +-----------+-----------+
                 |
                 v
        CAMPAIGN COMMIT GATE
                 |
                 v
          NEW AUTHORITATIVE STATE
                 |
       +---------+----------+
       |                    |
       v                    v
VIEW COMPILER         REPLAY / AUDIT
       |
       v
HUD / LLM NARRATIVE
```

---

# 18. Delivery operating model

## 18.1 Framework choice

Use a **lightweight scaled-Scrum delivery model**, borrowing useful concepts from Scrum, Scrum-of-Scrums, and scaled Agile/SAFe-style product hierarchy without adopting ceremonial overhead that adds no value.

This is not a claim of formal compliance with Scrum Guide, SAFe, LeSS, or Scrum@Scale.

Use the vocabulary because it improves:

- product focus;
- backlog coherence;
- sequencing;
- dependency management;
- assurance;
- architectural decision traceability;
- review discipline.

Do not manufacture roles or ceremonies merely to resemble an enterprise transformation deck.

> *Vendor-management practice note: framework compliance is not the objective. Clear accountabilities, visible dependencies, acceptance criteria, evidence, and decision rights are. A supplier that “does Agile” but cannot state the accepted outcome, risk, dependency, or definition of done is not giving you meaningful delivery control.*

---

# 19. Product hierarchy

The working hierarchy is:

```text
PRODUCT
  ↓
PROGRAM / RELEASE INCREMENT
  ↓
EPIC
  ↓
FEATURE
  ↓
PRODUCT BACKLOG ITEM / USER STORY / ENABLER
  ↓
TASK / SPIKE
```

Scrum itself formally centers Product Goal, Product Backlog, Sprint Goal, Sprint Backlog, Increment, and Definition of Done. Epic/Feature/Program Increment are used here as practical scaled-delivery constructs.

Engineering build IDs such as `P2-41` remain useful implementation sequence references.

They are **not** the same as Product Backlog identities.

Example:

```text
P2-43                     engineering build sequence
FLT-026                   product backlog item
Flight Director           feature
EPIC-FLT                  epic
Flight Operations MVP     release increment
LOOM Interactive Runtime  product
```

---

# 20. Logical delivery streams

The project operates through logical streams. These are capability domains, not necessarily separate people/vendors.

| Stream | Responsibility |
|---|---|
| RUN — Runtime & State | campaign kernel, clock, transactions, persistence, topology |
| FLT — Flight & Simulation | local physics, propulsion, GNC, Flight Director |
| SNS — Sensors & Contact Knowledge | observation, tracks, uncertainty, EW |
| MEC — Mechanics & Crew | character capabilities, mechanics adapters, load consequences |
| NAR — Narrative Runtime | narrative packets, technical explanation, LLM boundaries |
| UX — Player Experience | character HUD, SVG tactical HUD, interaction |
| NAV — Macro Navigation | Python Navigator adapter, NAV_STATE, map integration |
| ASR — Assurance & Governance | tests, audit, replay integrity, canon/version traceability |
| OPS — Packaging & Host | local runtime, save/reload, browser/PWA, optional ChatGPT adapter |

> *Vendor-management practice note: a delivery stream is not automatically a contract boundary. One supplier may span several streams; several suppliers may contribute to one stream. Keep capability ownership, contract ownership, and technical authority explicit rather than assuming they are the same thing.*

---

# 21. Scrum cadence

For a small project, use lightweight timeboxing.

## 21.1 Sprint

Default target:

- one-week sprint when calendar-based work is useful; or
- a coherent short engineering batch when work is being executed interactively.

Every Sprint has a **Sprint Goal**.

Do not treat “complete as many P2 numbers as possible” as a Sprint Goal.

Example:

> **Sprint Goal:** Produce a commit-authoritative local INTERCEPT/MATCH from observed target state and execute it through finite-burn physics, replay, and narrative audit.

## 21.2 Sprint Planning

Select only Ready backlog items needed for the Sprint Goal.

Confirm:

- acceptance criteria;
- dependencies;
- architecture decisions;
- source authority;
- assurance evidence expected.

## 21.3 Daily Scrum / execution check

For this project, this can be a very short checkpoint:

```text
Goal status?
What changed?
What is blocked?
What decision is needed?
What risk/dependency changed?
What can be safely sequenced next?
```

## 21.4 Sprint Review

Demonstrate the actual increment against acceptance criteria.

Prefer:

- running artifact;
- automated test;
- replay record;
- before/after state;
- failure behavior;

over narrative claims that work is “done.”

## 21.5 Retrospective

Ask:

- where did the LLM or UI overclaim?
- where was a requirement ambiguous?
- what created rework?
- which tests caught a real defect?
- which artifact was useless bureaucracy?
- which interface should be frozen?
- what should we stop doing?

## 21.6 Scrum of Scrums / dependency review

Use only when multiple streams have active dependency interactions.

Example:

```text
FLT needs SNS track uncertainty contract
UX needs FLT trajectory primitive contract
NAV needs RUN state binding
ASR needs evidence from all three
```

For LOOM, this is a dependency review, not a fake meeting between imaginary teams.

## 21.7 System Demo / Inspect & Adapt

At the end of each Release/Program Increment:

- run the end-to-end acceptance scenario;
- inspect architecture and assurance metrics;
- close/reclassify risks;
- review ADRs;
- re-prioritize backlog;
- update this baseline when architecture materially changes.

---

# 22. Definition of Ready

A backlog item is **Ready** when:

1. intended outcome is clear;
2. state/authority owner is known;
3. required input/output contracts are known or the item is explicitly a Spike to discover them;
4. relevant governing source/canon/model status is identified;
5. dependencies are visible;
6. testable acceptance criteria exist;
7. failure behavior is defined;
8. player/GM knowledge implications are considered;
9. unresolved design decisions are explicit rather than silently guessed;
10. estimated size is sufficiently understood for the current Sprint.

### Spike

Use a **Spike** when the goal is uncertainty reduction rather than product functionality.

A Spike must end with a defined output such as:

- decision;
- prototype;
- measurement;
- interface proposal;
- risk reduction;
- ADR recommendation;
- backlog refinement.

> *Vendor-management practice note: “we need to investigate” is not a deliverable. A useful Spike names the uncertainty being retired, the timebox, and the decision/artifact expected at the end.*

---

# 23. Definition of Done

A consequential PBI is Done only when applicable items are satisfied:

- implementation complete;
- automated qualification passes;
- acceptance criteria demonstrated;
- authority boundary preserved;
- stale/idempotency behavior tested where relevant;
- player/GM truth separation tested;
- runtime/model status updated;
- replay/provenance emitted where relevant;
- narrative packet/audit path updated where relevant;
- no dangling topology;
- HUD does not overstate implemented capability;
- source/canon/provenance impact recorded;
- open/deferred model seams remain explicit;
- documentation/backlog/ADR updated;
- residual risks recorded;
- replacement artifact packaged.

“Code exists” is not Done.

> *Vendor-management practice note: Definition of Done is a powerful antidote to the phrase “development complete.” If testing, documentation, security evidence, operational readiness, dependency closure, or acceptance evidence are required, they belong in Done rather than becoming somebody else's surprise later.*

---

# 24. Assurance as a delivery topology

Assurance is not a final gate.

Each material requirement should form a connected graph:

```text
RISK / REQUIREMENT
       ↓
ARCHITECTURE / CONTROL
       ↓
BACKLOG ITEM
       ↓
IMPLEMENTATION
       ↓
TEST
       ↓
EVIDENCE
       ↓
ACCEPTANCE
       ↓
RESIDUAL RISK
```

No dangling nodes.

Examples of assurance defects:

- requirement with no acceptance test;
- test with no requirement/control;
- control with no identified risk;
- vendor deliverable with no acceptance criterion;
- architecture decision with no constraint/rationale;
- risk with no accountable treatment;
- failed test with no disposition.

> *Vendor-management practice note: this is the same topology discipline as systems engineering. Assurance becomes far more useful when it can answer “which risk/control/requirement does this evidence support?” rather than producing a large unconnected evidence folder.*

---

# 25. Required project-management artifacts

Keep the set small and useful.

## 25.1 Product Backlog

Minimum fields:

```text
PBI ID
Epic
Feature
Title
Outcome
Status
Priority
Size
Dependencies
Acceptance Criteria
Assurance Evidence
ADR references
Risk references
Build references
```

Use stable IDs independent of engineering build sequence.

## 25.2 RAID Log

Track:

- Risks;
- Assumptions;
- Issues;
- Dependencies.

Minimum fields:

```text
ID
Type
Description
Likelihood
Impact
Exposure
Owner
Treatment
Trigger / due point
Residual exposure
Status
Related PBI / ADR / requirement
```

## 25.3 Architecture Decision Records (ADR)

Every consequential design choice should have:

```text
ADR ID
Title
Status
Context
Decision
Alternatives considered
Rationale
Consequences
Constraints
Affected contracts/components
Review trigger
```

## 25.4 Assurance Traceability Matrix

Minimum relationships:

```text
Requirement / Risk
Control / Design rule
PBI
Test / validation
Evidence artifact
Status
Residual risk / exception
```

Avoid a giant spreadsheet for its own sake. The objective is connected evidence.

## 25.5 Release Burnup

Track accepted product outcomes/features against release scope.

Prefer burnup over velocity as the primary progress view.

Story points are planning aids, not contractual units of productivity.

> *Vendor-management practice note: supplier velocity is not an outcome metric and cross-team story points are not comparable. Accepted scope, escaped defects, dependency closure, risk exposure, and forecast-to-complete are usually much more useful governance signals.*

---

# 26. Initial ADR register

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Python Campaign Runtime is sole mutable game-state/time authority. | ACCEPTED |
| ADR-002 | Preserve existing Python Navigator; integrate through contracts rather than rewrite. | ACCEPTED |
| ADR-003 | Local/browser/PWA-capable, zero-incremental-cost runtime is the baseline; native ChatGPT rich host is optional. | ACCEPTED |
| ADR-004 | Consequential actions use QUERY → PLAN → COMMIT with stale-state/idempotency controls. | ACCEPTED |
| ADR-005 | Renderer is presentation only; Navigator Python owns map semantics; local HUD owns camera/pixels only. | ACCEPTED |
| ADR-006 | Use certified propulsion/attitude control envelopes for MVP while detailed actuator geometry remains deferred. | ACCEPTED |
| ADR-007 | Use continuous finite-burn integration for authoritative flight validation/execution. | ACCEPTED |
| ADR-008 | Character mechanics are isolated behind a replaceable PilotEffect/crew-mechanics adapter. | ACCEPTED |
| ADR-009 | Contact visuals are knowledge bounded; oriented 3D symbology appears only when attitude is earned. | ACCEPTED |
| ADR-010 | Narrative receives a read-only truth packet after physics/mechanics; narrative does not originate physical results. | ACCEPTED |
| ADR-011 | Narrative audit is append-only/non-authoritative and stores exact LLM input/output. | ACCEPTED |
| ADR-012 | Flight replay is event sourced with separate player-observed and GM-objective contact histories. | ACCEPTED |
| ADR-013 | Flight/event/state/track/narrative topology rejects dangling committed nodes. | ACCEPTED |
| ADR-014 | Flight Director uses coarse candidate generation plus authoritative high-fidelity validation. | ACCEPTED |
| ADR-015 | Navigator integration freezes NAV_STATE and uses campaign-bound QUERY/PLAN/COMMIT semantics. | PROPOSED / NEXT NAV INCREMENT |

---

# 27. Initial RAID baseline

## Risks

| ID | Risk | L | I | Treatment |
|---|---|---:|---:|---|
| RSK-001 | LLM narrates unsupported physical state or intent. | M | H | Narrative Packet + post-turn audit + fail-closed knowledge boundary. |
| RSK-002 | Provisional engineering abstraction silently becomes treated as canon. | M | H | Runtime capability statuses + ADRs + explicit source/model labels. |
| RSK-003 | Navigator and campaign state diverge after integration. | M | H | One state authority; state-bound NAV plans; arrival binding; regression comparison. |
| RSK-004 | Native Android rich widget remains unreliable/unavailable. | H | M | Host-independent runtime; local browser/PWA; character HUD fallback. |
| RSK-005 | Finite-burn validation makes optimizer too slow. | M | M | Two-stage coarse candidate generation + final authoritative validation. |
| RSK-006 | Replay/audit storage grows unnecessarily. | M | L | Event-sourced checkpoints; do not retain integrator substeps by default. |
| RSK-007 | HUD presentation accumulates stale implementation labels. | M | M | Compile status from runtime capability contract. |
| RSK-008 | Sensor provisional rules create false precision. | M | H | Keep thresholds explicitly provisional; uncertainty fields; sensor-engineering backlog. |

## Assumptions

| ID | Assumption | Validation / review trigger |
|---|---|---|
| ASM-001 | Two-body local gravity is sufficient for initial tactical MVP. | Review for Lagrange/multi-body/high-precision scenarios. |
| ASM-002 | Certified control envelopes are conservative enough for MVP gameplay. | Replace/tune when detailed ship engineering closes. |
| ASM-003 | Existing RC5-style persistence remains adequate for single-user local runtime. | Review if concurrency/query/scale requirements appear. |
| ASM-004 | Existing Navigator can expose/freeze a stable NAV_STATE without numerical rewrite. | Validate during NAV integration Spike. |

## Issues

| ID | Issue | Status |
|---|---|---|
| ISS-001 | Full rigid-body angular dynamics not implemented. | DEFERRED / visible |
| ISS-002 | Thermal/strain/wear numerical coupling not implemented. | OPEN MODEL |
| ISS-003 | Final sensor SNR/radiometry/EW model not implemented. | OPEN MODEL |
| ISS-004 | Commit-authoritative INTERCEPT/MATCH finite-burn validator binding incomplete. | ACTIVE NEXT |

## Dependencies

| ID | Dependency | Critical path? |
|---|---|---|
| DEP-001 | Existing Python Navigator assets/contracts/runtime. | Yes for macro navigation; no for local Flight MVP. |
| DEP-002 | Canon/runtime source manifest and hashes. | Yes |
| DEP-003 | Character/mechanics source sheets. | Yes for crew mechanics; no for raw physics. |
| DEP-004 | Native ChatGPT rich-app support. | No |

---

# 28. Product backlog — epic baseline

## EPIC-RUN — Authoritative Runtime & State

**Goal:** one deterministic campaign authority.

**Status:** substantially complete for MVP.

Features:

- state/revision;
- time authority;
- typed actions;
- stale/idempotent commit;
- persistence;
- event topology;
- replay identity;
- runtime capability status.

## EPIC-FLT — Local Flight & Flight Director

**Goal:** physically valid local 3D flight and operational maneuver planning.

**Status:** active.

Completed/enabling features:

- 3D position/velocity;
- quaternion attitude;
- gravity/free-space;
- certified control envelopes;
- finite burns;
- remass;
- proper-g/load vectors;
- coarse optimizer;
- objective grammar.

Next:

- FLT-026 authoritative finite-burn candidate validator;
- FLT-027 INTERCEPT compiler;
- FLT-028 MATCH compiler;
- FLT-029 event-plan execution;
- FLT-030 commit through Campaign Kernel;
- FLT-031 trajectory primitives for HUD;
- FLT-032 playback/reacquisition verification.

## EPIC-SNS — Sensors & Contact Knowledge

**Goal:** uncertainty-bearing observable contact state that drives gameplay.

**Status:** architecture active / detailed engineering incomplete.

Backlog:

- SNS-010 persistent integration history;
- SNS-011 uncertainty covariance representation;
- SNS-012 occultation/occlusion;
- SNS-013 signature model;
- SNS-014 passive sensor SNR;
- SNS-015 active sensing/ranging;
- SNS-016 EW/ECCM;
- SNS-017 operator effectiveness adapter;
- SNS-018 class/configuration identification.

## EPIC-MEC — Character/Crew Mechanics Integration

**Goal:** character competence matters without violating physics.

**Status:** mechanics boundary active.

Backlog:

- MEC-010 task-context resolver;
- MEC-011 assistance/support rules;
- MEC-012 high-g biological consequence adapter;
- MEC-013 synthetic acceleration profiles;
- MEC-014 fatigue/recovery;
- MEC-015 degraded-flight competence;
- MEC-016 final mechanics adapter if Core Mechanics changes.

## EPIC-NAR — Narrative Runtime

**Goal:** LLM narrates committed truth and player-known information.

**Status:** architecture active.

Backlog:

- NAR-010 live packet integration with Campaign Kernel;
- NAR-011 technical explanation mode;
- NAR-012 dialogue/crew narrative composition;
- NAR-013 correction protocol after failed audit;
- NAR-014 narrative density/verbosity modes.

## EPIC-ASR — Assurance, Audit & Replay

**Goal:** continuous evidence that runtime, narrative and sources remain coherent.

**Status:** architecture active.

Backlog:

- ASR-010 persistent audit directory/rotation;
- ASR-011 automated post-turn narrative audit;
- ASR-012 regression metric dashboard;
- ASR-013 replay visual scrubber;
- ASR-014 requirement/test/evidence traceability export;
- ASR-015 release acceptance report.

## EPIC-UX — HUD & Player Experience

**Goal:** useful, readable portrait-first cockpit over player-known truth.

**Status:** active prototype.

Backlog:

- UX-020 real packet binding replacing remaining fixtures;
- UX-021 trajectory visualization;
- UX-022 uncertainty-volume/tube visualization;
- UX-023 vector toggles;
- UX-024 contact selection/detail;
- UX-025 portrait density pass;
- UX-026 landscape expansion;
- UX-027 replay scrubber;
- UX-028 character HUD parity.

## EPIC-NAV — Navigator Integration

**Goal:** use existing Python Navigator as macro flight/navigation subsystem and integrated map.

**Status:** planned.

Backlog:

- NAV-001 integration Spike / current Navigator inventory;
- NAV-002 freeze NAV_STATE integration version;
- NAV-003 campaign-state → Navigator query adapter;
- NAV-004 Navigator candidate-plan binding;
- NAV-005 NAV_PLAN hash/base-state semantics;
- NAV-006 compact integrated Solar map renderer;
- NAV-007 local-system Navigator renderer;
- NAV-008 leg inspector integration;
- NAV-009 macro COMMIT adapter;
- NAV-010 execution/timeline → Campaign Kernel;
- NAV-011 arrival-state binding;
- NAV-012 Navigator/full-HUD parity tests;
- NAV-013 standalone Navigator regression harness;
- NAV-014 replay/provenance join;
- NAV-015 local ↔ macro transition acceptance.

## EPIC-OPS — Product Packaging & Host

**Goal:** make the runtime usable without fragile infrastructure.

Backlog:

- OPS-010 one-command local launch;
- OPS-011 campaign create/load/save UX;
- OPS-012 self-contained PWA/browser package;
- OPS-013 Android local-browser qualification;
- OPS-014 export/import/backup;
- OPS-015 diagnostics page;
- OPS-016 optional MCP/Apps SDK adapter;
- OPS-017 native-host qualification when platform permits.

---

# 29. Release / Program Increment roadmap

## PI-0 — Architecture & Authority Foundation

**Status:** COMPLETE / maintenance mode.

Outcome:

- single authority;
- state/time discipline;
- HUD architecture;
- sensor/player truth boundary;
- core contracts;
- assurance philosophy.

## PI-1 — Local Flight Operations MVP

**Status:** CURRENT.

Goal:

> Player can observe a contact, request a physically valid maneuver, preview it, commit it, execute it through finite-burn physics, see the 3D result, receive crew/mechanics consequences, and obtain audited narration/replay.

Required exit criteria:

1. observed-track INTERCEPT works end-to-end;
2. MATCH works end-to-end;
3. invalid solution returns `NO VALID SOLUTION`;
4. finite-burn validation is authoritative;
5. game time advances once;
6. mass/remass changes once;
7. gravity/free-space both pass;
8. trajectory and ship attitude are visible in 3D;
9. contact knowledge remains filtered;
10. crew mechanics are applied only through adapter;
11. replay and narrative audit join by event;
12. save/reload preserves outcome.

## PI-2 — Tactical Encounter MVP

Goal:

> Support a complete local encounter rather than only a maneuver demonstration.

Scope:

- multi-contact tracking;
- approach/separate/hold/brake;
- local orbit states;
- docking/berthing framework;
- comms/hail event registration;
- limited EW/jamming if sensor engineering supports it;
- encounter replay;
- improved Atlas/environment context.

Exit requires a repeatable local encounter scenario with no LLM-invented physical transitions.

## PI-3 — Python Navigator Integration

Goal:

> Transition seamlessly between local flight and macro Solar-System navigation using the preserved Python Navigator.

Scope:

- freeze NAV_STATE;
- campaign adapter;
- map integration;
- route plan binding;
- Navigator QUERY/PLAN/COMMIT;
- macro execution;
- arrival-state handoff;
- standalone regression surface.

Exit requires the full Ganymede → Ceres golden path.

## PI-4 — Integrated Campaign Product

Goal:

> Play ordinary LOOM sessions through chat/HUD across local operations, macro navigation, character mechanics, and narrative without manual state repair.

Scope:

- campaign lifecycle;
- crew tasking;
- narrative integration;
- tactical/macro transitions;
- replay/audit viewer;
- source/canon diagnostic;
- resilient save/reload;
- failure/recovery.

## PI-5 — Product Hardening / Host Integration

Goal:

> Package the local product cleanly and attach richer hosts without moving authority into them.

Scope:

- browser/PWA polishing;
- Android qualification;
- diagnostics;
- performance;
- backup/export;
- optional MCP/Apps SDK adapter;
- native ChatGPT widget qualification when support is reliable.

## PI-6 — Post-MVP Engineering Fidelity

Potential increments:

- rigid-body angular dynamics;
- dynamic CoM/inertia;
- continuous attitude steering through finite burns;
- multi-body gravity;
- detailed sensor engineering;
- EW;
- thermal/strain/wear integration;
- deeper crew acceleration physiology/synthetic limits;
- advanced damage/degraded-control modeling.

These do not block the initial integrated product unless acceptance testing demonstrates that an approximation is inadequate for the required gameplay.

---

# 30. Current Sprint

## Sprint Goal

> Bind the Flight Director optimizer to the real finite-burn/gravity validator and produce commit-ready INTERCEPT and MATCH event plans from player-observed target state.

## Sprint Backlog

| PBI | Outcome |
|---|---|
| FLT-026 | Candidate validator uses actual finite-burn engine. |
| FLT-027 | INTERCEPT compiles a physically validated event plan. |
| FLT-028 | MATCH compiles a physically validated arrival-state event plan. |
| FLT-029 | Validated event plan executes through shared campaign state. |
| FLT-030 | Commit transaction updates time/resources/state exactly once. |
| ASR-016 | Flight topology/replay/audit evidence emitted for committed maneuver. |
| UX-021 | Renderer receives validated trajectory primitives. |

## Sprint acceptance

A contact with observed uncertain state must produce:

- 0–N coarse candidates;
- 0–N validated candidates;
- either a selected commit-ready plan or `NO VALID SOLUTION`;
- an actual state transition when committed;
- no use of hidden GM target truth;
- replay/audit lineage;
- reproducible result after reload/replay.

---

# 31. Work-package entry and exit gates

Use work-package gates for large features/epics even while the internal implementation remains agile.

## Example — NAV integration work package

### Entry criteria

- local campaign state contract stable;
- NAV_STATE inventory complete;
- Python Navigator regression baseline passes;
- base-state/hash binding agreed;
- current map contract identified;
- no unresolved question over authority ownership.

### Exit criteria

- integrated HUD and standalone Navigator agree on shared fields;
- QUERY and PLAN do not mutate campaign time/state;
- stale COMMIT rejects with zero mutation;
- committed route executes once;
- time/location/mass/remass remain coherent;
- arrival binds correctly into local runtime;
- map renderer reproduces Python primitives;
- provenance survives integration;
- standalone Navigator remains reproducible;
- replay links route plan and execution;
- LLM cannot bypass Python route/destination validation.

> *Vendor-management practice note: Agile iterations and contractual/work-package entry/exit criteria are not mutually exclusive. The former governs how work is developed; the latter can govern when a body of work is accepted or allowed to progress.*

---

# 32. Change control

Not every backlog refinement is a formal change.

Classify change:

### Backlog refinement

Within approved Product Goal/release scope.

Examples:

- split a PBI;
- adjust UI implementation;
- improve tests;
- tune provisional values within agreed model.

### Architecture decision

Changes technical approach or contract.

Requires ADR update.

### Baseline scope change

Changes Product Goal, release outcome, major dependency, cost model, or accepted authority boundary.

Requires explicit impact assessment against:

- scope;
- dependencies;
- schedule/sequence;
- risks;
- evidence/assurance;
- architecture;
- existing accepted work.

> *Vendor-management practice note: the useful question is not “is this Agile or a change request?” It is “does this alter the agreed baseline/outcome or is it normal refinement inside it?” Confusing the two either freezes delivery or creates uncontrolled scope.*

---

# 33. Prioritization

Primary priority order:

1. authority/integrity defects;
2. blockers to an end-to-end playable increment;
3. physics/knowledge defects that would create false gameplay;
4. dependency-unlocking enablers;
5. player usability;
6. fidelity enhancements;
7. polish.

For larger backlog decisions, a lightweight WSJF-style score may be used:

```text
(Value + Time Criticality + Risk Reduction / Dependency Unlock)
---------------------------------------------------------------
                         Job Size
```

Do not pretend the result is mathematically objective.

---

# 34. Metrics

Use metrics to inform decisions, not reward theatre.

Recommended:

### Delivery

- accepted PBIs/features;
- release burnup;
- lead time;
- blocked time;
- dependency age;
- escaped defects;
- reopen/rework rate.

### Assurance

- automated acceptance pass rate;
- replay hash integrity;
- stale/idempotency failures;
- narrative audit PASS/WARN/FAIL;
- physics fidelity failures;
- knowledge-boundary leaks;
- temporal fidelity failures;
- unsupported canon claims.

### Product/runtime

- time to load/resume campaign;
- action round-trip;
- optimizer candidate/validation time;
- HUD render/rebuild time;
- replay size;
- crash/recovery success.

Avoid:

- lines of code;
- number of P2 tasks;
- model tokens consumed;
- raw story-point velocity as a performance target.

---

# 35. Golden end-to-end acceptance scenario

This is the primary system-level acceptance test for the integrated product.

## Phase A — Resume

1. Load campaign.
2. Verify state ID/revision/hash.
3. Verify game epoch.
4. Verify Wayfarer ship state.
5. Verify current local environment.

## Phase B — Local contact

1. Passive detection of K2.
2. Track K2.
3. Knowledge state progresses without hidden-truth leak.
4. HUD contact symbology follows earned resolution.
5. Flight Director receives only observed target state.

## Phase C — Maneuver

1. Player requests `INTERCEPT K2`.
2. Coarse candidates generated.
3. Finite-burn validator accepts/rejects candidates.
4. Crew competence surfaced.
5. Player previews selected plan.
6. Player commits.
7. Rotate/burn/coast/counter-burn executes.
8. Gravity/free-space model is correct for environment.
9. remass/mass/time update exactly once.
10. HUD shows actual trajectory/attitude/velocity/load state.
11. replay records command/event/state.
12. narrative packet generated.
13. narration occurs.
14. audit evaluates narration.

## Phase D — Macro navigation

1. Player selects NAV.
2. Campaign state is passed to Navigator adapter.
3. Ceres queried.
4. Navigator produces plan bound to current state.
5. Integrated map renders Python-owned primitives.
6. Player inspects timeline/route.
7. Player commits.
8. stale/retry protections tested.
9. macro execution updates campaign state.
10. Navigator and HUD agree on execution state.

## Phase E — Arrival

1. Navigator arrival state binds into campaign state.
2. Local Ceres environment instantiates.
3. local HUD resumes.
4. time/location/mass/remass match macro result.
5. character/narrative context resumes.
6. save/reload reproduces arrival.
7. standalone Navigator replay/regression agrees.

## Phase F — Recovery

Test:

- UI reload;
- stale button;
- duplicated COMMIT;
- interrupted save;
- audit failure;
- missing source/hash;
- host widget disappearance.

None may create duplicate or guessed campaign state.

---

# 36. Quality gates

## Gate A — State authority

PASS when:

- one mutable state authority;
- one clock;
- one mutation gate;
- stale rejection;
- idempotent commit;
- recovery;
- player-view filtering.

## Gate B — Local Flight

PASS when:

- 3D position/velocity/attitude authoritative;
- gravity/free-space;
- finite burns;
- mass/remass;
- control envelopes;
- load vectors;
- validated local maneuvers;
- local replay/audit.

## Gate C — Tactical Play

PASS when:

- contacts/uncertainty;
- Flight Director objectives;
- crew integration;
- HUD action loop;
- complete encounter;
- no unregistered narrative physics.

## Gate D — Navigator Integration

PASS when:

- NAV_STATE frozen;
- campaign/Navigator adapters;
- QUERY/PLAN/COMMIT;
- map primitives preserved;
- macro execution;
- arrival binding;
- full Navigator regression.

## Gate E — Integrated Product

PASS when the golden end-to-end scenario completes from campaign resume through local flight, macro navigation, arrival, save/reload, replay, and audit.

## Gate F — Host/Operational Hardening

PASS when the product is easy to launch, recover, diagnose, back up, and use on target Android/browser surfaces without moving authority into the host.

---

# 37. Architecture runway

Maintain enough forward architecture to prevent upcoming work from becoming blocked, but do not implement speculative enterprise infrastructure.

Current runway items:

- stable Campaign State contract;
- stable event topology;
- stable narrative packet;
- stable replay ledger;
- stable Flight Director validator boundary;
- NAV_STATE integration contract;
- trajectory primitive contract;
- source/model-status registry;
- local packaging.

Potential future runway:

- angular-state contract;
- CoM/inertia state;
- multi-body environment interface;
- sensor covariance;
- thermal/strain/wear contract;
- networked/multi-client concurrency only if required.

---

# 38. Explicit non-goals

The following are not required for the first fully workable product:

- paid cloud hosting;
- Postgres merely for architectural appearance;
- server-side OpenAI API narration;
- native ChatGPT Android widget as sole UI;
- WebGL universe;
- full N-body Solar-System simulation for local tactical play;
- final detailed actuator geometry;
- finished biological acceleration model;
- exhaustive sensor electromagnetic engineering;
- multiplayer;
- a formal SAFe implementation;
- story-point velocity targets.

---

# 39. Immediate workflow from this baseline

For each new piece of work:

```text
1. Identify desired player/product outcome.
2. Place it in Epic / Feature / PBI.
3. Check Definition of Ready.
4. If uncertainty blocks Ready → run a Spike.
5. Record material architecture choice as ADR.
6. Identify risks/dependencies.
7. Define acceptance criteria and evidence.
8. Implement the smallest complete increment.
9. Run automated qualification.
10. Run end-to-end/system check where applicable.
11. Update runtime capability status.
12. Emit replay/audit evidence where applicable.
13. Review against Definition of Done.
14. Accept / reject / rework.
15. Update backlog, RAID, ADR, assurance matrix.
16. Sequence next Ready items supporting the Sprint Goal.
```

This becomes the default LOOM engineering workflow.

---

# 40. Suggested project-source artifacts

Maintain these alongside the implementation:

```text
LOOM_2226_Integrated_Runtime_Architecture_and_Delivery_Workflow_v1.0.md
LOOM_2226_Product_Backlog.md
LOOM_2226_RAID_Log.md
LOOM_2226_ADR_Register.md
LOOM_2226_Assurance_Traceability.md
LOOM_2226_Release_Acceptance.md
```

For the moment, this document contains the baseline content for all six. Split them into living files only when maintenance becomes easier than keeping the baseline together.

---

# Appendix A — PBI template

```text
ID:
Epic:
Feature:
Title:

Outcome:

User / operational value:

Authority owner:

Inputs:
Outputs:

Dependencies:

Acceptance criteria:
1.
2.
3.

Failure behavior:

Assurance evidence:

ADR refs:
RAID refs:
Source/canon refs:

Size:
Priority:
Status:

Engineering build refs:
```

---

# Appendix B — ADR template

```text
ADR-XXX — Title

Status:
Date:

Context:

Decision:

Alternatives:
A.
B.
C.

Rationale:

Consequences:

Affected contracts/components:

Risks:

Review trigger:
```

---

# Appendix C — RAID template

```text
ID:
Type: RISK | ASSUMPTION | ISSUE | DEPENDENCY

Description:

Likelihood:
Impact:
Exposure:

Owner:

Treatment / action:

Trigger / due point:

Residual exposure:

Related PBI:
Related ADR:
Related requirement:

Status:
```

---

# Appendix D — Assurance traceability template

| Requirement/Risk | Control/Design Rule | PBI | Test | Evidence | Status | Residual risk |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

---

# Appendix E — Sprint review template

```text
SPRINT GOAL

Planned increment:

Accepted:
Rejected:
Carried:

Demo evidence:

Automated tests:

Architecture decisions:

Risks changed:

Dependencies changed:

Audit/replay findings:

What should change next Sprint?
```

---

# Appendix F — Current source basis

This design is based on the active LOOM project materials and implementation work, including:

- `LOOM_2226_Canon_Baseline_Manifest_v2.4`
- `LOOM_2226_CANON_I_World_History_Frontier_v2.4`
- `LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4`
- `LOOM_2226_CANON_III_Authority_Continuity_GM_Model_v2.4`
- `LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2`
- `LOOM_2226_Core_Mechanics_v0.5`
- `LOOM_2226_HUD_Design_Review_and_Final_Standard_v0.3`
- `LOOM_2226_Test_Flights_Master_Record_v1.0`
- current Sol/Walter and Mara Venn character sheets
- `LOOM_Navigator_Workflow_Baseline_v1.0`
- `LOOM_Navigator_Map_Contract_v1.0.py`
- existing Navigator MVP / RC5 / execution-plan / timeline acceptance artifacts
- P1/P2 implementation qualification packages through the current Flight Director/topology work.

The existing Navigator map contract remains especially important:

> **THE RENDERER DOES NOT DESIGN THE MAP.**

That rule should survive intact through the final integrated product.

---

# Appendix G — Delivery-management learning notes

*Useful distinction: Product ownership answers “what outcome and why?” Architecture answers “what constraints and structure?” Engineering answers “how is it implemented?” Assurance answers “what evidence shows the requirement/control is satisfied?” Vendor management answers “who is accountable for which deliverable, dependency, risk, and acceptance obligation?” These overlap, but collapsing them into one role or artifact creates confusion.*

*Useful question for a vendor status meeting: “What is the current increment expected to make demonstrably true that is not true today?” It often produces a clearer answer than asking for percent complete.*

*Useful dependency question: “What is blocked, by whom, and what decision/date would unblock it?” A dependency without an owner or trigger is functionally just a future surprise.*

*Useful assurance question: “Show me the evidence path from requirement/risk to acceptance.” If the answer is a folder of documents with no traceability, the assurance system probably has dangling nodes.*

*Useful architecture question: “Is this a real constraint, an assumption, a design decision, or merely the current implementation?” Those four things should not be treated as synonyms.*

*Useful change-control question: “Does this change the agreed outcome/baseline, or is it normal refinement required to deliver that outcome?” That distinction helps prevent both scope creep and bureaucratic paralysis.*

---

**END — LOOM 2226 Integrated Runtime Architecture, Product Delivery Workflow, and Navigator Integration Plan v1.0**
