from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional, Protocol, Sequence, Tuple, TypeVar, Union

Vector3 = Tuple[float, float, float]
Tensor3 = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]
Quaternion = Tuple[float, float, float, float]
SolverResultT = TypeVar("SolverResultT", covariant=True)


class PhysicalDesignError(ValueError):
    """Fail-closed error for invalid or unsupported physical-design inputs."""


@dataclass(frozen=True)
class Transform:
    translation_m: Vector3
    quaternion_wxyz: Quaternion = (1.0, 0.0, 0.0, 0.0)


@dataclass(frozen=True)
class BoxGeometry:
    x_m: float
    y_m: float
    z_m: float


@dataclass(frozen=True)
class CylinderXGeometry:
    length_m: float
    diameter_m: float


Geometry = Union[BoxGeometry, CylinderXGeometry]


@dataclass(frozen=True)
class PhysicalComponentType:
    type_id: str
    mass_kg: float
    admitted_geometry: Optional[Geometry]
    authority_status: str
    provenance: str


@dataclass(frozen=True)
class PhysicalComponentInstance:
    instance_id: str
    component_type_id: str
    transform: Transform
    active: bool = True


@dataclass(frozen=True)
class PointMassContribution:
    source_id: str
    mass_kg: float
    centroid_m: Vector3
    authority_status: str
    provenance: str


@dataclass(frozen=True)
class KeepOutCircleYZ:
    keep_out_id: str
    center_yz_m: Tuple[float, float]
    radius_m: float
    authority_status: str
    provenance: str
    note: str = ""


@dataclass(frozen=True)
class DesignVariable:
    variable_id: str
    lower: float
    upper: float
    step: float
    units: str


@dataclass(frozen=True)
class HardConstraintResult:
    constraint_id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ObjectiveTerm:
    objective_id: str
    value: float
    units: str
    semantics: str


@dataclass(frozen=True)
class CandidateDesign:
    candidate_id: str
    seed: int
    component_types: Tuple[PhysicalComponentType, ...]
    component_instances: Tuple[PhysicalComponentInstance, ...]
    point_masses: Tuple[PointMassContribution, ...]
    keep_outs: Tuple[KeepOutCircleYZ, ...] = ()
    active_states: Mapping[str, str] = field(default_factory=dict)
    store_decomposition_kg: Mapping[str, float] = field(default_factory=dict)
    provenance_map: Mapping[str, str] = field(default_factory=dict)
    solver_version: str = "UNSET"
    input_hashes: Mapping[str, str] = field(default_factory=dict)
    open_geometry_used: Tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationResult:
    candidate_id: str
    mass_kg: float
    center_of_mass_m: Vector3
    parallel_axis_tensor_kg_m2: Tensor3
    admitted_centroidal_tensor_kg_m2: Tensor3
    candidate_aggregate_tensor_kg_m2: Tensor3
    unresolved_inertia_mass_fraction: float
    hard_constraints: Tuple[HardConstraintResult, ...]
    objective_vector: Tuple[ObjectiveTerm, ...]
    flight_dynamics_authority: bool
    authority_label: str


@dataclass(frozen=True)
class DesignAuthorityRecord:
    authority_id: str
    candidate_id: str
    status: str
    flight_dynamics_authority: bool
    solver_version: str
    input_hashes: Mapping[str, str]
    provenance_map: Mapping[str, str]


class PhysicalDesignSolver(Protocol[SolverResultT]):
    solver_version: str

    def solve(self, seed: int) -> SolverResultT:
        ...


def _finite_nonnegative(value: float, label: str, *, positive: bool = False) -> float:
    v = float(value)
    if not math.isfinite(v) or v < 0.0 or (positive and v <= 0.0):
        raise PhysicalDesignError(f"{label} must be finite and {'positive' if positive else 'non-negative'}")
    return v


def validate_transform(transform: Transform) -> None:
    if len(transform.translation_m) != 3 or not all(math.isfinite(float(v)) for v in transform.translation_m):
        raise PhysicalDesignError("Transform translation must be a finite 3-vector")
    if len(transform.quaternion_wxyz) != 4 or not all(math.isfinite(float(v)) for v in transform.quaternion_wxyz):
        raise PhysicalDesignError("Transform quaternion must be finite")
    norm = math.sqrt(sum(float(v) ** 2 for v in transform.quaternion_wxyz))
    if norm <= 0.0:
        raise PhysicalDesignError("Transform quaternion norm must be positive")
    q = tuple(float(v) / norm for v in transform.quaternion_wxyz)
    if max(abs(q[i] - (1.0 if i == 0 else 0.0)) for i in range(4)) > 1e-12:
        raise PhysicalDesignError("S1 evaluator supports identity-oriented admitted bodies only")


