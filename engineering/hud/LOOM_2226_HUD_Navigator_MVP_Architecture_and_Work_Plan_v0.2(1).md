# LOOM 2226
# HUD + Navigator MVP Architecture and Work Plan

**Version:** v0.2  
**Date:** 24 August 2026  
**Status:** IMPLEMENTATION GUIDE / NOT CANON  
**Scope:** MVP architecture for LLM-mediated gameplay  
**Part 1:** HUD MVP + authoritative runtime + handoff to existing Python Navigator and back  
**Part 2:** Fully integrate the existing Navigator map into the HUD/runtime architecture

---

## 0. Purpose

This document is the implementation guide for the next LOOM gameplay software work.

It supersedes the earlier v0.1 design proposal for MVP planning purposes while preserving its useful authority, persistence, anti-drift, and Navigator-reuse principles. It also incorporates the valuable findings from the independent adversarial review, especially:

- narrative time must not become a second clock;
- the LLM may describe intent before commit, but physical consequence only after an authoritative action result;
- player-known information must be separated from objective/GM truth;
- a committed navigation plan is authoritative execution state, not merely disposable derived display state;
- route execution must remain interruptible rather than treating COMMIT as teleport-to-arrival;
- stale actions and concurrent HUD/LLM actions must fail closed through revision binding;
- the portrait HUD should be mocked before freezing the final HUD payload;
- semantic HTML buttons are preferred over SVG-native controls for mobile reliability;
- the MVP does not require SQLite, WebSockets, SSE, paid cloud services, or a navigation rewrite.

This is a **guide**, not setting canon. Canon/model authority remains governed by the LOOM canon manifest and governing source files.

---

# 1. MVP outcome

The MVP should allow a player to move naturally between LLM gameplay, a functional HUD, and the existing Python Navigator without manually copying or reconciling state.

Target player loop:

```text
ordinary LLM play
        |
        v
current HUD
        |
        +---- [SCAN / SELECT / HOLD / other action]
        |
        +---- [NAV]
                 |
                 v
          existing Python Navigator
          QUERY / PLAN
                 |
                 v
          candidate NAV result
                 |
          [DETAIL] [RECALC]
                 |
             [COMMIT]
                 |
                 v
       authoritative Python commit
       time / ship / route state
                 |
                 v
            new HUD state
                 |
                 v
        LLM narrates result
```

There is no authoritative copy/merge handoff between systems.

**HUD, LLM, Navigator, and future subsystems all transact against one versioned LOOM campaign state.**

---

# 2. Governing architectural rules

## 2.1 One mutable authority

Python is the only component permitted to:

- commit consequential campaign state;
- advance authoritative simulation time;
- change authoritative ship position or navigation phase;
- change velocity or other implemented flight state;
- change mass, remass, thermal state, cargo, or implemented system state;
- establish committed navigation execution state;
- publish newly revealed sensor information;
- write the authoritative event/history record.

The LLM, HUD, browser, SVG, and standalone Navigator renderer are clients/views of that authority.

## 2.2 Intent -> Validate -> Commit -> Narrate

This is the primary MVP action lifecycle.

```text
PLAYER
  |
  | natural language or HUD control
  v
ACTION INTENT
  |
  v
PYTHON VALIDATION / RESOLUTION
  |
  +---- REJECTED ----------> no mutation
  |
  v
COMMITTED ACTION RESULT
  |
  v
AUTHORITATIVE NEW STATE
  |
  +----> HUD redraw
  |
  +----> player-known context packet
              |
              v
          LLM narration
```

### Narrative rule

**Before commit**, the LLM may narrate:

- player/crew intention;
- discussion;
- planning;
- already-established perception;
- non-consequential conversational material.

**After commit**, the LLM may narrate:

- physical outcome;
- elapsed game time;
- changed location/velocity;
- changed ship condition/resources;
- newly revealed sensor information;
- consequences produced by the engine.

The LLM must not establish a physical outcome merely because it sounds narratively reasonable.

## 2.3 No generic LLM clock authority

The LLM does not directly own `game_time += delta_t`.

If the player says:

> I spend three hours repairing the Loom array.

the LLM submits an intent such as:

```text
ACTION_INTENT
actor       MARA
action      REPAIR
target      LOOM_ARRAY
requested_duration  10800 s
base_revision       1842
```

Python validates and resolves it.

Only Python returns authoritative elapsed time:

```text
ACTION_RESULT
status              COMMITTED
elapsed_game_seconds 10800
result              PARTIAL_REPAIR
new_revision        1843
new_epoch           ...
```

The LLM then narrates the committed result.

## 2.4 No wall-clock coupling

Real elapsed time does not advance campaign time.

The following must never silently advance the game clock:

