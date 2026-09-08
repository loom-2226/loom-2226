#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

VERSION = "LOOM_SHIPYARD_PHASE6_REMASS_CANDIDATE_SCREEN_v0.1"
AUTHORITY = "EXTERNAL_RESEARCH_SCREENING_ONLY"
DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")

# Screening densities are external research values, not LOOM authority and not live engineering inputs.
# Water: NIST/IAPS table, saturated liquid at 20 C ~= 998.2 kg/m3.
# Methane: NASA TM-2000-209941, normal boiling point density 26.37 lbm/ft3 ~= 422.4 kg/m3.
# Hydrogen: NASA references, normal boiling point liquid density ~= 70.8 kg/m3.
CANDIDATES = (
    {
        "candidate_id": "REMASS_CANDIDATE::LIQUID_WATER_293K",
        "material": "H2O",
        "storage_state": "LIQUID_REFERENCE_SCREEN_AT_293.15_K",
        "screening_density_kg_m3": 998.2,
        "source": "NIST water-property tabulation / IAPS-IAPWS lineage",
        "source_url": "https://srd.nist.gov/jpcrdreprint/1.555763.pdf",
        "notes": "Density-only geometric screening reference. Does not admit Wayfarer temperature, pressure, ullage, tank construction, or water as selected remass.",
    },
    {
        "candidate_id": "REMASS_CANDIDATE::LIQUID_METHANE_NBP",
        "material": "CH4",
        "storage_state": "LIQUID_NORMAL_BOILING_POINT_SCREEN",
        "screening_density_kg_m3": 422.4,
        "source": "NASA/TM-2000-209941",
        "source_url": "https://ntrs.nasa.gov/api/citations/20000033847/downloads/20000033847.pdf",
        "notes": "Density-only cryogenic screening reference. Does not imply methane is LOOM remass or selected storage doctrine.",
    },
    {
        "candidate_id": "REMASS_CANDIDATE::LIQUID_HYDROGEN_NBP",
        "material": "H2",
        "storage_state": "LIQUID_NORMAL_BOILING_POINT_SCREEN",
        "screening_density_kg_m3": 70.8,
        "source": "NASA liquid-hydrogen references",
        "source_url": "https://ntrs.nasa.gov/api/citations/19790004067/downloads/19790004067.pdf",
        "notes": "Density-only cryogenic screening reference. Does not imply direct LH2 storage is LOOM authority.",
    },
)


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tables(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def classify_candidate(density_kg_m3: float, minimum_density_kg_m3: float) -> str:
    if density_kg_m3 <= 0 or minimum_density_kg_m3 <= 0:
        raise RuntimeError("candidate and bound densities must be positive")
    if density_kg_m3 < minimum_density_kg_m3:
        return "REJECT_OUTER_ENVELOPE_DENSITY_BOUND"
    return "NOT_REJECTED_BY_DENSITY_BOUND_ONLY"


def apply_phase6(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        required = {"design_state", "remass_feasibility_bound", "shipyard_migration", "engineering_input"}
        if not required.issubset(_tables(con)):
            raise RuntimeError("Refusing Phase-6 migration: target is not a Phase-5 Shipyard ledger")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS remass_candidate_model(
            candidate_id TEXT PRIMARY KEY,
            model_hash TEXT NOT NULL,
            model_json TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS remass_candidate_comparison(
            comparison_id TEXT PRIMARY KEY,
            state_id TEXT NOT NULL REFERENCES design_state(state_id),
            source_id TEXT NOT NULL,
            candidate_id TEXT NOT NULL REFERENCES remass_candidate_model(candidate_id),
            comparison_hash TEXT NOT NULL,
            comparison_json TEXT NOT NULL,
            screen_status TEXT NOT NULL,
            authority_status TEXT NOT NULL
        );
        """)
        existing = con.execute("SELECT result_json FROM shipyard_migration WHERE migration_id=?", (VERSION,)).fetchone()
        if existing:
            result = json.loads(existing[0]); result["already_applied"] = True; return result

        phase5 = con.execute("SELECT * FROM design_state WHERE state_kind='PHASE5_REMASS_INPUT_AUDIT_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if phase5 is None:
            raise RuntimeError("No Phase-5 remass input audit state found")
        child_state_id = phase5["state_id"].replace("PHASE5-REMASS-INPUT-AUDIT-v0.1", "PHASE6-REMASS-CANDIDATE-SCREEN-v0.1")
        phase5_json = json.loads(phase5["state_json"])

        for candidate in CANDIDATES:
            text = _canonical(candidate)
            con.execute(
                "INSERT INTO remass_candidate_model VALUES(?,?,?,?)",
                (candidate["candidate_id"], _sha(text), text, AUTHORITY),
            )

        bounds = con.execute(
            "SELECT source_id,bound_json FROM remass_feasibility_bound WHERE state_id=? ORDER BY source_id",
            (phase5["state_id"],),
        ).fetchall()
        if len(bounds) != 4:
            raise RuntimeError(f"Expected 4 Phase-5 remass bounds, found {len(bounds)}")

        comparisons = []
        rejected = 0
        not_rejected = 0
        for row in bounds:
            bound = json.loads(row["bound_json"])
            minimum_density = float(bound["minimum_equivalent_bulk_density_kg_m3"])
            max_outer_volume = float(bound["max_idealized_outer_cylinder_volume_m3"])
            for candidate in CANDIDATES:
                density = float(candidate["screening_density_kg_m3"])
                status = classify_candidate(density, minimum_density)
                if status.startswith("REJECT_"):
                    rejected += 1
                else:
                    not_rejected += 1
                fluid_volume = 62_500.0 / density
                comparison = {
                    "source_id": row["source_id"],
                    "candidate_id": candidate["candidate_id"],
                    "screening_density_kg_m3": density,
                    "minimum_equivalent_bulk_density_kg_m3": minimum_density,
                    "ideal_fluid_volume_m3": fluid_volume,
                    "max_idealized_outer_cylinder_volume_m3": max_outer_volume,
                    "outer_volume_utilization_fraction": fluid_volume / max_outer_volume,
                    "screen_status": status,
                    "screen_semantics": "FAIL_IS_DECISIVE_FOR_CURRENT_OUTER_BOUND_PASS_ONLY_MEANS_NOT_REJECTED_WALLS_ULLAGE_ENDS_THERMAL_AND_STRUCTURE_UNMODELED",
                    "live_input_admitted": False,
                    "spatial_envelope_admitted": False,
                    "authority_status": AUTHORITY,
                }
                comparisons.append(comparison)

        phase6_json = dict(phase5_json)
        phase6_json["phase6_candidate_models"] = list(CANDIDATES)
        phase6_json["phase6_candidate_comparisons"] = comparisons
        phase6_json["phase6_authority_status"] = AUTHORITY
        phase6_json["phase6_spatial_effect"] = "NONE_SCREENING_ONLY_NO_ENVELOPE_ADMITTED"
        phase6_json["phase6_selection_status"] = "NO_CANDIDATE_SELECTED"
        child_text = _canonical(phase6_json)
        child_hash = _sha(child_text)
        con.execute(
            "INSERT INTO design_state(state_id,run_id,candidate_id,parent_state_id,state_kind,state_hash,state_json,provenance_json) VALUES(?,?,?,?,?,?,?,?)",
            (child_state_id, phase5["run_id"], phase5["candidate_id"], phase5["state_id"], "PHASE6_REMASS_CANDIDATE_SCREEN_STATE", child_hash, child_text, json.dumps([VERSION, phase5["state_id"], "NIST", "NASA"])),
        )

        for comparison in comparisons:
            text = _canonical(comparison)
            cid = comparison["candidate_id"].split("::", 1)[1]
            con.execute(
                "INSERT INTO remass_candidate_comparison VALUES(?,?,?,?,?,?,?,?)",
                (f"SCREEN::{comparison['source_id']}::{cid}::{VERSION}", child_state_id, comparison["source_id"], comparison["candidate_id"], _sha(text), text, comparison["screen_status"], AUTHORITY),
            )

        result = {
            "migration_id": VERSION,
            "database": str(db_path),
            "parent_state_id": phase5["state_id"],
            "state_id": child_state_id,
            "state_hash": child_hash,
            "candidate_model_count": len(CANDIDATES),
            "tank_count": len(bounds),
            "comparison_count": len(comparisons),
            "rejected_comparison_count": rejected,
            "not_rejected_comparison_count": not_rejected,
            "selected_candidate_count": 0,
            "live_engineering_input_admission_count": 0,
            "spatial_effect": "NONE_SCREENING_ONLY_NO_ENVELOPE_ADMITTED",
            "canon_changed": False,
            "production_shipclasses_changed": False,
            "flight_dynamics_authority": False,
            "already_applied": False,
        }
        con.execute("INSERT INTO shipyard_migration(migration_id,source_version,result_json) VALUES(?,?,?)", (VERSION, VERSION, json.dumps(result, sort_keys=True)))
        con.commit(); return result
    except Exception:
        con.rollback(); raise
    finally:
        con.close()


if __name__ == "__main__":
    print(json.dumps(apply_phase6(), indent=2, sort_keys=True))