def validate_geometry(geometry: Geometry) -> None:
    if isinstance(geometry, BoxGeometry):
        _finite_nonnegative(geometry.x_m, "box x", positive=True)
        _finite_nonnegative(geometry.y_m, "box y", positive=True)
        _finite_nonnegative(geometry.z_m, "box z", positive=True)
    elif isinstance(geometry, CylinderXGeometry):
        _finite_nonnegative(geometry.length_m, "cylinder length", positive=True)
        _finite_nonnegative(geometry.diameter_m, "cylinder diameter", positive=True)
    else:
        raise PhysicalDesignError(f"Unsupported geometry type: {type(geometry).__name__}")


def zero_tensor() -> Tensor3:
    return ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))


def add_tensor(a: Tensor3, b: Tensor3) -> Tensor3:
    return tuple(tuple(a[i][j] + b[i][j] for j in range(3)) for i in range(3))  # type: ignore[return-value]


def centroidal_tensor(mass_kg: float, geometry: Geometry) -> Tensor3:
    m = _finite_nonnegative(mass_kg, "component mass", positive=True)
    validate_geometry(geometry)
    if isinstance(geometry, BoxGeometry):
        x, y, z = geometry.x_m, geometry.y_m, geometry.z_m
        return (
            (m * (y * y + z * z) / 12.0, 0.0, 0.0),
            (0.0, m * (x * x + z * z) / 12.0, 0.0),
            (0.0, 0.0, m * (x * x + y * y) / 12.0),
        )
    r = geometry.diameter_m / 2.0
    length = geometry.length_m
    return (
        (0.5 * m * r * r, 0.0, 0.0),
        (0.0, m * (3.0 * r * r + length * length) / 12.0, 0.0),
        (0.0, 0.0, m * (3.0 * r * r + length * length) / 12.0),
    )


def parallel_axis_tensor(mass_kg: float, centroid_m: Vector3, com_m: Vector3) -> Tensor3:
    m = _finite_nonnegative(mass_kg, "parallel-axis mass")
    dx = float(centroid_m[0]) - float(com_m[0])
    dy = float(centroid_m[1]) - float(com_m[1])
    dz = float(centroid_m[2]) - float(com_m[2])
    return (
        (m * (dy * dy + dz * dz), -m * dx * dy, -m * dx * dz),
        (-m * dx * dy, m * (dx * dx + dz * dz), -m * dy * dz),
        (-m * dx * dz, -m * dy * dz, m * (dx * dx + dy * dy)),
    )


def _interval_x(instance: PhysicalComponentInstance, geometry: Geometry) -> Tuple[float, float]:
    x = float(instance.transform.translation_m[0])
    half = (geometry.x_m if isinstance(geometry, BoxGeometry) else geometry.length_m) / 2.0
    return x - half, x + half


def bodies_collide(
    a_instance: PhysicalComponentInstance,
    a_geometry: Geometry,
    b_instance: PhysicalComponentInstance,
    b_geometry: Geometry,
    *,
    tolerance_m: float = 1e-9,
) -> bool:
    """Exact for identity-oriented BOX/CYLINDER_X combinations used by S1."""
    validate_transform(a_instance.transform)
    validate_transform(b_instance.transform)
    validate_geometry(a_geometry)
    validate_geometry(b_geometry)
    ax0, ax1 = _interval_x(a_instance, a_geometry)
    bx0, bx1 = _interval_x(b_instance, b_geometry)
    if min(ax1, bx1) <= max(ax0, bx0) + tolerance_m:
        return False

    ay, az = map(float, a_instance.transform.translation_m[1:])
    by, bz = map(float, b_instance.transform.translation_m[1:])

    if isinstance(a_geometry, CylinderXGeometry) and isinstance(b_geometry, CylinderXGeometry):
        ar = a_geometry.diameter_m / 2.0
        br = b_geometry.diameter_m / 2.0
        return math.hypot(ay - by, az - bz) < ar + br - tolerance_m

    if isinstance(a_geometry, BoxGeometry) and isinstance(b_geometry, BoxGeometry):
        return (
            abs(ay - by) < (a_geometry.y_m + b_geometry.y_m) / 2.0 - tolerance_m
            and abs(az - bz) < (a_geometry.z_m + b_geometry.z_m) / 2.0 - tolerance_m
        )

    if isinstance(a_geometry, BoxGeometry):
        box_i, box_g, cyl_i, cyl_g = a_instance, a_geometry, b_instance, b_geometry
    else:
        box_i, box_g, cyl_i, cyl_g = b_instance, b_geometry, a_instance, a_geometry
    assert isinstance(box_g, BoxGeometry) and isinstance(cyl_g, CylinderXGeometry)
    box_y, box_z = map(float, box_i.transform.translation_m[1:])
    cyl_y, cyl_z = map(float, cyl_i.transform.translation_m[1:])
    dy = max(abs(cyl_y - box_y) - box_g.y_m / 2.0, 0.0)
    dz = max(abs(cyl_z - box_z) - box_g.z_m / 2.0, 0.0)
    return math.hypot(dy, dz) < cyl_g.diameter_m / 2.0 - tolerance_m