- waiting for an LLM answer;
- leaving ChatGPT open;
- closing/reopening the browser;
- phone sleep;
- rotating portrait/landscape;
- network delay;
- application restart;
- time spent inspecting Navigator;
- time spent discussing a candidate plan.

## 2.5 Player-known state is not objective truth

The normal gameplay LLM and HUD should receive a **player-filtered view**, not unrestricted simulation truth, wherever practical.

```text
AUTHORITATIVE / GM TRUTH
          |
          +----> Python rules / hidden resolution
          |
          v
     VIEW COMPILER
          |
          v
    PLAYER-KNOWN STATE
          |
       +--+--+
       |     |
       v     v
      HUD   LLM
```

Example:

Objective truth may contain a hostile ship with exact position and identity.

Player-known state may contain only:

```text
BRG 286 +/-8 deg
MRK unresolved
RNG unresolved
TRK DETECTION
```

The ordinary narrative LLM does not need the hidden exact position to narrate the uncertain detection.

This preserves the existing HUD principle that **a point glyph is earned by sufficient positional track quality** and prevents accidental GM truth leakage.

---

# 3. Requirements baseline

## 3.1 Product requirements

| ID | Requirement | Priority |
|---|---|---|
| R-01 | Lightweight HUD usable during ordinary LLM gameplay. | MUST |
| R-02 | Real HTML/SVG interface; not AI-generated pictures of a HUD. | MUST |
| R-03 | Portrait-first Android phone design. | MUST |
| R-04 | Landscape/wide mode may expose more information without changing semantics. | SHOULD |
| R-05 | Major controls are touch-friendly semantic HTML buttons. | MUST |
| R-06 | HUD controls issue typed action requests rather than editing state locally. | MUST |
| R-07 | Authoritative game time survives chat/HUD/Navigator/restart transitions. | MUST |
| R-08 | Ship status, location, route state, mass/remass, thermal state, and implemented consequential state survive the same transitions. | MUST |
| R-09 | Low-friction HUD -> Navigator -> HUD flow with no manual copy/paste. | MUST |
| R-10 | Preserve existing Python Navigator calculations and semantics. | MUST |
| R-11 | Existing standalone Navigator remains a reference/regression surface during MVP development. | MUST |
| R-12 | Character/monospace HUD remains a fallback and parity surface. | MUST |
| R-13 | Unknown/provisional/test-fixture information remains explicitly unknown/provisional/test-fixture. | MUST |
| R-14 | Target eventual ChatGPT/Apps SDK embedding, but do not depend on native Android support for MVP success. | MUST |
| R-15 | Incremental operating cost target is A$0. | MUST |
| R-16 | No paid hosting, paid database, or separate OpenAI API requirement for MVP. | MUST |
| R-17 | No unnecessary infrastructure such as microservices, queues, Kubernetes, or distributed state. | MUST |
| R-18 | Existing RC5 persistence/recovery/replay behavior should be reused where adequate. | MUST |
| R-19 | Runtime knows governing canon/model/HUD/Navigator versions and hashes. | MUST |
| R-20 | Important state transitions are auditable/replayable. | MUST |

## 3.2 HUD instrument requirements

The graphical HUD is a new presentation layer over the existing HUD instrument family:

```text
NAV / SYSTEM
SENSOR / WIDE
TACTICAL / TRACK
TACTICAL / COMPACT
TACTICAL / TRIAGE
```

The existing tactical standard remains conceptually authoritative:

```text
MAIN + TOP + RANGE + CONTACTS
```

SIDE remains conditional/on request.

The graphical HUD may improve spatial presentation, but it must preserve:

- true 3-D interpretation;
- attitude versus velocity distinction;
- radial closing/opening/matched semantics;
- track-quality uncertainty;
- hazard versus hostility distinction;
- provenance honesty;
- player-known versus objective truth separation.

---

# 4. State model

## 4.1 Authoritative campaign state

Minimum proposed envelope:

```text
LOOM_RUNTIME_STATE_v0.2

schema_version
engine_version

campaign_id
ship_instance_id

state_id
revision
state_sha256

epoch_utc
campaign_display_epoch

operational_state
current_activity

location
  location_token
  reference_frame
  position        # where physically defined
  velocity        # where physically defined

ship
  wet_mass
  remass
  cargo           # implemented fields only
  thermal
  power           # when implemented
  systems         # implemented fields only

navigation
  active_plan_id
  execution_status
  current_phase
  current_timeline_sample
  navigation_semantics

sensors
  authoritative hidden state references
  player-known track state references

last_committed_event

canon_runtime_identity
navigator_baseline_identity
```

Fields unsupported by the current engine remain absent or explicitly OPEN. They are not invented for visual completeness.

## 4.2 State classes

The MVP must distinguish five classes.

### A. Authoritative persisted state

Persists as game truth.

Examples:

