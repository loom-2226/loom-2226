"""Typed Stage F-PB contracts for propulsion-regime state continuity.

These contracts do not implement trajectory physics. They preserve the
ordinary-space boundary state produced by an authoritative propagator and keep
natural terminal state, desired terminal state, physical certification and
traffic authorization explicitly separate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from loom.application.contracts import ContractError, SpatialState


CONTRACT_VERSION = "LOOM_F_PB_STATE_CONTINUITY_V1"


class TerminalMatchClass(StrEnum):
    NATURAL_MATCH = "NATURAL_MATCH"
    CORRECTABLE_MATCH = "CORRECTABLE_MATCH"
    REJECTED_MATCH = "REJECTED_MATCH"


class BoundaryStateSemantics(StrEnum):
    NATURAL = "NATURAL"
    DESIRED = "DESIRED"
    CORRECTED = "CORRECTED"


def _required_text(value: Any, name: str) -> str:
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


@dataclass(frozen=True)
class PropulsionBoundaryState:
    """One explicit ordinary-space state at a propulsion/dynamics boundary.

    Metric transit may remain relational/non-occupancy internally, but any
    ordinary acquisition or collapse boundary represented by this contract
    carries a full SpatialState and may not replace it with a semantic location.
    """

    transition_id: str
    semantics: BoundaryStateSemantics | str
    incoming_regime: str
    outgoing_regime: str
    spatial_state: SpatialState
    campaign_revision: int
    solution_id: str
    propagator_id: str
    calibration_id: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    qualification: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "transition_id", _required_text(self.transition_id, "transition_id"))
        try:
            semantics = BoundaryStateSemantics(str(self.semantics))
        except ValueError as exc:
            raise ContractError("semantics must be NATURAL, DESIRED or CORRECTED") from exc
        object.__setattr__(self, "semantics", semantics)
        object.__setattr__(self, "incoming_regime", _required_text(self.incoming_regime, "incoming_regime").upper())
        object.__setattr__(self, "outgoing_regime", _required_text(self.outgoing_regime, "outgoing_regime").upper())
        if not isinstance(self.spatial_state, SpatialState):
            raise ContractError("spatial_state must be SpatialState")
        if isinstance(self.campaign_revision, bool):
            raise ContractError("campaign_revision must be a non-negative integer")
        try:
            revision = int(self.campaign_revision)
        except (TypeError, ValueError) as exc:
            raise ContractError("campaign_revision must be a non-negative integer") from exc
        if revision < 0 or revision != self.campaign_revision:
            raise ContractError("campaign_revision must be a non-negative integer")
        object.__setattr__(self, "campaign_revision", revision)
        object.__setattr__(self, "solution_id", _required_text(self.solution_id, "solution_id"))
        object.__setattr__(self, "propagator_id", _required_text(self.propagator_id, "propagator_id"))
        object.__setattr__(self, "calibration_id", _optional_text(self.calibration_id))
        object.__setattr__(self, "provenance", _mapping(self.provenance))
        object.__setattr__(self, "qualification", _mapping(self.qualification))


@dataclass(frozen=True)
class TerminalStateResidual:
    """Exact ordinary-state mismatch between natural and desired terminal state.

    The states must be expressed at the same epoch and in the same reference
    frame before subtraction is permitted. No implicit transform or retiming is
    performed here.
    """

    natural_state: SpatialState
    desired_state: SpatialState

    def __post_init__(self) -> None:
        if not isinstance(self.natural_state, SpatialState) or not isinstance(self.desired_state, SpatialState):
            raise ContractError("natural_state and desired_state must be SpatialState")
        if self.natural_state.epoch_utc != self.desired_state.epoch_utc:
            raise ContractError("terminal states must share the same epoch before residual calculation")
        if self.natural_state.reference_frame != self.desired_state.reference_frame:
            raise ContractError("terminal states must share the same reference frame before residual calculation")

    @property
    def delta_position_km(self) -> tuple[float, float, float]:
        return tuple(
            desired - natural
            for natural, desired in zip(self.natural_state.position_km, self.desired_state.position_km)
        )  # type: ignore[return-value]

    @property
    def delta_velocity_km_s(self) -> tuple[float, float, float]:
        return tuple(
            desired - natural
            for natural, desired in zip(self.natural_state.velocity_km_s, self.desired_state.velocity_km_s)
        )  # type: ignore[return-value]


@dataclass(frozen=True)
class TerminalStateQualification:
    """Qualification result without conflating physics and traffic permission."""

    match_class: TerminalMatchClass | str
    residual: TerminalStateResidual
    physical_certification_status: str
    traffic_authorization_status: str
    correction_exchange: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            match_class = TerminalMatchClass(str(self.match_class))
        except ValueError as exc:
            raise ContractError("match_class must be NATURAL_MATCH, CORRECTABLE_MATCH or REJECTED_MATCH") from exc
        object.__setattr__(self, "match_class", match_class)
        if not isinstance(self.residual, TerminalStateResidual):
            raise ContractError("residual must be TerminalStateResidual")
        object.__setattr__(
            self,
            "physical_certification_status",
            _required_text(self.physical_certification_status, "physical_certification_status").upper(),
        )
        object.__setattr__(
            self,
            "traffic_authorization_status",
            _required_text(self.traffic_authorization_status, "traffic_authorization_status").upper(),
        )
        object.__setattr__(self, "correction_exchange", _optional_text(self.correction_exchange))
        object.__setattr__(self, "provenance", _mapping(self.provenance))
        object.__setattr__(self, "payload", _mapping(self.payload))
        if match_class == TerminalMatchClass.CORRECTABLE_MATCH and self.correction_exchange is None:
            raise ContractError("CORRECTABLE_MATCH requires an explicit correction_exchange")
