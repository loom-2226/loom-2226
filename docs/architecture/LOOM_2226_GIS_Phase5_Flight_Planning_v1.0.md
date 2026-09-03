# LOOM 2226 — GIS Phase 5 Flight Planning v1.0

**Status:** COMPLETE — Phase 5 qualification PASS  
**Governing plan:** `LOOM_2226_GIS_Navigator_Convergence_Architecture_and_Work_Plan_v1.0.md`  
**Branch:** `feature/gis-navigator-convergence`

## 1. Phase 5 decision

Phase 5 moves the **flight-planning interaction surface** into GIS while preserving Navigator as the sole navigation/flight calculation authority.

The supported user flow is now:

```text
SELECT DESTINATION ON GIS
        ↓
DISCOVER ROUTES
        ↓
NAVIGATOR PREPARES ACQUISITION + DISCOVERS CANDIDATES
        ↓
GIS PRESENTS CANDIDATE COMPARISON
        ↓
PLAN DETAILS / PREVIEW
        ↓
LOOM_ROUTE_LAYER_V1
        ↓
PHASE-4 GIS NAVIGATION OVERLAY
        ↓
COMMIT PLANNING CHOICE or CANCEL
```

The governing invariant remains:

> **GIS performs no flight math.**

## 2. Authority boundary

### GIS owns

- destination selection from the map;
- planning interaction state;
- candidate comparison presentation;
- `PLAN DETAILS` / preview interaction;
- `COMMIT` / `CANCEL` interaction;
- GIS-owned route symbology through the Phase-4 overlay.

### Navigator owns

- legacy mission-envelope adaptation;
- epoch normalization;
- Sequence-H acquisition;
- ephemeris/cache access;
- candidate discovery;
- route selection eligibility supplied by Navigator;
- deterministic flight compilation;
- `LOOM_ROUTE_LAYER_V1` production.

### Campaign runtime continues to own

- authoritative persistent campaign state;
- flight execution;
- epoch advancement;
- ship-location change;
- remass debit;
- history/ledger writes;
- job/cargo transitions.

Those persistence/execution responsibilities remain Phase 6 work.

## 3. Phase-5 commit semantics

`COMMIT` in Phase 5 means:

> **lock the selected compiled plan in the current in-memory planning session for Phase-6 handoff.**

It does **not** mean:

- execute the flight;
- write `LOOM_STATE_V1.json`;
- advance campaign time;
- change ship location;
- debit remass;
- append campaign history.

This distinction is intentional. It prevents the planning UI from becoming a second campaign-state authority.

## 4. New planning contract

Phase 5 introduces:

```text
LOOM_GIS_FLIGHT_PLANNING_V1
```

The planning state carries:

- planning session identity;
- authoritative origin from the campaign snapshot;
- selected destination;
- priority;
- Navigator candidate records;
- promoted comparison fields where Navigator supplies them;
- current preview route ID;
- committed planning route ID;
- Phase-4 preview overlay;
- campaign-snapshot hash.

Candidate summaries are projections of Navigator output only. GIS does not derive missing flight quantities.

If Navigator does not expose a comparison field in the candidate payload, GIS displays it as unavailable rather than manufacturing a value.

## 5. Navigator anti-corruption seam

GIS does not know the frozen Sequence-H request grammar.

`LegacyNavigationService` now owns adaptation of canonical `NavigationRequest` objects to the RC6.1 mission envelope, including the frozen-compatible requirements:

```text
schema          LOOM_NAV_REQUEST_v1
test_id         H-F######
epoch.local     Melbourne-local representation
timezone        Australia/Melbourne
ship            WAYFARER_BASELINE
requested_modes FAST / CRUISE defaults for new GIS requests
```

Existing imported/replay mission envelope fields remain authoritative when supplied.

The service also owns `prepare_context()`, so provider/cache/acquisition details do not leak into GIS.

## 6. GIS HTTP interaction surface

The converged GIS exposes:

```text
GET  /flight-planning.json
POST /flight-planning/discover
POST /flight-planning/preview
POST /flight-planning/commit
POST /flight-planning/cancel
```

Preview and commit update the read-only Phase-4 navigation overlay presented by GIS.

Cancel restores the pre-planning overlay.