- epoch;
- ship resources;
- committed location/flight state;
- active committed navigation plan;
- current execution phase;
- consequential damage/thermal state;
- state revision;
- last committed event;
- canon/runtime identity.

### B. Derived state

Recomputed from authoritative state.

Examples:

- friendly location labels;
- allowed actions;
- HUD geometry;
- current display summaries;
- many NAV_STATE rendering primitives;
- calculated display metrics.

Derived state is not an independent authority.

### C. Candidate state

Non-authoritative proposed future state.

Example:

```text
NAV_PLAN N-0084
status       CANDIDATE
base_rev     1842
```

Candidates may be cached or serialized for debugging, but they do not become campaign truth until committed.

### D. Presentation-only state

Never game truth.

Examples:

- selected UI tab;
- portrait/landscape layout;
- local animation frame;
- hover/focus state;
- panel expansion;
- CSS theme;
- browser-local countdown animation.

### E. Player-known state

A filtered product compiled from authoritative truth and observation rules.

It is authoritative as **what the player currently knows**, but it is not the complete objective simulation state.

---

# 5. Transaction model

## 5.1 Action request

```text
LOOM_ACTION_REQUEST_v0.2

campaign_id
expected_state_id
expected_revision
expected_state_sha256

action_type
arguments

idempotency_key
source
  HUD | LLM | NAVIGATOR | TEST

user_commit
```

No client wall-clock timestamp is required for authority.

Network delay does not determine simulation truth. Revision binding determines whether an action is still valid.

## 5.2 Result

Rejected:

```text
RESULT
status              REJECTED
reason
current_state_id
current_revision
no_mutation         true
```

Committed:

```text
RESULT
status              COMMITTED

state_before
state_after

elapsed_game_seconds
events
warnings

new_player_view
new_hud_state
```

## 5.3 Concurrency rule

All mutating requests pass through one commit gate.

Example:

```text
HUD COMMIT arrives against REV 1842
        |
        v
1842 -> 1843 SUCCESS

LLM action arrives against REV 1842
        |
        v
CURRENT REV = 1843
REJECT STALE
NO MUTATION
```

This is sufficient for the MVP single-player concurrency model.

## 5.4 Idempotency

A retry or double tap of the same action must not execute twice.

The runtime stores/reuses the result associated with a recent committed idempotency key.

## 5.5 Crash behavior

A consequential action must produce:

```text
complete new state + complete history/event record
```

or:

```text
no authoritative mutation
```

Reuse the existing RC5 atomic save/recovery semantics rather than introducing a new database solely for fashion.

---

# 6. Game-time model

## 6.1 Single clock authority

Only the Campaign State Kernel advances authoritative simulation time.

## 6.2 Interruptible execution

A navigation COMMIT does **not** imply immediate arrival.

It creates authoritative execution state.

```text
NAV PLAN
   |
 [COMMIT]
   |
   v
ACTIVE EXECUTION
   |
   +-- departure/setup
   |
   +-- torch phase
   |
   +-- metric acquisition
   |
   +-- metric transit
   |
   +-- interruption / sensor event / player decision
   |
   +-- collapse
   |
   +-- terminal phase
   |
   v
ARRIVAL
```

The runtime advances from one meaningful event/decision point to the next.

This permits gameplay during transit.

## 6.3 Example: Ganymede -> Ceres

Starting:

```text
REV      1842
EPOCH    T0
LOC      GANYMEDE
```

Player requests a fast route.

`NAV_QUERY` and `NAV_PLAN` do not mutate.

Navigator returns:

```text
PLAN N-0084
BASE REV 1842
STATUS   CANDIDATE
```

Player commits.

Python verifies REV 1842 and creates:

```text
REV      1843
PLAN     N-0084
STATUS   EXECUTING
PHASE    DEPARTURE
```

The runtime advances through the execution timeline.

At T+11 minutes a sensor condition becomes relevant.

Python commits the elapsed interval/event and publishes newly player-known sensor state.

The LLM narrates the contact only after receiving that committed result.

Returning to NAV reads the same current campaign epoch and execution state. No Navigator clock reconciliation occurs.

---

# 7. Canon and anti-drift

## 7.1 Runtime authority pack

The MVP should validate the current minimal game runtime rather than broadly searching the archive by default.

Current governing pack includes:

```text
LOOM_2226_Canon_Baseline_Manifest_v2.4
LOOM_2226_CANON_I_World_History_Frontier_v2.4
LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4
LOOM_2226_CANON_III_Authority_Continuity_GM_Model_v2.4
LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2
LOOM_2226_Core_Mechanics_v0.5
```

Relevant HUD, character, speech, and runtime companions are activated as needed.

Runtime identity should expose at least:

```text
CANON_RELEASE
CANON_MANIFEST_SHA256
ACTIVE_FILE_HASHES
MODEL_REGISTRY_VERSION
HUD_STANDARD_VERSION
NAV_BASELINE_VERSION
ENGINE_VERSION
```

