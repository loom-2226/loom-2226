# LOOM 2226 — Navigator Phase 3 Route Layer v1.0

**Status:** COMPLETE — Phase 3 qualification PASS  
**Branch:** `feature/gis-navigator-convergence`  
**Date:** 2026-09-03  
**Contract:** `LOOM_ROUTE_LAYER_V1`

## 1. Objective

Phase 3 establishes the versioned GIS-facing route contract required by the GIS / Navigator Convergence Architecture and Work Plan v1.0.

The route layer is a read-only anti-corruption boundary between authoritative Navigator output and downstream spatial presentation. It carries physics truth and semantic route state. It does not calculate flight physics, alter campaign state, or define GIS presentation.

The frozen Navigator / Sequence-H implementation remains authoritative.

## 2. Canonical contract

`src/loom/navigation/route_layer.py` defines:

- `LoomRouteLayerV1`
- `RouteLayerSegmentV1`
- `RouteLayerBodyV1`
- `LegacyRouteLayerAdapter`
- `ROUTE_LAYER_VERSION = LOOM_ROUTE_LAYER_V1`
- `GEOMETRY_MODE = AUTHORITATIVE_PHASE_ANCHORS_ONLY`

`LegacyNavigationService.get_route_layer(...)` is the supported service handoff. GIS consumers must use this boundary rather than inspect legacy Navigator dictionaries directly.

The V1 route object exposes the governing minimum fields:

- route ID and flight ID;
- origin and destination;
- departure and arrival epochs;
- strategy and route status;
- typed route segments;
- waypoints when supplied by Navigator;
- body references;
- maneuver markers when supplied or directly represented by authoritative Sequence-H phase events;
- current vehicle/campaign departure state;
- authoritative arrival state;
- source and determinism provenance.

## 3. Real Sequence-H mapping

Qualification against the frozen Pixel runtime showed that RC6.1 flight legs do not use a generic `geometry` / `phases` structure. The real authoritative leg schema contains:

- `metric_segment`;
- `terminal_burn`;
- `arrival`;
- `ordinary_velocity_memory`;
- `engineering_checkpoints`;
- metric and torch modes;
- mass ledger and solver provenance.

V1 therefore promotes those real structures directly.

### Metric segment

The route layer emits a `METRIC` segment whose authoritative fields include:

- departure epoch from the leg;
- metric-collapse epoch;
- metric-collapse position from `collapse_position_km_j2000_ecliptic`;
- `J2000_ECLIPTIC` coordinate-frame semantics implied by the authoritative source field;
- ordinary-velocity memory;
- engineering acceleration checkpoints;
- complete source metric payload.

### Terminal burn

The route layer emits a `TERMINAL_BURN` segment whose authoritative fields include:

- metric-collapse epoch as the known phase boundary;
- arrival epoch from the authoritative arrival object;
- metric-collapse position as the known start anchor;
- terminal delta-v and delta-v vector when present;
- initial/final acceleration and thrust values when present;
- ordinary-velocity memory;
- complete terminal-burn and arrival payloads.

### Maneuver semantics

When the runtime does not provide a separate maneuver collection, V1 promotes only events directly present in the authoritative leg structure:

- `METRIC_COLLAPSE`;
- `TERMINAL_BURN`.

No maneuver time is inferred by arithmetic when the source does not provide one.

## 4. Geometry authority boundary

A key Phase-3 finding is that the frozen RC6.1 runtime and its six deterministic canonical payloads do **not** expose a sampled spatial trajectory polyline.

The inspected payloads were:

- `decisionSeriesPayload`;
- `flightSolutionsPayload`;
- `headlinePayload`;
- `localRoutePayload`;
- `missionPayload`;
- `statusStripPayload`.

They contain route epochs, scalar flight solutions, leg semantics, provenance and local-route relationships, but not a sampled sequence of flight positions suitable for drawing a physically authoritative curved track.

Therefore V1 explicitly declares:

