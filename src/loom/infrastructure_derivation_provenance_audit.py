"""Read-only Stage F-PA derivation/provenance audit for all infrastructure nodes.

The audit follows exact Git-backed WORLD references. It reports source/model
coverage and canon-document mention coverage without promoting any coordinate,
frame, orbit or navigation grade. Text mention is not treated as numerical
agreement; absence of a mention is not treated as a conflict.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import sqlite3

CONTRACT = "LOOM_F_PA_INFRASTRUCTURE_DERIVATION_PROVENANCE_V1"
ATLAS_REL = Path("canon/current/LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2.md")


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


def infrastructure_derivation_provenance_audit(repo_root: Path | str) -> dict[str, Any]:
    root = Path(repo_root).expanduser().resolve()
    world = root / "data" / "LOOM_2226.sqlite3"
    atlas_path = root / ATLAS_REL
    if not atlas_path.is_file():
        raise FileNotFoundError(atlas_path)
    atlas = atlas_path.read_text(encoding="utf-8")

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

    atlas_upper = atlas.upper()
    rows_out: list[dict[str, Any]] = []
    for row in nodes:
        node_id = str(row.get("node_id") or "")
        node_name = str(row.get("node_name") or "")
        id_mentioned = bool(node_id and node_id.upper() in atlas_upper)
        name_mentioned = bool(node_name and node_name.upper() in atlas_upper)
        text_constraint = (
            "EXPLICIT_NODE_ID_AND_NAME_MENTION"
            if id_mentioned and name_mentioned
            else "EXPLICIT_NODE_ID_MENTION"
            if id_mentioned
            else "EXPLICIT_NODE_NAME_MENTION"
            if name_mentioned
            else "GENERAL_OR_NO_NODE_SPECIFIC_ATLAS_CONSTRAINT"
        )
        # This pass can establish provenance/reference coverage and text mention
        # coverage. It cannot certify semantic numerical agreement merely by
        # matching prose tokens, so conflict remains explicitly unproven unless a
        # governed machine-readable comparison exists.
        rows_out.append({
            **row,
            "PRIMARY_STRUCTURED_SOURCE": "WORLD_SQL",
            "REFERENCED_MODEL_SOURCE": row.get("derivation_model_id") or row.get("location_model_id") or row.get("state_model_id"),
            "TEXT_CANON_CONSTRAINT": text_constraint,
            "SOURCE_CONFLICT_STATUS": "NO_MACHINE_DEMONSTRATED_CONFLICT",
            "SPATIAL_DERIVABILITY": "CONSTRAINED_DESIGN_REQUIRED",
            "DERIVATION_STANDARD_OR_METHOD": "EXISTING_WORLD_ENGINEERING_REFERENCE_REQUIRES_QUALIFICATION",
            "QUALIFICATION_STATUS": "NON_NAVIGATION_GRADE_REDERIVATION_REQUIRED",
            "PROMOTION_TARGET": "WORLD_QUALIFIED_PHYSICAL_AUTHORITY",
            "atlas_node_id_mentioned": id_mentioned,
            "atlas_node_name_mentioned": name_mentioned,
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
        "source_conflict_status": _count([r.get("SOURCE_CONFLICT_STATUS") for r in rows_out]),
        "qualification_status": _count([r.get("QUALIFICATION_STATUS") for r in rows_out]),
    }
    return {
        "contract": CONTRACT,
        "world": str(world),
        "atlas": str(ATLAS_REL),
        "summary": summary,
        "source_tables": source_tables,
        "rows": rows_out,
    }
