from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple

from design_requirements import DoctrineProfile, RequirementsError, ScalarRequirement


SHIP_REQUIREMENTS_ADAPTER_VERSION = "LOOM_SHIP_REQUIREMENTS_ADAPTER_v0.1"


@dataclass(frozen=True)
class ShipMissionRequest:
    cargo_mass_t: Optional[float] = None
    cargo_volume_m3: Optional[float] = None
    passengers: Optional[int] = None
    crew: Optional[int] = None
    endurance_days: Optional[float] = None
    normal_acceleration_g: Optional[float] = None
    emergency_acceleration_g: Optional[float] = None
    delta_v_km_s: Optional[float] = None
    docking_ports: Optional[int] = None
    planetary_landing_required: Optional[bool] = None
    max_dry_mass_t: Optional[float] = None
    max_length_m: Optional[float] = None


def _scalar(
    requirement_id: str,
    value: float,
    unit: str,
    relation: str,
    *,
    provenance: str,
) -> ScalarRequirement:
    return ScalarRequirement(
        requirement_id=requirement_id,
        value=float(value),
        unit=unit,
        relation=relation,
        authority_status="USER_OR_SCENARIO_REQUIREMENT",
        provenance=provenance,
    )


def _count(value: int, label: str) -> int:
    if isinstance(value, bool):
        raise RequirementsError(f"{label} must be an integer count")
    ivalue = int(value)
    if ivalue != value or ivalue < 0:
        raise RequirementsError(f"{label} must be a non-negative integer count")
    return ivalue


def direct_requirements_from_ship_request(
    request: ShipMissionRequest,
    *,
    provenance: str = SHIP_REQUIREMENTS_ADAPTER_VERSION,
) -> Tuple[ScalarRequirement, ...]:
    """Translate a human/domain ship request into direct solver-facing demands.

    This adapter performs no hidden engineering conversion. Passenger count remains
    passenger count, cargo mass remains cargo mass, etc. Downstream derivation rules
    are responsible for turning those demands into physical engineering requirements.
    """

    rows = []
    numeric_specs = (
        ("ship.cargo_mass", request.cargo_mass_t, "t", "MIN"),
        ("ship.cargo_volume", request.cargo_volume_m3, "m3", "MIN"),
        ("ship.endurance", request.endurance_days, "day", "MIN"),
        ("ship.normal_acceleration", request.normal_acceleration_g, "g", "MIN"),
        ("ship.emergency_acceleration", request.emergency_acceleration_g, "g", "MIN"),
        ("ship.delta_v", request.delta_v_km_s, "km/s", "MIN"),
        ("ship.max_dry_mass", request.max_dry_mass_t, "t", "MAX"),
        ("ship.max_length", request.max_length_m, "m", "MAX"),
    )
    for requirement_id, value, unit, relation in numeric_specs:
        if value is not None:
            rows.append(_scalar(requirement_id, float(value), unit, relation, provenance=provenance))

    if request.passengers is not None:
        rows.append(
            _scalar(
                "ship.passengers",
                _count(request.passengers, "passengers"),
                "count",
                "MIN",
                provenance=provenance,
            )
        )
    if request.crew is not None:
        rows.append(
            _scalar(
                "ship.crew",
                _count(request.crew, "crew"),
                "count",
                "MIN",
                provenance=provenance,
            )
        )
    if request.docking_ports is not None:
        rows.append(
            _scalar(
                "ship.docking_ports",
                _count(request.docking_ports, "docking_ports"),
                "count",
                "MIN",
                provenance=provenance,
            )
        )
    if request.planetary_landing_required is not None:
        rows.append(
            _scalar(
                "ship.planetary_landing_required",
                1.0 if request.planetary_landing_required else 0.0,
                "bool",
                "EXACT",
                provenance=provenance,
            )
        )

    if not rows:
        raise RequirementsError("ShipMissionRequest must contain at least one explicit requirement")
    return tuple(rows)


def doctrine_profile(
    doctrine_id: str,
    *,
    objective_priority: Sequence[str],
    required_capabilities: Sequence[str] = (),
    authority_status: str = "QUALIFICATION_ONLY",
    provenance: str = SHIP_REQUIREMENTS_ADAPTER_VERSION,
) -> DoctrineProfile:
    """Create a ship doctrine profile without baking named ship classes into core code."""

    return DoctrineProfile(
        doctrine_id=str(doctrine_id),
        objective_priority=tuple(str(v) for v in objective_priority),
        required_capabilities=tuple(str(v) for v in required_capabilities),
        authority_status=authority_status,
        provenance=provenance,
    )
