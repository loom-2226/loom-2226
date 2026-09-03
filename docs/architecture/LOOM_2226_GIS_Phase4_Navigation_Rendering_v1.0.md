# LOOM 2226 — GIS Phase 4 Navigation Rendering v1.0

**Status:** PHASE 4 IMPLEMENTATION COMPLETE / GATE B REMAINS OPEN  
**Branch:** `feature/gis-navigator-convergence`  
**Governing plan:** `LOOM_2226_GIS_Navigator_Convergence_Architecture_and_Work_Plan_v1.0.md`  
**Source navigation contract:** `LOOM_ROUTE_LAYER_V1`  
**GIS overlay contract:** `LOOM_GIS_NAVIGATION_OVERLAY_V1`

## 1. Purpose

Phase 4 makes Solar GIS the rendering surface for authoritative Navigator route state without moving flight physics, ephemeris authority, campaign authority, or state mutation into GIS.

The implementation is deliberately additive. The known-good `loom_solar_gis.py` remains unchanged. The convergence launcher `loom_gis.py` imports that GIS and installs a read-only navigation extension at runtime. This keeps the production-qualified GIS easy to compare and roll back while convergence continues.

## 2. Authority boundary

Navigator remains authoritative for:

- flight discovery and planning;
- deterministic solve results;
- ephemeris/dependency state;
- flight phases and engineering state;
- metric-collapse position and epoch;
- terminal-burn delta-v and acceleration;
- departure/arrival semantics;
- current and arrival vehicle state.

GIS owns only presentation:

- phase colors;
- line/dash patterns;
- marker shapes;
- visibility controls;
- selection and intelligence-panel presentation.

GIS performs no propagation, interpolation, trajectory solving, ephemeris acquisition, campaign write, or state transition.

## 3. Implemented surfaces

### 3.1 Python GIS adapter

`src/loom/gis/navigation_overlay.py`

Converts `LOOM_ROUTE_LAYER_V1` into `LOOM_GIS_NAVIGATION_OVERLAY_V1` render primitives while retaining source identity through the route-layer SHA-256.

Supported route roles:

- ACTIVE;
- ALTERNATE;
- HISTORICAL.

Supported semantic states include:

- origin and destination;
- departure and arrival epochs;
- current vehicle location;
- phase ordering;
- metric-collapse anchor;
- terminal-burn state;
- authoritative sampled geometry when supplied by a future Navigator contract;
- maneuver records;
- arrival state.

### 3.2 Browser renderer

`src/loom/gis/navigation_overlay.js`

The extension appends to the existing GIS canvas renderer and exposes the governing navigation controls:

- ACTIVE;
- ALTS;
- PHASES;
- MANEUVERS;
- HISTORY;
- TRAFFIC / CIVSTATE.

The active route opens in the existing GIS intelligence/Atlas drawer. No separate Navigator visual surface is opened.

### 3.3 Convergence launcher

`src/loom_gis.py`

Accepted navigation inputs:

- `--nav-route`;
- repeatable `--nav-alt`;
- repeatable `--nav-history`;
- `LOOM_ROUTE_LAYER` environment variable;
- `LOOM_HOME/state/LOOM_ACTIVE_ROUTE_LAYER.json` when present.

The launcher installs `/navigation-overlay.json` and delegates the rest of runtime behavior to the known-good Solar GIS.

## 4. Geometry rule

The frozen RC6.1 Navigator route does **not** expose an authoritative sampled trajectory polyline.

The frozen Ceres -> Mars route exposes:

- `METRIC` phase;
- `TERMINAL_BURN` phase;
- metric-collapse position and epoch;
- terminal burn engineering state;
- departure and arrival body semantics.

Therefore Phase 4 renders those authoritative anchors and semantic states but does **not** connect unsampled anchors with an invented trajectory.

If a future Navigator service supplies `geometry_points_j2000_ecliptic_km`, GIS passes those points through unchanged and may render the resulting polyline. Sampling must occur on the Navigator/domain side or be obtained from an already-authoritative navigation payload. GIS must never synthesize flight physics for visual convenience.

## 5. Qualification

Phase 4 qualification uses the same coherent frozen Pixel runtime and Ceres -> Mars replay used for Gate A and Phase 3.

The qualification proves:

- all 34 Sequence-H ephemeris dependencies are satisfied from frozen cache;
- no provider replacement is needed;
- the authoritative Navigator runtime hash remains unchanged;
- the GIS adapter does not mutate campaign state;
- the GIS adapter does not mutate `LOOM_ROUTE_LAYER_V1`;
- metric and terminal-burn phases are retained in order;
- metric-collapse anchor is retained;
- GIS symbology is assigned only after crossing the route contract;
- no sampled geometry is invented;
- all required navigation controls are present;
- the browser renderer passes Node syntax validation;
- the actual converged GIS HTTP server starts with the frozen route attached;
- `/navigation-overlay.json` returns the correct live contract;
- `/app.js` contains the installed Phase 4 renderer.

Frozen authoritative runtime SHA-256:

`c834998cc9b8016dcbf5f0e200db781cb1d2f5dc9245c091a8f205dea280107b`

Current frozen route-layer SHA-256:

`b7d306b9bf38857dc66da518bb7a3699849b72ebf292fca0b0082df6e064b948`

Qualification workflow:

`.github/workflows/phase4-gis-navigation.yml`

## 6. Phase 4 disposition

**Phase 4 implementation is complete for every authoritative navigation state currently exposed through `LOOM_ROUTE_LAYER_V1`.**

The following governing-plan capabilities are structurally present:

- active route rendering;
- alternate-route rendering support;
- phase-specific rendering;
- maneuver rendering;
- historical-route rendering support;
- Traffic/CIVSTATE coexistence;
- route inspection through the GIS intelligence surface.

The alternate and historical collections are supported by the contract/renderer but are not yet populated by campaign workflow; that integration belongs to later planning/campaign phases.

## 7. Gate B disposition

**Gate B is NOT closed.**

Gate B requires GIS to visualize every meaningful authoritative flight state required from the old Navigator renderer. The current route contract lacks an authoritative sampled trajectory track. A visually continuous flight path would therefore require data Navigator has not yet exposed.

Gate B closes only after one of the following is proven:

1. Navigator exposes authoritative sampled trajectory geometry and GIS renders it; or
2. review of the legacy renderer proves no meaningful authoritative continuous trajectory state exists beyond the already-exposed phase anchors.

Until then, the absence of a continuous route line is an explicit truth-preservation constraint, not a rendering defect.

## 8. Next phase boundary

Phase 5 may begin moving **planning interaction** into GIS using the now-stable read-only route rendering surface:

`origin -> destination -> priority -> discover routes -> inspect candidates -> plan details -> commit/cancel`

All route discovery and flight calculations continue to come from `loom.navigation`.

The sampled-trajectory Gate B item remains a tracked visualization-parity dependency and must be resolved before retirement of the legacy Navigator visual renderer in Phase 9.
