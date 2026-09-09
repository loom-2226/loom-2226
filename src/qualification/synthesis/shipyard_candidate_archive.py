from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from generative_candidate_compiler import CompiledCandidateArtifact, compile_wayfarer_survivor_family
from generative_shipyard_foundation import ExperimentResult, run_wayfarer_config_experiment
from vehicle_dynamics_contract import VehicleDynamicsContract, build_vehicle_dynamics_contract

ARCHIVE_VERSION = "LOOM_SHIPYARD_CANDIDATE_ARCHIVE_v0.1"
ARCHIVE_AUTHORITY = "ENGINEERING_RESEARCH_CANDIDATE_ARCHIVE_ONLY"
_REQUIRED_LEDGER_TABLES = frozenset({"ledger_meta", "design_state", "derived_artifact"})


class CandidateArchiveError(ValueError):
    pass


@dataclass(frozen=True)
class ArchivedCandidate:
    campaign_id: str
    candidate_id: str
    parent_candidate_id: str | None
    generation: int
    status: str
    pareto_member: bool
    choices: dict[str, Any]
    objective_values: dict[str, float]
    mass_kg: float | None
    center_of_mass_m: tuple[float, float, float] | None
    governed_package_hash: str | None
    semantic_glb_sha256: str | None
    dynamics_contract_hash: str | None
    dynamics_authority: bool
    archive_authority: str = ARCHIVE_AUTHORITY


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _require_design_ledger(con: sqlite3.Connection) -> None:
    tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not _REQUIRED_LEDGER_TABLES.issubset(tables):
        raise CandidateArchiveError("target is not a LOOM Shipyard design ledger")
    row = con.execute("SELECT value FROM ledger_meta WHERE key='ledger_version'").fetchone()
    if row is None or not isinstance(row[0], str) or not row[0].startswith("LOOM_DESIGN_LEDGER_"):
        raise CandidateArchiveError("missing LOOM design-ledger identity")


def ensure_schema(con: sqlite3.Connection) -> None:
    _require_design_ledger(con)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS shipyard_campaign(
            campaign_id TEXT PRIMARY KEY,
            version TEXT NOT NULL,
            experiment_hash TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            candidate_count INTEGER NOT NULL,
            survivor_count INTEGER NOT NULL,
            rejected_count INTEGER NOT NULL,
            pareto_count INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS shipyard_candidate(
            campaign_id TEXT NOT NULL,
            candidate_id TEXT NOT NULL,
            parent_candidate_id TEXT,
            generation INTEGER NOT NULL,
            status TEXT NOT NULL,
            pareto_member INTEGER NOT NULL,
            choices_json TEXT NOT NULL,
            objective_json TEXT NOT NULL,
            rejection_reason TEXT,
            failed_constraints_json TEXT NOT NULL,
            mass_kg REAL,
            center_of_mass_json TEXT,
            governed_package_hash TEXT,
            semantic_glb_sha256 TEXT,
            dynamics_contract_hash TEXT,
            dynamics_authority INTEGER NOT NULL,
            authority_status TEXT NOT NULL,
            PRIMARY KEY(campaign_id,candidate_id)
        );
        CREATE INDEX IF NOT EXISTS idx_shipyard_candidate_status
            ON shipyard_candidate(campaign_id,status,pareto_member,generation);
        """
    )


def _campaign_id(result: ExperimentResult) -> str:
    return f"CAMPAIGN::WAYFARER::{result.experiment_hash[:20]}"


def _compiled_map(seed: int) -> dict[str, CompiledCandidateArtifact]:
    return {row.candidate_id: row for row in compile_wayfarer_survivor_family(seed)}


def archive_wayfarer_campaign(db_path: str | Path, seed: int = 2226) -> str:
    result = run_wayfarer_config_experiment(seed)
    campaign_id = _campaign_id(result)
    pareto = {row.candidate_id for row in result.pareto_frontier}
    compiled = _compiled_map(seed)
    contracts: dict[str, VehicleDynamicsContract] = {
        cid: build_vehicle_dynamics_contract(row) for cid, row in compiled.items()
    }
    survivors = [row for row in result.outcomes if row.status == "SURVIVED_SCREEN"]
    rejected = [row for row in result.outcomes if row.status.startswith("REJECTED_")]

    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise CandidateArchiveError(f"Shipyard design ledger not found: {path}")
    con = sqlite3.connect(str(path))
    try:
        ensure_schema(con)
        con.execute(
            """INSERT OR REPLACE INTO shipyard_campaign(
                campaign_id,version,experiment_hash,authority_status,candidate_count,
                survivor_count,rejected_count,pareto_count
            ) VALUES(?,?,?,?,?,?,?,?)""",
            (campaign_id, ARCHIVE_VERSION, result.experiment_hash, ARCHIVE_AUTHORITY,
             len(result.outcomes), len(survivors), len(rejected), len(pareto)),
        )
        for outcome in result.outcomes:
            artifact = compiled.get(outcome.candidate_id)
            contract = contracts.get(outcome.candidate_id)
            con.execute(
                """INSERT OR REPLACE INTO shipyard_candidate(
                    campaign_id,candidate_id,parent_candidate_id,generation,status,pareto_member,
                    choices_json,objective_json,rejection_reason,failed_constraints_json,
                    mass_kg,center_of_mass_json,governed_package_hash,semantic_glb_sha256,
                    dynamics_contract_hash,dynamics_authority,authority_status
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    campaign_id, outcome.candidate_id, outcome.lineage.parent_candidate_id,
                    int(outcome.lineage.generation), outcome.status, int(outcome.candidate_id in pareto),
                    _canonical(dict(outcome.lineage.choices)), _canonical(dict(outcome.objective_values)),
                    outcome.rejection_reason, _canonical(list(outcome.failed_constraint_ids)),
                    outcome.mass_kg,
                    None if outcome.center_of_mass_m is None else _canonical(list(outcome.center_of_mass_m)),
                    None if artifact is None else artifact.governed_package_hash,
                    None if artifact is None else artifact.glb_sha256,
                    None if contract is None else contract.contract_hash,
                    0,
                    ARCHIVE_AUTHORITY,
                ),
            )
        con.commit()
    finally:
        con.close()
    return campaign_id


