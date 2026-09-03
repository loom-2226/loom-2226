# LOOM 2226 — Phase-6 HUD / Trajectory Convergence Work Plan v1.0

**Date:** 2026-09-04  
**Branch:** `feature/gis-navigator-convergence`  
**Governing references:**
- `LOOM_2226_GIS_Navigator_Convergence_Architecture_and_Work_Plan_v1.0.md`
- `LOOM_2226_GIS_Navigator_Convergence_Status_and_Next_Steps_2026-09-03.md`

**Status:** Implementation work plan. Phase 7 remains blocked until this plan closes physical Phase-6 acceptance.

---

## 1. Executive decision

Phase 6 will finish as one converged GIS/HUD product, not as separate Android and Windows products.

The target interaction model is:

> **Shared map + mutually exclusive NAV / ATLAS modes + one contextual drawer + conditional route auto-fit + explicit FIT ROUTE / FOLLOW SHIP controls + visually dominant authoritative sampled trajectory + persistent historical routes + authoritative ship playback.**

Pixel and Windows must use the same application state model, same route contract, same DOM/controller architecture, same navigation semantics, and same planning behavior. Viewport size may alter placement, density, and drawer orientation only.

No platform-specific fork of product behavior is permitted in this phase.

---

## 2. Current physical findings

The physical Pixel run has proved the authoritative operational chain through real execution:

`GIS -> route discovery -> commit -> execute -> campaign-state mutation -> GIS refresh`

A Jupiter System -> Ceres execution completed successfully and the campaign advanced to Ceres / revision 5.

However physical Phase-6 acceptance remains open because:

1. the authoritative route is not operationally visible in the current camera/view despite route-overlay payloads being present;
2. route playback and ship visualization are not yet usable as the primary navigation experience;
3. Atlas and flight-planning surfaces still compete for map area rather than operating through one coherent HUD controller;
4. minor-body route-token resolution has been corrected in code but still requires a deliberate physical qualification using an actual minor body such as Davida;
5. Windows and Pixel must be qualified against the same interaction architecture before Phase 6 is frozen.

---

## 3. Non-negotiable invariants

1. GIS owns presentation and interaction only; it performs no flight physics.
2. Navigator remains authoritative for planning, solved trajectory, phase semantics, execution, arrival state, and ephemeris interpretation.
3. Campaign persistence has one state authority.
4. No fake trajectory geometry may be invented in GIS.
5. Metric displacement that lacks ordinary-space occupancy remains explicitly relational and visually distinct.
6. Missing / inapplicable engineering values render as `—`, never fabricated zeroes.
7. Pixel and Windows share one behavior/controller implementation; responsive layout is not a product fork.
8. User camera agency is preserved. Automatic framing may occur only under explicit, deterministic rules and must be reversible.
9. Closing/hiding a HUD surface must remain distinct from cancelling planning or mutating campaign state.
10. Phase 7 does not start until the same-head regression stack is green and physical Phase-6 acceptance is closed.

---

## 4. Target HUD state model

Create one shared HUD controller/state model consumed by Atlas, planning, route overlay, and camera behavior.

Minimum state:

```text
hud_mode
    NAV
    ATLAS

drawer_state
    CLOSED
    COLLAPSED
    EXPANDED

selected_entity
planning_state
active_route_id
playback_route_id

camera_intent
    USER
    FIT_ROUTE
    FOLLOW_SHIP
```

### Required behavior

- NAV and ATLAS are mutually exclusive modes.
- Selected-body state survives mode changes.
- NAV selection never implicitly opens Atlas.
- ATLAS selection never implicitly starts route discovery.
- `PLAN FLIGHT HERE` transfers the selected body into NAV as a proposed destination.
- Drawer state is independent of planning/campaign state.
- Closing a drawer never cancels a route or committed plan.
- Manual pan/zoom while following a ship exits `FOLLOW_SHIP` cleanly.

---

## 5. Shared responsive presentation

There is one UI implementation with responsive presentation rules.

### Compact viewport

Typical Pixel behavior:

- map remains the dominant surface;
- NAV / ATLAS mode switch remains persistently reachable;
- one contextual drawer occupies the bottom region;
- CLOSED = only a small mode/restore affordance;
- COLLAPSED = compact route/body summary strip;
- EXPANDED = internally scrollable working surface;
- only the active mode owns drawer content.

### Wide viewport

Typical Windows behavior:

- same controller and same states;
- drawer may present as a wider side dock or larger bottom panel through responsive CSS/layout rules;
- NAV and ATLAS remain the same modes and state transitions;
- no desktop-only alternate planning implementation;
- no Android-only alternate planning implementation.

