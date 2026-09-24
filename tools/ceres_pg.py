#!/usr/bin/env python3
"""Development-only, lossless Ceres source projection into a versioned LOOM PostgreSQL slice.

The current Atlas service is untouched. Source SQLite files are opened read-only.
Unresolved values remain in named, typed source tables and are labeled in
loom_control.field_semantics; they are never silently promoted to world facts.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import sqlite3
import struct
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "data/postgres/ceres_source_contract_v1.json"
MIGRATION_DIR = ROOT / "data/postgres/migrations"
MATRIX_PATH = ROOT / "docs/database_semantics/LOOM_WHOLE_SYSTEM_POSTGRES_GATE_A_ADMISSION_MATRIX_v0.1.json"
MANIFEST_PATH = ROOT / "docs/ceres/manifest.json"
MVP_A_PATH = ROOT / "data/postgres/evidence/LOOM_CERES_MVP_A_FIELD_QUALIFICATION_v0.1.json"
MVP_A_SHA256 = "2cf54b1626793e70f36c0412e0a4f6677d6c227c6455ed3b07fbbdb78c4be885"
SOURCE_PATHS = {
    "WORLD": ROOT / "data/LOOM_2226.sqlite3",
    "CIVSTATE": ROOT / "data/LOOM_2226_CIVSTATE.sqlite3",
    "MEDIA": Path("/tmp/loom_ceres_source/LOOM_2226_media.sqlite3"),
}
SOURCE_ROLES = {
    "WORLD": "repository WORLD SQLite",
    "CIVSTATE": "repository CIVSTATE SQLite",
    "MEDIA": "v0.1.0-runtime-baseline MEDIA release asset 542245032",
}
ATLAS_TABLES = {
    "WORLD": ["entities", "celestial_properties", "celestial_dynamics", "infrastructure_nodes"],
    "CIVSTATE": ["civ_demographic_state", "civ_economic_state", "civ_workforce_state",
                 "civ_runtime_place_context", "civ_infrastructure_state", "civ_social_state",
                 "civ_governance_profile", "civ_social_pressure", "civ_census_node_relation",
                 "v_graph_civstate_influence_edges", "civ_subject"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def psql(database: str, sql: str | None = None, *, file: Path | None = None,
         single_transaction: bool = False, extra: list[str] | None = None) -> str:
    args = ["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-d", database]
    if single_transaction:
        args.append("--single-transaction")
    if file:
        args += ["-f", str(file)]
    if sql:
        args += ["-c", sql]
    args += extra or []
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"psql failed: {result.stderr.strip()}")
    return result.stdout.strip()


def pg_json(database: str, sql: str, snapshot_id: str | None = None) -> object:
    prefix = ""
    if snapshot_id:
        prefix = f"SET loom.snapshot_id = {sql_literal(snapshot_id)}; SET search_path = loom_ceres; "
    return json.loads(psql(database, prefix + sql))


def contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text())


def validate_inputs(spec: dict, paths: dict[str, Path]) -> dict[str, str]:
    found = {key: sha256(path) for key, path in paths.items()}
    if found != spec["source_sha256"]:
        raise RuntimeError(f"SQLite source hash mismatch: expected {spec['source_sha256']}; found {found}")
    if sha256(MANIFEST_PATH) != spec["manifest_sha256"]:
        raise RuntimeError("Ceres manifest hash differs from consumer contract")
    if sha256(MATRIX_PATH) != spec["semantic_matrix_sha256"]:
        raise RuntimeError("Gate-A matrix hash differs from recorded semantic contract")
    if sha256(MVP_A_PATH) != MVP_A_SHA256:
        raise RuntimeError("MVP-A qualification evidence hash differs from the original")
    consumer = subprocess.check_output(
        ["git", "show", f"{spec['consumer_git_commit']}:{spec['consumer_query_path']}"], cwd=ROOT)
    if hashlib.sha256(consumer).hexdigest() != spec["consumer_query_blob_sha256"]:
        raise RuntimeError("Atlas consumer query revision changed")
    for table in spec["tables"]:
        with sqlite3.connect(f"file:{paths[table['database']]}?mode=ro&immutable=1", uri=True) as source:
            actual = [(r[1], r[2], r[5]) for r in source.execute(f"PRAGMA table_info('{table['table']}')")]
        expected = [(r["name"], r["source_type"], r["pk_order"]) for r in table["columns"]]
        if actual != expected:
            raise RuntimeError(f"Source column shape changed: {table['database']}.{table['table']}")
    for view in spec["views"]:
        with sqlite3.connect(f"file:{paths[view['database']]}?mode=ro&immutable=1", uri=True) as source:
            definition = source.execute("SELECT sql FROM sqlite_master WHERE name=?", (view["name"],)).fetchone()[0]
            cols = [r[1] for r in source.execute(f"PRAGMA table_info('{view['name']}')")]
        if hashlib.sha256(definition.encode()).hexdigest() != view["sqlite_definition_sha256"] or cols != view["columns"]:
            raise RuntimeError(f"Source view changed: {view['name']}")
    return found


def migrate(database: str) -> str:
    outcome = []
    for migration in sorted(MIGRATION_DIR.glob("[0-9][0-9][0-9]_*.sql")):
        revision, script_hash = migration.stem, sha256(migration)
        exists = psql(database, "SELECT to_regclass('loom_control.schema_migration') IS NOT NULL")
        prior = (psql(database, f"SELECT script_sha256 FROM loom_control.schema_migration "
                      f"WHERE revision={sql_literal(revision)}") if exists == "t" else "")
        if prior:
            if prior != script_hash:
                raise RuntimeError(f"Migration hash changed after application: {revision}")
            outcome.append(f"{revision}: already applied")
            continue
        insert = ("INSERT INTO loom_control.schema_migration(revision,script_sha256) VALUES "
                  f"({sql_literal(revision)},{sql_literal(script_hash)})")
        psql(database, insert, file=migration, single_transaction=True)
        outcome.append(f"{revision}: applied")
    return "; ".join(outcome)


def select_rows(source: sqlite3.Connection, table: str, where: str = "1=1",
                params: tuple = ()) -> list[dict]:
    source.row_factory = sqlite3.Row
    return [dict(row) for row in source.execute(f"SELECT * FROM {table} WHERE {where}", params)]


def by_key(rows: list[dict], key: str) -> dict:
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate selected identity in {key}")
    return result


def selected_rows(spec: dict, paths: dict[str, Path]) -> tuple[dict[tuple[str, str], list[dict]], list[dict]]:
    connections = {key: sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
                   for key, path in paths.items()}
    try:
        world, civ, media = (connections[key] for key in ("WORLD", "CIVSTATE", "MEDIA"))
        manifest = json.loads(MANIFEST_PATH.read_text())
        node_ids = {row["node_id"] for row in manifest}
        if node_ids != {f"CER-P{i:02}" for i in range(1, 6)}:
            raise RuntimeError("Manifest facility identity set changed")
        node_subjects = {f"NODE:{node}" for node in node_ids}
        body = "BODY:CERES:CERES"
        result: dict[tuple[str, str], list[dict]] = {}

        def put(database: str, table: str, connection: sqlite3.Connection,
                where: str, params: tuple = ()) -> list[dict]:
            rows = select_rows(connection, table, where, params)
            result[(database, table)] = rows
            return rows

        facilities = put("WORLD", "infrastructure_nodes", world,
                         "parent_entity_id='CER' AND node_id LIKE 'CER-P%'")
        if {r["node_id"] for r in facilities} != node_ids:
            raise RuntimeError("WORLD facility identity set differs from manifest")
        entity_ids = {"CER", "SOL"} | node_ids | {r["entity_id"] for r in facilities}
        entity_ids |= {r["parent_entity_id"] for r in facilities if r["parent_entity_id"]}
        all_entities = by_key(select_rows(world, "entities"), "entity_id")
        pending = list(entity_ids)
        while pending:
            item = pending.pop()
            if item not in all_entities:
                raise RuntimeError(f"Missing WORLD entity {item}")
            parent = all_entities[item]["parent_entity_id"]
            if parent and parent not in entity_ids:
                entity_ids.add(parent)
                pending.append(parent)
        result[("WORLD", "entities")] = [all_entities[key] for key in sorted(entity_ids)]
        put("WORLD", "celestial_properties", world, "entity_id='CER'")
        put("WORLD", "celestial_dynamics", world, "entity_id='CER'")
        asset_ids = {r["asset_id"] for r in manifest} | {spec["media_body_hero"]["asset_id"]}
        all_assets = by_key(select_rows(world, "image_assets"), "asset_id")
        if not asset_ids <= all_assets.keys():
            raise RuntimeError("Approved WORLD image asset is missing")
        result[("WORLD", "image_assets")] = [all_assets[key] for key in sorted(asset_ids)]
        noun_ids = {r["entity_id"] for r in result[("WORLD", "image_assets")]} | {r["noun_id"] for r in manifest}
        all_nouns = by_key(select_rows(world, "knowledge_entities"), "noun_id")
        if not noun_ids <= all_nouns.keys():
            raise RuntimeError("WORLD media noun mapping is missing")
        result[("WORLD", "knowledge_entities")] = [all_nouns[key] for key in sorted(noun_ids)]
        source_ids = {r["source_id"] for r in result[("WORLD", "celestial_properties")] if r["source_id"]}
        result[("WORLD", "provenance_sources")] = [r for r in select_rows(world, "provenance_sources")
                                                     if r["source_id"] in source_ids]

        zones = select_rows(civ, "civ_subject", "parent_subject_id=? AND subject_class='CENSUS_ZONE'", (body,))
        if len(zones) != 3:
            raise RuntimeError("Expected three Ceres census-zone subjects")
        zone_ids = {r["subject_id"] for r in zones}
        edges = put("CIVSTATE", "civ_influence_edge", civ,
                    "year=2226 AND subject_id LIKE 'NODE:CER-P%'")
        subject_ids = {body} | node_subjects | zone_ids | {r["actor_subject_id"] for r in edges}
        subject_ids |= {r["subject_id"] for r in select_rows(civ, "civ_subject",
                                 "subject_id LIKE 'NOUN:%' AND active_2226=1")}
        all_subjects = by_key(select_rows(civ, "civ_subject"), "subject_id")
        pending = list(subject_ids)
        while pending:
            item = pending.pop()
            if item not in all_subjects:
                raise RuntimeError(f"Missing CIVSTATE subject {item}")
            parent = all_subjects[item]["parent_subject_id"]
            if parent and parent not in subject_ids:
                subject_ids.add(parent)
                pending.append(parent)
        result[("CIVSTATE", "civ_subject")] = [all_subjects[key] for key in sorted(subject_ids)]
        targets = {
            "civ_demographic_state": ("year=2226 AND subject_id IN (" + ",".join("?" * (len(zone_ids) + 1)) + ")", tuple(sorted(zone_ids | {body}))),
            "civ_economic_state": ("subject_id=? AND year=2226", (body,)),
            "civ_workforce_state": ("subject_id=? AND year=2226 AND sector_id='ALL'", (body,)),
            "civ_place_dna": ("year=2226 AND subject_id LIKE 'NODE:CER-P%'", ()),
            "civ_governance_profile": ("year=2226 AND subject_id LIKE 'NODE:CER-P%'", ()),
            "civ_infrastructure_state": ("year=2226 AND node_subject_id LIKE 'NODE:CER-P%'", ()),
            "civ_social_state": ("year=2226 AND subject_id LIKE 'NODE:CER-P%'", ()),
            "civ_social_pressure": ("year=2226 AND subject_id LIKE 'NODE:CER-P%'", ()),
            "civ_census_node_relation": ("year=2226 AND node_subject_id LIKE 'NODE:CER-P%'", ()),
        }
        for table, (where, params) in targets.items():
            put("CIVSTATE", table, civ, where, params)
        derivation_ids = {row["derivation_id"] for (db, table), rows in result.items()
                          if db == "CIVSTATE" and table not in ("civ_subject", "civ_influence_edge")
                          for row in rows if "derivation_id" in row and row["derivation_id"]}
        derivation_ids |= {r["derivation_id"] for r in edges if r["derivation_id"]}
        all_derivations = by_key(select_rows(civ, "civ_derivation"), "derivation_id")
        if not derivation_ids <= all_derivations.keys():
            raise RuntimeError("CIVSTATE derivation registry is incomplete")
        result[("CIVSTATE", "civ_derivation")] = [all_derivations[key] for key in sorted(derivation_ids)]
        run_ids = {r["run_id"] for r in result[("CIVSTATE", "civ_derivation")] if r["run_id"]}
        all_runs = by_key(select_rows(civ, "civ_model_run"), "run_id")
        if not run_ids <= all_runs.keys():
            raise RuntimeError("CIVSTATE model-run registry is incomplete")
        result[("CIVSTATE", "civ_model_run")] = [all_runs[key] for key in sorted(run_ids)]

        media_keys = {r["media_key"] for r in manifest} | {spec["media_body_hero"]["media_key"]}
        media_rows = select_rows(media, "media_assets",
                                 "media_key IN (" + ",".join("?" * len(media_keys)) + ")",
                                 tuple(sorted(media_keys)))
        if {r["media_key"] for r in media_rows} != media_keys:
            raise RuntimeError("MEDIA source is missing an approved Ceres image")
        for row in media_rows:
            content = row["original_blob"]
            if hashlib.sha256(content).hexdigest() != row["original_sha256"] or len(content) != row["original_byte_length"]:
                raise RuntimeError(f"MEDIA source blob integrity failed: {row['media_key']}")
        result[("MEDIA", "media_assets")] = media_rows
        if set(result) != {(t["database"], t["table"]) for t in spec["tables"]}:
            raise RuntimeError("Importer did not select every contracted source table")
        return result, manifest
    finally:
        for connection in connections.values():
            connection.close()


def copy_cell(value: object) -> str:
    if value is None:
        return r"\N"
    if isinstance(value, bytes):
        value = r"\x" + value.hex()
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise RuntimeError("Non-finite SQLite REAL requires an explicit representation decision")
        value = repr(value)
    elif isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    else:
        value = str(value)
    return '"' + value.replace('"', '""') + '"'


def write_copy(stream, table: str, columns: list[str], rows: list[dict]) -> None:
    stream.write(f"COPY {table} ({', '.join(columns)}) FROM STDIN WITH (FORMAT csv, NULL '\\N');\n")
    for row in rows:
        stream.write(",".join(copy_cell(row[col]) for col in columns) + "\n")
    stream.write("\\.\n")


def snapshot_id(spec: dict) -> str:
    material = json.dumps({"sources": spec["source_sha256"], "manifest": spec["manifest_sha256"],
                           "consumer": spec["consumer_git_commit"], "contract": sha256(CONTRACT_PATH)},
                          sort_keys=True).encode()
    return "ceres-v1-" + hashlib.sha256(material).hexdigest()[:32]


def presentation_label(column: dict) -> str:
    status = column["semantic_status"]
    embedded = column.get("embedded_claim_status") or "NOT_APPLICABLE"
    if status in ("UNRESOLVED", "NOT_ASSESSED") or embedded in ("UNRESOLVED", "NOT_ASSESSED"):
        return "Unresolved legacy data"
    if status == "QUALIFIED" and column.get("qualified_row_filter"):
        return "Qualified only within recorded row filter; unresolved legacy elsewhere"
    return status


def import_snapshot(database: str, spec: dict, paths: dict[str, Path], selected: dict,
                    manifest: list[dict]) -> tuple[str, str]:
    sid = snapshot_id(spec)
    existing = psql(database, f"SELECT state FROM loom_control.snapshot WHERE snapshot_id={sql_literal(sid)}")
    if existing:
        if existing not in ("CANDIDATE", "VALIDATED"):
            raise RuntimeError("Existing snapshot is retired")
        return sid, "already present; verification required"
    with tempfile.NamedTemporaryFile("w", suffix=".sql", prefix="loom_ceres_import_", delete=False) as temp:
        script = Path(temp.name)
        temp.write("INSERT INTO loom_control.semantic_version(semantic_sha256,source_path) VALUES "
                   f"({sql_literal(spec['semantic_matrix_sha256'])},{sql_literal(str(MATRIX_PATH.relative_to(ROOT)))}) "
                   "ON CONFLICT DO NOTHING;\n")
        for db, path in paths.items():
            digest = spec["source_sha256"][db]
            location = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else SOURCE_ROLES[db]
            temp.write("INSERT INTO loom_control.source_artifact "
                       "(artifact_sha256,source_role,source_path,byte_count,retained_location) VALUES "
                       f"({sql_literal(digest)},{sql_literal(db)},{sql_literal(SOURCE_ROLES[db])},"
                       f"{path.stat().st_size},{sql_literal(location)}) ON CONFLICT DO NOTHING;\n")
        temp.write("INSERT INTO loom_control.snapshot "
                   "(snapshot_id,consumer_git_commit,consumer_query_sha256,contract_sha256,semantic_sha256,state) VALUES "
                   f"({sql_literal(sid)},{sql_literal(spec['consumer_git_commit'])},"
                   f"{sql_literal(spec['consumer_query_blob_sha256'])},{sql_literal(sha256(CONTRACT_PATH))},"
                   f"{sql_literal(spec['semantic_matrix_sha256'])},'CANDIDATE');\n")
        for db in paths:
            temp.write("INSERT INTO loom_control.snapshot_source(snapshot_id,artifact_sha256,source_role) VALUES "
                       f"({sql_literal(sid)},{sql_literal(spec['source_sha256'][db])},{sql_literal(db)});\n")
        for table in spec["tables"]:
            db, name = table["database"], table["table"]
            rows = [{"snapshot_id": sid, **row} for row in selected[(db, name)]]
            columns = ["snapshot_id"] + [c["name"] for c in table["columns"]]
            write_copy(temp, f"{table['target_schema']}.{name}", columns, rows)
        manifest_rows = [{"snapshot_id": sid, **row} for row in manifest]
        manifest_cols = ["snapshot_id", "node_id", "name", "facility_type", "noun_id", "asset_id", "role",
                         "is_current", "review_status", "media_key", "civstate_zones", "export_status",
                         "filename", "sha256", "byte_length"]
        write_copy(temp, "loom_media.ceres_manifest_asset", manifest_cols, manifest_rows)
        relation_rows = [dict(snapshot_id=sid, node_id=row["node_id"], zone_subject_id=rel["zone"],
                              relationship_type=rel["relationship"], primary_relation=rel["primary"],
                              confidence=rel["confidence"], basis_code=rel["basis"])
                         for row in manifest for rel in row["civstate_zones"]]
        write_copy(temp, "loom_media.ceres_manifest_zone_relation",
                   ["snapshot_id", "node_id", "zone_subject_id", "relationship_type",
                    "primary_relation", "confidence", "basis_code"], relation_rows)
        semantic_rows = []
        for table in spec["tables"]:
            for column in table["columns"]:
                status = column["semantic_status"]
                semantic_rows.append(dict(
                    snapshot_id=sid, source_database=table["database"], source_table=table["table"],
                    source_column=column["name"], semantic_status=status,
                    presentation_label=presentation_label(column),
                    definition=column["semantic_definition"], unit=column["unit"], grain=column["grain"],
                    epoch_basis=column["epoch"], accounting_population_basis=column["basis"],
                    evidence_reference=(column["evidence_reference"] if isinstance(column["evidence_reference"], list)
                                        else [{"path": column["evidence_reference"]}]),
                    missing_evidence=column.get("specific_missing_evidence")))
        for name in manifest[0]:
            status = "STRUCTURAL" if name in ("node_id", "noun_id", "asset_id", "media_key", "civstate_zones") else (
                "QUALIFIED" if name in ("name", "facility_type") else "NOT_APPLICABLE")
            semantic_rows.append(dict(snapshot_id=sid, source_database="MANIFEST",
                                      source_table="docs/ceres/manifest.json", source_column=name,
                                      semantic_status=status, presentation_label=status,
                                      definition="Ceres approved media manifest field; exact source value retained",
                                      unit="category or identifier", grain="one facility asset",
                                      epoch_basis="manifest snapshot", accounting_population_basis="not applicable",
                                      evidence_reference=[{"path": "docs/ceres/manifest.json"}],
                                      missing_evidence=None))
        sem_cols = ["snapshot_id", "source_database", "source_table", "source_column", "semantic_status",
                    "presentation_label", "definition", "unit", "grain", "epoch_basis",
                    "accounting_population_basis", "evidence_reference", "missing_evidence"]
        write_copy(temp, "loom_control.field_semantics", sem_cols, semantic_rows)
    try:
        psql(database, file=script, single_transaction=True)
    finally:
        script.unlink(missing_ok=True)
    return sid, "imported"


def sync_lineage_and_semantics(database: str, spec: dict, sid: str) -> None:
    """Idempotently attach source keys and field claim labels to an imported snapshot."""
    evidence = {
        "MANIFEST": MANIFEST_PATH,
        "GATE_A_MATRIX": MATRIX_PATH,
        "MVP_A_QUALIFICATION": MVP_A_PATH,
        "MVP_A_DISPLAY_CONTRACT": ROOT / "docs/database_semantics/LOOM_CERES_MVP_A_DISPLAY_CONTRACT_v0.1.md",
    }
    with tempfile.NamedTemporaryFile("w", suffix=".sql", prefix="loom_ceres_lineage_", delete=False) as temp:
        script = Path(temp.name)
        for role, path in evidence.items():
            digest = sha256(path)
            rel = str(path.relative_to(ROOT))
            temp.write("INSERT INTO loom_control.source_artifact "
                       "(artifact_sha256,source_role,source_path,byte_count,retained_location) VALUES "
                       f"({sql_literal(digest)},{sql_literal(role)},{sql_literal(rel)},"
                       f"{path.stat().st_size},{sql_literal(rel)}) ON CONFLICT DO NOTHING;\n")
            temp.write("INSERT INTO loom_control.snapshot_source(snapshot_id,artifact_sha256,source_role) VALUES "
                       f"({sql_literal(sid)},{sql_literal(digest)},{sql_literal(role)}) "
                       "ON CONFLICT DO NOTHING;\n")
        for table in spec["tables"]:
            db, name, schema = table["database"], table["table"], table["target_schema"]
            for column in table["columns"]:
                status = column["semantic_status"]
                embedded = column.get("embedded_claim_status") or "NOT_APPLICABLE"
                label = presentation_label(column)
                temp.write("UPDATE loom_control.field_semantics SET "
                           f"embedded_claim_status={sql_literal(embedded)},"
                           f"admission_scope={sql_literal(column.get('admission_scope') or 'NONE')},"
                           f"qualified_row_filter={sql_literal(column.get('qualified_row_filter'))},"
                           f"presentation_label={sql_literal(label)} "
                           f"WHERE snapshot_id={sql_literal(sid)} AND source_database={sql_literal(db)} "
                           f"AND source_table={sql_literal(name)} AND source_column={sql_literal(column['name'])};\n")
            key_expr = ", ".join(f"{sql_literal(key)}, {key}" for key in table["primary_key"])
            temp.write("INSERT INTO loom_control.row_lineage "
                       "(snapshot_id,target_schema,target_table,source_database,source_table,source_artifact_sha256,source_key) "
                       f"SELECT snapshot_id,{sql_literal(schema)},{sql_literal(name)},{sql_literal(db)},"
                       f"{sql_literal(name)},{sql_literal(spec['source_sha256'][db])},"
                       f"jsonb_build_object({key_expr}) FROM {schema}.{name} "
                       f"WHERE snapshot_id={sql_literal(sid)} ON CONFLICT DO NOTHING;\n")
        manifest_sha = sha256(MANIFEST_PATH)
        temp.write("INSERT INTO loom_control.row_lineage "
                   "(snapshot_id,target_schema,target_table,source_database,source_table,source_artifact_sha256,source_key) "
                   "SELECT snapshot_id,'loom_media','ceres_manifest_asset','MANIFEST','docs/ceres/manifest.json',"
                   f"{sql_literal(manifest_sha)},jsonb_build_object('node_id',node_id) "
                   f"FROM loom_media.ceres_manifest_asset WHERE snapshot_id={sql_literal(sid)} "
                   "ON CONFLICT DO NOTHING;\n")
        temp.write("INSERT INTO loom_control.row_lineage "
                   "(snapshot_id,target_schema,target_table,source_database,source_table,source_artifact_sha256,source_key) "
                   "SELECT snapshot_id,'loom_media','ceres_manifest_zone_relation','MANIFEST',"
                   "'docs/ceres/manifest.json:civstate_zones',"
                   f"{sql_literal(manifest_sha)},jsonb_build_object('node_id',node_id,"
                   "'zone_subject_id',zone_subject_id,'relationship_type',relationship_type) "
                   f"FROM loom_media.ceres_manifest_zone_relation WHERE snapshot_id={sql_literal(sid)} "
                   "ON CONFLICT DO NOTHING;\n")
    try:
        psql(database, file=script, single_transaction=True)
    finally:
        script.unlink(missing_ok=True)


def canonical(value: object, target_type: str, from_pg: bool = False) -> object:
    if value is None:
        return None
    if target_type == "bytea":
        return bytes.fromhex(value[2:]) if from_pg else bytes(value)
    if target_type == "double precision":
        return struct.pack("!d", float(value)).hex()
    return value


class PgCursor:
    def __init__(self, rows: list[dict]):
        self.rows = rows

    def fetchall(self) -> list[dict]:
        return self.rows


class PgCompatConnection:
    """Read-only verification adapter for the Atlas consumer's exact SELECT statements."""
    def __init__(self, database: str, sid: str):
        self.database, self.sid, self.row_factory = database, sid, None

    def execute(self, sql: str, parameters: tuple = ()) -> PgCursor:
        if parameters or not sql.lstrip().upper().startswith("SELECT"):
            raise RuntimeError("Only Atlas's fixed, parameter-free read queries are supported")
        wrapped = f"SELECT coalesce(json_agg(row_to_json(q)), '[]'::json) FROM ({sql}) q"
        return PgCursor(pg_json(self.database, wrapped, self.sid))

    def close(self) -> None:
        pass