Required hash mismatch:

```text
FAIL CLOSED
```

or:

```text
DIAGNOSTIC / NON-AUTHORITATIVE MODE
```

Never silently substitute another version.

## 7.2 LLM canon access

Do not dump the full canon corpus into every LLM turn.

The normal LLM context packet should contain:

- current state identity;
- authoritative epoch;
- player-known location/status;
- selected ship fields;
- operational phase;
- allowed actions;
- warnings/open states;
- current HUD/NAV summary;
- relevant canon/model identities.

Specific canon/rules text should be retrieved only when needed.

The LLM does not promote OPEN/PROVISIONAL/TEST FIXTURE material into settled canon.

---

# 8. Presentation architecture

```text
                    LOOM CANON / MODEL AUTHORITY
                              |
                              v
                   CAMPAIGN STATE KERNEL
                      PYTHON AUTHORITY
                              |
              +---------------+---------------+
              |                               |
              v                               v
       SIMULATION SERVICES             NAVIGATOR PYTHON
              |                        existing solver
              +---------------+---------------+
                              |
                              v
                         VIEW COMPILER
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
             HUD_STATE              NAV_STATE
                  |                       |
        +---------+---------+             |
        |                   |             |
        v                   v             v
 CHARACTER HUD          SVG HUD      FULL NAVIGATOR
 fallback/parity        normal play  reference/regression
```

Future Apps SDK/MCP embedding is another presentation/client adapter. It is not the simulation architecture.

---

# 9. HUD MVP design

## 9.1 Static mock before payload freeze

Do not design the final `HUD_STATE` abstractly first.

Sequence:

```text
state/action contracts
        |
        v
static portrait HUD mock
representative hard-coded state
        |
        v
identify actual display primitives
        |
        v
freeze HUD_STATE
        |
        v
build deterministic View Compiler
```

This incorporates the external review finding without allowing UI aesthetics to dictate simulation authority.

## 9.2 MVP portrait layout

The MVP should prove one dense but usable portrait cockpit.

Suggested normal state:

```text
+-----------------------------+
| TACTICAL / TRACK            |
| EPOCH              REV      |
+-----------------------------+
|                             |
|       MAIN SVG PLOT         |
|                             |
+-----------------------------+
| SELECTED CONTACT / STATUS   |
| RNG / RR / TRK / CPA ...    |
+-----------------------------+
| OWN                         |
| MASS / REM / THERM / PHASE  |
+-----------------------------+
| [SCAN] [NAV] [HOLD] [MORE]  |
+-----------------------------+
```

The exact visual styling is not frozen by this document.

## 9.3 Controls

Prefer semantic HTML:

```html
<button>SCAN</button>
<button>NAV</button>
<button>HOLD</button>
<button>COMMIT</button>
```

over SVG `<g>` controls.

SVG remains appropriate for:

- plots;
- contact glyphs;
- route lines;
- orbit/map geometry;
- attitude markers;
- range rings;
- instrument graphics.

Minimum touch target: approximately 44 CSS px.

## 9.4 No authoritative JavaScript math

JavaScript may:

- draw supplied coordinates;
- select a contact;
- change panels;
- animate a non-authoritative visual;
- send an action request;
- render the returned state.

JavaScript may not authoritatively:

- advance campaign time;
- calculate ephemeris;
- consume remass;
- resolve thermal state;
- improve sensor track quality;
- execute route physics;
- decide whether an action succeeded.

## 9.5 Character HUD parity

The character HUD remains a guaranteed fallback and validation surface.

At a sampled state:

```text
authoritative state
        |
    +---+---+
    |       |
    v       v
 text HUD  SVG HUD
```

Shared values must agree.

---

# 10. PART 1 — HUD MVP + Navigator handoff and return

## 10.1 Part 1 goal

Produce a playable authoritative HUD/runtime and prove a low-friction round trip into the **existing Navigator** and back without yet replacing the full Navigator map.

Part 1 deliberately does **not** fully embed/rebuild the Navigator map.

It proves the seam first.

## 10.2 Part 1 target flow

```text
LLM / HUD
   |
 [NAV]
   |
   v
current authoritative campaign state
   |
   v
Navigator adapter / existing Python
   |
   v
existing Navigator presentation
   |
QUERY / PLAN
   |
   v
candidate plan bound to campaign REV
   |
 [COMMIT]
   |
   v
Campaign State Kernel
   |
validate / commit / advance as appropriate
   |
   v
new authoritative state
   |
   v
HUD + LLM
```

The player should not manually type:

- current date;
- ship mass;
- origin;
- velocity;
- remass;
- route result;
- arrival time.

Those fields move through structured state.

## 10.3 Part 1 Navigator contract

