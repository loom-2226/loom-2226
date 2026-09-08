from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence, Tuple

from governed_ship_synthesis import GovernedSynthesisPackage, build_wayfarer_governed_synthesis, canonical_json as synthesis_json
from wayfarer_s1_solver import result_payload, solve

LEDGER_VERSION = "LOOM_DESIGN_LEDGER_v0.1"
DISCIPLINE_RESULT_VERSION = "LOOM_DISCIPLINE_RESULT_v0.1"
DEPENDENCY_GRAPH_VERSION = "LOOM_ENGINEERING_DEPENDENCY_GRAPH_v0.1"
LEDGER_AUTHORITY = "DESIGN_HISTORY_EVIDENCE_ONLY"
DISCIPLINE_AUTHORITY = "DECLARED_DISCIPLINE_EVIDENCE_ONLY"
DEPENDENCY_AUTHORITY = "DEPENDENCY_DECLARATION_ONLY"
STATUS = ("ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION")
FIDELITY_CLASSES = frozenset({"L0_ANALYTIC", "L1_DETERMINISTIC_REDUCED_ORDER", "L2_HIGHER_FIDELITY", "OPEN"})
RESULT_STATUSES = frozenset({"PASS", "FAIL", "MEASURED", "OPEN"})
EDGE_STATUSES = frozenset({"ADMITTED", "OPEN"})


class DesignLedgerError(ValueError):
    pass


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DesignLedgerError(f"{label} must be a non-empty string")
    return value.strip()


def _tuple(values: Sequence[str], label: str, *, allow_empty: bool = True) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise DesignLedgerError(f"{label} must be a sequence")
    out = tuple(_text(v, label) for v in values)
    if not allow_empty and not out:
        raise DesignLedgerError(f"{label} must not be empty")
    if len(out) != len(set(out)):
        raise DesignLedgerError(f"{label} must contain unique values")
    return out


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _hex64(value: str, label: str) -> str:
    value = _text(value, label).lower()
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise DesignLedgerError(f"{label} must be a 64-character hex digest")
    return value


