#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

VERSION = "LOOM_SHIPYARD_PHASE4_REMASS_SIZING_v0.1"
MODEL_ID = "loom_remass_tank_equivalent_envelope"
MODEL_VERSION = "LOOM_REMASS_TANK_EQUIVALENT_ENVELOPE_v0.1"
MODEL_AUTHORITY = "DETERMINISTIC_SIZING_MODEL_ONLY"
INPUT_AUTHORITY = "ENGINEERING_INPUT_EVIDENCE_ONLY"
ATTEMPT_AUTHORITY = "DISCIPLINE_EXECUTION_EVIDENCE_ONLY"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
REMASS_SOURCES = tuple(f"normal_remass_tank_{i}" for i in range(1, 5))
LIVE_REQUIRED = (
    "remass_density_kg_m3",
    "ullage_fraction",
    "pressure_temperature_state",
    "tankage_fraction_semantics",
    "tank_geometry_rule",
)


def _canonical(value: object) -> str:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _finite_positive(value: object, label: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out <= 0.0:
        raise RuntimeError(f"{label} must be finite and positive")
    return out


def _fraction(value: object, label: str) -> float:
    out = float(value)
    if not math.isfinite(out) or not 0.0 <= out < 1.0:
        raise RuntimeError(f"{label} must be finite in [0,1)")
    return out


@dataclass(frozen=True)
class RemassTankSizingInput:
    remass_mass_kg: float
    remass_density_kg_m3: float
    ullage_fraction: float
    internal_diameter_m: float
    external_diameter_m: float
    axial_end_allowance_m: float
    pressure_temperature_state: str
    tankage_fraction_semantics: str
    geometry_rule: str


@dataclass(frozen=True)
class RemassTankSizingResult:
    model_id: str
    model_version: str
    fluid_volume_m3: float
    required_internal_volume_m3: float
    internal_cylinder_length_m: float
    external_envelope_length_m: float
    external_envelope_diameter_m: float
    authority_status: str
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def evaluate_remass_tank(inp: RemassTankSizingInput) -> RemassTankSizingResult:
    mass = _finite_positive(inp.remass_mass_kg, "remass_mass_kg")
    density = _finite_positive(inp.remass_density_kg_m3, "remass_density_kg_m3")
    ullage = _fraction(inp.ullage_fraction, "ullage_fraction")
    di = _finite_positive(inp.internal_diameter_m, "internal_diameter_m")
    de = _finite_positive(inp.external_diameter_m, "external_diameter_m")
    allowance = float(inp.axial_end_allowance_m)
    if not math.isfinite(allowance) or allowance < 0.0:
        raise RuntimeError("axial_end_allowance_m must be finite and non-negative")
    if de < di:
        raise RuntimeError("external_diameter_m may not be smaller than internal_diameter_m")
    for label, value in (
        ("pressure_temperature_state", inp.pressure_temperature_state),
        ("tankage_fraction_semantics", inp.tankage_fraction_semantics),
        ("geometry_rule", inp.geometry_rule),
    ):
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"{label} must be explicit")
    if inp.geometry_rule != "CYLINDER_X_EQUIVALENT_WITH_EXPLICIT_INTERNAL_DIAMETER_AND_END_ALLOWANCE":
        raise RuntimeError("unsupported remass tank geometry_rule")
    if inp.tankage_fraction_semantics != "NOT_USED_FOR_VOLUME_SIZING_EXPLICITLY_DECLARED":
        raise RuntimeError("tankage_fraction semantics are unresolved; model refuses silent reinterpretation")

    fluid_volume = mass / density
    required_internal_volume = fluid_volume / (1.0 - ullage)
    area = math.pi * (di * 0.5) ** 2
    internal_length = required_internal_volume / area
    external_length = internal_length + allowance
    result = RemassTankSizingResult(
        model_id=MODEL_ID,
        model_version=MODEL_VERSION,
        fluid_volume_m3=fluid_volume,
        required_internal_volume_m3=required_internal_volume,
        internal_cylinder_length_m=internal_length,
        external_envelope_length_m=external_length,
        external_envelope_diameter_m=de,
        authority_status=MODEL_AUTHORITY,
    )
    if result.flight_dynamics_authority or result.canon_changed or result.production_shipclasses_changed:
        raise RuntimeError("sizing result authority escalation")
    return result


