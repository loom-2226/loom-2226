"""Adapter from accepted Navigator route output to cross-application trajectory state.

E1 is deliberately representation-only. Navigator and Sequence-B remain physics
authority; this module does no trajectory math, interpolation, propagation, or
campaign mutation. It converts the established ``LOOM_ROUTE_LAYER_V1`` boundary
into the canonical application ``TrajectorySolution`` contract so GIS, HUD,
playback, and future conversational clients can consume one typed shape.

Metric/relational samples are never assigned invented ordinary-space positions.
Their authoritative timeline rows remain attached as segment payload metadata,
while ``SpatialState`` samples are emitted only when Sequence-B supplies a
complete ordinary position and velocity.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
import hashlib
from typing import Any

from loom.application import SpatialState, TrajectorySegment, TrajectorySolution

from .contracts import FlightPlan, NavigationContext
from .route_layer import LegacyRouteLayerAdapter, LoomRouteLayerV1, ROUTE_LAYER_VERSION

TRAJECTORY_PACKET_ADAPTER_VERSION = "LOOM_TRAJECTORY_PACKET_ADAPTER_E1_V1"


class TrajectoryPacketAdapterError(ValueError):
    """Raised when authoritative Navigator output cannot form an E1 packet."""


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _utc(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise TrajectoryPacketAdapterError(f"{name} is required")
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise TrajectoryPacketAdapterError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise TrajectoryPacketAdapterError(f"{name} must include timezone")
    return text


def _revision(value: Any) -> int:
    if isinstance(value, bool):
        raise TrajectoryPacketAdapterError("campaign revision must be a non-negative integer")
    try:
        revision = int(value)
    except (TypeError, ValueError) as exc:
        raise TrajectoryPacketAdapterError("campaign revision must be a non-negative integer") from exc
    if revision < 0 or revision != value:
        raise TrajectoryPacketAdapterError("campaign revision must be a non-negative integer")
    return revision


def _complete_vec3(row: Mapping[str, Any], keys: tuple[str, str, str]) -> tuple[float, float, float] | None:
    values = tuple(row.get(key) for key in keys)
    if any(value is None for value in values):
        return None
    try:
        return tuple(float(value) for value in values)  # type: ignore[return-value]
    except (TypeError, ValueError):
        return None


def _ordinary_state(row: Mapping[str, Any], *, reference_frame: str, entity_id: str) -> SpatialState | None:
    position = _complete_vec3(
        row,
        ("ordinary_pos_x_km", "ordinary_pos_y_km", "ordinary_pos_z_km"),
    )
    velocity = _complete_vec3(
        row,
        ("ordinary_vel_x_km_s", "ordinary_vel_y_km_s", "ordinary_vel_z_km_s"),
    )
    if position is None or velocity is None or row.get("epoch_utc") is None:
        return None
    return SpatialState(
        entity_id=entity_id,
        epoch_utc=_utc(row.get("epoch_utc"), "trajectory sample epoch_utc"),
        reference_frame=reference_frame,
        position_km=position,
        velocity_km_s=velocity,
        provenance={
            "authority": "PYTHON_AUTHORED_SEQUENCE_B",
            "adapter": TRAJECTORY_PACKET_ADAPTER_VERSION,
        },
        payload=dict(row),
    )


def _phase_groups(rows: Sequence[Mapping[str, Any]]) -> tuple[tuple[Mapping[str, Any], ...], ...]:
    groups: list[list[Mapping[str, Any]]] = []
    current: list[Mapping[str, Any]] = []
    current_phase: Any = object()
    for row in rows:
        phase = row.get("phase_code")
        if current and phase != current_phase:
            groups.append(current)
            current = []
        current.append(row)
        current_phase = phase
    if current:
        groups.append(current)
    return tuple(tuple(group) for group in groups)


def trajectory_solution_from_route_layer(
    layer: LoomRouteLayerV1,
    *,
    campaign_revision: int,
    solution_epoch: str | None = None,
    ship_entity_id: str = "SHIP",
) -> TrajectorySolution:
    """Promote one accepted route layer into a canonical trajectory solution.

    This is an anti-corruption boundary, not a solver. Missing authoritative
    Sequence-B timeline data is an error rather than an invitation to synthesize
    geometry.
    """
    if layer.contract != ROUTE_LAYER_VERSION:
        raise TrajectoryPacketAdapterError(f"unsupported route layer contract: {layer.contract}")

    trajectory = _mapping(layer.payload.get("trajectory"))
    raw_rows = trajectory.get("samples")
    if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, (str, bytes, bytearray)) or not raw_rows:
        raise TrajectoryPacketAdapterError("route layer has no authoritative Sequence-B trajectory samples")
    rows = tuple(dict(row) for row in raw_rows if isinstance(row, Mapping))
    if not rows:
        raise TrajectoryPacketAdapterError("route layer trajectory contains no mapping samples")

    reference_frame = str(trajectory.get("coordinate_frame") or "").strip()
    if not reference_frame:
        raise TrajectoryPacketAdapterError("trajectory coordinate_frame is required")

    departure_epoch = _utc(layer.departure_epoch or rows[0].get("epoch_utc"), "departure_epoch")
    arrival_epoch = _utc(layer.arrival_epoch or rows[-1].get("epoch_utc"), "arrival_epoch")
    solved_epoch = _utc(solution_epoch or departure_epoch, "solution_epoch")
    revision = _revision(campaign_revision)

    segments: list[TrajectorySegment] = []
    for index, group in enumerate(_phase_groups(rows)):
        first = group[0]
        last = group[-1]
        start_epoch = _utc(first.get("epoch_utc"), f"segment[{index}].start_epoch")
        end_epoch = _utc(last.get("epoch_utc"), f"segment[{index}].end_epoch")
        phase = str(first.get("phase_code") or "UNSPECIFIED").strip() or "UNSPECIFIED"
        states = tuple(
            state
            for state in (
                _ordinary_state(row, reference_frame=reference_frame, entity_id=ship_entity_id)
                for row in group
            )
            if state is not None
        )
        segments.append(
            TrajectorySegment(
                segment_id=f"{layer.flight_id}:{index:03d}",
                segment_type=phase,
                start_epoch=start_epoch,
                end_epoch=end_epoch,
                start_state=states[0] if states else None,
                end_state=states[-1] if states else None,
                samples=states,
                payload={
                    "source_timeline_rows": tuple(dict(row) for row in group),
                    "ordinary_space_samples_available": bool(states),
                    "metric_semantics": trajectory.get("metric_semantics"),
                    "ordinary_semantics": trajectory.get("ordinary_semantics"),
                },
            )
        )

    identity = f"{layer.flight_id}|{layer.route_id}|{revision}|{solved_epoch}".encode("utf-8")
    trajectory_id = "traj-" + hashlib.sha256(identity).hexdigest()[:20]
    provenance = {
        "authority": trajectory.get("authority") or "PYTHON_AUTHORED_SEQUENCE_B",
        "adapter": TRAJECTORY_PACKET_ADAPTER_VERSION,
        "source_route_layer_contract": layer.contract,
        "source_route_layer_sha256": layer.sha256(),
        "renderer_rule": trajectory.get("renderer_rule"),
        "geometry_mode": layer.payload.get("geometry_mode"),
        "flight_id": layer.flight_id,
        "route_id": layer.route_id,
    }

    return TrajectorySolution(
        trajectory_id=trajectory_id,
        campaign_revision=revision,
        solution_epoch=solved_epoch,
        origin=layer.origin,
        destination=layer.destination,
        reference_frame=reference_frame,
        departure_epoch=departure_epoch,
        arrival_epoch=arrival_epoch,
        segments=tuple(segments),
        provenance=provenance,
        payload={
            "adapter_contract": TRAJECTORY_PACKET_ADAPTER_VERSION,
            "events": tuple(trajectory.get("events") or ()),
            "route_plan_id": trajectory.get("route_plan_id"),
            "solution_key": trajectory.get("solution_key"),
            "sample_count": trajectory.get("sample_count"),
        },
    )


def trajectory_solution_from_flight_plan(
    plan: FlightPlan,
    context: NavigationContext,
    *,
    route_adapter: LegacyRouteLayerAdapter | None = None,
    ship_entity_id: str = "SHIP",
) -> TrajectorySolution:
    """Build the route layer through the accepted adapter, then promote E1 state."""
    campaign = dict(context.campaign_state)
    if "revision" not in campaign:
        raise TrajectoryPacketAdapterError("campaign state revision is required")
    epoch = campaign.get("epoch_utc") or plan.candidate.departure_epoch
    if epoch is None:
        raise TrajectoryPacketAdapterError("campaign/solution epoch is required")
    layer = (route_adapter or LegacyRouteLayerAdapter()).build(plan, context)
    return trajectory_solution_from_route_layer(
        layer,
        campaign_revision=campaign["revision"],
        solution_epoch=str(epoch),
        ship_entity_id=ship_entity_id,
    )
