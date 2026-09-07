"""Stage F-PB hostile seam qualification for metric-collapse orbital claims.

This module does not propagate trajectories and does not choose a terminal state.
It checks that a declared terminal-match class is consistent with both the exact
state residual and the ordinary orbital consequence derived from the natural
collapse state.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from loom.application.contracts import ContractError
from loom.physical_state_contracts import TerminalMatchClass, TerminalStateQualification
from loom.spatial.orbit_consequence import OrbitClass, OrbitalConsequence


ORBIT_TERMINAL_QUALIFICATION_VERSION = "LOOM_F_PB_ORBIT_TERMINAL_QUALIFICATION_V1"


class OrbitTerminalQualificationError(ContractError):
    """Raised when a terminal-match claim contradicts its orbital consequence."""


def _norm3(v: tuple[float, float, float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


@dataclass(frozen=True)
class TerminalMatchTolerance:
    """Explicit caller-supplied tolerance; no hidden flight tolerance lives here."""

    max_position_error_km: float
    max_velocity_error_km_s: float

    def __post_init__(self) -> None:
        p = float(self.max_position_error_km)
        v = float(self.max_velocity_error_km_s)
        if not math.isfinite(p) or p < 0.0:
            raise OrbitTerminalQualificationError("max_position_error_km must be finite and non-negative")
        if not math.isfinite(v) or v < 0.0:
            raise OrbitTerminalQualificationError("max_velocity_error_km_s must be finite and non-negative")
        object.__setattr__(self, "max_position_error_km", p)
        object.__setattr__(self, "max_velocity_error_km_s", v)


@dataclass(frozen=True)
class OrbitTerminalQualificationResult:
    claimed_match_class: TerminalMatchClass
    residual_position_km: float
    residual_velocity_km_s: float
    residual_within_tolerance: bool
    actual_orbit_class: OrbitClass
    orbit_class_allowed: bool
    surface_safe: bool | None
    atmosphere_safe: bool | None
    natural_match_physically_consistent: bool


def validate_terminal_match_against_orbit_consequence(
    qualification: TerminalStateQualification,
    consequence: OrbitalConsequence,
    *,
    tolerance: TerminalMatchTolerance,
    accepted_natural_orbit_classes: Iterable[OrbitClass | str],
    prohibit_surface_intersection: bool = True,
    prohibit_atmosphere_intersection: bool = False,
) -> OrbitTerminalQualificationResult:
    """Fail closed if a NATURAL_MATCH claim contradicts exact ordinary physics.

    A requested/desired orbit cannot make the natural collapse state circular,
    bound, or safe by declaration. The orbital consequence must already satisfy
    the allowed class and safety gates, and the exact six-state residual must be
    within the explicit caller-supplied tolerances.

    CORRECTABLE_MATCH and REJECTED_MATCH are not upgraded here. They are merely
    reported; any correction remains owned by an explicit momentum-exchange path.
    """
    if not isinstance(qualification, TerminalStateQualification):
        raise OrbitTerminalQualificationError("qualification must be TerminalStateQualification")
    if not isinstance(consequence, OrbitalConsequence):
        raise OrbitTerminalQualificationError("consequence must be OrbitalConsequence")
    if not isinstance(tolerance, TerminalMatchTolerance):
        raise OrbitTerminalQualificationError("tolerance must be TerminalMatchTolerance")

    # The consequence must have been derived from the exact same natural state
    # that participates in the residual. Identity is intentional: no hidden copy,
    # retiming or frame conversion is accepted at this seam.
    if consequence.state is not qualification.residual.natural_state:
        raise OrbitTerminalQualificationError(
            "orbital consequence must be derived from qualification.residual.natural_state"
        )

    accepted: set[OrbitClass] = set()
    for value in accepted_natural_orbit_classes:
        try:
            accepted.add(value if isinstance(value, OrbitClass) else OrbitClass(str(value)))
        except ValueError as exc:
            raise OrbitTerminalQualificationError(f"unknown accepted orbit class: {value}") from exc
    if not accepted:
        raise OrbitTerminalQualificationError("accepted_natural_orbit_classes may not be empty")

    dp = _norm3(qualification.residual.delta_position_km)
    dv = _norm3(qualification.residual.delta_velocity_km_s)
    residual_ok = dp <= tolerance.max_position_error_km and dv <= tolerance.max_velocity_error_km_s
    orbit_ok = consequence.orbit_class in accepted

    surface_safe = None if consequence.intersects_reference_surface is None else not consequence.intersects_reference_surface
    atmosphere_safe = None if consequence.intersects_atmosphere_interface is None else not consequence.intersects_atmosphere_interface

    safety_ok = True
    if prohibit_surface_intersection:
        safety_ok = surface_safe is True
    if prohibit_atmosphere_intersection:
        safety_ok = safety_ok and atmosphere_safe is True

    natural_consistent = residual_ok and orbit_ok and safety_ok
    if qualification.match_class == TerminalMatchClass.NATURAL_MATCH and not natural_consistent:
        raise OrbitTerminalQualificationError(
            "NATURAL_MATCH contradicts exact terminal residual and/or derived orbital consequence"
        )

    return OrbitTerminalQualificationResult(
        claimed_match_class=qualification.match_class,
        residual_position_km=dp,
        residual_velocity_km_s=dv,
        residual_within_tolerance=residual_ok,
        actual_orbit_class=consequence.orbit_class,
        orbit_class_allowed=orbit_ok,
        surface_safe=surface_safe,
        atmosphere_safe=atmosphere_safe,
        natural_match_physically_consistent=natural_consistent,
    )