def _table_names(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _point_mass_from_phase1(con: sqlite3.Connection, source_id: str) -> tuple[float, list[float]]:
    row = con.execute("SELECT state_json FROM design_state WHERE state_kind='GOVERNED_SYNTHESIS_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
    if row is None:
        raise RuntimeError("No governed synthesis state found")
    payload = json.loads(row[0])
    for node in payload.get("design_state", {}).get("nodes", []):
        if node.get("source_kind") == "POINT_MASS" and node.get("source_id") == source_id:
            anchor = [float(x) for x in node["position_m"]]
            break
    else:
        raise RuntimeError(f"Missing point-mass anchor for {source_id}")
    return 62_500.0, anchor


def apply_phase4(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        required = {"design_state", "discipline_contract", "workflow_gate", "functional_region_contract", "shipyard_migration"}
        if not required.issubset(_table_names(con)):
            raise RuntimeError("Refusing Phase-4 migration: target is not a Phase-3 Shipyard ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS discipline_model(
            model_id TEXT NOT NULL,
            model_version TEXT NOT NULL,
            discipline_id TEXT NOT NULL,
            fidelity_class TEXT NOT NULL,
            model_hash TEXT NOT NULL,
            model_json TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            PRIMARY KEY(model_id, model_version)
        );
        CREATE TABLE IF NOT EXISTS engineering_input(
            input_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            input_name TEXT NOT NULL,
            value_json TEXT NOT NULL,
            unit TEXT,
            admission_status TEXT NOT NULL,
            provenance_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS discipline_execution_attempt(
            attempt_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            model_version TEXT NOT NULL,
            execution_status TEXT NOT NULL,
            missing_inputs_json TEXT NOT NULL,
            result_json TEXT,
            result_hash TEXT,
            authority_status TEXT NOT NULL
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0]); result["already_applied"] = True; return result

        phase3 = con.execute("SELECT * FROM design_state WHERE state_kind='PHASE3_DISCIPLINE_GATE_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if phase3 is None:
            raise RuntimeError("No Phase-3 discipline-gate state found")
        phase3_json = json.loads(phase3["state_json"])
        child_state_id = phase3["state_id"].replace("PHASE3-DISCIPLINE-GATES-v0.1", "PHASE4-REMASS-SIZING-v0.1")

        model_spec = {
            "model_id": MODEL_ID,
            "model_version": MODEL_VERSION,
            "discipline_id": "REMASS_TANK_SIZING",
            "fidelity_class": "L0_ANALYTIC",
            "equations": [
                "fluid_volume=remass_mass/density",
                "required_internal_volume=fluid_volume/(1-ullage_fraction)",
                "internal_length=required_internal_volume/(pi*(internal_diameter/2)^2)",
                "external_length=internal_length+axial_end_allowance",
            ],
            "live_required_inputs": list(LIVE_REQUIRED),
            "authority_status": MODEL_AUTHORITY,
            "notes": [
                "Model is executable only when every physical input is explicitly admitted.",
                "No remass density, ullage, pressure/temperature state, internal diameter, wall/end allowance, or tankage semantics are invented by this migration.",
                "Nominal 3.0 m external diameter from S1 is packaging evidence only, not an inferred internal diameter.",
            ],
        }
        model_text = _canonical(model_spec)
        con.execute("INSERT INTO discipline_model VALUES(?,?,?,?,?,?,?)", (MODEL_ID, MODEL_VERSION, "REMASS_TANK_SIZING", "L0_ANALYTIC", _sha(model_text), model_text, MODEL_AUTHORITY))

        per_source: dict[str, dict] = {}
        attempts = []
        for source_id in REMASS_SOURCES:
            mass, anchor = _point_mass_from_phase1(con, source_id)
            admitted = {
                "remass_mass_kg": (mass, "kg", ["WAYFARER_S1_TEST_DEFINITION_v0.1", source_id]),
                "external_diameter_m": (3.0, "m", ["WAYFARER_S1_TEST_DEFINITION_v0.1", "nominal tank external diameter"]),
                "anchor_position_m": (anchor, "m", [phase3["parent_state_id"], source_id]),
            }
            per_source[source_id] = admitted
            attempts.append({
                "attempt_id": f"ATTEMPT::{source_id}::{MODEL_VERSION}",
                "source_id": source_id,
                "execution_status": "BLOCKED_MISSING_ADMITTED_INPUTS",
                "missing_inputs": list(LIVE_REQUIRED),
                "admitted_support_inputs": sorted(admitted),
                "model_id": MODEL_ID,
                "model_version": MODEL_VERSION,
                "result_admitted": False,
            })

        phase4_json = dict(phase3_json)
        phase4_json["phase4_remass_sizing_model"] = model_spec
        phase4_json["phase4_remass_execution_attempts"] = attempts
        phase4_json["phase4_status"] = ["ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION"]
        phase4_json["phase4_authority_status"] = "DISCIPLINE_MODEL_AND_INPUT_EVIDENCE_ONLY"
        phase4_json["phase4_spatial_effect"] = "NONE_BLOCKED_NO_ENVELOPE_ADMITTED"
        child_text = _canonical(phase4_json)
        child_hash = _sha(child_text)
        con.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (child_state_id, phase3["run_id"], phase3["candidate_id"], phase3["state_id"], "PHASE4_REMASS_SIZING_STATE", child_hash, child_text, json.dumps([VERSION, phase3["state_id"], MODEL_VERSION])),
        )

        for source_id, admitted in per_source.items():
            for name, (value, unit, refs) in admitted.items():
                con.execute(
                    "INSERT INTO engineering_input VALUES(?,?,?,?,?,?,?,?,?)",
                    (f"INPUT::{source_id}::{name}", child_state_id, source_id, name, _canonical(value), unit, "ADMITTED_FROM_EXISTING_EVIDENCE", json.dumps(refs), INPUT_AUTHORITY),
                )
        for attempt in attempts:
            con.execute(
                "INSERT INTO discipline_execution_attempt VALUES(?,?,?,?,?,?,?,?,?,?)",
                (attempt["attempt_id"], child_state_id, attempt["source_id"], MODEL_ID, MODEL_VERSION, attempt["execution_status"], json.dumps(attempt["missing_inputs"]), None, None, ATTEMPT_AUTHORITY),
            )

        result = {
            "migration_id": VERSION,
            "database": str(db_path),
            "parent_state_id": phase3["state_id"],
            "state_id": child_state_id,
            "state_hash": child_hash,
            "model_id": MODEL_ID,
            "model_version": MODEL_VERSION,
            "model_fidelity": "L0_ANALYTIC",
            "remass_tank_count": 4,
            "admitted_support_input_count": 12,
            "blocked_attempt_count": 4,
            "executed_attempt_count": 0,
            "remaining_open_count": len(phase4_json.get("packaging", {}).get("open_items", [])),
            "spatial_effect": "NONE_BLOCKED_NO_ENVELOPE_ADMITTED",
            "canon_changed": False,
            "production_shipclasses_changed": False,
            "flight_dynamics_authority": False,
            "already_applied": False,
        }
        con.execute("INSERT INTO shipyard_migration(migration_id,source_version,result_json) VALUES(?,?,?)", (VERSION, VERSION, json.dumps(result, sort_keys=True)))
        con.commit()
        return result
    except Exception:
        con.rollback(); raise
    finally:
        con.close()


if __name__ == "__main__":
    print(json.dumps(apply_phase4(), indent=2, sort_keys=True))
