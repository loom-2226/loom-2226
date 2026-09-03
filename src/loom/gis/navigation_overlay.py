"""Read-only GIS rendering adapter for LOOM_ROUTE_LAYER_V1.

This module is deliberately display-side. It consumes authoritative navigation
truth and emits GIS render primitives plus GIS-owned symbology. It performs no
flight planning, propagation, interpolation, campaign writes, or ephemeris work.

RC6.1 currently exposes authoritative phase anchors rather than a sampled
trajectory polyline. The adapter therefore marks geometry availability
explicitly and never fabricates intermediate trajectory points.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse
import json

from loom.navigation import LoomRouteLayerV1, ROUTE_LAYER_VERSION

GIS_NAV_OVERLAY_VERSION = "LOOM_GIS_NAVIGATION_OVERLAY_V1"

# Presentation belongs here, not in Navigator contracts.
_PHASE_STYLE = {
    "TORCH": {"stroke": "#e2a85f", "dash": [], "width": 2.2},
    "METRIC": {"stroke": "#bda5ff", "dash": [6, 5], "width": 2.2},
    "COAST": {"stroke": "#8da0b8", "dash": [2, 5], "width": 1.5},
    "TERMINAL_BURN": {"stroke": "#63d6e5", "dash": [], "width": 2.0},
    "ARRIVAL_ACQUISITION": {"stroke": "#77d6a5", "dash": [3, 3], "width": 1.8},
    "UNSPECIFIED": {"stroke": "#9aa7b8", "dash": [2, 4], "width": 1.2},
}


class GISNavigationOverlayError(ValueError):
    pass


def _mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _vector3(value: Any) -> list[float] | None:
    if isinstance(value, Mapping):
        for key in (
            "values",
            "position_km",
            "position_km_j2000_ecliptic",
            "collapse_position_km",
            "collapse_position_km_j2000_ecliptic",
        ):
            candidate = value.get(key)
            if isinstance(candidate, (list, tuple)):
                value = candidate
                break
        else:
            if all(k in value for k in ("x", "y", "z")):
                value = [value["x"], value["y"], value["z"]]
            else:
                return None
    if not isinstance(value, (list, tuple)) or len(value) < 3:
        return None
    try:
        return [float(value[0]), float(value[1]), float(value[2])]
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class GISRouteAnchorV1:
    anchor_type: str
    epoch_utc: str | None = None
    position_j2000_ecliptic_km: tuple[float, float, float] | None = None
    body_id: str | None = None
    label: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GISRouteSegmentRenderV1:
    type: str
    phase: str | None
    start_epoch: str | None
    end_epoch: str | None
    start_position_j2000_ecliptic_km: tuple[float, float, float] | None
    end_position_j2000_ecliptic_km: tuple[float, float, float] | None
    geometry_points_j2000_ecliptic_km: tuple[tuple[float, float, float], ...]
    geometry_authority: str
    style: Mapping[str, Any]
    engineering: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GISRouteRenderV1:
    route_id: str
    flight_id: str
    origin: str
    destination: str
    departure_epoch: str | None
    arrival_epoch: str | None
    strategy: str | None
    status: str
    segments: tuple[GISRouteSegmentRenderV1, ...]
    anchors: tuple[GISRouteAnchorV1, ...]
    maneuvers: tuple[Mapping[str, Any], ...]
    current_vehicle_state: Mapping[str, Any]
    arrival_state: Mapping[str, Any]
    source_contract: str
    source_sha256: str
    role: str = "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GISNavigationOverlayV1:
    active_route: GISRouteRenderV1 | None = None
    alternate_routes: tuple[GISRouteRenderV1, ...] = ()
    historical_routes: tuple[GISRouteRenderV1, ...] = ()
    contract: str = GIS_NAV_OVERLAY_VERSION
    controls: tuple[str, ...] = (
        "ACTIVE_ROUTE",
        "ALTERNATE_ROUTES",
        "FLIGHT_PHASES",
        "MANEUVERS",
        "HISTORICAL_TRACKS",
        "TRAFFIC_CIVSTATE",
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def json_bytes(self) -> bytes:
        return (json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def _segment_engineering(seg: Any) -> dict[str, Any]:
    payload = _mapping(getattr(seg, "payload", None))
    velocity = _mapping(getattr(seg, "velocity", None))
    acceleration = _mapping(getattr(seg, "acceleration", None))
    geometry = _mapping(getattr(seg, "geometry", None))
    out: dict[str, Any] = {}
    aliases = {
        "delta_v_km_s": (velocity, "delta_v_km_s"),
        "dv_km_s": (payload, "dv_km_s"),
        "initial_accel_g": (acceleration, "initial_accel_g"),
        "final_accel_g": (acceleration, "final_accel_g"),
        "acceleration_g": (acceleration, "acceleration_g"),
        "velocity_memory_km_s": (velocity, "velocity_memory_km_s"),
        "engineering_checkpoints": (geometry, "engineering_checkpoints"),
    }
    for name, (source, key) in aliases.items():
        if key in source:
            out[name] = source[key]
    for key in (
        "dv_km_s",
        "delta_v_km_s",
        "initial_accel_g",
        "final_accel_g",
        "acceleration_g",
        "velocity_memory_km_s",
        "engineering_checkpoints",
    ):
        if key in payload and key not in out:
            out[key] = payload[key]
    return out


def _render_segment(seg: Any) -> GISRouteSegmentRenderV1:
    seg_type = str(getattr(seg, "type", None) or "UNSPECIFIED").upper()
    start = _vector3(getattr(seg, "start_position", None))
    end = _vector3(getattr(seg, "end_position", None))
    geom = _mapping(getattr(seg, "geometry", None))
    raw_points = geom.get("points") or geom.get("values") or []
    points: list[tuple[float, float, float]] = []
    if isinstance(raw_points, (list, tuple)):
        for raw in raw_points:
            v = _vector3(raw)
            if v is not None:
                points.append(tuple(v))
    authority = "AUTHORITATIVE_SAMPLED_GEOMETRY" if len(points) >= 2 else "AUTHORITATIVE_PHASE_ANCHORS_ONLY"
    return GISRouteSegmentRenderV1(
        type=seg_type,
        phase=getattr(seg, "phase", None),
        start_epoch=getattr(seg, "start_epoch", None),
        end_epoch=getattr(seg, "end_epoch", None),
        start_position_j2000_ecliptic_km=tuple(start) if start else None,
        end_position_j2000_ecliptic_km=tuple(end) if end else None,
        geometry_points_j2000_ecliptic_km=tuple(points),
        geometry_authority=authority,
        style=dict(_PHASE_STYLE.get(seg_type, _PHASE_STYLE["UNSPECIFIED"])),
        engineering=_segment_engineering(seg),
    )


def route_to_gis(route: LoomRouteLayerV1, *, role: str = "ACTIVE") -> GISRouteRenderV1:
    if route.contract != ROUTE_LAYER_VERSION:
        raise GISNavigationOverlayError(f"unsupported source route contract: {route.contract}")
    segments = tuple(_render_segment(seg) for seg in route.segments)
    anchors: list[GISRouteAnchorV1] = [
        GISRouteAnchorV1("DEPARTURE", route.departure_epoch, body_id=route.origin, label=route.origin),
        GISRouteAnchorV1("ARRIVAL", route.arrival_epoch, body_id=route.destination, label=route.destination),
    ]
    for seg in segments:
        if seg.type == "METRIC":
            p = seg.end_position_j2000_ecliptic_km or seg.start_position_j2000_ecliptic_km
            epoch = seg.end_epoch or seg.start_epoch
            if p is not None:
                anchors.append(GISRouteAnchorV1("METRIC_COLLAPSE", epoch, p, label="METRIC COLLAPSE"))
        elif seg.type == "TERMINAL_BURN":
            p = seg.start_position_j2000_ecliptic_km or seg.end_position_j2000_ecliptic_km
            if p is not None:
                anchors.append(GISRouteAnchorV1("TERMINAL_BURN", seg.start_epoch, p, label="TERMINAL BURN"))
    return GISRouteRenderV1(
        route_id=route.route_id,
        flight_id=route.flight_id,
        origin=route.origin,
        destination=route.destination,
        departure_epoch=route.departure_epoch,
        arrival_epoch=route.arrival_epoch,
        strategy=route.strategy,
        status=route.status,
        segments=segments,
        anchors=tuple(anchors),
        maneuvers=tuple(dict(x) for x in route.maneuvers),
        current_vehicle_state=dict(route.current_vehicle_state),
        arrival_state=dict(route.arrival_state),
        source_contract=route.contract,
        source_sha256=route.sha256(),
        role=role,
    )


def build_navigation_overlay(
    active_route: LoomRouteLayerV1 | None = None,
    alternate_routes: Iterable[LoomRouteLayerV1] = (),
    historical_routes: Iterable[LoomRouteLayerV1] = (),
) -> GISNavigationOverlayV1:
    return GISNavigationOverlayV1(
        active_route=route_to_gis(active_route, role="ACTIVE") if active_route is not None else None,
        alternate_routes=tuple(route_to_gis(x, role="ALTERNATE") for x in alternate_routes),
        historical_routes=tuple(route_to_gis(x, role="HISTORICAL") for x in historical_routes),
    )


def route_layer_from_dict(data: Mapping[str, Any]) -> LoomRouteLayerV1:
    """Hydrate a V1 route layer without duplicating Navigator adaptation rules."""
    from loom.navigation import RouteLayerBodyV1, RouteLayerSegmentV1

    if data.get("contract") != ROUTE_LAYER_VERSION:
        raise GISNavigationOverlayError(f"route JSON must be {ROUTE_LAYER_VERSION}")
    return LoomRouteLayerV1(
        route_id=data["route_id"],
        flight_id=data["flight_id"],
        origin=data["origin"],
        destination=data["destination"],
        departure_epoch=data.get("departure_epoch"),
        arrival_epoch=data.get("arrival_epoch"),
        strategy=data.get("strategy"),
        status=data.get("status") or "PLANNED",
        segments=tuple(RouteLayerSegmentV1(**x) for x in data.get("segments") or []),
        waypoints=tuple(data.get("waypoints") or []),
        bodies=tuple(RouteLayerBodyV1(**x) for x in data.get("bodies") or []),
        maneuvers=tuple(data.get("maneuvers") or []),
        current_vehicle_state=data.get("current_vehicle_state") or {},
        arrival_state=data.get("arrival_state") or {},
        payload=data.get("payload") or {},
        contract=data.get("contract"),
    )


def load_route_layer(path: str | Path) -> LoomRouteLayerV1:
    return route_layer_from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def client_extension_js() -> str:
    return Path(__file__).with_name("navigation_overlay.js").read_text(encoding="utf-8")


def install_navigation_overlay(gis_module: Any, overlay: GISNavigationOverlayV1) -> None:
    """Add Phase-4 endpoint + renderer to the frozen GIS module at runtime.

    The existing GIS source file is not edited. The extension owns presentation
    and only reads the route-layer payload.
    """
    handler = gis_module.SolarHandler
    handler.navigation_overlay_json = overlay.json_bytes()
    old_get = handler.do_GET

    def do_GET(self):
        if urlparse(self.path).path == "/navigation-overlay.json":
            self._send(200, "application/json; charset=utf-8", self.navigation_overlay_json)
            return
        return old_get(self)

    handler.do_GET = do_GET
    marker = "/* LOOM_PHASE4_NAVIGATION_OVERLAY */"
    if marker not in gis_module.CLIENT_JS:
        gis_module.CLIENT_JS += "\n" + marker + "\n" + client_extension_js() + "\n"