The first Phase-5 browser implementation intentionally reloads the GIS after preview/commit/cancel so the already-qualified Phase-4 renderer consumes the changed overlay through its normal startup path. This is a reliability choice, not an architectural requirement; later UI work may make the update dynamic without changing the domain contracts.

## 7. Map interaction

The Phase-5 browser controller maps selected first-class GIS entities to Navigator destination tokens where a canonical mapping exists, including the major planet/system tokens already used by the courier runtime.

The current interaction is:

```text
select map entity
→ DISCOVER ROUTES · <destination>
→ inspect candidate cards
→ PLAN DETAILS
→ COMMIT or CANCEL
```

The comparison panel exposes only Navigator-supplied values, including where available:

- arrival/departure epoch;
- strategy / metric and torch modes;
- remass;
- duration;
- holonomy;
- confidence;
- selectable state.

## 8. Frozen qualification

Phase 5 was qualified against the preserved Pixel pre-clean runtime archive and the coherent frozen Ceres departure state used by the earlier convergence gates.

The qualification used:

```text
origin:             CERES
destination:        MARS
priority:           BALANCED
ephemeris mode:     FROZEN_OFFLINE_ONLY
Sequence-H entries: 34 cache hits
provider fills:     0
```

Navigator returned:

```text
candidate_count:    24
selected_route_id:  route1-2a63602ce1f2b4af
strategy:           HARD / CRUISE
remass_t:           12.01419999622317
```

Fields not promoted by the actual candidate payload remained null/unavailable rather than being inferred.

The preserved frozen runtime physics reference remains:

```text
c834998cc9b8016dcbf5f0e200db781cb1d2f5dc9245c091a8f205dea280107b
```

The frozen campaign snapshot semantic hash used by the direct Phase-5 qualifier was:

```text
e7fd0c2bfce7f5f08169db454cfe12d2e608740a185e1a28e5eaac91cdb3d0c0
```

A preview route-layer SHA is emitted by each qualification run as provenance for that produced planning artifact. It is **not** promoted here as a new physics golden oracle; Phase 5 qualifies planning interaction and authority separation, while the frozen Navigator runtime remains the governing physics reference.

## 9. Live HTTP qualification

GitHub Actions additionally launched the real converged GIS HTTP server against a copied coherent frozen runtime and exercised the same API surface used by the browser.

The live smoke proved:

```text
GET planning state           PASS
POST discover CERES→MARS     PASS · 24 candidates
POST preview                 PASS
Phase-4 overlay swap         PASS
POST commit                  PASS
POST cancel                  PASS
base overlay restoration     PASS
Phase-5 browser bundle       PASS
```

The HTTP test-runtime `LOOM_STATE_V1.json` was hashed immediately before and after the full discover/preview/commit/cancel sequence.

Result:

```text
LIVE PHASE5 CAMPAIGN MUTATION NONE
```

This is the Phase-5 persistence boundary proof.

## 10. Automated qualification

The Phase-5 workflow performs:

- Python compilation;
- Node syntax validation for the browser controller;
- five Phase-5 planning unit tests;
- frozen runtime download and coherent-bundle selection;
- direct real-Navigator frozen planning qualification;
- locked CIVSTATE selection by SHA;
- live converged GIS server startup;
- real HTTP discover/preview/commit/cancel calls;
- Phase-4 overlay validation;
- browser bundle validation;
- before/after campaign-file SHA comparison.

## 11. Gate B note

Phase 5 does not alter the Phase-4 sampled-geometry decision.

Gate B remains separately open because RC6.1 currently exposes authoritative phase anchors rather than a fully sampled continuous flight trajectory. GIS continues to refuse to invent intermediate flight geometry.

This does not block Phase 5 because route discovery, candidate comparison, preview state, phase anchors, and planning selection all operate through the existing authoritative contracts.

## 12. Phase 6 handoff

Phase 6 may now consume the Phase-5 committed in-memory `FlightPlan` and integrate it with the authoritative campaign transaction boundary.

The required Phase-6 flow is:

```text
GIS COMMITTED PLAN
        ↓
Navigator execute_flight() authoritative transition result
        ↓
Campaign validates pre-state / job / cargo authority
        ↓
Single atomic campaign commit
        ↓
epoch + location + remass + flight/job history updated once
        ↓
GIS refreshes from the new authoritative state
```

Phase 6 must not introduce a second epoch, ship-location, or persistence authority.

---

**Phase 5 status: COMPLETE.**