The Campaign Runtime supplies Navigator with the authoritative inputs it needs, including:

```text
campaign_id
ship_instance_id
base_state_id
base_state_revision
epoch_utc
origin/location state
ship mass/remass inputs
implemented flight state
destination/query
mode/preferences
canon/model identity
```

Navigator returns candidate results and display/state packages without owning a separate persistent campaign clock.

## 10.4 Navigator time ownership

The Campaign Kernel is the sole master of campaign `epoch_utc`.

Navigator may internally calculate epochs and deterministic timeline samples as part of a plan, but it must not maintain a competing persistent "current game time."

Its calculations are bound to the injected campaign epoch and state revision.

## 10.5 Part 1 deliverables

### P1-0 — freeze contracts

Deliver:

- `LOOM_RUNTIME_STATE_v0.2`
- `LOOM_ACTION_REQUEST_v0.2`
- `LOOM_ACTION_RESULT_v0.2`
- player-view contract
- initial Navigator handoff contract

Exit:

- only one mutable state authority is identifiable;
- only one authoritative clock exists;
- consequence narration cannot occur before commit by design.

### P1-1 — static portrait HUD

Build:

- hard-coded representative tactical state;
- MAIN tactical SVG;
- selected-contact panel;
- ownship strip;
- touch buttons;
- portrait responsive shell.

No live engine connection required.

Exit:

- readable on target phone width;
- controls are touch-safe;
- no horizontal scrolling;
- unknown sensor state can be represented honestly.

### P1-2 — freeze HUD_STATE and build View Compiler

Build:

- exact `HUD_STATE` payload required by the static mock;
- deterministic player-view filtering;
- character HUD renderer from the same player-known state;
- SVG renderer from the same payload.

Exit:

- character/SVG parity;
- no objective truth leak;
- renderer cannot improve track quality.

### P1-3 — wrap existing RC5 runtime authority

Reuse:

- atomic save behavior;
- primary/backup recovery;
- stale-state checks;
- hash-chained compressed history;
- divergence checks;
- replay/handoff semantics.

Expose:

```text
get_current_state()
get_player_view()
get_allowed_actions()
submit_action()
```

Exit:

- restart restores authoritative state;
- stale action mutates nothing;
- duplicate action executes once;
- failed commit leaves time/state unchanged.

### P1-4 — narrative action boundary

Implement/test:

```text
INTENT -> VALIDATE -> COMMIT -> NARRATE
```

Fixtures:

- "wait ten minutes";
- "scan for one minute";
- "spend three hours repairing";
- invalid action;
- stale LLM action;
- simultaneous HUD/LLM action.

Exit:

- no prose-only time advancement;
- no consequence narration required before `ACTION_RESULT`;
- one commit gate handles HUD and LLM requests.

### P1-5 — Navigator round trip

Connect existing Navigator without changing map semantics.

Prove:

```text
HUD
 -> NAV
 -> current campaign state
 -> existing Python Navigator
 -> QUERY / PLAN
 -> candidate
 -> COMMIT
 -> campaign kernel
 -> new state
 -> HUD / LLM
```

Exit:

- no manual state entry;
- candidate bound to base revision;
- stale candidate rejected;
- committed plan survives restart;
- return to HUD shows correct epoch/ship/route state.

### P1-6 — local Android/PWA qualification

Target A$0:

- local Python;
- local browser/PWA;
- no paid service;
- no external CDN requirement.

Test:

- portrait;
- rotate/reopen;
- browser process death;
- stale old control;
- double tap;
- fresh session reload.

Optional:

- test web ChatGPT Apps SDK/MCP if account/platform access permits.

Native Android ChatGPT embedding is **not** a Part 1 completion dependency.

## 10.6 Part 1 completion definition

Part 1 is complete when a player can:

1. load a persistent LOOM campaign;
2. see a functional portrait SVG HUD;
3. issue a consequential HUD action;
4. have Python advance time/state exactly once;
5. continue ordinary LLM play from the committed result;
6. enter the existing Navigator without manually re-entering state;
7. generate/inspect a route;
8. commit it through the authoritative campaign runtime;
9. return to the HUD/LLM with correct time, route, location, and ship state;
10. restart the client/runtime and recover the same authoritative campaign.

At this point LOOM is already meaningfully playable.

---

# 11. PART 2 — fully integrate the Navigator map

## 11.1 Part 2 goal

Replace the standalone Navigator as the routine player-facing navigation surface while preserving:

- its Python calculations;
- its deterministic timelines;
- its map contract;
- its ephemeris/provenance;
- its route semantics;
- its existing full interface as a reference/regression tool.

Part 2 is a presentation/integration project, **not a navigation rewrite**.

## 11.2 Existing assets to preserve

Current Navigator work already provides:

