"""Read-only Stage F-PA derivation/provenance audit for all infrastructure nodes.

The audit follows exact Git-backed WORLD references. It reports source/model
coverage and governed text-canon mention coverage without promoting any
coordinate, frame, orbit or navigation grade. Text mention is not treated as
numerical agreement; absence of a mention is not treated as a conflict.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import sqlite3

CONTRACT = "LOOM_F_PA_INFRASTRUCTURE_DERIVATION_PROVENANCE_V2"
ATLAS_REL = Path("canon/current/LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2.md")
CANON_I_REL = Path("canon/current/LOOM_2226_CANON_I_World_History_Frontier_v2.4.md")


def _connect(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(path)
    conn = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})")]


def _table_rows(conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(f"SELECT * FROM {table}")]


def _count(values: list[Any]) -> dict[str, int]:
    c = Counter("<NULL>" if value is None else str(value) for value in values)
    return dict(sorted(c.items()))


def _index(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(row[key]): row for row in rows if row.get(key) is not None}


def _mention(text_upper: str, node_id: str, node_name: str) -> str:
    id_mentioned = bool(node_id and node_id.upper() in text_upper)
    name_mentioned = bool(node_name and node_name.upper() in text_upper)
    if id_mentioned and name_mentioned:
        return "EXPLICIT_NODE_ID_AND_NAME_MENTION"
    if id_mentioned:
        return "EXPLICIT_NODE_ID_MENTION"
    if name_mentioned:
        return "EXPLICIT_NODE_NAME_MENTION"
    return "NO_NODE_SPECIFIC_MENTION"


def infrastructure_derivation_provenance_audit(repo_root: Path | str) -> dict[str, Any]:
    root = Path(repo_root).expanduser().resolve()
    world = root / "data" / "LOOM_2226.sqlite3"
    atlas_path = root / ATLAS_REL
    canon_i_path = root / CANON_I_REL
    for path in (atlas_path, canon_i_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    atlas_upper = atlas_path.read_text(encoding="utf-8").upper()
    canon_i_upper = canon_i_path.read_text(encoding="utf-8").upper()

    with _connect(world) as conn:
        nodes = [dict(row) for row in conn.execute(
            """
            SELECT
                n.node_id,n.node_name,n.system,n.parent_body,n.facility_type,
                n.source AS node_source,n.entity_id,n.parent_entity_id,
                l.model_id AS location_model_id,l.position_authority,
                l.frame_family,l.geometry_kind,l.precision_class,
                o.source_id AS orbit_source_id,o.derivation_model_id,
                o.epistemic_status AS orbit_epistemic_status,
                s.state_source,s.model_id AS state_model_id,s.validity_status
            FROM infrastructure_nodes n
            LEFT JOIN entity_location_models l ON l.entity_id=n.entity_id
            LEFT JOIN orbit_geometry_models o ON o.entity_id=n.entity_id
            LEFT JOIN spatial_states s ON s.entity_id=n.entity_id
            ORDER BY n.node_id
            """
        )]

        source_tables: dict[str, dict[str, Any]] = {}
        for table in ("placement_models", "derivation_models", "provenance_sources"):
            source_tables[table] = {
                "columns": _table_columns(conn, table),
                "rows": _table_rows(conn, table),
            }

    placement_by_id = _index(source_tables["placement_models"]["rows"], "model_id")
    derivation_by_id = _index(source_tables["derivation_models"]["rows"], "model_id")
    provenance_by_id = _index(source_tables["provenance_sources"]["rows"], "source_id")

    rows_out: list[dict[str, Any]] = []
    for row in nodes:
        node_id = str(row.get("node_id") or "")
        node_name = str(row.get("node_name") or "")
        atlas_mention = _mention(atlas_upper, node_id, node_name)
        canon_i_mention = _mention(canon_i_upper, node_id, node_name)

        placement = placement_by_id.get(str(row.get("location_model_id") or ""))
        derivation = derivation_by_id.get(str(row.get("derivation_model_id") or ""))
        orbit_source = provenance_by_id.get(str(row.get("orbit_source_id") or ""))
        derivation_source = None
        if derivation is not None and derivation.get("source_id") is not None:
            derivation_source = provenance_by_id.get(str(derivation["source_id"]))

        provenance_complete = all(
            item is not None for item in (placement, derivation, orbit_source, derivation_source)
        )
        if canon_i_mention != "NO_NODE_SPECIFIC_MENTION":
            text_constraint = "CANON_I_NODE_SPECIFIC"
        elif atlas_mention != "NO_NODE_SPECIFIC_MENTION":
            text_constraint = "ATLAS_NODE_SPECIFIC"
        else:
            text_constraint = "GENERAL_CANON_CONTEXT_ONLY"

        rows_out.append({
            **row,
            "PRIMARY_STRUCTURED_SOURCE": "WORLD_SQL",
            "REFERENCED_MODEL_SOURCE": row.get("derivation_model_id") or row.get("location_model_id") or row.get("state_model_id"),
            "TEXT_CANON_CONSTRAINT": text_constraint,
            "SOURCE_CONFLICT_STATUS": "NO_CONFLICT_DEMONSTRATED_AUDIT_ONLY_NO_PROMOTION",
            "SPATIAL_DERIVABILITY": "CONSTRAINED_DESIGN_REQUIRED",
            "DERIVATION_STANDARD_OR_METHOD": "EXISTING_WORLD_ENGINEERING_REFERENCE_REQUIRES_QUALIFICATION",
            "QUALIFICATION_STATUS": "NON_NAVIGATION_GRADE_REDERIVATION_REQUIRED",
            "PROMOTION_TARGET": "WORLD_QUALIFIED_PHYSICAL_AUTHORITY",
            "atlas_mention": atlas_mention,
            "canon_i_mention": canon_i_mention,
            "placement_model_status": None if placement is None else placement.get("status"),
            "placement_model_provenance": None if placement is None else placement.get("provenance"),
            "derivation_model_status": None if derivation is None else derivation.get("status"),
            "derivation_model_source_id": None if derivation is None else derivation.get("source_id"),
            "orbit_source_authority_status": None if orbit_source is None else orbit_source.get("authority_status"),
            "derivation_source_authority_status": None if derivation_source is None else derivation_source.get("authority_status"),
            "provenance_chain_status": "COMPLETE_STRUCTURED_REFERENCE_CHAIN" if provenance_complete else "INCOMPLETE_STRUCTURED_REFERENCE_CHAIN",
        })

    summary = {
        "row_count": len(rows_out),
        "node_source": _count([r.get("node_source") for r in rows_out]),
        "location_model_id": _count([r.get("location_model_id") for r in rows_out]),
        "orbit_source_id": _count([r.get("orbit_source_id") for r in rows_out]),
        "derivation_model_id": _count([r.get("derivation_model_id") for r in rows_out]),
        "state_source": _count([r.get("state_source") for r in rows_out]),
        "state_model_id": _count([r.get("state_model_id") for r in rows_out]),
        "text_canon_constraint": _count([r.get("TEXT_CANON_CONSTRAINT") for r in rows_out]),
        "atlas_mention": _count([r.get("atlas_mention") for r in rows_out]),
        "canon_i_mention": _count([r.get("canon_i_mention") for r in rows_out]),
        "source_conflict_status": _count([r.get("SOURCE_CONFLICT_STATUS") for r in rows_out]),
        "qualification_status": _count([r.get("QUALIFICATION_STATUS") for r in rows_out]),
        "placement_model_status": _count([r.get("placement_model_status") for r in rows_out]),
        "derivation_model_status": _count([r.get("derivation_model_status") for r in rows_out]),
        "orbit_source_authority_status": _count([r.get("orbit_source_authority_status") for r in rows_out]),
        "derivation_source_authority_status": _count([r.get("derivation_source_authority_status") for r in rows_out]),
        "provenance_chain_status": _count([r.get("provenance_chain_status") for r in rows_out]),
    }
    return {
        "contract": CONTRACT,
        "world": str(world),
        "atlas": str(ATLAS_REL),
        "canon_i": str(CANON_I_REL),
        "summary": summary,
        "source_tables": source_tables,
        "rows": rows_out,
    }
