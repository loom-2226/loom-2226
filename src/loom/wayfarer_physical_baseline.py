"""Typed bridge from the governed Wayfarer geometry system into simulator contracts.

The geometry compiler remains the dimensional source. This module consumes its
LOOM.Wayfarer.Geometry payload and exposes only values needed for vehicle-state
and frame work while preserving provenance/status. It never promotes DESIGN_BASELINE
or OPEN geometry to canon/navigation authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math
from typing import Any, Mapping, Sequence


WAYFARER_PHYSICAL_BASELINE_VERSION = "LOOM_F_PB_WAYFARER_PHYSICAL_BASELINE_V1"
EXPECTED_SCHEMA = "LOOM.Wayfarer.Geometry"
EXPECTED_SCHEMA_VERSION = "0.1"


class BaselineStatus(StrEnum):
    CANON = "CANON"
    DESIGN_BASELINE = "DESIGN_BASELINE"
    DERIVED = "DERIVED"
    LEGACY_COMPATIBLE = "LEGACY_COMPATIBLE"
    VISUAL_REFERENCE = "VISUAL_REFERENCE"
    OPEN = "OPEN"
    CANON_MASS_DESIGN_POSITION = "CANON_MASS_DESIGN_POSITION"


class WayfarerBaselineError(ValueError):
    pass


@dataclass(frozen=True)
class QualifiedScalar:
    value: float
    unit: str | None
    status: BaselineStatus
    source: str


@dataclass(frozen=True)
class WayfarerBodyFrame:
    frame_id: str
    origin_description: str
    x_axis_description: str
    y_axis_description: str
    z_axis_description: str


@dataclass(frozen=True)
class WayfarerMassState:
    configuration: str
    dry_mass_t: float
    wet_mass_t: float
    dry_com_m: tuple[float, float, float]
    wet_com_m: tuple[float, float, float]


@dataclass(frozen=True)
class WayfarerPhysicalBaseline:
    body_frame: WayfarerBodyFrame
    length_m: QualifiedScalar
    main_body_diameter_m: QualifiedScalar
    docking_collar_center_m: tuple[float, float, float]
    docking_geometry_status: BaselineStatus
    launch_bay_center_m: tuple[float, float, float]
    launch_geometry_status: BaselineStatus
    docked_mass: WayfarerMassState
    launch_absent_mass: WayfarerMassState
    launch_states: tuple[str, ...]
    radiator_states: tuple[str, ...]
    docking_states: tuple[str, ...]
    torch_states: tuple[str, ...]


def _vec3(value: Sequence[Any], name: str) -> tuple[float, float, float]:
    if len(value) != 3:
        raise WayfarerBaselineError(f"{name} must contain three values")
    out = tuple(float(v) for v in value)
    if not all(math.isfinite(v) for v in out):
        raise WayfarerBaselineError(f"{name} must contain finite values")
    return out  # type: ignore[return-value]


def _parameter(parameters: Mapping[str, Any], key: str) -> QualifiedScalar:
    try:
        raw = parameters[key]
    except KeyError as exc:
        raise WayfarerBaselineError(f"missing geometry parameter {key}") from exc
    try:
        status = BaselineStatus(str(raw["status"]))
        value = float(raw["value"])
    except (KeyError, TypeError, ValueError) as exc:
        raise WayfarerBaselineError(f"invalid geometry parameter {key}") from exc
    if not math.isfinite(value):
        raise WayfarerBaselineError(f"non-finite geometry parameter {key}")
    return QualifiedScalar(value=value, unit=raw.get("unit"), status=status, source=str(raw.get("source") or key))


def _component(components: Sequence[Mapping[str, Any]], component_id: str) -> Mapping[str, Any]:
    matches = [c for c in components if c.get("id") == component_id]
    if len(matches) != 1:
        raise WayfarerBaselineError(f"expected exactly one component {component_id}")
    return matches[0]


def _mass_state(raw: Mapping[str, Any], configuration: str) -> WayfarerMassState:
    dry_mass = float(raw["dry_mass_t"])
    wet_mass = float(raw["wet_mass_t"])
    if not all(math.isfinite(v) and v > 0.0 for v in (dry_mass, wet_mass)):
        raise WayfarerBaselineError(f"invalid {configuration} mass state")
    if wet_mass < dry_mass:
        raise WayfarerBaselineError(f"{configuration} wet mass cannot be below dry mass")
    return WayfarerMassState(
        configuration=configuration,
        dry_mass_t=dry_mass,
        wet_mass_t=wet_mass,
        dry_com_m=_vec3(raw["dry_com_m"], f"{configuration}.dry_com_m"),
        wet_com_m=_vec3(raw["wet_com_m"], f"{configuration}.wet_com_m"),
    )


def baseline_from_geometry_payload(payload: Mapping[str, Any]) -> WayfarerPhysicalBaseline:
    """Validate and extract the simulator-facing Wayfarer dimensional baseline."""
    if payload.get("schema") != EXPECTED_SCHEMA or str(payload.get("schema_version")) != EXPECTED_SCHEMA_VERSION:
        raise WayfarerBaselineError("unsupported Wayfarer geometry schema")

    coordinate = payload.get("coordinate_system")
    if not isinstance(coordinate, Mapping):
        raise WayfarerBaselineError("missing coordinate_system")
    x_desc = str(coordinate.get("x") or "")
    y_desc = str(coordinate.get("y") or "")
    z_desc = str(coordinate.get("z") or "")
    if "bow datum x=0 m" not in x_desc or "+Z launch-bay side" not in z_desc or "-Z docking side" not in z_desc:
        raise WayfarerBaselineError("Wayfarer body-frame convention does not match governed geometry baseline")

    parameters = payload.get("parameters")
    components = payload.get("components")
    mass_states = payload.get("mass_states")
    states = payload.get("states")
    if not isinstance(parameters, Mapping) or not isinstance(components, Sequence) or not isinstance(mass_states, Mapping) or not isinstance(states, Mapping):
        raise WayfarerBaselineError("incomplete Wayfarer geometry payload")

    length = _parameter(parameters, "ship.length_m")
    diameter = _parameter(parameters, "ship.main_body_diameter_m")
    dock = _component(components, "docking_collar")
    launch = _component(components, "launch_bay")

    return WayfarerPhysicalBaseline(
        body_frame=WayfarerBodyFrame(
            frame_id="WAYFARER_BODY",
            origin_description="bow datum at x=0 m on longitudinal thrust axis",
            x_axis_description=x_desc,
            y_axis_description=y_desc,
            z_axis_description=z_desc,
        ),
        length_m=length,
        main_body_diameter_m=diameter,
        docking_collar_center_m=_vec3(dock["center_m"], "docking_collar.center_m"),
        docking_geometry_status=BaselineStatus(str(dock["status"])),
        launch_bay_center_m=_vec3(launch["center_m"], "launch_bay.center_m"),
        launch_geometry_status=BaselineStatus(str(launch["status"])),
        docked_mass=_mass_state(mass_states["DOCKED"], "DOCKED"),
        launch_absent_mass=_mass_state(mass_states["ABSENT"], "ABSENT"),
        launch_states=tuple(str(v) for v in states["launch"]),
        radiator_states=tuple(str(v) for v in states["radiators"]),
        docking_states=tuple(str(v) for v in states["docking"]),
        torch_states=tuple(str(v) for v in states["torch"]),
    )
