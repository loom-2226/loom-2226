"""Read-only Stage F-PA-3 audit of CIVSTATE vs physical-navigation authority.

This module inventories exact governed SQLite structure and linkage without
promoting civil/institutional data into trajectory or navigation authority.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import sqlite3

CIVSTATE_BOUNDARY_CONTRACT = "LOOM_F_PA_CIVSTATE_BOUNDARY_AUDIT_V1"


def _connect(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(path)
    conn = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _tables(conn: sqlite3.Connection) -> list[str]:
    return [
        str(r[0])
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(r[1]) for r in conn.execute(f"PRAGMA table_info({_q(table)})")]


def _count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {_q(table)}").fetchone()[0])


def _classify_table(name: str, columns: list[str]) -> tuple[str, list[str]]:
    """Conservative structural classification, not semantic promotion."""
    n = name.lower()
    cols = {c.lower() for c in columns}
    joined = " ".join(sorted(cols))

    cache_tokens = ("cache", "refresh", "materialized", "search_index")
    physical_tokens = (
        "x_km", "y_km", "z_km", "vx_km_s", "vy_km_s", "vz_km_s",
        "semi_major", "eccentricity", "inclination", "raan", "mean_anomaly",
        "reference_frame", "navigation_grade", "gm_km3", "latitude", "longitude",
        "lat_deg", "lon_deg", "elevation", "body_fixed", "prime_meridian",
    )
    civil_tokens = (
        "country", "population", "demographic", "economic", "gdp", "institution",
        "authority", "commercial", "ownership", "organization", "policy", "regime",
        "capacity", "employment", "trade", "mobility", "security", "governance",
    )
    linkage_tokens = ("entity_id", "node_id", "organization_id", "authority_id", "source_id")

    reasons: list[str] = []
    if any(tok in n or tok in joined for tok in cache_tokens):
        reasons.append("cache_or_derived_token")
    if any(tok in joined for tok in physical_tokens):
        reasons.append("physical_state_token")
    if any(tok in n or tok in joined for tok in civil_tokens):
        reasons.append("civil_context_token")
    if any(tok in cols for tok in linkage_tokens):
        reasons.append("shared_identity_linkage_token")

    if "physical_state_token" in reasons:
        classification = "PHYSICAL_NAVIGATION_CANDIDATE_REQUIRES_REVIEW"
    elif "cache_or_derived_token" in reasons:
        classification = "CACHE_OR_DERIVED_NONAUTHORITY"
    elif "civil_context_token" in reasons:
        classification = "CIVIL_INSTITUTIONAL_CONTEXT"
    elif "shared_identity_linkage_token" in reasons:
        classification = "SHARED_IDENTITY_OR_LINKAGE"
    else:
        classification = "UNCLASSIFIED_REVIEW_REQUIRED"
    return classification, reasons


def _distinct_nonnull(conn: sqlite3.Connection, table: str, column: str) -> list[str]:
    sql = f"SELECT DISTINCT {_q(column)} FROM {_q(table)} WHERE {_q(column)} IS NOT NULL ORDER BY 1"
    return [str(r[0]) for r in conn.execute(sql)]


def civstate_boundary_audit(world_path: Path | str, civstate_path: Path | str) -> dict[str, Any]:
    world = Path(world_path).expanduser().resolve()
    civ = Path(civstate_path).expanduser().resolve()

    with _connect(world) as w, _connect(civ) as c:
        infra_cols = _columns(w, "infrastructure_nodes")
        hub_cols = _columns(w, "transport_hubs")
        infra_entity_ids = set(_distinct_nonnull(w, "infrastructure_nodes", "entity_id"))
        infra_node_ids = set(_distinct_nonnull(w, "infrastructure_nodes", "node_id"))
        hub_entity_ids = set(_distinct_nonnull(w, "transport_hubs", "entity_id"))

        hub_entity_to_infra_entity = sorted(hub_entity_ids & infra_entity_ids)
        hub_entity_to_node_id = sorted(hub_entity_ids & infra_node_ids)

        # Compare all transport_hubs text/id-like columns to infrastructure identity domains.
        hub_identity_matches: dict[str, dict[str, list[str]]] = {}
        for col in hub_cols:
            lc = col.lower()
            if not (lc.endswith("_id") or lc in {"entity_id", "roadstead_id"}):
                continue
            vals = set(_distinct_nonnull(w, "transport_hubs", col))
            matches_entity = sorted(vals & infra_entity_ids)
            matches_node = sorted(vals & infra_node_ids)
            if matches_entity or matches_node:
                hub_identity_matches[col] = {
                    "matches_infrastructure_entity_id": matches_entity,
                    "matches_infrastructure_node_id": matches_node,
                }

        table_rows: list[dict[str, Any]] = []
        for table in _tables(c):
            cols = _columns(c, table)
            classification, reasons = _classify_table(table, cols)
            table_rows.append({
                "table": table,
                "row_count": _count(c, table),
                "columns": cols,
                "boundary_classification": classification,
                "classification_reasons": reasons,
            })

        # Exact cross-db identity-domain overlap, where CIVSTATE exposes entity_id/node_id.
        cross_db_identity: list[dict[str, Any]] = []
        for row in table_rows:
            table = str(row["table"])
            cols = set(str(x) for x in row["columns"])
            item: dict[str, Any] = {"table": table}
            meaningful = False
            if "entity_id" in cols:
                vals = set(_distinct_nonnull(c, table, "entity_id"))
                item["entity_id_distinct"] = len(vals)
                item["entity_id_matches_world_infrastructure"] = len(vals & infra_entity_ids)
                meaningful = True
            if "node_id" in cols:
                vals = set(_distinct_nonnull(c, table, "node_id"))
                item["node_id_distinct"] = len(vals)
                item["node_id_matches_world_infrastructure"] = len(vals & infra_node_ids)
                meaningful = True
            if meaningful:
                cross_db_identity.append(item)

    classification_counts = dict(sorted(Counter(r["boundary_classification"] for r in table_rows).items()))
    return {
        "contract": CIVSTATE_BOUNDARY_CONTRACT,
        "world": str(world),
        "civstate": str(civ),
        "civstate_table_count": len(table_rows),
        "classification_counts": classification_counts,
        "tables": table_rows,
        "transport_hubs": {
            "row_count": len(hub_entity_ids),
            "entity_ids": sorted(hub_entity_ids),
            "direct_entity_id_matches_infrastructure_entity_id": hub_entity_to_infra_entity,
            "direct_entity_id_matches_infrastructure_node_id": hub_entity_to_node_id,
            "identity_column_matches": hub_identity_matches,
            "infrastructure_identity_columns": infra_cols,
        },
        "cross_db_identity": cross_db_identity,
    }
