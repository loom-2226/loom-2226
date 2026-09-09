from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence, Tuple

from physical_design_core import BoxGeometry, CandidateDesign, CylinderXGeometry, PhysicalDesignError
from wayfarer_s1_solver import solve

SYNTHESIS_VERSION = "LOOM_GOVERNED_SHIP_SYNTHESIS_v0.1"
DESIGN_STATE_AUTHORITY = "DESIGN_STATE_EVIDENCE_ONLY"
TOPOLOGY_AUTHORITY = "TOPOLOGY_HYPOTHESIS_ONLY"
PACKAGING_AUTHORITY = "PACKAGING_HYPOTHESIS_ONLY"
STRUCTURE_AUTHORITY = "STRUCTURAL_HYPOTHESIS_ONLY"
GEOMETRY_AUTHORITY = "DERIVED_GEOMETRY_ONLY"
PACKAGE_AUTHORITY = "DESIGN_SYNTHESIS_RESEARCH_ONLY"
STATUS = ("ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION")


class GovernedSynthesisError(PhysicalDesignError):
    """Fail-closed error for the governed synthesis research slice."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GovernedSynthesisError(f"{label} must be a non-empty string")
    return value.strip()


def _vec3(values: Sequence[float], label: str) -> Tuple[float, float, float]:
    if len(values) != 3:
        raise GovernedSynthesisError(f"{label} must contain exactly 3 values")
    out = tuple(float(v) for v in values)
    if any(not math.isfinite(v) for v in out):
        raise GovernedSynthesisError(f"{label} must be finite")
    return out  # type: ignore[return-value]


def _positive(value: float, label: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out <= 0.0:
        raise GovernedSynthesisError(f"{label} must be finite and positive")
    return out


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DesignNode:
    node_id: str
    source_kind: str
    source_id: str
    position_m: Tuple[float, float, float]
    provenance_refs: Tuple[str, ...]
    authority_status: str = DESIGN_STATE_AUTHORITY


@dataclass(frozen=True)
class DesignState:
    version: str
    candidate_id: str
    candidate_source_hash: str
    nodes: Tuple[DesignNode, ...]
    dependency_graph_status: str
    provenance_refs: Tuple[str, ...]
    authority_status: str = DESIGN_STATE_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


@dataclass(frozen=True)
class TopologyNode:
    node_id: str
    position_m: Tuple[float, float, float]
    node_kind: str
    source_refs: Tuple[str, ...]
    authority_status: str = TOPOLOGY_AUTHORITY


@dataclass(frozen=True)
class TopologyEdge:
    edge_id: str
    node_a: str
    node_b: str
    relation: str
    rationale: str
    source_refs: Tuple[str, ...]
    authority_status: str = TOPOLOGY_AUTHORITY


@dataclass(frozen=True)
class PhysicalTopology:
    nodes: Tuple[TopologyNode, ...]
    edges: Tuple[TopologyEdge, ...]
    authority_status: str = TOPOLOGY_AUTHORITY


@dataclass(frozen=True)
class SpatialRegion:
    region_id: str
    region_kind: str
    center_m: Tuple[float, float, float]
    dimensions_m: Tuple[float, float, float]
    source_refs: Tuple[str, ...]
    authority_status: str = PACKAGING_AUTHORITY


@dataclass(frozen=True)
class PackagingState:
    regions: Tuple[SpatialRegion, ...]
    open_items: Tuple[str, ...]
    authority_status: str = PACKAGING_AUTHORITY


@dataclass(frozen=True)
class StructuralMember:
    member_id: str
    node_a: str
    node_b: str
    radius_m: float
    member_kind: str
    rationale: str
    source_refs: Tuple[str, ...]
    authority_status: str = STRUCTURE_AUTHORITY


@dataclass(frozen=True)
class StructuralGraph:
    members: Tuple[StructuralMember, ...]
    qualification_status: str
    authority_status: str = STRUCTURE_AUTHORITY


@dataclass(frozen=True)
class MeshPrimitive:
    primitive_id: str
    primitive_kind: str
    vertices_m: Tuple[Tuple[float, float, float], ...]
    triangles: Tuple[Tuple[int, int, int], ...]
    source_refs: Tuple[str, ...]
    authority_status: str = GEOMETRY_AUTHORITY


@dataclass(frozen=True)
class GeometryPackage:
    primitives: Tuple[MeshPrimitive, ...]
    authority_status: str = GEOMETRY_AUTHORITY


@dataclass(frozen=True)
class GovernedSynthesisPackage:
    version: str
    design_state: DesignState
    topology: PhysicalTopology
    packaging: PackagingState
    structure: StructuralGraph
    geometry: GeometryPackage
    package_hash: str
    authority_status: str = PACKAGE_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def _candidate_snapshot(candidate: CandidateDesign) -> dict:
    return {
        "candidate_id": candidate.candidate_id,
        "instances": [
            {
                "instance_id": row.instance_id,
                "component_type_id": row.component_type_id,
                "active": bool(row.active),
                "translation_m": [float(v) for v in row.transform.translation_m],
                "quaternion_wxyz": [float(v) for v in row.transform.quaternion_wxyz],
            }
            for row in sorted(candidate.component_instances, key=lambda r: r.instance_id)
        ],
        "points": [
            {
                "source_id": row.source_id,
                "mass_kg": float(row.mass_kg),
                "centroid_m": [float(v) for v in row.centroid_m],
            }
            for row in sorted(candidate.point_masses, key=lambda r: r.source_id)
        ],
        "input_hashes": list(candidate.input_hashes),
        "solver_version": candidate.solver_version,
    }


def candidate_source_hash(candidate: CandidateDesign) -> str:
    text = json.dumps(_candidate_snapshot(candidate), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return _sha(text)


def build_design_state(candidate: CandidateDesign) -> DesignState:
    nodes = []
    for row in sorted(candidate.component_instances, key=lambda r: r.instance_id):
        if not row.active:
            continue
        nodes.append(
            DesignNode(
                node_id=f"COMP::{row.instance_id}",
                source_kind="COMPONENT_INSTANCE",
                source_id=row.instance_id,
                position_m=_vec3(row.transform.translation_m, f"{row.instance_id}.translation_m"),
                provenance_refs=(candidate.candidate_id, row.instance_id, row.component_type_id),
            )
        )
    for row in sorted(candidate.point_masses, key=lambda r: r.source_id):
        nodes.append(
            DesignNode(
                node_id=f"MASS::{row.source_id}",
                source_kind="POINT_MASS",
                source_id=row.source_id,
                position_m=_vec3(row.centroid_m, f"{row.source_id}.centroid_m"),
                provenance_refs=(candidate.candidate_id, row.source_id),
            )
        )
    if not nodes:
        raise GovernedSynthesisError("candidate has no active design nodes")
    return DesignState(
        version=SYNTHESIS_VERSION,
        candidate_id=candidate.candidate_id,
        candidate_source_hash=candidate_source_hash(candidate),
        nodes=tuple(nodes),
        dependency_graph_status="OPEN_NO_COUPLED_DISCIPLINE_GRAPH_ADMITTED_v0.1",
        provenance_refs=(candidate.candidate_id,) + tuple(candidate.input_hashes),
    )


def build_topology(state: DesignState) -> PhysicalTopology:
    if state.authority_status != DESIGN_STATE_AUTHORITY:
        raise GovernedSynthesisError("design state authority escalation")
    source_nodes = tuple(
        TopologyNode(
            node_id=row.node_id,
            position_m=row.position_m,
            node_kind=row.source_kind,
            source_refs=row.provenance_refs,
        )
        for row in state.nodes
    )
    xs = sorted({round(row.position_m[0], 9) for row in state.nodes})
    if len(xs) == 1:
        xs = [xs[0] - 0.5, xs[0] + 0.5]
    spine_nodes = tuple(
        TopologyNode(
            node_id=f"SPINE::{index:03d}",
            position_m=(x, 0.0, 0.0),
            node_kind="SYNTHESIS_SPINE_ANCHOR",
            source_refs=(state.candidate_id, "DETERMINISTIC_X_STATION_PROJECTION"),
        )
        for index, x in enumerate(xs)
    )
    edges = []
    for index in range(len(spine_nodes) - 1):
        a, b = spine_nodes[index], spine_nodes[index + 1]
        edges.append(
            TopologyEdge(
                edge_id=f"EDGE::SPINE::{index:03d}",
                node_a=a.node_id,
                node_b=b.node_id,
                relation="SYNTHESIS_BACKBONE_HYPOTHESIS",
                rationale="Deterministic coarse synthesis backbone between adjacent occupied x stations; not a validated load path.",
                source_refs=(state.candidate_id,),
            )
        )
    by_x = {node.position_m[0]: node for node in spine_nodes}
    for index, node in enumerate(source_nodes):
        anchor_x = min(by_x, key=lambda x: (abs(x - node.position_m[0]), x))
        anchor = by_x[anchor_x]
        if math.dist(node.position_m, anchor.position_m) < 1e-9:
            continue
        edges.append(
            TopologyEdge(
                edge_id=f"EDGE::BRANCH::{index:03d}",
                node_a=anchor.node_id,
                node_b=node.node_id,
                relation="SYNTHESIS_ATTACHMENT_HYPOTHESIS",
                rationale="Deterministic connection of an admitted source node to the coarse synthesis backbone; not qualified structure.",
                source_refs=node.source_refs,
            )
        )
    topology = PhysicalTopology(nodes=spine_nodes + source_nodes, edges=tuple(edges))
    validate_topology(topology)
    return topology


def build_packaging(candidate: CandidateDesign, state: DesignState) -> PackagingState:
    type_map = {row.type_id: row for row in candidate.component_types}
    regions = []
    admitted = set()
    for row in sorted(candidate.component_instances, key=lambda r: r.instance_id):
        if not row.active:
            continue
        ctype = type_map.get(row.component_type_id)
        if ctype is None or ctype.admitted_geometry is None:
            continue
        geom = ctype.admitted_geometry
        if isinstance(geom, BoxGeometry):
            dims = (float(geom.x_m), float(geom.y_m), float(geom.z_m))
            kind = "ADMITTED_BOX_ENVELOPE"
        elif isinstance(geom, CylinderXGeometry):
            dims = (float(geom.length_m), float(geom.diameter_m), float(geom.diameter_m))
            kind = "ADMITTED_CYLINDER_X_ENVELOPE"
        else:
            raise GovernedSynthesisError(f"unsupported admitted geometry {type(geom).__name__}")
        regions.append(
            SpatialRegion(
                region_id=f"REGION::{row.instance_id}",
                region_kind=kind,
                center_m=_vec3(row.transform.translation_m, "translation_m"),
                dimensions_m=tuple(_positive(v, "region dimension") for v in dims),  # type: ignore[arg-type]
                source_refs=(state.candidate_id, row.instance_id, row.component_type_id),
            )
        )
        admitted.add(row.instance_id)
    open_items = tuple(
        f"NO_ADMITTED_VOLUME::{row.source_id}"
        for row in sorted(candidate.point_masses, key=lambda r: r.source_id)
    )
    return PackagingState(regions=tuple(regions), open_items=open_items)


def build_structural_graph(topology: PhysicalTopology) -> StructuralGraph:
    validate_topology(topology)
    members = []
    for edge in topology.edges:
        is_spine = edge.relation == "SYNTHESIS_BACKBONE_HYPOTHESIS"
        members.append(
            StructuralMember(
                member_id=edge.edge_id.replace("EDGE::", "MEMBER::", 1),
                node_a=edge.node_a,
                node_b=edge.node_b,
                radius_m=0.18 if is_spine else 0.10,
                member_kind="COARSE_BACKBONE_MEMBER" if is_spine else "COARSE_ATTACHMENT_MEMBER",
                rationale=edge.rationale + " Member radius is a v0.1 visualization/synthesis parameter, not a strength-derived size.",
                source_refs=edge.source_refs,
            )
        )
    return StructuralGraph(
        members=tuple(members),
        qualification_status="NOT_STRUCTURALLY_QUALIFIED",
    )


def _box_mesh(primitive_id: str, center: Sequence[float], dims: Sequence[float], refs: Tuple[str, ...]) -> MeshPrimitive:
    cx, cy, cz = _vec3(center, "box center")
    dx, dy, dz = (_positive(v, "box dimension") / 2.0 for v in dims)
    vertices = (
        (cx-dx, cy-dy, cz-dz), (cx+dx, cy-dy, cz-dz), (cx+dx, cy+dy, cz-dz), (cx-dx, cy+dy, cz-dz),
        (cx-dx, cy-dy, cz+dz), (cx+dx, cy-dy, cz+dz), (cx+dx, cy+dy, cz+dz), (cx-dx, cy+dy, cz+dz),
    )
    triangles = (
        (0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),
        (3,2,6),(3,6,7),(1,5,6),(1,6,2),(0,3,7),(0,7,4),
    )
    return MeshPrimitive(primitive_id, "REGION_ENVELOPE", vertices, triangles, refs)


def _tube_mesh(
    primitive_id: str,
    p0: Sequence[float],
    p1: Sequence[float],
    radius: float,
    refs: Tuple[str, ...],
    *,
    sides: int = 8,
    kind: str = "STRUCTURAL_MEMBER",
) -> MeshPrimitive:
    a, b = _vec3(p0, "tube p0"), _vec3(p1, "tube p1")
    r = _positive(radius, "tube radius")
    axis = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    length = math.sqrt(sum(v*v for v in axis))
    if length <= 1e-12:
        raise GovernedSynthesisError("zero-length tube")
    u = tuple(v/length for v in axis)
    helper = (0.0, 0.0, 1.0) if abs(u[2]) < 0.9 else (0.0, 1.0, 0.0)
    v = (
        u[1]*helper[2]-u[2]*helper[1],
        u[2]*helper[0]-u[0]*helper[2],
        u[0]*helper[1]-u[1]*helper[0],
    )
    vm = math.sqrt(sum(x*x for x in v))
    v = tuple(x/vm for x in v)
    w = (
        u[1]*v[2]-u[2]*v[1],
        u[2]*v[0]-u[0]*v[2],
        u[0]*v[1]-u[1]*v[0],
    )
    vertices = []
    for base in (a, b):
        for i in range(sides):
            ang = 2.0 * math.pi * i / sides
            off = tuple(r * (math.cos(ang)*v[j] + math.sin(ang)*w[j]) for j in range(3))
            vertices.append(tuple(base[j] + off[j] for j in range(3)))
    triangles = []
    for i in range(sides):
        j = (i + 1) % sides
        triangles.extend(((i, sides+i, sides+j), (i, sides+j, j)))
    return MeshPrimitive(primitive_id, kind, tuple(vertices), tuple(triangles), refs)


def _octa_mesh(primitive_id: str, center: Sequence[float], radius: float, refs: Tuple[str, ...]) -> MeshPrimitive:
    x, y, z = _vec3(center, "point center")
    r = _positive(radius, "point radius")
    vertices = ((x+r,y,z),(x-r,y,z),(x,y+r,z),(x,y-r,z),(x,y,z+r),(x,y,z-r))
    triangles = ((0,2,4),(0,4,3),(0,3,5),(0,5,2),(1,4,2),(1,3,4),(1,5,3),(1,2,5))
    return MeshPrimitive(primitive_id, "SOURCE_NODE", vertices, triangles, refs)


def compile_geometry(
    candidate: CandidateDesign,
    state: DesignState,
    topology: PhysicalTopology,
    packaging: PackagingState,
    structure: StructuralGraph,
) -> GeometryPackage:
    positions = {row.node_id: row.position_m for row in topology.nodes}
    primitives = []
    for region in packaging.regions:
        primitives.append(_box_mesh(f"MESH::{region.region_id}", region.center_m, region.dimensions_m, region.source_refs))
    for member in structure.members:
        if member.node_a not in positions or member.node_b not in positions:
            raise GovernedSynthesisError("structural member references unknown topology node")
        primitives.append(
            _tube_mesh(
                f"MESH::{member.member_id}",
                positions[member.node_a],
                positions[member.node_b],
                member.radius_m,
                member.source_refs,
            )
        )
    for node in state.nodes:
        primitives.append(_octa_mesh(f"MESH::NODE::{node.node_id}", node.position_m, 0.22, node.provenance_refs))
    return GeometryPackage(primitives=tuple(primitives))


def validate_topology(topology: PhysicalTopology) -> None:
    if topology.authority_status != TOPOLOGY_AUTHORITY:
        raise GovernedSynthesisError("topology may not claim engineering authority")
    node_ids = [row.node_id for row in topology.nodes]
    if len(node_ids) != len(set(node_ids)):
        raise GovernedSynthesisError("duplicate topology node id")
    known = set(node_ids)
    edge_ids = set()
    for edge in topology.edges:
        if edge.authority_status != TOPOLOGY_AUTHORITY:
            raise GovernedSynthesisError("topology edge authority escalation")
        if edge.edge_id in edge_ids:
            raise GovernedSynthesisError("duplicate topology edge id")
        edge_ids.add(edge.edge_id)
        if edge.node_a == edge.node_b:
            raise GovernedSynthesisError("topology self-edge")
        if edge.node_a not in known or edge.node_b not in known:
            raise GovernedSynthesisError("topology edge references unknown node")


def validate_package(package: GovernedSynthesisPackage) -> None:
    if package.authority_status != PACKAGE_AUTHORITY:
        raise GovernedSynthesisError("package authority escalation")
    if package.flight_dynamics_authority or package.canon_changed or package.production_shipclasses_changed:
        raise GovernedSynthesisError("synthesis package may not mutate frozen authority")
    if package.design_state.authority_status != DESIGN_STATE_AUTHORITY:
        raise GovernedSynthesisError("design state authority escalation")
    validate_topology(package.topology)
    if package.packaging.authority_status != PACKAGING_AUTHORITY:
        raise GovernedSynthesisError("packaging authority escalation")
    if package.structure.authority_status != STRUCTURE_AUTHORITY:
        raise GovernedSynthesisError("structure authority escalation")
    if package.structure.qualification_status != "NOT_STRUCTURALLY_QUALIFIED":
        raise GovernedSynthesisError("v0.1 structural synthesis is not qualification evidence")
    if package.geometry.authority_status != GEOMETRY_AUTHORITY:
        raise GovernedSynthesisError("geometry authority escalation")
    for primitive in package.geometry.primitives:
        if primitive.authority_status != GEOMETRY_AUTHORITY:
            raise GovernedSynthesisError("mesh primitive authority escalation")
        if not primitive.vertices_m or not primitive.triangles:
            raise GovernedSynthesisError("mesh primitive must contain geometry")
        for tri in primitive.triangles:
            if len(tri) != 3 or min(tri) < 0 or max(tri) >= len(primitive.vertices_m):
                raise GovernedSynthesisError("invalid mesh triangle index")
    expected = package_hash_without_hash(package)
    if package.package_hash != expected:
        raise GovernedSynthesisError("package hash mismatch")


def package_hash_without_hash(package: GovernedSynthesisPackage) -> str:
    payload = asdict(package)
    payload["package_hash"] = ""
    return _sha(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))


def build_governed_synthesis(candidate: CandidateDesign) -> GovernedSynthesisPackage:
    state = build_design_state(candidate)
    topology = build_topology(state)
    packaging = build_packaging(candidate, state)
    structure = build_structural_graph(topology)
    geometry = compile_geometry(candidate, state, topology, packaging, structure)
    provisional = GovernedSynthesisPackage(
        version=SYNTHESIS_VERSION,
        design_state=state,
        topology=topology,
        packaging=packaging,
        structure=structure,
        geometry=geometry,
        package_hash="",
    )
    final = GovernedSynthesisPackage(**{**asdict(provisional), "package_hash": package_hash_without_hash(provisional)})
    # asdict() turns nested dataclasses into dicts, so rebuild directly instead of accepting that structure.
    final = GovernedSynthesisPackage(
        version=provisional.version,
        design_state=provisional.design_state,
        topology=provisional.topology,
        packaging=provisional.packaging,
        structure=provisional.structure,
        geometry=provisional.geometry,
        package_hash=package_hash_without_hash(provisional),
    )
    validate_package(final)
    return final


def build_wayfarer_governed_synthesis(seed: int = 2226) -> GovernedSynthesisPackage:
    return build_governed_synthesis(solve(seed).candidate)


def canonical_json(package: GovernedSynthesisPackage) -> str:
    validate_package(package)
    return json.dumps(asdict(package), sort_keys=True, separators=(",", ":"), allow_nan=False)