- JPL/Horizons acquisition and provenance;
- synchronized Solar/local ephemeris tracks;
- moving-target route-node composition;
- declared NAV model semantics;
- torch/metric/terminal phase solving;
- wet-mass/remass accounting;
- deterministic flight timelines;
- map contract/projection primitives;
- Atlas/navigation separation;
- route/leg inspector data;
- hash/validation locks;
- replay/determinism evidence;
- `NAV_STATE_v0.1`, already identified as a HUD-ready candidate.

The N6 acceptance package records 24 flight plans and 4,488 deterministic timeline samples and explicitly names a common Navigator/HUD interface as the next phase.

## 11.3 Freeze NAV_STATE_v0.2

Part 2 begins by freezing the common contract.

Recommended campaign binding additions:

```text
campaign_id
ship_instance_id

base_state_id
base_state_revision
base_state_sha256

nav_plan_id
nav_plan_sha256

status
  CANDIDATE
  COMMITTED
  EXECUTING
  COMPLETE
  ABORTED

current_timeline_sample_id
execution_phase

arrival_state_binding
allowed_nav_actions
```

The contract must distinguish:

- candidate plan;
- committed execution plan;
- current derived display state.

## 11.4 NAV_STATE ownership rules

Campaign Kernel owns:

- authoritative campaign epoch;
- current committed execution identity;
- consequential ship resources;
- campaign revision;
- authoritative current phase/event state.

Navigator owns/calculates:

- route solution;
- deterministic flight timeline;
- ephemeris-derived map state;
- projection/map primitives;
- route geometry;
- declared navigation-model outputs.

Renderer owns:

- display only.

No JS interpolation becomes authoritative navigation state.

## 11.5 Integrated portrait NAV mode

The normal HUD should gain a compact navigation instrument.

Example:

```text
+-----------------------------+
| NAV / FLIGHT PLAN           |
| GAN -> CER                  |
+-----------------------------+
|                             |
|      SOLAR NAV SVG          |
|                             |
+-----------------------------+
| PLAN N-0084                 |
| ETA       61h 36m           |
| REMASS    39.4 t            |
| PHASES    T/M/T             |
| STATUS    CANDIDATE         |
+-----------------------------+
| [DETAIL] [RECALC] [COMMIT]  |
+-----------------------------+
```

## 11.6 Expanded Navigator mode

Landscape/wide or explicit `DETAIL` may expose:

```text
SOLAR MAP
LOCAL SYSTEM MAP
FLIGHT TIMELINE
ROUTE / LEG INSPECTOR
ATLAS / PROVENANCE
SHIP / PHASE STATUS
```

This may reuse or adapt the current full Navigator renderer.

The compact and expanded views consume the same Python-supplied state.

## 11.7 Part 2 deliverables

### P2-0 — NAV_STATE freeze

Inventory current N6 outputs and freeze v0.2.

Exit:

- no duplicate campaign clock;
- candidate/committed/executing semantics explicit;
- no solver semantic rewrite required.

### P2-1 — Navigator service adapter

Wrap existing Python calls behind a stable runtime interface.

Example:

```text
nav_query()
nav_plan()
nav_get_state()
nav_commit_request()
nav_recalculate()
```

`nav_commit_request()` still commits through the Campaign Kernel rather than directly mutating campaign files.

### P2-2 — compact integrated NAV HUD

Build:

- portrait map;
- plan summary;
- phase/status;
- semantic HTML controls;
- candidate selection/inspection.

Exit:

- same plan values as standalone Navigator;
- no renderer-authored geometry.

### P2-3 — expanded map integration

Reuse/adapt:

- Solar map;
- local-system map;
- timeline;
- route inspector;
- Atlas/provenance.

Exit:

- portrait and landscape use same NAV_STATE;
- no map calculation migrated into JS.

### P2-4 — execution integration

Drive map/HUD from live committed campaign execution.

Prove:

- route begins at commit;
- execution can stop at meaningful decision/event points;
- sensor events can interrupt transit;
- returning to NAV uses current campaign epoch;
- metric ordinary-position null semantics remain preserved where applicable;
- collapse/terminal transition matches current Navigator semantics.

### P2-5 — regression/parity

Compare at sampled states:

```text
authoritative state
character HUD
integrated SVG HUD
integrated NAV
standalone Navigator
```

Shared authoritative values must agree.

Retain standalone Navigator as regression oracle until the integrated surface has demonstrated parity over the qualifying missions.

## 11.8 Part 2 completion definition

Part 2 is complete when routine gameplay no longer requires leaving the integrated LOOM cockpit for navigation, while the existing Python Navigator remains the underlying solver and the standalone Navigator remains reproducible as a reference/test surface.

---

# 12. Failure handling