def canonical_json(value: object) -> str:
    return json.dumps(asdict(value), sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash(value: object) -> str:
    return _sha(canonical_json(value))


@dataclass(frozen=True)
class DisciplineResult:
    version: str
    result_id: str
    state_id: str
    discipline_id: str
    model_id: str
    model_version: str
    fidelity_class: str
    assumptions_hash: str
    input_hash: str
    result_hash: str
    result_status: str
    summary_json: str
    provenance_refs: Tuple[str, ...]
    authority_status: str = DISCIPLINE_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


@dataclass(frozen=True)
class DependencyNode:
    node_id: str
    node_kind: str
    description: str


@dataclass(frozen=True)
class DependencyEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    quantity: str
    status: str
    provenance_refs: Tuple[str, ...]


@dataclass(frozen=True)
class EngineeringDependencyGraph:
    version: str
    graph_id: str
    state_id: str
    nodes: Tuple[DependencyNode, ...]
    edges: Tuple[DependencyEdge, ...]
    coupled_physics_status: str
    authority_status: str = DEPENDENCY_AUTHORITY


def validate_discipline_result(row: DisciplineResult) -> None:
    for field in ("version", "result_id", "state_id", "discipline_id", "model_id", "model_version"):
        _text(getattr(row, field), field)
    if row.version != DISCIPLINE_RESULT_VERSION:
        raise DesignLedgerError("unsupported discipline-result version")
    if row.fidelity_class not in FIDELITY_CLASSES:
        raise DesignLedgerError(f"unsupported fidelity_class {row.fidelity_class}")
    if row.result_status not in RESULT_STATUSES:
        raise DesignLedgerError(f"unsupported result_status {row.result_status}")
    _hex64(row.assumptions_hash, "assumptions_hash")
    _hex64(row.input_hash, "input_hash")
    _hex64(row.result_hash, "result_hash")
    try:
        json.loads(row.summary_json)
    except json.JSONDecodeError as exc:
        raise DesignLedgerError("summary_json must be valid JSON") from exc
    _tuple(row.provenance_refs, "provenance_refs", allow_empty=False)
    if row.authority_status != DISCIPLINE_AUTHORITY:
        raise DesignLedgerError("discipline result may not claim higher authority")
    if row.flight_dynamics_authority or row.canon_changed or row.production_shipclasses_changed:
        raise DesignLedgerError("discipline result authority escalation")


def validate_dependency_graph(graph: EngineeringDependencyGraph) -> None:
    if graph.version != DEPENDENCY_GRAPH_VERSION:
        raise DesignLedgerError("unsupported dependency-graph version")
    _text(graph.graph_id, "graph_id")
    _text(graph.state_id, "state_id")
    _text(graph.coupled_physics_status, "coupled_physics_status")
    if graph.authority_status != DEPENDENCY_AUTHORITY:
        raise DesignLedgerError("dependency graph authority escalation")
    node_ids = set()
    for node in graph.nodes:
        _text(node.node_id, "node_id")
        _text(node.node_kind, "node_kind")
        _text(node.description, "description")
        if node.node_id in node_ids:
            raise DesignLedgerError(f"duplicate dependency node {node.node_id}")
        node_ids.add(node.node_id)
    edge_ids = set()
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for edge in graph.edges:
        _text(edge.edge_id, "edge_id")
        _text(edge.quantity, "quantity")
        if edge.edge_id in edge_ids:
            raise DesignLedgerError(f"duplicate dependency edge {edge.edge_id}")
        edge_ids.add(edge.edge_id)
        if edge.source_node_id not in node_ids or edge.target_node_id not in node_ids:
            raise DesignLedgerError("dependency edge references unknown node")
        if edge.source_node_id == edge.target_node_id:
            raise DesignLedgerError("dependency self-edge forbidden")
        if edge.status not in EDGE_STATUSES:
            raise DesignLedgerError(f"unsupported dependency edge status {edge.status}")
        _tuple(edge.provenance_refs, "provenance_refs", allow_empty=False)
        if edge.status == "ADMITTED":
            adjacency[edge.source_node_id].add(edge.target_node_id)
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise DesignLedgerError("admitted dependency graph contains a cycle; coupled solve contract not yet admitted")
        if node_id in visited:
            return
        visiting.add(node_id)
        for nxt in sorted(adjacency[node_id]):
            visit(nxt)
        visiting.remove(node_id)
        visited.add(node_id)
    for node_id in sorted(node_ids):
        visit(node_id)


def _schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS ledger_meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS design_run(
            run_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            seed INTEGER NOT NULL,
            status_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS design_state(
            state_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL REFERENCES design_run(run_id),
            candidate_id TEXT NOT NULL,
            parent_state_id TEXT REFERENCES design_state(state_id),
            state_kind TEXT NOT NULL,
            state_hash TEXT NOT NULL,
            state_json TEXT NOT NULL,
            provenance_json TEXT NOT NULL,
            UNIQUE(run_id, state_hash)
        );
        CREATE TABLE IF NOT EXISTS discipline_result(
            result_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            discipline_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            model_version TEXT NOT NULL,
            fidelity_class TEXT NOT NULL,
            assumptions_hash TEXT NOT NULL,
            input_hash TEXT NOT NULL,
            result_hash TEXT NOT NULL,
            result_status TEXT NOT NULL,
            summary_json TEXT NOT NULL,
            provenance_json TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            UNIQUE(state_id, discipline_id, model_id, model_version, input_hash)
        );
        CREATE TABLE IF NOT EXISTS dependency_graph(
            graph_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            graph_hash TEXT NOT NULL,
            graph_json TEXT NOT NULL,
            coupled_physics_status TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS derived_artifact(
            artifact_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            artifact_kind TEXT NOT NULL,
            artifact_hash TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            provenance_json TEXT NOT NULL
        );
        """
    )
    connection.execute("INSERT OR REPLACE INTO ledger_meta(key,value) VALUES('ledger_version',?)", (LEDGER_VERSION,))


class DesignLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.connection = sqlite3.connect(str(self.path))
        self.connection.row_factory = sqlite3.Row
        _schema(self.connection)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "DesignLedger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.close()

    def add_run(self, *, run_id: str, created_at: str, seed: int) -> None:
        self.connection.execute(
            "INSERT INTO design_run(run_id,created_at,seed,status_json,authority_status) VALUES(?,?,?,?,?)",
            (_text(run_id, "run_id"), _text(created_at, "created_at"), int(seed), json.dumps(STATUS), LEDGER_AUTHORITY),
        )

    def add_state(self, *, state_id: str, run_id: str, candidate_id: str, state_kind: str,
                  state_json: str, provenance_refs: Sequence[str], parent_state_id: str | None = None) -> str:
        json.loads(state_json)
        state_hash = _sha(state_json)
        self.connection.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (_text(state_id, "state_id"), _text(run_id, "run_id"), _text(candidate_id, "candidate_id"), parent_state_id,
             _text(state_kind, "state_kind"), state_hash, state_json, json.dumps(_tuple(provenance_refs, "provenance_refs", allow_empty=False))),
        )
        return state_hash

    def add_discipline_result(self, row: DisciplineResult) -> None:
        validate_discipline_result(row)
        self.connection.execute(
            "INSERT INTO discipline_result(result_id,state_id,discipline_id,model_id,model_version,fidelity_class,assumptions_hash,input_hash,result_hash,result_status,summary_json,provenance_json,authority_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (row.result_id,row.state_id,row.discipline_id,row.model_id,row.model_version,row.fidelity_class,row.assumptions_hash,
             row.input_hash,row.result_hash,row.result_status,row.summary_json,json.dumps(row.provenance_refs),row.authority_status),
        )

    def add_dependency_graph(self, graph: EngineeringDependencyGraph) -> str:
        validate_dependency_graph(graph)
        text = canonical_json(graph)
        digest = _sha(text)
        self.connection.execute(
            "INSERT INTO dependency_graph(graph_id,state_id,graph_hash,graph_json,coupled_physics_status,authority_status) VALUES(?,?,?,?,?,?)",
            (graph.graph_id, graph.state_id, digest, text, graph.coupled_physics_status, graph.authority_status),
        )
        return digest

    def add_artifact(self, *, artifact_id: str, state_id: str, artifact_kind: str, artifact_hash: str,
                     authority_status: str, provenance_refs: Sequence[str]) -> None:
        self.connection.execute(
            "INSERT INTO derived_artifact(artifact_id,state_id,artifact_kind,artifact_hash,authority_status,provenance_json) VALUES(?,?,?,?,?,?)",
            (_text(artifact_id,"artifact_id"),_text(state_id,"state_id"),_text(artifact_kind,"artifact_kind"),
             _hex64(artifact_hash,"artifact_hash"),_text(authority_status,"authority_status"),json.dumps(_tuple(provenance_refs,"provenance_refs",allow_empty=False))),
        )

    def counts(self) -> dict[str, int]:
        return {table: int(self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in ("design_run","design_state","discipline_result","dependency_graph","derived_artifact")}


def wayfarer_dependency_graph(state_id: str) -> EngineeringDependencyGraph:
    nodes = (
        DependencyNode("MISSION_REQUIREMENTS", "INPUT", "Existing Wayfarer S1 requirement/test authority inputs."),
        DependencyNode("S1_LAYOUT_EVALUATION", "DISCIPLINE", "Existing deterministic S1 layout/mass/constraint evaluation."),
        DependencyNode("DESIGN_STATE", "STATE", "Governed synthesis design-state projection."),
        DependencyNode("PACKAGING", "SYNTHESIS", "Admitted envelopes plus explicit OPEN volumes."),
        DependencyNode("PHYSICAL_TOPOLOGY", "SYNTHESIS", "Coarse topology hypothesis."),
        DependencyNode("STRUCTURAL_GRAPH", "SYNTHESIS", "Coarse structural hypothesis; not qualified."),
        DependencyNode("GEOMETRY", "DERIVED", "Deterministic derived mesh geometry."),
        DependencyNode("COUPLED_THERMAL_POWER_PROPULSION", "OPEN_DISCIPLINE", "No admitted coupled thermal/power/propulsion solve in Phase 1."),
    )
    edges = (
        DependencyEdge("DEP-001","MISSION_REQUIREMENTS","S1_LAYOUT_EVALUATION","requirements + design variables","ADMITTED",("WAYFARER_S1_TEST_DEFINITION_v0.1",)),
        DependencyEdge("DEP-002","S1_LAYOUT_EVALUATION","DESIGN_STATE","candidate layout state","ADMITTED",("wayfarer_s1_solver",)),
        DependencyEdge("DEP-003","DESIGN_STATE","PACKAGING","component envelopes / point-mass OPENs","ADMITTED",("governed_ship_synthesis_v0.1",)),
        DependencyEdge("DEP-004","DESIGN_STATE","PHYSICAL_TOPOLOGY","source-node positions","ADMITTED",("governed_ship_synthesis_v0.1",)),
        DependencyEdge("DEP-005","PHYSICAL_TOPOLOGY","STRUCTURAL_GRAPH","topology edges","ADMITTED",("governed_ship_synthesis_v0.1",)),
        DependencyEdge("DEP-006","PACKAGING","GEOMETRY","region envelopes","ADMITTED",("governed_ship_synthesis_v0.1",)),
        DependencyEdge("DEP-007","STRUCTURAL_GRAPH","GEOMETRY","coarse member graph","ADMITTED",("governed_ship_synthesis_v0.1",)),
        DependencyEdge("DEP-OPEN-001","S1_LAYOUT_EVALUATION","COUPLED_THERMAL_POWER_PROPULSION","coupled physics feedback","OPEN",("PHASE1_OPEN",)),
        DependencyEdge("DEP-OPEN-002","COUPLED_THERMAL_POWER_PROPULSION","PACKAGING","thermal/power/propulsion spatial feedback","OPEN",("PHASE1_OPEN",)),
    )
    graph = EngineeringDependencyGraph(
        version=DEPENDENCY_GRAPH_VERSION,
        graph_id=f"DEPGRAPH::{state_id}",
        state_id=state_id,
        nodes=nodes,
        edges=edges,
        coupled_physics_status="OPEN_NO_COUPLED_MDAO_SOLVE_ADMITTED_v0.1",
    )
    validate_dependency_graph(graph)
    return graph


def _s1_result(state_id: str, seed: int) -> DisciplineResult:
    result = solve(seed)
    payload = result_payload(result)
    summary = {
        "candidate_id": payload["candidate_id"],
        "mass_kg": payload["mass_kg"],
        "center_of_mass_m": payload["center_of_mass_m"],
        "hard_constraints": payload["hard_constraints"],
        "objective_vector": payload["objective_vector"],
        "flight_dynamics_authority": False,
        "wayfarer_flight_inertia_qualified": False,
    }
    summary_json = json.dumps(summary, sort_keys=True, separators=(",", ":"), allow_nan=False)
    input_hash = _sha(json.dumps(payload["input_hashes"], sort_keys=True, separators=(",", ":")))
    assumptions_hash = _sha(json.dumps({"solver_version": payload["solver_version"], "schema": payload["schema"], "schema_version": payload["schema_version"]}, sort_keys=True, separators=(",", ":")))
    result_hash = _sha(summary_json)
    hard_pass = all(row["passed"] for row in payload["hard_constraints"])
    row = DisciplineResult(
        version=DISCIPLINE_RESULT_VERSION,
        result_id=f"DISCIPLINE::WAYFARER_S1::{state_id}",
        state_id=state_id,
        discipline_id="WAYFARER_S1_LAYOUT_MASS_CONSTRAINTS",
        model_id="wayfarer_s1_solver",
        model_version=payload["solver_version"],
        fidelity_class="L1_DETERMINISTIC_REDUCED_ORDER",
        assumptions_hash=assumptions_hash,
        input_hash=input_hash,
        result_hash=result_hash,
        result_status="PASS" if hard_pass else "FAIL",
        summary_json=summary_json,
        provenance_refs=(payload["candidate_id"], payload["solver_version"]),
    )
    validate_discipline_result(row)
    return row


def build_wayfarer_phase1_ledger(path: str | Path, *, seed: int = 2226, created_at: str = "2026-09-08T00:00:00Z") -> dict[str, object]:
    synthesis = build_wayfarer_governed_synthesis(seed)
    state_id = f"STATE::{synthesis.design_state.candidate_id}::SYNTH-v0.1"
    run_id = f"RUN::WAYFARER::{seed}::PHASE1-v0.1"
    state_json = synthesis_json(synthesis)
    ledger_path = Path(path)
    if ledger_path.exists():
        ledger_path.unlink()
    with DesignLedger(ledger_path) as ledger:
        ledger.add_run(run_id=run_id, created_at=created_at, seed=seed)
        state_hash = ledger.add_state(
            state_id=state_id,
            run_id=run_id,
            candidate_id=synthesis.design_state.candidate_id,
            state_kind="GOVERNED_SYNTHESIS_STATE",
            state_json=state_json,
            provenance_refs=(synthesis.design_state.candidate_id, synthesis.package_hash),
        )
        discipline = _s1_result(state_id, seed)
        ledger.add_discipline_result(discipline)
        graph = wayfarer_dependency_graph(state_id)
        graph_hash = ledger.add_dependency_graph(graph)
        ledger.add_artifact(
            artifact_id=f"ARTIFACT::GEOMETRY::{state_id}",
            state_id=state_id,
            artifact_kind="DERIVED_GEOMETRY_PACKAGE",
            artifact_hash=content_hash(synthesis.geometry),
            authority_status=synthesis.geometry.authority_status,
            provenance_refs=(synthesis.package_hash,),
        )
        counts = ledger.counts()
        ledger.connection.commit()
    return {
        "ledger_version": LEDGER_VERSION,
        "ledger_path": str(ledger_path),
        "run_id": run_id,
        "state_id": state_id,
        "state_hash": state_hash,
        "discipline_result_id": discipline.result_id,
        "dependency_graph_hash": graph_hash,
        "synthesis_package_hash": synthesis.package_hash,
        "counts": counts,
        "coupled_physics_status": graph.coupled_physics_status,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }
