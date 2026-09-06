"""Canonical cross-application contracts for LOOM 2226 next-phase runtime.

These contracts sit above persistence and presentation. They are deliberately
small, typed, and serialization-friendly so Campaign, Navigator, GIS, HUD, and
future conversational clients can exchange stable application state without
coupling to a particular database or UI payload.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Sequence


class ContractError(ValueError):
    """Raised when a canonical application contract is invalid."""


def _text(value: Any, name: str) -> str:
    out = str(value).strip() if value is not None else ""
    if not out:
        raise ContractError(f"{name} is required")
    return out


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    out = str(value).strip()
    return out or None


def _mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _utc_text(value: str, name: str) -> str:
    text = _text(value, name)
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise ContractError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{name} must include timezone")
    return text


def _vec3(value: Sequence[float], name: str) -> tuple[float, float, float]:
    try:
        out = tuple(float(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{name} must contain three numeric values") from exc
    if len(out) != 3:
        raise ContractError(f"{name} must contain exactly three values")
    return out  # type: ignore[return-value]


def _revision(value: int, name: str = "revision") -> int:
    if isinstance(value, bool):
        raise ContractError(f"{name} must be a non-negative integer")
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{name} must be a non-negative integer") from exc
    if out < 0 or out != value:
        raise ContractError(f"{name} must be a non-negative integer")
    return out


@dataclass(frozen=True)
class CampaignClockState:
    """Authoritative campaign time/revision snapshot.

    Playback and historical query cursors must never be substituted for this
    value. Persistence may remain JSON/history or later promote to SQLite;
    consumers only depend on this contract.
    """

    campaign_id: str
    revision: int
    epoch_utc: str
    last_transition_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "campaign_id", _text(self.campaign_id, "campaign_id"))
        object.__setattr__(self, "revision", _revision(self.revision))
        object.__setattr__(self, "epoch_utc", _utc_text(self.epoch_utc, "epoch_utc"))
        object.__setattr__(self, "last_transition_id", _optional_text(self.last_transition_id))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class SpatialState:
    """Physical state of one entity at one epoch in an explicit frame."""

    entity_id: str
    epoch_utc: str
    reference_frame: str
    position_km: Sequence[float]
    velocity_km_s: Sequence[float]
    orientation: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    navigation_grade: bool | None = None
    uncertainty: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entity_id", _text(self.entity_id, "entity_id"))
        object.__setattr__(self, "epoch_utc", _utc_text(self.epoch_utc, "epoch_utc"))
        object.__setattr__(self, "reference_frame", _text(self.reference_frame, "reference_frame"))
        object.__setattr__(self, "position_km", _vec3(self.position_km, "position_km"))
        object.__setattr__(self, "velocity_km_s", _vec3(self.velocity_km_s, "velocity_km_s"))
        object.__setattr__(self, "orientation", _mapping(self.orientation))
        object.__setattr__(self, "provenance", _mapping(self.provenance))
        object.__setattr__(self, "uncertainty", _mapping(self.uncertainty))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class TrajectorySegment:
    """One time-bounded portion of a solved physical trajectory."""

    segment_id: str
    segment_type: str
    start_epoch: str
    end_epoch: str
    propulsion_regime: str | None = None
    start_state: SpatialState | None = None
    end_state: SpatialState | None = None
    samples: tuple[SpatialState, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "segment_id", _text(self.segment_id, "segment_id"))
        object.__setattr__(self, "segment_type", _text(self.segment_type, "segment_type"))
        object.__setattr__(self, "start_epoch", _utc_text(self.start_epoch, "start_epoch"))
        object.__setattr__(self, "end_epoch", _utc_text(self.end_epoch, "end_epoch"))
        object.__setattr__(self, "propulsion_regime", _optional_text(self.propulsion_regime))
        object.__setattr__(self, "samples", tuple(self.samples))
        object.__setattr__(self, "payload", _mapping(self.payload))
        if datetime.fromisoformat(self.end_epoch.replace("Z", "+00:00")) < datetime.fromisoformat(self.start_epoch.replace("Z", "+00:00")):
            raise ContractError("end_epoch must not precede start_epoch")


@dataclass(frozen=True)
class TrajectorySolution:
    """Campaign-stamped 3D trajectory solution.

    The solution becomes stale when its campaign revision/solution epoch no
    longer matches the authoritative planning context unless explicitly
    revalidated by Navigator.
    """

    trajectory_id: str
    campaign_revision: int
    solution_epoch: str
    origin: str
    destination: str
    reference_frame: str
    departure_epoch: str
    arrival_epoch: str
    segments: tuple[TrajectorySegment, ...] = ()
    qualification: Mapping[str, Any] = field(default_factory=dict)
    costs: Mapping[str, Any] = field(default_factory=dict)
    risk: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "trajectory_id", _text(self.trajectory_id, "trajectory_id"))
        object.__setattr__(self, "campaign_revision", _revision(self.campaign_revision, "campaign_revision"))
        object.__setattr__(self, "solution_epoch", _utc_text(self.solution_epoch, "solution_epoch"))
        object.__setattr__(self, "origin", _text(self.origin, "origin"))
        object.__setattr__(self, "destination", _text(self.destination, "destination"))
        object.__setattr__(self, "reference_frame", _text(self.reference_frame, "reference_frame"))
        object.__setattr__(self, "departure_epoch", _utc_text(self.departure_epoch, "departure_epoch"))
        object.__setattr__(self, "arrival_epoch", _utc_text(self.arrival_epoch, "arrival_epoch"))
        object.__setattr__(self, "segments", tuple(self.segments))
        object.__setattr__(self, "qualification", _mapping(self.qualification))
        object.__setattr__(self, "costs", _mapping(self.costs))
        object.__setattr__(self, "risk", _mapping(self.risk))
        object.__setattr__(self, "provenance", _mapping(self.provenance))
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class LoomRouteSolution:
    """Relational Loom solution, intentionally distinct from metric trajectory."""

    route_id: str
    campaign_revision: int
    solution_epoch: str
    source_domain: str
    destination_domain: str
    relational_edges: tuple[Mapping[str, Any], ...] = ()
    solution_confidence: float | None = None
    directionality: str | None = None
    endpoint_geometry: Mapping[str, Any] = field(default_factory=dict)
    timing: Mapping[str, Any] = field(default_factory=dict)
    terminal_state: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "route_id", _text(self.route_id, "route_id"))
        object.__setattr__(self, "campaign_revision", _revision(self.campaign_revision, "campaign_revision"))
        object.__setattr__(self, "solution_epoch", _utc_text(self.solution_epoch, "solution_epoch"))
        object.__setattr__(self, "source_domain", _text(self.source_domain, "source_domain"))
        object.__setattr__(self, "destination_domain", _text(self.destination_domain, "destination_domain"))
        object.__setattr__(self, "relational_edges", tuple(_mapping(edge) for edge in self.relational_edges))
        object.__setattr__(self, "directionality", _optional_text(self.directionality))
        object.__setattr__(self, "endpoint_geometry", _mapping(self.endpoint_geometry))
        object.__setattr__(self, "timing", _mapping(self.timing))
        object.__setattr__(self, "terminal_state", _mapping(self.terminal_state))
        object.__setattr__(self, "payload", _mapping(self.payload))
        if self.solution_confidence is not None:
            confidence = float(self.solution_confidence)
            if not 0.0 <= confidence <= 1.0:
                raise ContractError("solution_confidence must be between 0 and 1")
            object.__setattr__(self, "solution_confidence", confidence)


@dataclass(frozen=True)
class FlightPlaybackState:
    """Non-authoritative animation/replay cursor over an authoritative flight."""

    flight_id: str
    trajectory_id: str
    authoritative_start_epoch: str
    authoritative_end_epoch: str
    cursor_epoch: str
    playback_rate: float = 1.0
    camera_mode: str = "SYSTEM"
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "flight_id", _text(self.flight_id, "flight_id"))
        object.__setattr__(self, "trajectory_id", _text(self.trajectory_id, "trajectory_id"))
        object.__setattr__(self, "authoritative_start_epoch", _utc_text(self.authoritative_start_epoch, "authoritative_start_epoch"))
        object.__setattr__(self, "authoritative_end_epoch", _utc_text(self.authoritative_end_epoch, "authoritative_end_epoch"))
        object.__setattr__(self, "cursor_epoch", _utc_text(self.cursor_epoch, "cursor_epoch"))
        rate = float(self.playback_rate)
        if rate <= 0:
            raise ContractError("playback_rate must be greater than zero")
        object.__setattr__(self, "playback_rate", rate)
        object.__setattr__(self, "camera_mode", _text(self.camera_mode, "camera_mode").upper())
        object.__setattr__(self, "payload", _mapping(self.payload))


@dataclass(frozen=True)
class LoomSessionState:
    """Durable application-session identity shared by UI/LLM clients.

    This is not campaign authority. It links conversational/application context
    to a specific campaign revision and epoch without owning either.
    """

    session_id: str
    campaign_id: str
    campaign_revision: int
    epoch_utc: str
    selected_entity_id: str | None = None
    conversation_refs: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", _text(self.session_id, "session_id"))
        object.__setattr__(self, "campaign_id", _text(self.campaign_id, "campaign_id"))
        object.__setattr__(self, "campaign_revision", _revision(self.campaign_revision, "campaign_revision"))
        object.__setattr__(self, "epoch_utc", _utc_text(self.epoch_utc, "epoch_utc"))
        object.__setattr__(self, "selected_entity_id", _optional_text(self.selected_entity_id))
        object.__setattr__(self, "conversation_refs", tuple(_text(v, "conversation_ref") for v in self.conversation_refs))
        object.__setattr__(self, "payload", _mapping(self.payload))
