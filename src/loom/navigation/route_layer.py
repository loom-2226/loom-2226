"""GIS-facing navigation route contract for LOOM 2226.

Phase 3 establishes a versioned, display-agnostic handoff from authoritative
Navigator truth to GIS. This module performs no flight math. It promotes stable
semantic fields from a solved FlightPlan and retains source payloads for
provenance while centralizing legacy-key adaptation in one place.

RC6.1 does not expose a sampled trajectory polyline. The V1 adapter therefore
publishes only authoritative phase anchors and engineering state. Consumers may
render those truths, but must not interpolate or invent flight physics.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Iterable, Mapping
import hashlib
import json

from .contracts import FlightPlan, NavigationContext

ROUTE_LAYER_VERSION = "LOOM_ROUTE_LAYER_V1"
GEOMETRY_MODE = "AUTHORITATIVE_PHASE_ANCHORS_ONLY"


class RouteLayerError(ValueError):
    """Raised when a GIS route-layer contract cannot be built safely."""


def _mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _text(value: Any, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    out = str(value).strip() if value is not None else ""
    if not out:
        if optional:
            return None
        raise RouteLayerError(f"{name} is required")
    return out


def _utc(value: Any, name: str, *, optional: bool = True) -> str | None:
    text = _text(value, name, optional=optional)
    if text is None:
        return None
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise RouteLayerError(f"{name} must be ISO-8601") from exc
    if dt.tzinfo is None:
        raise RouteLayerError(f"{name} must include timezone")
    return text


def _first(mapping: Mapping[str, Any], names: Iterable[str], default: Any = None) -> Any:
    """Single legacy-access seam; callers never scatter payload-key fallbacks."""
    for name in names:
        if name in mapping and mapping[name] is not None:
            return mapping[name]
    return default


@dataclass(frozen=True)
class RouteLayerSegmentV1:
    type: str
    start_epoch: str | None = None
    end_epoch: str | None = None
    start_position: Mapping[str, Any] = field(default_factory=dict)
    end_position: Mapping[str, Any] = field(default_factory=dict)
    geometry: Mapping[str, Any] = field(default_factory=dict)
    velocity: Mapping[str, Any] = field(default_factory=dict)
    acceleration: Mapping[str, Any] = field(default_factory=dict)
    phase: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "type", _text(self.type, "segment.type"))
        object.__setattr__(self, "start_epoch", _utc(self.start_epoch, "segment.start_epoch"))
        object.__setattr__(self, "end_epoch", _utc(self.end_epoch, "segment.end_epoch"))
        object.__setattr__(self, "phase", _text(self.phase, "segment.phase", optional=True))
        for name in ("start_position", "end_position", "geometry", "velocity", "acceleration", "payload"):
            object.__setattr__(self, name, _mapping(getattr(self, name)))


@dataclass(frozen=True)
class RouteLayerBodyV1:
    body_id: str
    role: str | None = None
    state: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "body_id", _text(self.body_id, "body_id"))
        object.__setattr__(self, "role", _text(self.role, "body.role", optional=True))
        object.__setattr__(self, "state", _mapping(self.state))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class LoomRouteLayerV1:
    route_id: str
    flight_id: str
    origin: str
    destination: str
    departure_epoch: str | None
    arrival_epoch: str | None
    strategy: str | None
    status: str
    segments: tuple[RouteLayerSegmentV1, ...] = ()
    waypoints: tuple[Mapping[str, Any], ...] = ()
    bodies: tuple[RouteLayerBodyV1, ...] = ()
    maneuvers: tuple[Mapping[str, Any], ...] = ()
    current_vehicle_state: Mapping[str, Any] = field(default_factory=dict)
    arrival_state: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)
    contract: str = ROUTE_LAYER_VERSION

    def __post_init__(self) -> None:
        if self.contract != ROUTE_LAYER_VERSION:
            raise RouteLayerError(f"unsupported route contract: {self.contract}")
        for name in ("route_id", "flight_id", "origin", "destination", "status"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(self, "departure_epoch", _utc(self.departure_epoch, "departure_epoch"))
        object.__setattr__(self, "arrival_epoch", _utc(self.arrival_epoch, "arrival_epoch"))
        object.__setattr__(self, "strategy", _text(self.strategy, "strategy", optional=True))
        object.__setattr__(self, "segments", tuple(self.segments))
        object.__setattr__(self, "waypoints", tuple(_mapping(x) for x in self.waypoints))
        object.__setattr__(self, "bodies", tuple(self.bodies))
        object.__setattr__(self, "maneuvers", tuple(_mapping(x) for x in self.maneuvers))
        object.__setattr__(self, "current_vehicle_state", _mapping(self.current_vehicle_state))
        object.__setattr__(self, "arrival_state", _mapping(self.arrival_state))
        object.__setattr__(self, "payload", _mapping(self.payload))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), default=str)

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


class LegacyRouteLayerAdapter:
    """Read-only anti-corruption adapter from solved Navigator output to GIS V1."""

    SEGMENT_ALIASES = {
        "type": ("type", "kind", "segment_type", "mode"),
        "start_epoch": ("start_epoch", "start_epoch_utc", "departure_epoch_utc"),
        "end_epoch": ("end_epoch", "end_epoch_utc", "arrival_epoch_utc"),
        "start_position": ("start_position", "start_position_km", "r0_km"),
        "end_position": ("end_position", "end_position_km", "r1_km"),
        "geometry": ("geometry", "trajectory", "path"),
        "velocity": ("velocity", "velocity_km_s", "v_km_s"),
        "acceleration": ("acceleration", "acceleration_g", "accel_g"),
        "phase": ("phase", "phase_name", "label"),
    }

    def build(self, plan: FlightPlan, context: NavigationContext | None = None) -> LoomRouteLayerV1:
        packed = dict(plan.payload)
        runtime = _mapping(packed.get("runtime"))
        flight = _mapping(runtime.get("flight"))
        candidate = plan.candidate

        departure = candidate.departure_epoch
        if departure is None and context is not None:
            departure = context.campaign_state.get("epoch_utc")
        arrival = candidate.arrival_epoch or _first(flight, ("final_epoch_utc", "arrival_epoch_utc"))

        current_state = dict(context.campaign_state) if context is not None else {}
        arrival_state = self._arrival_state(plan, flight)
        segments = self._segments(flight)
        waypoints = self._mapping_list(_first(flight, ("waypoints", "route_waypoints"), []))
        maneuvers = self._maneuvers(flight)
        bodies = self._body_refs(candidate.origin, candidate.destination)

        status = candidate.status or "PLANNED"
        prior_flight = _mapping(current_state.get("last_flight")) if current_state else {}
        if prior_flight.get("flight_id") == plan.flight_id:
            status = str(current_state.get("status") or "EXECUTED")

        return LoomRouteLayerV1(
            route_id=candidate.route_id,
            flight_id=plan.flight_id,
            origin=candidate.origin,
            destination=candidate.destination,
            departure_epoch=departure,
            arrival_epoch=arrival,
            strategy=candidate.strategy,
            status=status,
            segments=segments,
            waypoints=waypoints,
            bodies=bodies,
            maneuvers=maneuvers,
            current_vehicle_state=current_state,
            arrival_state=arrival_state,
            payload={
                "source": "AUTHORITATIVE_NAVIGATOR_SERVICE",
                "geometry_mode": GEOMETRY_MODE,
                "runtime_model": flight.get("model"),
                "model_status": flight.get("model_status"),
                "runtime_flight": flight,
                "determinism": _mapping(packed.get("determinism")),
            },
        )

    def _segments(self, flight: Mapping[str, Any]) -> tuple[RouteLayerSegmentV1, ...]:
        raw_legs = _first(flight, ("legs", "segments"), [])
        if not isinstance(raw_legs, (list, tuple)):
            return ()
        out: list[RouteLayerSegmentV1] = []
        for leg in raw_legs:
            if not isinstance(leg, Mapping):
                continue
            if isinstance(leg.get("metric_segment"), Mapping) or isinstance(leg.get("terminal_burn"), Mapping):
                out.extend(self._sequence_h_segments(leg))
                continue
            nested = _first(leg, ("phases", "segments"))
            rows = nested if isinstance(nested, (list, tuple)) and nested else [leg]
            for row in rows:
                if isinstance(row, Mapping):
                    out.append(self._generic_segment(row, leg))
        return tuple(out)

    def _sequence_h_segments(self, leg: Mapping[str, Any]) -> tuple[RouteLayerSegmentV1, ...]:
        metric = _mapping(leg.get("metric_segment"))
        terminal = _mapping(leg.get("terminal_burn"))
        arrival = _mapping(leg.get("arrival"))
        velocity_memory = _mapping(leg.get("ordinary_velocity_memory"))
        checkpoints = self._mapping_list(leg.get("engineering_checkpoints"))
        collapse_epoch = metric.get("collapse_epoch_utc")
        collapse_position = metric.get("collapse_position_km_j2000_ecliptic")
        collapse_anchor = self._position_anchor(collapse_position)
        out: list[RouteLayerSegmentV1] = []

        if metric:
            out.append(RouteLayerSegmentV1(
                type="METRIC",
                start_epoch=leg.get("departure_epoch_utc"),
                end_epoch=collapse_epoch,
                end_position=collapse_anchor,
                geometry={
                    "mode": GEOMETRY_MODE,
                    "coordinate_frame": "J2000_ECLIPTIC",
                    "collapse_position_km": list(collapse_position) if isinstance(collapse_position, (list, tuple)) else collapse_position,
                } if collapse_position is not None else {"mode": GEOMETRY_MODE},
                velocity=velocity_memory,
                acceleration={"engineering_checkpoints": list(checkpoints)} if checkpoints else {},
                phase=str(metric.get("semantics") or leg.get("metric_mode") or "METRIC_TRANSIT"),
                payload={
                    "leg_id": leg.get("leg_id"),
                    "metric_mode": leg.get("metric_mode"),
                    "metric_segment": metric,
                    "ordinary_velocity_memory": velocity_memory,
                    "engineering_checkpoints": list(checkpoints),
                },
            ))

        if terminal:
            terminal_velocity = {
                key: terminal[key]
                for key in ("delta_v_km_s", "delta_v_vec_km_s", "dv_hat", "ve_km_s")
                if terminal.get(key) is not None
            }
            if velocity_memory:
                terminal_velocity["ordinary_velocity_memory"] = velocity_memory
            terminal_acceleration = {
                key: terminal[key]
                for key in ("initial_accel_g", "final_accel_g", "thrust_N", "thrust_MN")
                if terminal.get(key) is not None
            }
            out.append(RouteLayerSegmentV1(
                type="TERMINAL_BURN",
                start_epoch=collapse_epoch,
                end_epoch=arrival.get("epoch_utc"),
                start_position=collapse_anchor,
                geometry={"mode": GEOMETRY_MODE},
                velocity=terminal_velocity,
                acceleration=terminal_acceleration,
                phase="ARRIVAL_ACQUISITION",
                payload={
                    "leg_id": leg.get("leg_id"),
                    "torch_mode": leg.get("torch_mode"),
                    "terminal_burn": terminal,
                    "arrival": arrival,
                },
            ))

        if not out:
            out.append(self._generic_segment(leg, leg))
        return tuple(out)

    def _generic_segment(self, row: Mapping[str, Any], parent: Mapping[str, Any]) -> RouteLayerSegmentV1:
        merged = dict(parent)
        merged.update(row)
        values = {name: _first(merged, aliases) for name, aliases in self.SEGMENT_ALIASES.items()}
        segment_type = values["type"] or values["phase"] or "UNSPECIFIED"
        return RouteLayerSegmentV1(
            type=str(segment_type),
            start_epoch=values["start_epoch"],
            end_epoch=values["end_epoch"],
            start_position=self._as_mapping(values["start_position"]),
            end_position=self._as_mapping(values["end_position"]),
            geometry=self._as_mapping(values["geometry"]),
            velocity=self._as_mapping(values["velocity"]),
            acceleration=self._as_mapping(values["acceleration"]),
            phase=str(values["phase"]) if values["phase"] is not None else None,
            payload=dict(row),
        )

    def _maneuvers(self, flight: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
        explicit = self._mapping_list(_first(flight, ("maneuvers", "events", "maneuver_markers"), []))
        if explicit:
            return explicit
        out: list[Mapping[str, Any]] = []
        for leg in flight.get("legs") or []:
            if not isinstance(leg, Mapping):
                continue
            metric = _mapping(leg.get("metric_segment"))
            terminal = _mapping(leg.get("terminal_burn"))
            arrival = _mapping(leg.get("arrival"))
            if metric.get("collapse_epoch_utc") is not None:
                out.append({
                    "type": "METRIC_COLLAPSE",
                    "leg_id": leg.get("leg_id"),
                    "epoch_utc": metric.get("collapse_epoch_utc"),
                    "position_km_j2000_ecliptic": metric.get("collapse_position_km_j2000_ecliptic"),
                    "metric_mode": leg.get("metric_mode"),
                })
            if terminal:
                out.append({
                    "type": "TERMINAL_BURN",
                    "leg_id": leg.get("leg_id"),
                    "arrival_epoch_utc": arrival.get("epoch_utc"),
                    "burn_s": terminal.get("burn_s"),
                    "delta_v_km_s": terminal.get("delta_v_km_s"),
                    "remass_used_t": terminal.get("remass_used_t"),
                    "torch_mode": leg.get("torch_mode"),
                })
        return tuple(out)

    @staticmethod
    def _position_anchor(value: Any) -> dict[str, Any]:
        if isinstance(value, (list, tuple)):
            return {"coordinate_frame": "J2000_ECLIPTIC", "position_km": list(value)}
        if value is None:
            return {}
        return {"coordinate_frame": "J2000_ECLIPTIC", "position_km": value}

    @staticmethod
    def _as_mapping(value: Any) -> dict[str, Any]:
        if isinstance(value, Mapping):
            return dict(value)
        if isinstance(value, (list, tuple)):
            return {"values": list(value)}
        if value is None:
            return {}
        return {"value": value}

    @staticmethod
    def _mapping_list(value: Any) -> tuple[Mapping[str, Any], ...]:
        if not isinstance(value, (list, tuple)):
            return ()
        return tuple(dict(x) for x in value if isinstance(x, Mapping))

    @staticmethod
    def _arrival_state(plan: FlightPlan, flight: Mapping[str, Any]) -> dict[str, Any]:
        if plan.arrival_state is not None:
            out = dict(plan.arrival_state.payload)
            if plan.arrival_state.epoch_utc is not None:
                out.setdefault("epoch_utc", plan.arrival_state.epoch_utc)
            if plan.arrival_state.location is not None:
                out.setdefault("location", plan.arrival_state.location)
            return out
        mass = _mapping(flight.get("mass_ledger"))
        out: dict[str, Any] = {
            "epoch_utc": _first(flight, ("final_epoch_utc", "arrival_epoch_utc")),
            "location": plan.candidate.destination,
        }
        if mass:
            out["mass_ledger"] = mass
        return {k: v for k, v in out.items() if v is not None}

    @staticmethod
    def _body_refs(origin: str, destination: str) -> tuple[RouteLayerBodyV1, ...]:
        if origin == destination:
            return (RouteLayerBodyV1(origin, role="ORIGIN_DESTINATION"),)
        return (
            RouteLayerBodyV1(origin, role="ORIGIN"),
            RouteLayerBodyV1(destination, role="DESTINATION"),
        )
