"""Canonical typed contracts for the LOOM navigation domain.

These objects deliberately preserve an opaque ``payload`` mapping. During the
Phase-2 extraction the legacy Navigator engine remains authoritative, so the
contracts validate stable cross-domain identity/state while retaining the full
legacy result losslessly. Later phases can promote additional fields without
forcing consumers to couple to legacy dictionary keys.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


class ContractError(ValueError):
    """Raised when a canonical navigation contract is invalid."""


def _text(value: Any, name: str) -> str:
    out = str(value).strip() if value is not None else ""
    if not out:
        raise ContractError(f"{name} is required")
    return out


def _mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _utc_text(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    text = _text(value, name)
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise ContractError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{name} must include timezone")
    return text


@dataclass(frozen=True)
class NavigationRequest:
    origin: str
    destination: str
    priority: str = "BALANCED"
    requested_modes: Mapping[str, Any] = field(default_factory=dict)
    options: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin", _text(self.origin, "origin"))
        object.__setattr__(self, "destination", _text(self.destination, "destination"))
        object.__setattr__(self, "priority", _text(self.priority, "priority").upper())
        object.__setattr__(self, "requested_modes", _mapping(self.requested_modes))
        object.__setattr__(self, "options", _mapping(self.options))
        object.__setattr__(self, "payload", _mapping(self.payload))

    def to_legacy_mission(self) -> dict[str, Any]:
        mission = dict(self.payload)
        mission["route"] = [self.origin, self.destination]
        if self.requested_modes:
            mission["requested_modes"] = dict(self.requested_modes)
        mission.update(self.options)
        return mission


@dataclass(frozen=True)
class NavigationContext:
    campaign_state: Mapping[str, Any]
    acquisition: Any = None
    cache_dir: Any = None
    b1_package: Any = None
    runtime_root: Any = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "campaign_state", _mapping(self.campaign_state))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class RouteCandidate:
    route_id: str
    origin: str
    destination: str
    departure_epoch: str | None = None
    arrival_epoch: str | None = None
    strategy: str | None = None
    status: str = "PLANNED"
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "route_id", _text(self.route_id, "route_id"))
        object.__setattr__(self, "origin", _text(self.origin, "origin"))
        object.__setattr__(self, "destination", _text(self.destination, "destination"))
        object.__setattr__(self, "departure_epoch", _utc_text(self.departure_epoch, "departure_epoch"))
        object.__setattr__(self, "arrival_epoch", _utc_text(self.arrival_epoch, "arrival_epoch"))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class TrajectorySegment:
    segment_type: str
    start_epoch: str | None = None
    end_epoch: str | None = None
    phase: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "segment_type", _text(self.segment_type, "segment_type"))
        object.__setattr__(self, "start_epoch", _utc_text(self.start_epoch, "start_epoch"))
        object.__setattr__(self, "end_epoch", _utc_text(self.end_epoch, "end_epoch"))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class ArrivalState:
    epoch_utc: str | None = None
    location: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "epoch_utc", _utc_text(self.epoch_utc, "epoch_utc"))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class FlightPlan:
    flight_id: str
    candidate: RouteCandidate
    segments: tuple[TrajectorySegment, ...] = ()
    arrival_state: ArrivalState | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "flight_id", _text(self.flight_id, "flight_id"))
        object.__setattr__(self, "segments", tuple(self.segments))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class FlightExecutionResult:
    flight_id: str
    status: str
    final_state: Mapping[str, Any]
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "flight_id", _text(self.flight_id, "flight_id"))
        object.__setattr__(self, "status", _text(self.status, "status"))
        object.__setattr__(self, "final_state", _mapping(self.final_state))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class EphemerisSnapshot:
    epoch_utc: str
    bodies: Mapping[str, Any]
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "epoch_utc", _utc_text(self.epoch_utc, "epoch_utc"))
        object.__setattr__(self, "bodies", _mapping(self.bodies))
        object.__setattr__(self, "payload", _mapping(self.payload))
