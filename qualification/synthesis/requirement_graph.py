from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, Sequence, Tuple


GRAPH_VERSION = "LOOM_REQUIREMENT_GRAPH_v0.1"


class RequirementGraphError(ValueError):
    """Fail-closed error for invalid requirement/provenance graphs."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RequirementGraphError(f"{label} must be a non-empty string")
    return value.strip()


def _finite_nonnegative(value: float, label: str) -> float:
    v = float(value)
    if not math.isfinite(v) or v < 0.0:
        raise RequirementGraphError(f"{label} must be finite and non-negative")
    return v


@dataclass(frozen=True)
class UnitSpec:
    unit_id: str
    dimension_id: str
    symbol: str
    to_si_scale: float
    to_si_offset: float = 0.0


@dataclass(frozen=True)
class RequirementNode:
    requirement_id: str
    value: float
    unit_id: str
    relation: str
    authority_status: str
    provenance_ref: str


@dataclass(frozen=True)
class RequirementEdge:
    edge_id: str
    source_ids: Tuple[str, ...]
    target_id: str
    rule_ref: str
    authority_status: str
    provenance_ref: str


@dataclass(frozen=True)
class RequirementGraph:
    version: str
    nodes: Tuple[RequirementNode, ...]
    edges: Tuple[RequirementEdge, ...]
    units: Tuple[UnitSpec, ...]
    graph_hash: str


def validate_unit(unit: UnitSpec) -> None:
    _text(unit.unit_id, "unit_id")
    _text(unit.dimension_id, "dimension_id")
    _text(unit.symbol, "symbol")
    scale = float(unit.to_si_scale)
    offset = float(unit.to_si_offset)
    if not math.isfinite(scale) or scale <= 0.0:
        raise RequirementGraphError(f"unit {unit.unit_id} scale must be finite and positive")
    if not math.isfinite(offset):
        raise RequirementGraphError(f"unit {unit.unit_id} offset must be finite")


def validate_node(node: RequirementNode) -> None:
    _text(node.requirement_id, "requirement_id")
    _finite_nonnegative(node.value, f"requirement {node.requirement_id}")
    _text(node.unit_id, "unit_id")
    relation = _text(node.relation, "relation").upper()
    if relation not in {"MIN", "MAX", "EXACT"}:
        raise RequirementGraphError(f"unsupported relation {node.relation}")
    _text(node.authority_status, "authority_status")
    _text(node.provenance_ref, "provenance_ref")


def validate_edge(edge: RequirementEdge) -> None:
    _text(edge.edge_id, "edge_id")
    if isinstance(edge.source_ids, (str, bytes)) or not edge.source_ids:
        raise RequirementGraphError("source_ids must be a non-empty sequence")
    cleaned = tuple(_text(v, "source_id") for v in edge.source_ids)
    if len(set(cleaned)) != len(cleaned):
        raise RequirementGraphError(f"edge {edge.edge_id} has duplicate source_ids")
    _text(edge.target_id, "target_id")
    _text(edge.rule_ref, "rule_ref")
    _text(edge.authority_status, "authority_status")
    _text(edge.provenance_ref, "provenance_ref")


def _canonical_payload(nodes: Sequence[RequirementNode], edges: Sequence[RequirementEdge], units: Sequence[UnitSpec]) -> str:
    payload = {
        "version": GRAPH_VERSION,
        "nodes": [asdict(v) for v in sorted(nodes, key=lambda x: x.requirement_id)],
        "edges": [asdict(v) for v in sorted(edges, key=lambda x: x.edge_id)],
        "units": [asdict(v) for v in sorted(units, key=lambda x: x.unit_id)],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def build_requirement_graph(
    nodes: Sequence[RequirementNode],
    *,
    edges: Sequence[RequirementEdge] = (),
    units: Sequence[UnitSpec],
) -> RequirementGraph:
    unit_map: Dict[str, UnitSpec] = {}
    for unit in units:
        validate_unit(unit)
        if unit.unit_id in unit_map:
            raise RequirementGraphError(f"duplicate unit_id {unit.unit_id}")
        unit_map[unit.unit_id] = unit

    node_map: Dict[str, RequirementNode] = {}
    for node in nodes:
        validate_node(node)
        if node.requirement_id in node_map:
            raise RequirementGraphError(f"duplicate requirement_id {node.requirement_id}")
        if node.unit_id not in unit_map:
            raise RequirementGraphError(f"unknown unit_id {node.unit_id} for {node.requirement_id}")
        node_map[node.requirement_id] = node

    edge_ids = set()
    produced_targets = set()
    for edge in edges:
        validate_edge(edge)
        if edge.edge_id in edge_ids:
            raise RequirementGraphError(f"duplicate edge_id {edge.edge_id}")
        edge_ids.add(edge.edge_id)
        if edge.target_id not in node_map:
            raise RequirementGraphError(f"edge target not found: {edge.target_id}")
        for source_id in edge.source_ids:
            if source_id not in node_map:
                raise RequirementGraphError(f"edge source not found: {source_id}")
        if edge.target_id in edge.source_ids:
            raise RequirementGraphError(f"self dependency not allowed: {edge.edge_id}")
        if edge.target_id in produced_targets:
            raise RequirementGraphError(f"multiple provenance edges for target {edge.target_id} not admitted in v0.1")
        produced_targets.add(edge.target_id)

    adjacency = {node_id: [] for node_id in node_map}
    for edge in edges:
        for source_id in edge.source_ids:
            adjacency[source_id].append(edge.target_id)
    visiting = set()
    visited = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise RequirementGraphError("requirement dependency cycle detected")
        if node_id in visited:
            return
        visiting.add(node_id)
        for nxt in adjacency[node_id]:
            visit(nxt)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(node_map):
        visit(node_id)

    canonical = _canonical_payload(nodes, edges, units)
    return RequirementGraph(
        version=GRAPH_VERSION,
        nodes=tuple(sorted(node_map.values(), key=lambda x: x.requirement_id)),
        edges=tuple(sorted(edges, key=lambda x: x.edge_id)),
        units=tuple(sorted(unit_map.values(), key=lambda x: x.unit_id)),
        graph_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )


def convert_value(value: float, from_unit: UnitSpec, to_unit: UnitSpec) -> float:
    validate_unit(from_unit)
    validate_unit(to_unit)
    if from_unit.dimension_id != to_unit.dimension_id:
        raise RequirementGraphError(
            f"dimension mismatch: {from_unit.dimension_id} -> {to_unit.dimension_id}"
        )
    source = float(value)
    if not math.isfinite(source):
        raise RequirementGraphError("value must be finite")
    si_value = source * from_unit.to_si_scale + from_unit.to_si_offset
    return (si_value - to_unit.to_si_offset) / to_unit.to_si_scale
