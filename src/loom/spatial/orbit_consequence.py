"""Derive ordinary two-body orbital consequences from one explicit body-relative state.

This is a consequence/qualification layer, not a trajectory propagator. It consumes
an already-resolved body-centered inertial SpatialState plus an explicit GM and
reports what orbit that state actually implies. It never rewrites the input state
or substitutes a requested orbit.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import math
from typing import Any, Mapping, Sequence

from loom.application.contracts import ContractError, SpatialState


ORBIT_CONSEQUENCE_VERSION = "LOOM_F_PB_ORBIT_CONSEQUENCE_V1"


class OrbitClass(StrEnum):
    CIRCULAR = "CIRCULAR"
    ELLIPTIC = "ELLIPTIC"
    PARABOLIC = "PARABOLIC"
    HYPERBOLIC = "HYPERBOLIC"
    RADIAL = "RADIAL"


class OrbitConsequenceError(ContractError):
    """Raised when an orbital consequence cannot be derived safely."""


def _finite_positive(value: float, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out <= 0.0:
        raise OrbitConsequenceError(f"{name} must be finite and greater than zero")
    return out


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    )


@dataclass(frozen=True)
class CentralBodyOrbitContext:
    """Explicit authority needed to interpret a body-relative ordinary state."""

    central_body_id: str
    reference_frame: str
    mu_km3_s2: float
    reference_surface_radius_km: float | None = None
    atmosphere_interface_radius_km: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        body = str(self.central_body_id).strip()
        frame = str(self.reference_frame).strip()
        if not body:
            raise OrbitConsequenceError("central_body_id is required")
        if not frame:
            raise OrbitConsequenceError("reference_frame is required")
        object.__setattr__(self, "central_body_id", body)
        object.__setattr__(self, "reference_frame", frame)
        object.__setattr__(self, "mu_km3_s2", _finite_positive(self.mu_km3_s2, "mu_km3_s2"))
        if self.reference_surface_radius_km is not None:
            object.__setattr__(
                self,
                "reference_surface_radius_km",
                _finite_positive(self.reference_surface_radius_km, "reference_surface_radius_km"),
            )
        if self.atmosphere_interface_radius_km is not None:
            object.__setattr__(
                self,
                "atmosphere_interface_radius_km",
                _finite_positive(self.atmosphere_interface_radius_km, "atmosphere_interface_radius_km"),
            )
        object.__setattr__(self, "provenance", dict(self.provenance))


@dataclass(frozen=True)
class OrbitalConsequence:
    """Two-body osculating consequence of one exact body-relative state."""

    state: SpatialState
    central_body_id: str
    mu_km3_s2: float
    orbit_class: OrbitClass
    radius_km: float
    speed_km_s: float
    radial_velocity_km_s: float
    specific_energy_km2_s2: float
    angular_momentum_km2_s: tuple[float, float, float]
    angular_momentum_magnitude_km2_s: float
    eccentricity_vector: tuple[float, float, float]
    eccentricity: float
    semi_major_axis_km: float | None
    periapsis_radius_km: float | None
    apoapsis_radius_km: float | None
    inclination_deg: float | None
    intersects_reference_surface: bool | None
    intersects_atmosphere_interface: bool | None
    model: str = "TWO_BODY_OSCULATING_FROM_EXACT_STATE"
    provenance: Mapping[str, Any] = field(default_factory=dict)



def derive_orbital_consequence(
    state: SpatialState,
    context: CentralBodyOrbitContext,
    *,
    eccentricity_tolerance: float = 1e-10,
    energy_tolerance_km2_s2: float = 1e-12,
    angular_momentum_tolerance_km2_s: float = 1e-12,
) -> OrbitalConsequence:
    """Return the ordinary orbital consequence of ``state`` under point-mass gravity.

    The caller is responsible for first transforming the ship state into the
    declared body-centered inertial frame. This function refuses hidden frame
    conversion and never infers GM or collision radius from entity names.
    """
    if not isinstance(state, SpatialState):
        raise OrbitConsequenceError("state must be SpatialState")
    if not isinstance(context, CentralBodyOrbitContext):
        raise OrbitConsequenceError("context must be CentralBodyOrbitContext")
    if state.reference_frame != context.reference_frame:
        raise OrbitConsequenceError("state must already be expressed in context.reference_frame")

    r = tuple(float(v) for v in state.position_km)
    v = tuple(float(v) for v in state.velocity_km_s)
    if not all(math.isfinite(x) for x in (*r, *v)):
        raise OrbitConsequenceError("state vectors must be finite")
    rmag = _norm(r)
    if rmag <= 0.0:
        raise OrbitConsequenceError("body-relative radius must be greater than zero")
    vmag = _norm(v)
    mu = context.mu_km3_s2

    h = _cross(r, v)
    hmag = _norm(h)
    radial_velocity = _dot(r, v) / rmag
    energy = 0.5 * vmag * vmag - mu / rmag

    if hmag <= float(angular_momentum_tolerance_km2_s):
        orbit_class = OrbitClass.RADIAL
        evec = (0.0, 0.0, 0.0)
        ecc = 1.0
        semi_major = None if abs(energy) <= energy_tolerance_km2_s2 else -mu / (2.0 * energy)
        periapsis = 0.0
        apoapsis = None
        inclination = None
    else:
        vxh = _cross(v, h)
        evec = tuple(vxh[i] / mu - r[i] / rmag for i in range(3))
        ecc = _norm(evec)
        p = hmag * hmag / mu
        periapsis = p / (1.0 + ecc)
        inclination = math.degrees(math.acos(max(-1.0, min(1.0, h[2] / hmag))))

        if abs(energy) <= float(energy_tolerance_km2_s2):
            orbit_class = OrbitClass.PARABOLIC
            semi_major = None
            apoapsis = None
        elif energy > 0.0:
            orbit_class = OrbitClass.HYPERBOLIC
            semi_major = -mu / (2.0 * energy)
            apoapsis = None
        else:
            semi_major = -mu / (2.0 * energy)
            if ecc <= float(eccentricity_tolerance):
                orbit_class = OrbitClass.CIRCULAR
            else:
                orbit_class = OrbitClass.ELLIPTIC
            apoapsis = semi_major * (1.0 + ecc)

    surface_hit = None
    if context.reference_surface_radius_km is not None and periapsis is not None:
        surface_hit = periapsis <= context.reference_surface_radius_km
    atmosphere_hit = None
    if context.atmosphere_interface_radius_km is not None and periapsis is not None:
        atmosphere_hit = periapsis <= context.atmosphere_interface_radius_km

    return OrbitalConsequence(
        state=state,
        central_body_id=context.central_body_id,
        mu_km3_s2=mu,
        orbit_class=orbit_class,
        radius_km=rmag,
        speed_km_s=vmag,
        radial_velocity_km_s=radial_velocity,
        specific_energy_km2_s2=energy,
        angular_momentum_km2_s=h,
        angular_momentum_magnitude_km2_s=hmag,
        eccentricity_vector=evec,  # type: ignore[arg-type]
        eccentricity=ecc,
        semi_major_axis_km=semi_major,
        periapsis_radius_km=periapsis,
        apoapsis_radius_km=apoapsis,
        inclination_deg=inclination,
        intersects_reference_surface=surface_hit,
        intersects_atmosphere_interface=atmosphere_hit,
        provenance={
            "state_provenance": dict(state.provenance),
            "central_body_context": dict(context.provenance),
            "qualification": "DERIVED_FROM_SUPPLIED_EXACT_STATE_AND_GM",
            "model_limit": "POINT_MASS_TWO_BODY_OSCULATING_CONSEQUENCE",
        },
    )