def list_campaign_candidates(db_path: str | Path, campaign_id: str) -> list[ArchivedCandidate]:
    path = Path(db_path).expanduser().resolve()
    con = sqlite3.connect(str(path)); con.row_factory = sqlite3.Row
    try:
        ensure_schema(con)
        rows = con.execute(
            "SELECT * FROM shipyard_candidate WHERE campaign_id=? ORDER BY generation,candidate_id",
            (campaign_id,),
        ).fetchall()
        out: list[ArchivedCandidate] = []
        for row in rows:
            com = None if row["center_of_mass_json"] is None else tuple(json.loads(row["center_of_mass_json"]))
            out.append(ArchivedCandidate(
                campaign_id=row["campaign_id"], candidate_id=row["candidate_id"],
                parent_candidate_id=row["parent_candidate_id"], generation=int(row["generation"]),
                status=row["status"], pareto_member=bool(row["pareto_member"]),
                choices=json.loads(row["choices_json"]), objective_values=json.loads(row["objective_json"]),
                mass_kg=row["mass_kg"], center_of_mass_m=com,
                governed_package_hash=row["governed_package_hash"], semantic_glb_sha256=row["semantic_glb_sha256"],
                dynamics_contract_hash=row["dynamics_contract_hash"], dynamics_authority=bool(row["dynamics_authority"]),
                archive_authority=row["authority_status"],
            ))
        return out
    finally:
        con.close()


def campaign_summary(db_path: str | Path, campaign_id: str) -> dict[str, Any]:
    path = Path(db_path).expanduser().resolve()
    con = sqlite3.connect(str(path)); con.row_factory = sqlite3.Row
    try:
        ensure_schema(con)
        row = con.execute("SELECT * FROM shipyard_campaign WHERE campaign_id=?", (campaign_id,)).fetchone()
        if row is None:
            raise CandidateArchiveError(f"campaign not found: {campaign_id}")
        result = dict(row)
        result["candidates"] = [asdict(x) for x in list_campaign_candidates(path, campaign_id)]
        result["summary_hash"] = _sha(result)
        return result
    finally:
        con.close()
