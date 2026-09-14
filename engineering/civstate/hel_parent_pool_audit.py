#!/usr/bin/env python3
import argparse
import json
import sqlite3
from collections import defaultdict

HARD_FIELDS = (
    "resident_population",
    "workforce",
    "annual_value_added",
    "capital_stock",
    "replacement_value",
)

FORBIDDEN_DOWNSTREAM_TABLES = {
    "civ_node_texture_overlay",
    "civ_place_dna",
    "civ_social_pressure",
    "civ_social_state",
}

CURRENT_DRIVER_TABLES = {
    "civ_governance_profile",
    "civ_influence_edge",
    "civ_census_node_relation",
}

IDENTITY_FIELDS = {
    "subject_id", "node_subject_id", "spatial_subject_id", "display_name",
    "navigator_entity_id", "navigator_node_id", "navigator_noun_id",
    "year", "derivation_id",
}

SUBJECT_KEY_PRIORITY = (
    "node_subject_id", "subject_id", "spatial_subject_id", "entity_subject_id",
    "zone_subject_id", "parent_subject_id",
)


def compare_pool(parent_total, named_total, comparable):
    if not comparable:
        return {"status": "SEMANTICS_UNRESOLVED", "parent_total": parent_total,
                "named_total": named_total, "residual": None}
    residual = float(parent_total) - float(named_total)
    status = "COMPARABLE" if residual >= -1e-9 else "OVERALLOCATED_OR_SEMANTIC_MISMATCH"
    return {"status": status, "parent_total": parent_total,
            "named_total": named_total, "residual": residual}


def filter_additional_driver_tables(table_names):
    return sorted(t for t in table_names if t.startswith("civ_") and t not in FORBIDDEN_DOWNSTREAM_TABLES)


def qident(name):
    return '"' + name.replace('"', '""') + '"'


def table_columns(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({qident(table)})")]


def all_tables(conn):
    return [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'civ_%' ORDER BY name"
    )]


def choose_subject_key(columns):
    for key in SUBJECT_KEY_PRIORITY:
        if key in columns:
            return key
    return None


def year_clause(columns):
    return " AND (year=2226 OR year IS NULL)" if "year" in columns else ""


def scalar_rows(conn, table, key, ids):
    if not ids:
        return []
    cols = table_columns(conn, table)
    placeholders = ",".join("?" for _ in ids)
    sql = f"SELECT * FROM {qident(table)} WHERE {qident(key)} IN ({placeholders}){year_clause(cols)}"
    cur = conn.execute(sql, tuple(ids))
    names = [d[0] for d in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]


