#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

VERSION = "LOOM_SHIPYARD_PHASE3_DISCIPLINE_GATES_v0.1"
AUTHORITY = "DISCIPLINE_ORCHESTRATION_ONLY"
CONTRACT_AUTHORITY = "DISCIPLINE_CONTRACT_ONLY"
GATE_AUTHORITY = "WORKFLOW_GATE_ONLY"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")

PHASES = (
    "FUNCTIONAL_REGION_CONTRACTS",
    "DISCIPLINE_INPUT_ADMISSION",
    "DISCIPLINE_EVALUATION",
    "SPATIAL_ENVELOPE_ADMISSION",
)


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(value: object) -> str:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _table_names(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{label} must be a non-empty string")
    return value.strip()


def _string_list(values: object, label: str) -> tuple[str, ...]:
    if not isinstance(values, list):
        raise RuntimeError(f"{label} must be a list")
    out = tuple(_text(v, label) for v in values)
    if len(out) != len(set(out)):
        raise RuntimeError(f"{label} must contain unique values")
    return out


@dataclass(frozen=True)
class DisciplineContract:
    version: str
    contract_id: str
    state_id: str
    source_id: str
    discipline_id: str
    model_id: str
    model_version: str
    fidelity_class: str
    required_inputs: tuple[str, ...]
    admitted_inputs: tuple[str, ...]
    open_inputs: tuple[str, ...]
    execution_status: str
    result_admission_status: str
    authority_status: str = CONTRACT_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


@dataclass(frozen=True)
class WorkflowGate:
    version: str
    gate_id: str
    state_id: str
    phase_name: str
    gate_status: str
    blocking_items: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    authority_status: str = GATE_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def _discipline_identity(function_class: str) -> tuple[str, str, str, str]:
    mapping = {
        "PROPULSION": ("PROPULSION_ENVELOPE_SIZING", "loom_propulsion_envelope_sizing", "OPEN_NO_ADMITTED_MODEL_v0.1", "OPEN"),
        "REMASS_STORAGE": ("REMASS_TANK_SIZING", "loom_remass_tank_sizing", "OPEN_NO_ADMITTED_MODEL_v0.1", "OPEN"),
        "THERMAL_REJECTION": ("THERMAL_RADIATOR_SIZING", "loom_radiator_sizing", "OPEN_NO_ADMITTED_MODEL_v0.1", "OPEN"),
        "HABITATION": ("HABITATION_VOLUME_SIZING", "loom_habitation_sizing", "OPEN_NO_ADMITTED_MODEL_v0.1", "OPEN"),
        "WATER_AND_SHIELDING": ("WATER_SHIELDING_SIZING", "loom_water_shielding_sizing", "OPEN_NO_ADMITTED_MODEL_v0.1", "OPEN"),
        "PRIMARY_STRUCTURE": ("PRIMARY_STRUCTURE_SIZING", "loom_primary_structure_sizing", "OPEN_NO_ADMITTED_MODEL_v0.1", "OPEN"),
    }
    if function_class not in mapping:
        raise RuntimeError(f"No Phase-3 discipline contract for function_class={function_class!r}")
    return mapping[function_class]


def validate_contract(row: DisciplineContract) -> None:
    if row.version != VERSION:
        raise RuntimeError("unsupported Phase-3 discipline-contract version")
    for field in ("contract_id", "state_id", "source_id", "discipline_id", "model_id", "model_version", "fidelity_class"):
        _text(getattr(row, field), field)
    if row.authority_status != CONTRACT_AUTHORITY:
        raise RuntimeError("discipline contract authority escalation")
    if row.flight_dynamics_authority or row.canon_changed or row.production_shipclasses_changed:
        raise RuntimeError("discipline contract may not mutate frozen authority")
    if set(row.admitted_inputs) & set(row.open_inputs):
        raise RuntimeError("discipline input may not be both admitted and OPEN")
    if set(row.admitted_inputs) | set(row.open_inputs) != set(row.required_inputs):
        raise RuntimeError("discipline input partition must exactly cover required_inputs")
    if row.execution_status not in {"READY_FOR_DETERMINISTIC_EXECUTION", "BLOCKED_MISSING_ADMITTED_INPUTS"}:
        raise RuntimeError("unsupported discipline execution status")
    expected = "READY_FOR_DETERMINISTIC_EXECUTION" if not row.open_inputs else "BLOCKED_MISSING_ADMITTED_INPUTS"
    if row.execution_status != expected:
        raise RuntimeError("discipline execution status does not match input admission state")
    if row.result_admission_status != "NO_RESULT_ADMITTED":
        raise RuntimeError("Phase-3 contracts may not silently admit a sizing result")


def validate_gate(row: WorkflowGate) -> None:
    if row.version != VERSION:
        raise RuntimeError("unsupported Phase-3 gate version")
    if row.phase_name not in PHASES:
        raise RuntimeError(f"unsupported phase_name {row.phase_name}")
    if row.gate_status not in {"SATISFIED", "BLOCKED"}:
        raise RuntimeError("unsupported gate status")
    if row.authority_status != GATE_AUTHORITY:
        raise RuntimeError("workflow gate authority escalation")
    if row.flight_dynamics_authority or row.canon_changed or row.production_shipclasses_changed:
        raise RuntimeError("workflow gate may not mutate frozen authority")
    if row.gate_status == "SATISFIED" and row.blocking_items:
        raise RuntimeError("satisfied gate may not contain blockers")
    if row.gate_status == "BLOCKED" and not row.blocking_items:
        raise RuntimeError("blocked gate requires blockers")
    if not row.evidence_refs:
        raise RuntimeError("workflow gate requires evidence refs")


def build_contracts(state_id: str, phase2_rows: Iterable[sqlite3.Row]) -> tuple[DisciplineContract, ...]:
    out = []
    for row in phase2_rows:
        contract_json = json.loads(row["contract_json"])
        source_id = _text(contract_json.get("source_id"), "source_id")
        function_class = _text(contract_json.get("function_class"), "function_class")
        required = _string_list(contract_json.get("unresolved_sizing_inputs"), "unresolved_sizing_inputs")
        discipline_id, model_id, model_version, fidelity = _discipline_identity(function_class)
        item = DisciplineContract(
            version=VERSION,
            contract_id=f"DISCIPLINE-CONTRACT::{source_id}",
            state_id=state_id,
            source_id=source_id,
            discipline_id=discipline_id,
            model_id=model_id,
            model_version=model_version,
            fidelity_class=fidelity,
            required_inputs=required,
            admitted_inputs=(),
            open_inputs=required,
            execution_status="BLOCKED_MISSING_ADMITTED_INPUTS",
            result_admission_status="NO_RESULT_ADMITTED",
        )
        validate_contract(item)
        out.append(item)
    if not out:
        raise RuntimeError("Phase-3 requires at least one Phase-2 functional-region contract")
    return tuple(sorted(out, key=lambda r: r.source_id))


def build_gates(state_id: str, contracts: tuple[DisciplineContract, ...], phase2_state_id: str) -> tuple[WorkflowGate, ...]:
    blocked_inputs = tuple(sorted(f"{row.source_id}::{name}" for row in contracts for name in row.open_inputs))
    gates = (
        WorkflowGate(VERSION, "GATE::FUNCTIONAL_REGION_CONTRACTS", state_id, PHASES[0], "SATISFIED", (), (phase2_state_id,)),
        WorkflowGate(VERSION, "GATE::DISCIPLINE_INPUT_ADMISSION", state_id, PHASES[1], "BLOCKED", blocked_inputs, (phase2_state_id, VERSION)),
        WorkflowGate(VERSION, "GATE::DISCIPLINE_EVALUATION", state_id, PHASES[2], "BLOCKED", ("NO_DISCIPLINE_READY_FOR_EXECUTION",), (VERSION,)),
        WorkflowGate(VERSION, "GATE::SPATIAL_ENVELOPE_ADMISSION", state_id, PHASES[3], "BLOCKED", ("NO_SIZING_RESULT_ADMITTED",), (VERSION,)),
    )
    for row in gates:
        validate_gate(row)
    return gates


def apply_phase3(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        required_tables = {"design_run", "design_state", "discipline_result", "dependency_graph", "derived_artifact", "functional_region_contract", "shipyard_migration"}
        if not required_tables.issubset(_table_names(con)):
            raise RuntimeError("Refusing Phase-3 migration: target SQLite is not a Phase-2 LOOM Shipyard design ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS discipline_contract(
            contract_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            discipline_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            model_version TEXT NOT NULL,
            fidelity_class TEXT NOT NULL,
            execution_status TEXT NOT NULL,
            contract_hash TEXT NOT NULL,
            contract_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS workflow_gate(
            gate_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            phase_name TEXT NOT NULL,
            gate_status TEXT NOT NULL,
            gate_hash TEXT NOT NULL,
            gate_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0])
            result["already_applied"] = True
            return result

        phase2 = con.execute("SELECT state_id,run_id,candidate_id,state_json FROM design_state WHERE state_kind='PHASE2_FUNCTIONAL_REGION_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if phase2 is None:
            raise RuntimeError("No Phase-2 functional-region state found in Shipyard editing ledger")
        phase2_state_id = phase2["state_id"]
        phase2_json = json.loads(phase2["state_json"])
        phase2_rows = list(con.execute("SELECT * FROM functional_region_contract WHERE state_id=? ORDER BY source_id", (phase2_state_id,)))
        child_state_id = phase2_state_id.replace("PHASE2-FUNCTIONAL-REGIONS-v0.1", "PHASE3-DISCIPLINE-GATES-v0.1")
        contracts = build_contracts(child_state_id, phase2_rows)
        gates = build_gates(child_state_id, contracts, phase2_state_id)

        phase3_json = dict(phase2_json)
        phase3_json["phase3_discipline_contracts"] = [asdict(row) for row in contracts]
        phase3_json["phase3_workflow_gates"] = [asdict(row) for row in gates]
        phase3_json["phase3_status"] = ["ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION"]
        phase3_json["phase3_authority_status"] = AUTHORITY
        phase3_json["phase3_spatial_effect"] = "NONE_NO_ENVELOPE_ADMITTED"
        child_text = _canonical(phase3_json)
        child_hash = _sha_text(child_text)
        con.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (child_state_id, phase2["run_id"], phase2["candidate_id"], phase2_state_id, "PHASE3_DISCIPLINE_GATE_STATE", child_hash, child_text, json.dumps([VERSION, phase2_state_id])),
        )
        for row in contracts:
            text = _canonical(row)
            con.execute(
                "INSERT INTO discipline_contract(contract_id,state_id,source_id,discipline_id,model_id,model_version,fidelity_class,execution_status,contract_hash,contract_json,authority_status) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (row.contract_id, child_state_id, row.source_id, row.discipline_id, row.model_id, row.model_version, row.fidelity_class, row.execution_status, _sha_text(text), text, row.authority_status),
            )
        for row in gates:
            text = _canonical(row)
            con.execute(
                "INSERT INTO workflow_gate(gate_id,state_id,phase_name,gate_status,gate_hash,gate_json,authority_status) VALUES(?,?,?,?,?,?,?)",
                (row.gate_id, child_state_id, row.phase_name, row.gate_status, _sha_text(text), text, row.authority_status),
            )

        remaining_open = len(phase3_json.get("packaging", {}).get("open_items", []))
        result = {
            "migration_id": VERSION,
            "database": str(db_path),
            "parent_state_id": phase2_state_id,
            "state_id": child_state_id,
            "state_hash": child_hash,
            "discipline_contract_count": len(contracts),
            "ready_contract_count": sum(1 for row in contracts if row.execution_status == "READY_FOR_DETERMINISTIC_EXECUTION"),
            "blocked_contract_count": sum(1 for row in contracts if row.execution_status == "BLOCKED_MISSING_ADMITTED_INPUTS"),
            "workflow_gate_count": len(gates),
            "satisfied_gate_count": sum(1 for row in gates if row.gate_status == "SATISFIED"),
            "blocked_gate_count": sum(1 for row in gates if row.gate_status == "BLOCKED"),
            "remaining_open_count": remaining_open,
            "spatial_effect": "NONE_NO_ENVELOPE_ADMITTED",
            "authority_status": AUTHORITY,
            "canon_changed": False,
            "production_shipclasses_changed": False,
            "flight_dynamics_authority": False,
            "already_applied": False,
        }
        con.execute("INSERT INTO shipyard_migration(migration_id,source_version,result_json) VALUES(?,?,?)", (VERSION, VERSION, json.dumps(result, sort_keys=True)))
        con.commit()
        return result
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    print(json.dumps(apply_phase3(), indent=2, sort_keys=True))