A later phase may permit optional simultaneous desktop panes, but not until the common mode/controller architecture is frozen and qualified.

---

## 6. Work sequence

### Work Package 6A — Freeze and characterize current route truth

Before UI changes:

1. preserve the current green branch head and qualification evidence;
2. inspect `LOOM_GIS_NAVIGATION_OVERLAY_V1` for the most recently executed/previewed route;
3. prove the sampled trajectory count, phase segmentation, ordinary-space sample availability, Metric relational semantics, and historical-route retention;
4. identify why route geometry is outside / too compressed for the current camera rather than assuming a missing backend trajectory;
5. add a regression fixture proving the route contract contains the geometry the browser renderer expects.

**Exit:** route data availability is proven independently of camera/rendering.

### Work Package 6B — Route visibility and camera contract

Implement shared camera helpers around authoritative route geometry.

Required controls:

```text
FIT ROUTE
FOLLOW SHIP
PLAY ROUTE / STOP
```

Conditional auto-fit rule:

- on first successful route preview, calculate whether the authoritative visible route envelope is materially outside the current viewport;
- if so, fit the route once;
- if already reasonably visible, preserve the user's camera;
- subsequent preview/commit operations do not repeatedly steal camera control;
- manual camera interaction cancels follow mode;
- historical route display does not auto-fit.

The route fit envelope should include all authoritative ordinary-space geometry plus origin/destination/phase anchors required to understand the flight.

Metric relational segments may contribute endpoint/semantic framing but must not be treated as ordinary-space sampled occupancy.

**Exit:** a planned route is unmistakably visible without requiring accidental camera placement.

### Work Package 6C — Operational trajectory symbology

Make active/preview routes visually dominant while retaining semantic truth.

Required hierarchy:

- broad low-alpha route under-stroke for legibility;
- narrower authoritative phase centerline;
- visually distinct torch / terminal / coast / acquisition segments where present;
- Metric relational segment clearly dashed and labelled relational;
- strong departure, collapse/transition, terminal, and arrival anchors;
- authoritative Wayfarer ship icon;
- historical routes retained at substantially lower alpha;
- alternate candidates lower priority than active/preview route.

Do not encode unsupported physical meaning through styling.

**Exit:** on both Pixel and Windows, a user can immediately distinguish current ship, active route, alternates, and history.

### Work Package 6D — Authoritative ship playback

Bind playback to Navigator-authored timeline samples.

Required behavior:

- `PLAY ROUTE` begins at sample 0 and walks the authoritative timeline;
- ordinary-space samples place the ship at supplied J2000 coordinates;
- Metric samples without ordinary-space occupancy are shown using explicitly relational playback semantics rather than fabricated XYZ positions;
- `FOLLOW SHIP` keeps the ship framed while active;
- manual camera input disengages follow mode without stopping playback;
- playback is presentation-only and never mutates campaign state;
- executed arrival remains canonical campaign state, not the final playback frame.

**Exit:** the user can watch the Wayfarer traverse the authoritative route without confusing playback with simulation-state mutation.

### Work Package 6E — Unified NAV / ATLAS HUD controller

Replace direct cross-panel DOM manipulation with the shared HUD state/controller.

NAV drawer contents:

- current origin/current ship state;
- selected destination;
- `PLAN HERE` / destination selection;
- route discovery;
- compact candidate comparison;
- preview / plan details;
- commit;
- execute;
- FIT ROUTE;
- PLAY/STOP;
- FOLLOW SHIP;
- cancel planning where appropriate.

ATLAS drawer contents:

- selected body identity and imagery;
- body attributes and existing Atlas categories;
- center/find actions;
- `PLAN FLIGHT HERE` action that transitions to NAV while retaining selection;
- explicit close.

Remove the independent simultaneous mobile planner + Atlas competition.

**Exit:** one drawer, one owner at a time, deterministic state transitions.

### Work Package 6F — Consolidate platform-specific browser code

Review `flight_planning_pixel_nav.js` and other Pixel-named browser helpers.

Classify each responsibility as:

```text
PRODUCT BEHAVIOR
RESPONSIVE PRESENTATION
RUNTIME/ENVIRONMENT GLUE
LEGACY
```

Move PRODUCT BEHAVIOR into shared planning/navigation/HUD modules. Move responsive behavior to shared CSS/layout logic. Retain Pixel-specific code only where it truly concerns environment/runtime integration; otherwise delete or reduce the helper.

No Windows-specific duplicate browser controller is to be introduced.

**Exit:** one shared UI behavior implementation serves both platforms.

### Work Package 6G — Minor-body navigation qualification

After the shared HUD is stable, deliberately test a real minor-body destination.

Suggested physical test:

`CERES -> DAVIDA`

Qualification must prove:

1. selected GIS entity resolves to the authoritative Navigator route token/name;
2. route discovery either succeeds or returns a truthful Navigator-domain rejection;
3. no short GIS entity ID such as `DAV` leaks into Navigator unless Navigator explicitly defines it;
4. successful minor-body routes use the same trajectory/camera/HUD pipeline as major bodies.

This is adapter qualification, not a special Davida code path.

**Exit:** generic minor-body selection behavior is proven.

### Work Package 6H — Cross-platform same-head acceptance

No platform fork.

Run the same application head on:

- physical Pixel / Termux;
- Windows desktop runtime.

Qualify the same interaction sequence on both:

```text
select destination
plan/discover
preview
route becomes visibly framed
inspect trajectory
commit
play route
follow ship
stop playback
execute
arrive
historical route persists
second execute is rejected
switch NAV <-> ATLAS without losing selection/context
close/restore drawer without cancelling state
```

Responsive placement may differ; semantics and state transitions must not.

**Exit:** both platforms accept the same head with no behavioral divergence.

---

## 7. Regression strategy

Before every Pixel/Windows release candidate:

### Unit / focused regression

- HUD state transitions;
- selection retention across NAV/ATLAS;
- close vs cancel semantics;
- GIS-to-Navigator destination token resolution;
- route-fit bounding/envelope logic;
- missing summary values -> em dash;
- trajectory sample decoding/adapter;
- playback never mutates campaign state.

### Functional / integration

- route discovery -> preview -> overlay;
- preview -> conditional fit;
- commit preserves route visibility;
- execute mutates campaign once;
- post-arrival history persists;
- duplicate execute rejected;
- selected body -> PLAN FLIGHT HERE -> NAV transition;
- Pixel-sized and desktop-sized browser smoke tests using the same JS modules.

### Same-head stack required before physical acceptance

At minimum:

- Python regression;
- Ephemeris provider qualification;
- Phase 4 GIS navigation;
- Phase 5 GIS flight planning;
- Phase 6 Gate C campaign execution;
- new HUD/trajectory qualification added by this work plan.

Do not mix green results from adjacent SHAs.

---

## 8. Physical Phase-6 acceptance gate

Physical Phase 6 closes only when all are true on one same-head build:

1. authoritative route trajectory is visibly rendered and can be fitted to view;
2. ship icon is visible and authoritative playback works;
3. FOLLOW SHIP works and releases on manual camera control;
4. active/preview/history route hierarchy is visually understandable;
5. NAV and ATLAS are mutually exclusive modes with one contextual drawer;
6. close/minimize/restore do not cancel planning state;
7. PLAN FLIGHT HERE transfers selected Atlas body into NAV correctly;
8. route discovery/commit/execute/arrival works on Pixel;
9. duplicate execute is rejected;
10. minor-body destination resolution is physically qualified;
11. the same interaction/state model works on Windows at the same head;
12. full required regression stack is green at that exact head.

Only then:

- declare physical Gate C closed;
- assess Gate B parity again;
- freeze the Phase-6 convergence runtime;
- consider promotion/merge strategy;
- begin Phase 7 SQL migration discipline.

---

## 9. Explicit non-goals for this phase

Do not add:

- separate Android and Windows UX implementations;
- new flight physics;
- GIS-side trajectory interpolation that changes authoritative geometry;
- new SQL migration work;
- traffic simulation expansion;
- unrelated Atlas feature expansion;
- old Navigator renderer retirement before parity/acceptance;
- platform-specific feature forks disguised as responsive behavior.

---

## 10. Recommended implementation order

Safest sequence:

```text
6A prove route truth
 -> 6B route-fit/camera contract
 -> 6C trajectory visibility
 -> 6D ship playback/follow
 -> 6E unified HUD controller
 -> 6F remove product behavior from Pixel-specific helper
 -> focused regression
 -> 6G minor-body qualification
 -> full same-head regression
 -> 6H Pixel + Windows physical acceptance
 -> Phase-6 freeze
```

The route should become visible before the HUD is substantially reorganized so renderer/camera defects are not confused with UI-state defects. The shared HUD controller should be installed before cross-platform qualification so Pixel and Windows test the same interaction grammar rather than two transitional layouts.

---

**Implementation command phrase:** `Execute the Phase-6 HUD / Trajectory Convergence Work Plan v1.0 on feature/gis-navigator-convergence.`