def cardinality(values):
    normalized = []
    for v in values:
        if isinstance(v, float):
            normalized.append(round(v, 12))
        else:
            normalized.append(v)
    return len(set(normalized))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    args = ap.parse_args()

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    tables = all_tables(conn)
    required = {"civ_subject", "civ_infrastructure_state", "civ_census_node_relation"}
    missing_required = sorted(required - set(tables))
    if missing_required:
        print(json.dumps({"schema": "LOOM_CIVSTATE_HEL_PARENT_POOL_AUDIT_V1",
                          "status": "FAIL_MISSING_REQUIRED_TABLES",
                          "missing": missing_required}, indent=2, sort_keys=True))
        raise SystemExit(2)

    subject_cols = table_columns(conn, "civ_subject")
    hel_subject_rows = conn.execute(
        "SELECT * FROM civ_subject WHERE subject_id LIKE 'NODE:HEL-%' ORDER BY subject_id"
    ).fetchall()
    hel_nodes = [r["subject_id"] for r in hel_subject_rows]
    hel_entities = sorted({r["spatial_subject_id"] for r in hel_subject_rows
                           if "spatial_subject_id" in subject_cols and r["spatial_subject_id"]})
    parent_subjects = sorted({r["parent_subject_id"] for r in hel_subject_rows
                              if "parent_subject_id" in subject_cols and r["parent_subject_id"]})

    rel_cols = table_columns(conn, "civ_census_node_relation")
    rel_rows = scalar_rows(conn, "civ_census_node_relation", "node_subject_id", hel_nodes)
    zone_ids = sorted({r.get("zone_subject_id") for r in rel_rows if r.get("zone_subject_id")})

    candidate_parent_ids = sorted(set(zone_ids + parent_subjects + hel_entities))

    infra_cols = table_columns(conn, "civ_infrastructure_state")
    infra_rows = scalar_rows(conn, "civ_infrastructure_state", "node_subject_id", hel_nodes)
    named_totals = {}
    for field in HARD_FIELDS:
        if field in infra_cols:
            vals = [r.get(field) for r in infra_rows if isinstance(r.get(field), (int, float))]
            named_totals[field] = sum(vals) if vals else None
        else:
            named_totals[field] = None

    pool_candidates = defaultdict(list)
    for table in tables:
        if table == "civ_infrastructure_state":
            continue
        cols = table_columns(conn, table)
        key = choose_subject_key(cols)
        if not key:
            continue
        matching_fields = [f for f in HARD_FIELDS if f in cols]
        if not matching_fields:
            continue
        rows = scalar_rows(conn, table, key, candidate_parent_ids)
        for row in rows:
            for field in matching_fields:
                val = row.get(field)
                if isinstance(val, (int, float)):
                    pool_candidates[field].append({
                        "table": table,
                        "subject_key": key,
                        "subject_value": row.get(key),
                        "value": val,
                        "comparison_basis": "EXACT_FIELD_NAME_AND_PARENT_CANDIDATE_ID",
                    })

    pool_results = {}
    for field in HARD_FIELDS:
        candidates = pool_candidates.get(field, [])
        named_total = named_totals.get(field)
        comparisons = []
        for c in candidates:
            # Exact field-name continuity is evidence of unit compatibility, but not enough
            # to assert allocation-parent semantics. Keep arithmetic unresolved until an
            # explicit binding is found.
            comp = compare_pool(c["value"], named_total, comparable=False)
            comparisons.append({**c, **comp})
        pool_results[field] = {
            "named_infrastructure_total": named_total,
            "parent_candidates": comparisons,
            "allocation_parent_binding": "UNRESOLVED" if comparisons else "NOT_FOUND",
        }

    # Discover additional non-downstream HEL-keyed state that could expand the upstream
    # evidence surface. Variation is reported only; no field becomes allocator-authoritative.
    additional_driver_evidence = []
    target_ids = hel_nodes + hel_entities
    for table in filter_additional_driver_tables(tables):
        if table in CURRENT_DRIVER_TABLES or table in {"civ_infrastructure_state", "civ_subject", "civ_census_node_relation"}:
            continue
        cols = table_columns(conn, table)
        key = choose_subject_key(cols)
        if not key:
            continue
        rows = scalar_rows(conn, table, key, target_ids)
        if not rows:
            continue
        varying = []
        constants = []
        for field in cols:
            if field in IDENTITY_FIELDS or field == key:
                continue
            vals = [r.get(field) for r in rows if r.get(field) is not None]
            if not vals:
                continue
            (varying if cardinality(vals) > 1 else constants).append(field)
        additional_driver_evidence.append({
            "table": table,
            "subject_key": key,
            "row_count": len(rows),
            "varying_fields": varying,
            "constant_fields": constants,
            "allocator_authority": "EVIDENCE_ONLY_REQUIRES_SEPARATE_CAUSAL_QUALIFICATION",
        })

    # Capture A20 verbatim from the database when available.
    assumptions = []
    if "civ_assumption" in tables:
        cols = table_columns(conn, "civ_assumption")
        if "assumption_id" in cols:
            cur = conn.execute("SELECT * FROM civ_assumption WHERE assumption_id IN ('A08','A20') ORDER BY assumption_id")
            names = [d[0] for d in cur.description]
            assumptions = [dict(zip(names, row)) for row in cur.fetchall()]

    output = {
        "schema": "LOOM_CIVSTATE_HEL_PARENT_POOL_AUDIT_V1",
        "scope": "HEL_PARENT_ALLOCATION_POOLS_AND_ADDITIONAL_UPSTREAM_EVIDENCE",
        "status": "PASS",
        "mutation_authority": "ZERO",
        "allocator_implementation_authority": "ZERO",
        "coefficient_invention_authority": "ZERO",
        "hel_node_count": len(hel_nodes),
        "hel_nodes": hel_nodes,
        "hel_entities": hel_entities,
        "parent_subject_ids": parent_subjects,
        "census_zone_ids": zone_ids,
        "candidate_parent_ids": candidate_parent_ids,
        "named_infrastructure_totals": named_totals,
        "parent_pool_results": pool_results,
        "additional_upstream_evidence": additional_driver_evidence,
        "locked_assumptions": assumptions,
        "semantic_guardrail": "DO_NOT_COMPUTE_OR_CONSUME_A_RESIDUAL_UNTIL_PARENT_BINDING_AND_FIELD_SEMANTICS_ARE_EXPLICITLY_QUALIFIED",
        "additional_driver_guardrail": "VARIATION_OUTSIDE_THE_CURRENT_DRIVER_SET_IS_EVIDENCE_ONLY_NOT_ALLOCATOR_AUTHORITY",
        "next_action": "QUALIFY_EXPLICIT_PARENT_BINDINGS_AND_ANY_ADDITIONAL_UPSTREAM_DRIVER_CAUSALITY_BEFORE_REALLOCATION",
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