```text
GEOMETRY_MODE=AUTHORITATIVE_PHASE_ANCHORS_ONLY
SAMPLED_TRACK=NOT_EXPOSED_BY_RC6_1
```

This is an authority constraint, not missing GIS work.

**GIS must not interpolate, estimate or manufacture flight physics between authoritative anchors.** If Phase 4 requires a sampled flight track, sampling must be implemented behind the Navigator authority boundary and returned as Navigator-owned geometry. The renderer may then draw it without recalculation.

## 5. Presentation boundary

`LOOM_ROUTE_LAYER_V1` contains no presentation authority. The Phase-3 qualification recursively rejects display keys including color/colour, icon, stroke, fill, opacity, line width, symbol, CSS, style and symbology.

GIS owns:

- colors;
- line styles;
- icons;
- labels;
- layer visibility;
- selection/highlight state;
- animation and viewport behavior.

Navigator owns the route facts those visual decisions represent.

## 6. State and persistence boundary

The route adapter is read-only.

Qualification verifies that constructing a route layer does not mutate:

- the solved `FlightPlan` payload;
- the canonical campaign/departure state.

`current_vehicle_state` is the exact departure state supplied to the navigation context. `arrival_state` is exposed from solved Navigator output. Campaign commitment, ledger writes, job/reward processing and authoritative state advancement remain outside Phase 3 and remain assigned to the campaign integration phase.

A planned service solve may carry its deterministic service flight identifier. Campaign-assigned committed flight identity remains a persistence-layer concern and may replace/bind that identifier when Phase 6 performs the authoritative commit.

## 7. Qualification

Phase-3 unit qualification at the final semantic-mapping implementation:

```text
9 tests
PASS
```

Coverage includes:

- governing minimum contract fields;
- real Sequence-H metric mapping;
- exact metric-collapse anchor promotion;
- real terminal-burn delta-v and acceleration mapping;
- no invented sampled track;
- null prior-flight departure state;
- display-agnostic contract enforcement;
- non-mutation of flight/campaign state;
- deterministic canonical serialization;
- fail-closed contract versioning.

Frozen integration qualification re-solved the coherent Pixel Ceres→Mars flight using the archived Sequence-H cache only:

```text
PHASE3_ROUTE_LAYER_V1=PASS
EPHEMERIS_MODE=FROZEN_OFFLINE_ONLY
GEOMETRY_MODE=AUTHORITATIVE_PHASE_ANCHORS_ONLY
SAMPLED_TRACK=NOT_EXPOSED_BY_RC6_1
route=['CERES', 'MARS']
segment_types=['METRIC', 'TERMINAL_BURN']
maneuvers=2
runtime_sha256=c834998cc9b8016dcbf5f0e200db781cb1d2f5dc9245c091a8f205dea280107b
route_layer_sha256=913288388ee6c4fc1172131093044e0bf5931f8c8140b98dd72a5e53f8e70a42
```

The authoritative runtime SHA is identical to the Phase-2 Gate-A frozen oracle. Phase 3 therefore changes no Navigator physics or deterministic result.

## 8. Phase 3 exit criteria

Phase 3 is complete when the final branch head confirms:

1. Python regression remains green;
2. live ephemeris-provider qualification remains green;
3. Phase-2 Gate A remains green;
4. Phase-3 route-layer qualification remains green;
5. the frozen runtime SHA remains unchanged;
6. the route contract contains no presentation instructions;
7. no sampled trajectory is fabricated outside Navigator authority.

## 9. Phase 4 handoff

Phase 4 may now build GIS rendering against `LegacyNavigationService.get_route_layer(...)` / `LOOM_ROUTE_LAYER_V1`.

The renderer may display authoritative endpoints, phase anchors, body references, maneuver semantics, epochs and vehicle state immediately.

If a continuous physically authoritative route line is required, Phase 4 must first request a Navigator-owned sampled-geometry service extension. It must not create a physics interpolation inside GIS.
