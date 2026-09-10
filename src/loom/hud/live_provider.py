from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import os

from loom.application.contracts import CampaignClockState, SpatialState
from loom.campaign.clock import LegacyCampaignClockService
from loom.runtime import resolve_runtime_roots
from loom.spatial.sqlite_source import CANONICAL_FRAME, SQLiteSpatialStateSource


LIVE_VIEW_CONTRACT = "LOOM_HUD_LIVE_FLIGHT_VIEW_V1"


class LiveFlightViewError(RuntimeError):
    """Raised when a live HUD view cannot be resolved without inventing state."""


def _vec3(value: Any) -> tuple[float, float, float] | None:
    if isinstance(value, Mapping):
        for key in ("position_km", "velocity_km_s", "values"):
            if key in value:
                value = value[key]
                break
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        return None
    try:
        return (float(value[0]), float(value[1]), float(value[2]))
    except (TypeError, ValueError):
        return None


def _candidate_ownship_ids(state: Mapping[str, Any]) -> tuple[str, ...]:
    out: list[str] = []
    env_id = str(os.environ.get("LOOM_HUD_OWNSHIP_ID") or "").strip()
    if env_id:
        out.append(env_id)
    for node in (state, state.get("current_vehicle_state") or {}, state.get("last_flight") or {}):
        if not isinstance(node, Mapping):
            continue
        for key in ("entity_id", "vehicle_id", "ship_id"):
            value = str(node.get(key) or "").strip()
            if value and value not in out:
                out.append(value)
    if "WAYFARER" not in out:
        out.append("WAYFARER")
    return tuple(out)


def _explicit_ownship_from_campaign(state: Mapping[str, Any], clock: CampaignClockState) -> SpatialState | None:
    candidates: list[Mapping[str, Any]] = []
    for node in (
        state.get("current_vehicle_state"),
        state.get("vehicle_state"),
        state.get("ship_state"),
    ):
        if isinstance(node, Mapping):
            candidates.append(node)
    last = state.get("last_flight")
    if isinstance(last, Mapping):
        for node in (last.get("current_vehicle_state"), last.get("arrival_state")):
            if isinstance(node, Mapping):
                candidates.append(node)

    for node in candidates:
        pos = _vec3(node.get("position_km"))
        vel = _vec3(node.get("velocity_km_s"))
        epoch = str(node.get("epoch_utc") or "").strip()
        frame = str(node.get("reference_frame") or node.get("frame") or "").strip()
        entity_id = str(node.get("entity_id") or node.get("vehicle_id") or node.get("ship_id") or "").strip()
        if not (pos and vel and epoch and frame and entity_id):
            continue
        if epoch != clock.epoch_utc:
            continue
        return SpatialState(
            entity_id=entity_id,
            epoch_utc=epoch,
            reference_frame=frame,
            position_km=pos,
            velocity_km_s=vel,
            orientation=node.get("orientation") or {},
            provenance={"state_source": "CAMPAIGN_JSON_EXPLICIT_VEHICLE_STATE"},
            navigation_grade=node.get("navigation_grade"),
            payload={"state_class": "VEHICLE", "name": node.get("name") or entity_id},
        )
    return None


def _camera_quaternion_from_orientation(orientation: Mapping[str, Any]) -> tuple[float, float, float, float] | None:
    for key in ("camera_from_inertial_xyzw", "body_from_inertial_xyzw", "quaternion_xyzw"):
        value = orientation.get(key)
        if isinstance(value, (list, tuple)) and len(value) == 4:
            try:
                q = tuple(float(v) for v in value)
            except (TypeError, ValueError):
                continue
            if any(q):
                return q  # type: ignore[return-value]
    return None