| Failure | Required behavior |
|---|---|
| LLM narrates proposed action | No physical consequence until engine commit. |
| LLM attempts stale mutation | Reject; no state/time change. |
| HUD double tap | Same idempotency result; execute once. |
| HUD and LLM mutate simultaneously | First valid revision wins; second rejects stale. |
| Old chat contains COMMIT button | Expected revision mismatch rejects it. |
| Browser/widget dies | Rebuild from authoritative state; local JS is disposable. |
| Real time passes | No campaign-time change. |
| NAV candidate becomes stale | Reject commit; recalculate. |
| Navigator restarted | Inject current campaign epoch/state; no independent persistent clock. |
| Canon/hash mismatch | Fail closed or diagnostic non-authoritative mode. |
| Objective truth not player-known | Do not include in normal LLM/HUD view. |
| Renderer lacks data | Show unknown/open; do not invent. |
| Torn save/history | Recover demonstrably valid state or stop. |
| Network request delayed | Revision validation determines validity, not client wall-clock timestamp. |

---

# 13. Testing strategy

## 13.1 Core invariants

Automated tests should enforce:

1. revision increases only on committed mutation;
2. epoch never decreases;
3. QUERY does not mutate;
4. PLAN does not mutate;
5. failed/stale action leaves state hash unchanged;
6. idempotent retry cannot advance twice;
7. HUD/LLM race produces at most one valid mutation from a base revision;
8. renderer cannot advance time;
9. renderer cannot alter mass/remass;
10. renderer cannot improve sensor knowledge;
11. player view contains no hidden GM fields;
12. committed NAV plan survives restart;
13. NAV candidate cannot commit against a changed base revision;
14. current campaign epoch is the epoch supplied to Navigator;
15. no second persistent Navigator clock exists.

## 13.2 Narrative-time fixtures

Explicitly test:

```text
"I wait ten minutes."
"I spend three hours repairing the Loom array."
"I look at the map for a while."
"We talk about the route for twenty minutes."
```

Expected:

- declared physical waiting/repair becomes an action intent and only advances on commit;
- map inspection does not advance time;
- conversational discussion does not automatically advance time unless the player actually declares an in-world time-consuming action and the engine commits it.

## 13.3 GM truth-leak fixtures

Provide objective contacts with incomplete player observations.

Assert:

- HUD displays only permitted uncertainty;
- LLM context packet excludes hidden identity/range/intent;
- renderer does not draw unresolved positions;
- newly resolved information appears only after an authoritative observation result.

## 13.4 Golden Navigator tests

Use existing Navigator payloads, test flights, timeline outputs, and map-contract results as golden references.

The integrated NAV renderer must preserve supplied:

- coordinates;
- epochs;
- route geometry;
- timeline semantics;
- metric relational semantics;
- arrival residual behavior;
- provenance.

## 13.5 Recovery tests

Retain/re-run RC5-class cases:

- corrupt primary / valid backup;
- history ahead of state;
- torn write;
- duplicate record;
- semantic tamper;
- stale state;
- replay/reconstruction.

## 13.6 Mobile tests

At minimum:

- portrait target width;
- landscape rotation;
- no horizontal overflow;
- 44px-class touch targets;
- double tap;
- background/foreground;
- browser reload;
- PWA restart;
- stale control after reload.

Native ChatGPT Android widget behavior is separately qualified when platform support is available.

---

# 14. Zero-cost implementation target

MVP stack:

```text
Python
existing Navigator Python
existing RC5 persistence/history
HTML
CSS
JavaScript
SVG
local HTTP server
Android browser / optional PWA
Git / project files
```

Target incremental operating cost:

```text
A$0
```

Not required for MVP:

- paid hosting;
- paid database;
- AWS/Azure;
- separate OpenAI API calls;
- Business-tier ChatGPT solely for development;
- microservices;
- WebSockets;
- SSE;
- Kubernetes.

Future ChatGPT Apps SDK/MCP integration should be an adapter over the same runtime contracts.

---

# 15. Suggested code organization

Conceptual only; final names may differ.

```text
LOOM_RUNTIME/

  runtime/
    state.py
    actions.py
    commit.py
    view.py
    canon_gate.py

  persistence/
    rc5_store.py
    history.py
    recovery.py

  navigation/
    adapter.py
    [existing Navigator modules preserved]

  hud/
    index.html
    hud.css
    hud.js
    tactical_svg.js
    nav_svg.js

  contracts/
    runtime_state_v0.2.json
    action_request_v0.2.json
    action_result_v0.2.json
    hud_state_v0.1.json
    nav_state_v0.2.json

  tests/
    test_time.py
    test_transactions.py
    test_player_view.py
    test_nav_roundtrip.py
    test_recovery.py
    test_hud_parity.py
```

Do not split this into separate services for the MVP.

---

# 16. Work sequence

## PART 1