def evaluate_mass_inertia(candidate: CandidateDesign) -> Tuple[float, Vector3, Tensor3, Tensor3, Tensor3, float]:
    type_map: Dict[str, PhysicalComponentType] = {}
    component_rows = []
    resolved_centroidal_mass = 0.0

    for component_type in candidate.component_types:
        if component_type.type_id in type_map:
            raise PhysicalDesignError(f"Duplicate component type {component_type.type_id}")
        _finite_nonnegative(component_type.mass_kg, f"mass {component_type.type_id}", positive=True)
        if component_type.admitted_geometry is not None:
            validate_geometry(component_type.admitted_geometry)
        type_map[component_type.type_id] = component_type

    seen_instances = set()
    for instance in candidate.component_instances:
        if instance.instance_id in seen_instances:
            raise PhysicalDesignError(f"Duplicate component instance {instance.instance_id}")
        seen_instances.add(instance.instance_id)
        if instance.component_type_id not in type_map:
            raise PhysicalDesignError(f"Unknown component type {instance.component_type_id}")
        validate_transform(instance.transform)
        if not instance.active:
            continue
        ctype = type_map[instance.component_type_id]
        component_rows.append((ctype.mass_kg, instance.transform.translation_m, ctype.admitted_geometry))
        if ctype.admitted_geometry is not None:
            resolved_centroidal_mass += ctype.mass_kg

    for point in candidate.point_masses:
        _finite_nonnegative(point.mass_kg, f"point mass {point.source_id}", positive=True)
        if len(point.centroid_m) != 3 or not all(math.isfinite(float(v)) for v in point.centroid_m):
            raise PhysicalDesignError(f"Invalid centroid for {point.source_id}")

    rows = [(m, c) for m, c, _ in component_rows] + [(p.mass_kg, p.centroid_m) for p in candidate.point_masses]
    total_mass = sum(float(m) for m, _ in rows)
    if not math.isfinite(total_mass) or total_mass <= 0.0:
        raise PhysicalDesignError("Candidate total mass must be finite and positive")
    com: Vector3 = tuple(
        sum(float(m) * float(c[i]) for m, c in rows) / total_mass for i in range(3)
    )  # type: ignore[assignment]

    pa = zero_tensor()
    centroidal = zero_tensor()
    for mass, centroid, geometry in component_rows:
        pa = add_tensor(pa, parallel_axis_tensor(mass, centroid, com))
        if geometry is not None:
            centroidal = add_tensor(centroidal, centroidal_tensor(mass, geometry))
    for point in candidate.point_masses:
        pa = add_tensor(pa, parallel_axis_tensor(point.mass_kg, point.centroid_m, com))

    aggregate = add_tensor(pa, centroidal)
    unresolved_fraction = max(0.0, min(1.0, 1.0 - resolved_centroidal_mass / total_mass))
    return total_mass, com, pa, centroidal, aggregate, unresolved_fraction


def component_collisions(candidate: CandidateDesign) -> Tuple[Tuple[str, str], ...]:
    type_map = {c.type_id: c for c in candidate.component_types}
    admitted = []
    for instance in candidate.component_instances:
        ctype = type_map.get(instance.component_type_id)
        if instance.active and ctype is not None and ctype.admitted_geometry is not None:
            admitted.append((instance, ctype.admitted_geometry))
    collisions = []
    for i in range(len(admitted)):
        for j in range(i + 1, len(admitted)):
            a_i, a_g = admitted[i]
            b_i, b_g = admitted[j]
            if bodies_collide(a_i, a_g, b_i, b_g):
                collisions.append((a_i.instance_id, b_i.instance_id))
    return tuple(collisions)