def atlas_payload_from_source(spec: dict, paths: dict[str, Path]) -> tuple[dict, object]:
    text = subprocess.check_output(["git", "show", f"{spec['consumer_git_commit']}:{spec['consumer_query_path']}"], cwd=ROOT)
    namespace = {"__name__": "ceres_atlas_verified_source", "__file__": str(ROOT / spec["consumer_query_path"])}
    exec(compile(text, namespace["__file__"], "exec"), namespace)
    source_payload = namespace["load_atlas_data"](paths["WORLD"], paths["CIVSTATE"])
    return source_payload, namespace


def verify(database: str, spec: dict, paths: dict[str, Path], selected: dict,
           manifest: list[dict], sid: str, report_path: Path) -> dict:
    report: dict = {"snapshot_id": sid, "consumer_git_commit": spec["consumer_git_commit"],
                    "source_sha256": spec["source_sha256"], "semantic_matrix_sha256": spec["semantic_matrix_sha256"],
                    "tables": [], "views": [], "manifest": {}, "media": {}, "atlas_payload": {},
                    "derived_values": {}, "referential_integrity": {}, "discrepancies": []}
    for table in spec["tables"]:
        db, name, schema = table["database"], table["table"], table["target_schema"]
        cols = table["columns"]
        names = [c["name"] for c in cols]
        order = ", ".join(table["primary_key"])
        query = ("SELECT coalesce(json_agg(row_to_json(q)), '[]'::json) FROM "
                 f"(SELECT {', '.join(names)} FROM {schema}.{name} "
                 f"WHERE snapshot_id={sql_literal(sid)} ORDER BY {order}) q")
        target = pg_json(database, query)
        source = sorted(selected[(db, name)], key=lambda r: tuple(r[k] for k in table["primary_key"]))
        item = {"database": db, "table": name, "postgres_table": f"{schema}.{name}",
                "source_rows": len(source), "postgres_rows": len(target),
                "columns": []}
        if len(source) != len(target):
            report["discrepancies"].append(f"{db}.{name}: row count {len(source)} != {len(target)}")
        for col in cols:
            key, typ = col["name"], col["target_type"]
            matches = len(source) == len(target) and all(
                canonical(a[key], typ) == canonical(b[key], typ, True)
                for a, b in zip(source, target))
            null_source = sum(r[key] is None for r in source)
            null_target = sum(r[key] is None for r in target)
            item["columns"].append({"column": key, "postgres_column": f"{schema}.{name}.{key}",
                                    "semantic_status": col["semantic_status"],
                                    "presentation_label": presentation_label(col),
                                    "source_nulls": null_source, "postgres_nulls": null_target,
                                    "exact_values_match": matches})
            if not matches:
                report["discrepancies"].append(f"{db}.{name}.{key}: value or row-order mismatch")
        report["tables"].append(item)
    view_source = {
        "civ_runtime_place_context": {
            **{name: "civ_subject." + name for name in
               ("subject_id", "display_name", "navigator_entity_id", "navigator_node_id")},
            **{name: "civ_place_dna." + name for name in
               ("governance_style", "security_posture", "commercial_openness", "corporate_proxy_level",
                "local_autonomy", "institutional_trust", "synthetic_acceptance", "migration_openness",
                "frontier_mentality", "scarcity_pressure", "social_tension", "law_enforcement_reach",
                "data_sharing_level", "outsider_attitude", "concise_behavioral_prompt")},
            **{name: "civ_governance_profile." + name for name in
               ("ultimate_sovereign", "local_civil_authority", "administrative_authority",
                "security_provider", "primary_owner_operator", "primary_financier", "primary_certifier",
                "torch_corporate_legacy", "metric_reassertion", "loom_frontier_disruption")},
            **{name: "civ_infrastructure_state." + name for name in
               ("resident_population", "transient_daily_population", "workforce", "annual_value_added",
                "power_average_mw", "cargo_throughput_tonnes_year", "strategic_importance",
                "economic_centrality", "transport_centrality")},
        },
        "v_graph_civstate_influence_edges": {
            **{name: "civ_influence_edge." + name for name in
               ("subject_id", "actor_subject_id", "year", "influence_domain", "influence_weight",
                "control_class", "basis", "derivation_id")},
            "subject_name": "civ_subject[subject].display_name",
            "subject_node_key": "CASE civ_subject[subject].navigator_entity_id/navigator_noun_id",
            "actor_name": "civ_subject[actor].display_name",
            "actor_node_key": "CASE civ_subject[actor].navigator_entity_id/navigator_noun_id",
        },
    }
    view_filters = {
        "civ_runtime_place_context": ("navigator_node_id LIKE 'CER-P%'", "navigator_node_id"),
        "v_graph_civstate_influence_edges": (
            "year=2226 AND subject_id LIKE 'NODE:CER-P%' AND actor_node_key IS NOT NULL "
            "AND influence_domain IN ('GOVERNANCE','OPERATIONS','SECURITY','SUPPLY')",
            "subject_id, influence_domain, actor_subject_id"),
    }
    for view in spec["views"]:
        name = view["name"]
        where, order = view_filters[name]
        with sqlite3.connect(f"file:{paths['CIVSTATE']}?mode=ro&immutable=1", uri=True) as source_connection:
            source_connection.row_factory = sqlite3.Row
            source_view_rows = [dict(r) for r in source_connection.execute(
                f"SELECT * FROM {name} WHERE {where} ORDER BY {order}")]
        target_view_rows = pg_json(database, "SELECT coalesce(json_agg(row_to_json(q)), '[]'::json) "
                                   f"FROM (SELECT * FROM {name} WHERE {where} ORDER BY {order}) q", sid)
        if set(view["columns"]) != set(view_source[name]):
            raise RuntimeError(f"View source mapping is incomplete: {name}")
        view_item = {"database": "CIVSTATE", "view": name,
                     "postgres_view": f"loom_ceres.{name}", "source_rows": len(source_view_rows),
                     "postgres_rows": len(target_view_rows), "columns": []}
        for column in view["columns"]:
            match = len(source_view_rows) == len(target_view_rows) and all(
                a[column] == b[column] for a, b in zip(source_view_rows, target_view_rows))
            view_item["columns"].append({"column": column,
                                         "postgres_column": f"loom_ceres.{name}.{column}",
                                         "sqlite_source_expression": view_source[name][column],
                                         "exact_values_match": match})
            if not match:
                report["discrepancies"].append(f"CIVSTATE view {name}.{column} differs")
        report["views"].append(view_item)
    source_payload, consumer = atlas_payload_from_source(spec, paths)
    original_connect = consumer["_connect_readonly"]
    try:
        consumer["_connect_readonly"] = lambda _path: PgCompatConnection(database, sid)
        pg_payload = consumer["load_atlas_data"](paths["WORLD"], paths["CIVSTATE"])
    finally:
        consumer["_connect_readonly"] = original_connect
    report["atlas_payload"] = {
        "exact_match": source_payload == pg_payload,
        "facilities": len(pg_payload["facilities"]), "zones": len(pg_payload["zones"]),
        "institutions": len(pg_payload["institutions"]),
        "facility_institution_edges": sum(len(x["institutions"]) for x in pg_payload["facilities"].values()),
        "pressure_records": sum(len(x["social_pressures"]) for x in pg_payload["facilities"].values()),
        "census_relations": len(pg_payload["census_relations"]),
    }
    if source_payload != pg_payload:
        report["discrepancies"].append("Complete Atlas JSON payload differs from SQLite consumer")
    # The actual UI formulas are applied to both fully matched payloads, including every facility.
    def calculations(payload: dict) -> dict:
        demographic = payload["body"]["demographic"]
        economy = payload["body"]["economy"]
        bio, synth = demographic["biological_population"], demographic["synthetic_population"]
        combined = bio + synth if bio is not None and synth is not None else None
        output, investment = economy["value_added"], economy["investment"]
        radius, gm = payload["world"]["mean_radius_km"], payload["world"]["gm_km3_s2"]
        result = {"combined_residents": combined,
                  "biological_share_percent": bio / combined * 100 if combined else None,
                  "synthetic_share_percent": synth / combined * 100 if combined else None,
                  "investment_bar_percent": investment / output * 100 if output else None,
                  "diameter_km": radius * 2 if radius is not None else None,
                  "surface_gravity_m_s2": gm / (radius * radius) * 1000 if gm is not None and radius else None,
                  "escape_speed_km_s": math.sqrt(2 * gm / radius) if gm is not None and radius else None,
                  "rotation_hours": payload["world"]["rotation_period_s"] / 3600,
                  "facility_count": len(payload["facilities"]),
                  "pressure_record_count": sum(len(x["social_pressures"]) for x in payload["facilities"].values())}
        for node, facility in payload["facilities"].items():
            row = facility["infrastructure"]
            result[node] = {key: row[key] for key in (
                "resident_population", "transient_daily_population", "workforce", "habitable_capacity",
                "annual_value_added", "capital_stock", "annual_operating_cost", "replacement_value",
                "cargo_throughput_tonnes_year", "passenger_movements_year", "ship_calls_year",
                "power_average_mw", "power_peak_mw", "utilization", "industrial_capacity_index")}
        return result
    derived_source, derived_target = calculations(source_payload), calculations(pg_payload)
    report["derived_values"] = {"exact_match": derived_source == derived_target,
                                 "checked_formula_or_dimension_count": len(derived_target) - 5 + 5 * 15}
    if derived_source != derived_target:
        report["discrepancies"].append("Atlas derived values differ")
    qualification = json.loads(MVP_A_PATH.read_text())
    field_index = {(t["database"], t["table"], c["column"]): c["exact_values_match"]
                   for t in report["tables"] for c in t["columns"]}
    field_index.update({("CIVSTATE", v["view"], c["column"]): c["exact_values_match"]
                        for v in report["views"] for c in v["columns"]})
    target_index = {(t["database"], t["table"], c["column"]): c["postgres_column"]
                    for t in report["tables"] for c in t["columns"]}
    target_index.update({("CIVSTATE", v["view"], c["column"]): c["postgres_column"]
                         for v in report["views"] for c in v["columns"]})
    dbnames = {"LOOM_2226.sqlite3": "WORLD", "LOOM_2226_CIVSTATE.sqlite3": "CIVSTATE"}
    consumed = []
    for record in qualification["records"]:
        source = record["source"]
        if "database" in source:
            key = (dbnames[source["database"]], source["table"], source["column"])
            if key not in field_index:
                raise RuntimeError(f"MVP-A consumed source has no PostgreSQL field mapping: {record['id']}")
            matched = field_index[key]
            target = target_index[key]
        elif "manifest" in source:
            matched = True  # Exact field comparison below covers all 14 source manifest columns.
            target = "loom_media.ceres_manifest_asset." + source["column"]
        else:
            matched = report["atlas_payload"]["exact_match"]
            target = "unchanged consumer expression over exact PostgreSQL Atlas payload"
        consumed.append({"identity": record["id"], "mvp_a_gate_a_status": record["a_status"],
                         "source": source, "postgres_target": target, "value_or_expression_parity": matched})
        if not matched:
            report["discrepancies"].append(f"MVP-A consumed identity differs: {record['id']}")
    if len(consumed) != 117 or len({x["identity"] for x in consumed}) != 117:
        raise RuntimeError("MVP-A consumed identity inventory is incomplete")
    report["consumed_identities"] = consumed
    manifest_columns = list(manifest[0])
    pg_manifest = pg_json(database, "SELECT coalesce(json_agg(row_to_json(q)), '[]'::json) FROM ("
                          f"SELECT {', '.join(manifest_columns)} FROM loom_media.ceres_manifest_asset "
                          f"WHERE snapshot_id={sql_literal(sid)} ORDER BY node_id) q")
    report["manifest"] = {"source_records": len(manifest), "postgres_records": len(pg_manifest),
                          "all_fields_match": sorted(manifest, key=lambda x: x["node_id"]) == pg_manifest,
                          "field_count": len(manifest_columns)}
    if not report["manifest"]["all_fields_match"]:
        report["discrepancies"].append("Manifest fields differ")
    source_relations = sorted((row["node_id"], r["zone"], r["relationship"], r["primary"],
                               r["confidence"], r["basis"]) for row in manifest for r in row["civstate_zones"])
    target_relations = pg_json(database,
        "SELECT coalesce(json_agg(row_to_json(q)), '[]'::json) FROM ("
        "SELECT node_id,zone_subject_id,relationship_type,primary_relation,confidence,basis_code "
        "FROM loom_media.ceres_manifest_zone_relation "
        f"WHERE snapshot_id={sql_literal(sid)} ORDER BY node_id,zone_subject_id,relationship_type) q")
    target_relation_values = sorted((r["node_id"], r["zone_subject_id"], r["relationship_type"],
                                     r["primary_relation"], r["confidence"], r["basis_code"])
                                    for r in target_relations)
    report["manifest"]["zone_relation_count"] = len(target_relations)
    report["manifest"]["zone_relations_match"] = source_relations == target_relation_values
    if source_relations != target_relation_values:
        report["discrepancies"].append("Manifest zone relationship normalization differs")
    media_rows = selected[("MEDIA", "media_assets")]
    report["media"] = {"approved_asset_count": len(media_rows),
                       "all_original_blob_hashes_match": all(hashlib.sha256(row["original_blob"]).hexdigest() == row["original_sha256"] for row in media_rows)}
    fk = pg_json(database, "SELECT json_build_object('foreign_keys',count(*),'all_validated',bool_and(convalidated)) "
                 "FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
                 "WHERE c.contype='f' AND n.nspname IN ('loom_world','loom_civ','loom_media')")
    report["referential_integrity"] = fk
    if not fk["all_validated"]:
        report["discrepancies"].append("PostgreSQL foreign key is unvalidated")
    lineage = pg_json(database,
        "SELECT json_build_object('source_rows',count(*) FILTER (WHERE source_database IN ('WORLD','CIVSTATE','MEDIA')),'all_rows',count(*)) "
        f"FROM loom_control.row_lineage WHERE snapshot_id={sql_literal(sid)}")
    expected_rows = sum(len(rows) for rows in selected.values())
    report["row_lineage"] = {**lineage, "expected_source_rows": expected_rows}
    if lineage["source_rows"] != expected_rows or lineage["all_rows"] != expected_rows + len(manifest) + len(source_relations):
        report["discrepancies"].append("Row lineage coverage is incomplete")
    pg_lineage = pg_json(database,
        "SELECT coalesce(json_agg(row_to_json(q)), '[]'::json) FROM ("
        "SELECT target_schema,target_table,source_database,source_table,source_artifact_sha256,source_key "
        f"FROM loom_control.row_lineage WHERE snapshot_id={sql_literal(sid)} "
        "ORDER BY target_schema,target_table,source_key::text) q")
    actual_keys = {(r["target_schema"], r["target_table"], r["source_database"], r["source_table"],
                    r["source_artifact_sha256"], json.dumps(r["source_key"], sort_keys=True))
                   for r in pg_lineage}
    expected_keys = set()
    for table in spec["tables"]:
        db, name = table["database"], table["table"]
        for row in selected[(db, name)]:
            key = {column: row[column] for column in table["primary_key"]}
            expected_keys.add((table["target_schema"], name, db, name,
                               spec["source_sha256"][db], json.dumps(key, sort_keys=True)))
    manifest_sha = spec["manifest_sha256"]
    for row in manifest:
        expected_keys.add(("loom_media", "ceres_manifest_asset", "MANIFEST", "docs/ceres/manifest.json",
                           manifest_sha, json.dumps({"node_id": row["node_id"]}, sort_keys=True)))
        for rel in row["civstate_zones"]:
            key = {"node_id": row["node_id"], "zone_subject_id": rel["zone"],
                   "relationship_type": rel["relationship"]}
            expected_keys.add(("loom_media", "ceres_manifest_zone_relation", "MANIFEST",
                               "docs/ceres/manifest.json:civstate_zones", manifest_sha,
                               json.dumps(key, sort_keys=True)))
    report["row_lineage"]["exact_keys_match"] = actual_keys == expected_keys
    if actual_keys != expected_keys:
        report["discrepancies"].append("Row lineage source keys or hashes differ")
    semantic_counts = pg_json(database,
        "SELECT coalesce(json_object_agg(semantic_status,n), '{}'::json) FROM ("
        "SELECT semantic_status,count(*) n FROM loom_control.field_semantics "
        f"WHERE snapshot_id={sql_literal(sid)} GROUP BY semantic_status) q")
    report["field_semantics"] = {"counts": semantic_counts,
                                 "unresolved_legacy_label_count": int(psql(database,
         "SELECT count(*) FROM loom_control.field_semantics WHERE presentation_label='Unresolved legacy data' "
         f"AND snapshot_id={sql_literal(sid)}")),
                                 "qualified_row_scoped_count": int(psql(database,
         "SELECT count(*) FROM loom_control.field_semantics WHERE semantic_status='QUALIFIED' "
         f"AND qualified_row_filter IS NOT NULL AND snapshot_id={sql_literal(sid)}"))}
    pg_semantics = pg_json(database,
        "SELECT coalesce(json_agg(row_to_json(q)), '[]'::json) FROM ("
        "SELECT source_database,source_table,source_column,semantic_status,embedded_claim_status,"
        "admission_scope,qualified_row_filter,presentation_label FROM loom_control.field_semantics "
        f"WHERE snapshot_id={sql_literal(sid)}) q")
    sem_index = {(r["source_database"], r["source_table"], r["source_column"]): r
                 for r in pg_semantics}
    semantic_match = len(pg_semantics) == sum(len(t["columns"]) for t in spec["tables"]) + len(manifest[0])
    for table in spec["tables"]:
        for col in table["columns"]:
            key = (table["database"], table["table"], col["name"])
            row = sem_index.get(key)
            embedded = col.get("embedded_claim_status") or "NOT_APPLICABLE"
            label = presentation_label(col)
            semantic_match &= bool(row and row["semantic_status"] == col["semantic_status"]
                                   and row["embedded_claim_status"] == embedded
                                   and row["admission_scope"] == (col.get("admission_scope") or "NONE")
                                   and row["qualified_row_filter"] == col.get("qualified_row_filter")
                                   and row["presentation_label"] == label)
    report["field_semantics"]["exact_contract_match"] = semantic_match
    if not semantic_match:
        report["discrepancies"].append("PostgreSQL semantic metadata differs from pinned field contract")
    report["status"] = "PASS" if not report["discrepancies"] else "FAIL"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["migrate", "import", "verify", "run"])
    parser.add_argument("--database", default="loom_dev")
    parser.add_argument("--media-db", type=Path, default=SOURCE_PATHS["MEDIA"])
    parser.add_argument("--report", type=Path, default=ROOT / "docs/database_semantics/LOOM_CERES_POSTGRES_DEV_COVERAGE_v0.1.json")
    args = parser.parse_args()
    spec = contract()
    paths = {**SOURCE_PATHS, "MEDIA": args.media_db}
    hashes = validate_inputs(spec, paths)
    assert hashes == spec["source_sha256"]
    if args.command in ("migrate", "run"):
        print("migration:", migrate(args.database))
    if args.command == "migrate":
        return
    selected, manifest = selected_rows(spec, paths)
    sid = snapshot_id(spec)
    if args.command in ("import", "run"):
        sid, state = import_snapshot(args.database, spec, paths, selected, manifest)
        sync_lineage_and_semantics(args.database, spec, sid)
        print("import:", state, sid)
    if args.command in ("verify", "run"):
        report = verify(args.database, spec, paths, selected, manifest, sid, args.report)
        print("coverage:", report["status"], args.report)
        if report["status"] != "PASS":
            raise SystemExit(1)
        psql(args.database, f"UPDATE loom_control.snapshot SET state='VALIDATED' WHERE snapshot_id={sql_literal(sid)}")


if __name__ == "__main__":
    main()