```text
P1-0  Freeze state/action/player-view contracts
  |
P1-1  Static portrait HUD mock
  |
P1-2  Freeze HUD_STATE + View Compiler
  |
P1-3  Wrap RC5 authoritative runtime
  |
P1-4  Implement Intent -> Commit -> Narrate boundary
  |
P1-5  Existing Navigator round trip
  |
P1-6  Android browser/PWA qualification
```

**Part 1 exit:** playable persistent HUD + authoritative time/state + low-friction existing-Navigator handoff and return.

## PART 2

```text
P2-0  Freeze NAV_STATE_v0.2
  |
P2-1  Navigator service adapter
  |
P2-2  Compact portrait NAV HUD
  |
P2-3  Expanded map/timeline integration
  |
P2-4  Live execution + interrupt integration
  |
P2-5  Regression/parity qualification
```

**Part 2 exit:** Navigator is native to the LOOM cockpit; standalone Navigator becomes primarily a reference/regression surface.

---

# 17. Relative effort

Use complete Navigator development to date as:

```text
NAVIGATOR = 10 units
```

Current estimate:

| Work | Relative effort |
|---|---:|
| Part 1 contracts + minimal runtime | 2–3 |
| Part 1 functional/playable HUD | 1–2 additional |
| Part 1 Navigator handoff/return | 1–2 additional |
| **Part 1 total** | **4–6** |
| Part 2 NAV_STATE/adaptor integration | 1–2 |
| Part 2 compact + expanded NAV rendering | 1–2 |
| Part 2 execution/regression hardening | 1–2 |
| **Part 2 additional** | **3–5** |

These are intentionally conservative guide values, not schedules.

The largest technical risk is **state/action discipline at the LLM boundary**, not SVG rendering.

The largest external dependency is **native ChatGPT Android embedded-widget reliability**, which is intentionally outside the MVP critical path.

---

# 18. MVP non-goals

Do not allow the MVP to expand into:

- complete ship subsystem simulation;
- full tactical combat engine;
- autonomous continuously running universe;
- multiplayer;
- cloud synchronization;
- sophisticated NPC background simulation;
- production SaaS security architecture;
- replacing all existing persistence;
- rewriting Navigator;
- rebuilding every HUD instrument before basic gameplay works;
- solving native ChatGPT Android limitations ourselves.

These can be revisited after actual gameplay demonstrates need.

---

# 19. Implementation gates

## Gate A — authority

Before serious UI work:

- one authoritative campaign state;
- one authoritative clock;
- one mutation gate;
- typed actions;
- stale rejection;
- idempotency;
- player-view separation.

## Gate B — playable HUD

Before Navigator integration:

- portrait HUD works;
- state survives restart;
- actions advance exactly once;
- text/SVG parity passes;
- narrative consequence follows committed result.

## Gate C — Navigator round trip

Before replacing the map:

- live campaign state enters existing Navigator automatically;
- candidate plan returns automatically;
- commit passes through Campaign Kernel;
- HUD/LLM resumes from correct state.

## Gate D — integrated Navigator

Before retiring standalone Navigator from routine play:

- integrated NAV matches golden Navigator outputs;
- live execution semantics match;
- current qualifying missions pass;
- standalone Navigator remains reproducible.

---

# 20. Final design position

The MVP is not an SVG game attached to an LLM.

It is:

> **a deterministic LOOM campaign runtime with an LLM narrator/interpreter, an SVG cockpit, and the existing Python Navigator as a solver subsystem.**

The LLM provides language intelligence.

Python provides simulation authority.

The HUD provides operational interaction.

Navigator provides navigation mathematics and map state.

Canon files provide governing world/model authority.

The player should experience these as one continuous game, but the software must keep their responsibilities sharply separated.

The central invariant is:

```text
INTENT
  -> VALIDATE
  -> COMMIT
  -> AUTHORITATIVE STATE
  -> PLAYER VIEW
  -> HUD + NARRATION
```

If that invariant survives every action, restart, navigation transition, and client change, LOOM can move between character HUD, SVG HUD, standalone Navigator, future ChatGPT widgets, and other presentation surfaces without losing game time, ship state, location, or canon integrity.

---

## Source basis for this guide

This implementation guide is grounded in the current LOOM project sources, particularly:

- `LOOM_2226_Integrated_HUD_Navigator_Architecture_and_Work_Plan_v0.1`
- `LOOM_2226_HUD_Design_Review_and_Final_Standard_v0.3`
- current LOOM v2.4 canon baseline/manifest and authority model
- existing RC5 Navigator workflow/persistence work
- `LOOM_Navigator_N6_Flight_Timeline_Acceptance_v1.0`
- current `NAV_STATE_v0.1` HUD-ready candidate and Navigator map-contract architecture

It also incorporates useful findings from the 24 August 2026 independent adversarial review supplied in chat. Those review findings are treated here as design input, not canon authority.