def build_live_view_from_states(
    *,
    clock: CampaignClockState,
    campaign_state: Mapping[str, Any],
    states: Sequence[SpatialState],
) -> dict[str, Any]:
    """Build a read-only HUD payload from already-resolved spatial states.

    This function does no propagation, interpolation, endpoint invention or body-
    center substitution. It requires an explicit ownship 6D state at the current
    campaign epoch and keeps missing attitude explicit.
    """
    if not states:
        raise LiveFlightViewError("no spatial states exist at the campaign epoch")

    ownship = _explicit_ownship_from_campaign(campaign_state, clock)
    by_id = {state.entity_id: state for state in states}
    if ownship is None:
        for entity_id in _candidate_ownship_ids(campaign_state):
            candidate = by_id.get(entity_id)
            if candidate is not None:
                ownship = candidate
                break
    if ownship is None:
        raise LiveFlightViewError(
            "authoritative ownship 6D state unavailable; refusing to place Wayfarer at a body/station by inference"
        )
    if ownship.epoch_utc != clock.epoch_utc:
        raise LiveFlightViewError("ownship epoch differs from campaign epoch")

    frame = ownship.reference_frame
    mismatched = [s.entity_id for s in states if s.reference_frame != frame]
    if mismatched:
        raise LiveFlightViewError(
            "live scene contains mixed frames; normalize upstream before HUD consumption"
        )

    q = _camera_quaternion_from_orientation(ownship.orientation)
    camera_status = "AVAILABLE" if q is not None else "UNAVAILABLE"
    # Identity is only an explicitly labeled inertial debug camera when attitude
    # authority is absent. It must never be described as ship-forward.
    camera_q = q or (0.0, 0.0, 0.0, 1.0)

    objects = []
    for state in states:
        if state.entity_id == ownship.entity_id:
            continue
        objects.append({
            "object_id": state.entity_id,
            "label": str(state.payload.get("name") or state.entity_id),
            "object_type": str(state.payload.get("state_class") or "UNKNOWN"),
            "position_km": list(state.position_km),
            "velocity_km_s": list(state.velocity_km_s),
            "navigation_grade": state.navigation_grade,
            "provenance": dict(state.provenance),
            "payload": dict(state.payload),
        })

    return {
        "contract": LIVE_VIEW_CONTRACT,
        "status": "LIVE" if q is not None else "PARTIAL",
        "authority": "CANONICAL_SPATIAL_STATE",
        "epoch_utc": clock.epoch_utc,
        "campaign_revision": clock.revision,
        "inertial_frame": frame,
        "ownship": {
            "entity_id": ownship.entity_id,
            "position_km": list(ownship.position_km),
            "velocity_km_s": list(ownship.velocity_km_s),
            "navigation_grade": ownship.navigation_grade,
            "orientation": dict(ownship.orientation),
            "provenance": dict(ownship.provenance),
        },
        "camera": {
            "status": camera_status,
            "camera_from_inertial_xyzw": list(camera_q),
            "semantics": "SHIP_FORWARD" if q is not None else "INERTIAL_DEBUG_NOT_SHIP_FORWARD",
        },
        "objects": objects,
        "source": {
            "campaign": "LOOM_STATE_V1.json",
            "spatial": "SQLiteSpatialStateSource",
            "mode": "READ_ONLY",
        },
    }


def load_live_flight_view(*, data_root: Path | str | None = None, campaign_root: Path | str | None = None) -> dict[str, Any]:
    roots = resolve_runtime_roots(data_root=data_root, campaign_root=campaign_root)
    campaign_service = LegacyCampaignClockService(roots.campaign_root)
    clock = campaign_service.now()
    state = json.loads(campaign_service.state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise LiveFlightViewError("canonical campaign state must be a JSON object")
    db_path = Path(os.environ.get("LOOM_SPATIAL_DB") or (roots.data_root / "LOOM_2226.sqlite3"))
    states = SQLiteSpatialStateSource(db_path).states_at(clock.epoch_utc)
    return build_live_view_from_states(clock=clock, campaign_state=state, states=states)


def unavailable_live_payload(exc: Exception) -> dict[str, Any]:
    return {
        "contract": LIVE_VIEW_CONTRACT,
        "status": "UNAVAILABLE",
        "authority": "UNAVAILABLE",
        "reason": str(exc),
        "objects": [],
        "source": {"mode": "READ_ONLY"},
    }
