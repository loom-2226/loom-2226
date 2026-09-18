#!/usr/bin/env python3
"""Serve the private Ceres Atlas using read-only WORLD, CIVSTATE, and MEDIA SQLite."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SHA256 = "6ae473bf6b6063b17a08e876d7b0057166135d397ce56e276423d319a44ccd81"
FIELDS = (
    "node_id", "name", "facility_type", "noun_id", "asset_id", "role",
    "is_current", "review_status", "media_key", "export_status", "filename",
    "sha256", "byte_length",
)
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.mjs": ("app.mjs", "text/javascript; charset=utf-8"),
    "/model.mjs": ("model.mjs", "text/javascript; charset=utf-8"),
    "/assets/loom-wordmark-white.svg": ("assets/loom-wordmark-white.svg", "image/svg+xml"),
}
BODY_HERO = {
    "noun_id": "N-75BA5C617E79",
    "asset_id": "0e516224-6345-4e97-b6d1-569bf193f495",
    "media_key": "2c6211b6-6cd2-4b62-89f7-cb795fdbac51",
    "sha256": "fa5fc5876d8f66631837ce498d77e139444b9247e8b2a66ff6dd8ad611e1f08e",
    "byte_length": 1261154,
}
BODY_HERO_PATH = "/assets/ceres-world-hero.png"

CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
)


def load_manifest(root: Path) -> dict:
    raw = (root / "docs/ceres/manifest.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError("Ceres manifest differs from the verified slice-1 snapshot")
    records = json.loads(raw)
    expected = {f"CER-P{i:02}" for i in range(1, 6)}
    if len(records) != 5 or {r["node_id"] for r in records} != expected:
        raise ValueError("Expected exactly the five verified Ceres facilities")
    for record in records:
        if (record["role"], record["is_current"], record["review_status"], record["export_status"]) != (
            "HERO", 1, "APPROVED_REFERENCE", "VERIFIED"
        ):
            raise ValueError("Unapproved Ceres image record")
        filename = f'{record["node_id"]}_{record["asset_id"]}.png'
        if record["filename"] != filename or not re.fullmatch(r"CER-P0[1-5]_[a-f0-9-]+\.png", filename):
            raise ValueError("Invalid Ceres asset filename")
    return {
        "schema_version": 1,
        "source": "docs/ceres/manifest.json",
        "source_sha256": MANIFEST_SHA256,
        "facilities": [{key: r[key] for key in FIELDS} for r in records],
    }


def _connect_readonly(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise ValueError("Database is unavailable")
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)


def read_media_blob(world_db: Path, media_db: Path, record: dict) -> tuple[str, bytes]:
    try:
        with closing(_connect_readonly(world_db)) as world:
            identity = world.execute("""
                SELECT entity_id, asset_role, review_status, media_key,
                       content_hash, byte_length, is_current
                FROM image_assets WHERE asset_id=?
            """, (record["asset_id"],)).fetchall()
        expected_identity = [(
            record["noun_id"], "HERO", "APPROVED_REFERENCE", record["media_key"],
            record["sha256"], record["byte_length"], 1,
        )]
        if identity != expected_identity:
            raise ValueError("WORLD asset identity or approval does not match")

        with closing(_connect_readonly(media_db)) as media:
            rows = media.execute("""
                SELECT asset_id, mime_type, original_blob,
                       original_byte_length, original_sha256
                FROM media_assets WHERE media_key=?
            """, (record["media_key"],)).fetchall()
        if len(rows) != 1:
            raise ValueError("MEDIA asset is unavailable")
        asset_id, mime_type, blob, byte_length, sha256 = rows[0]
        content = bytes(blob) if blob is not None else b""
        if (asset_id != record["asset_id"] or mime_type != "image/png" or
                byte_length != record["byte_length"] or sha256 != record["sha256"] or
                len(content) != record["byte_length"] or
                hashlib.sha256(content).hexdigest() != record["sha256"]):
            raise ValueError("MEDIA blob identity or integrity does not match")
        return mime_type, content
    except sqlite3.Error as error:
        raise ValueError("Image database could not be read") from error



def _dict_rows(connection: sqlite3.Connection, sql: str, parameters: tuple = ()) -> list[dict]:
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(sql, parameters).fetchall()]


def _one_or_none(rows: list[dict]) -> dict | None:
    if len(rows) > 1:
        raise ValueError("Atlas query returned duplicate identity rows")
    return rows[0] if rows else None


def _load_atlas_data(world_db: Path, civstate_db: Path) -> dict[str, object]:
    """Return the bounded Ceres dossier projection from fixed read-only queries."""
    try:
        with closing(_connect_readonly(world_db)) as world:
            world_body = _one_or_none(_dict_rows(world, """
                SELECT e.entity_id, e.name, e.entity_class, e.parent_entity_id,
                       p.gm_km3_s2, p.mean_radius_km, p.rotation_period_s,
                       p.source_id AS physical_source_id, p.status AS physical_status,
                       d.atmosphere_class, d.source AS dynamics_source
                FROM entities e
                LEFT JOIN celestial_properties p ON p.entity_id=e.entity_id
                LEFT JOIN celestial_dynamics d ON d.entity_id=e.entity_id
                WHERE e.entity_id='CER'
            """))
            world_facilities = _dict_rows(world, """
                SELECT node_id, node_name, facility_type, traffic, commercial_1,
                       commercial_2, commercial_regime, civil_authority,
                       administrative_authority, security_authority, source,
                       entity_id, parent_entity_id
                FROM infrastructure_nodes
                WHERE parent_entity_id='CER' AND node_id LIKE 'CER-P%'
                ORDER BY node_id
            """)
        expected = [f"CER-P{i:02}" for i in range(1, 6)]
        if (not world_body or world_body.get("name") != "Ceres" or
                [row["node_id"] for row in world_facilities] != expected or
                any(not row.get("node_name") or not row.get("facility_type")
                    for row in world_facilities)):
            raise ValueError("WORLD Ceres identity set is incomplete")

        with closing(_connect_readonly(civstate_db)) as civ:
            demographic = _one_or_none(_dict_rows(civ, """
                SELECT * FROM civ_demographic_state
                WHERE subject_id='BODY:CERES:CERES' AND year=2226
            """))
            economy = _one_or_none(_dict_rows(civ, """
                SELECT * FROM civ_economic_state
                WHERE subject_id='BODY:CERES:CERES' AND year=2226
            """))
            workforce = _one_or_none(_dict_rows(civ, """
                SELECT * FROM civ_workforce_state
                WHERE subject_id='BODY:CERES:CERES' AND year=2226 AND sector_id='ALL'
            """))
            place_context = {row["navigator_node_id"]: row for row in _dict_rows(civ, """
                SELECT * FROM civ_runtime_place_context
                WHERE navigator_node_id LIKE 'CER-P%'
                ORDER BY navigator_node_id
            """)}
            infrastructure = {row["node_subject_id"].removeprefix("NODE:"): row for row in _dict_rows(civ, """
                SELECT * FROM civ_infrastructure_state
                WHERE year=2226 AND node_subject_id LIKE 'NODE:CER-P%'
                ORDER BY node_subject_id
            """)}
            social = {row["subject_id"].removeprefix("NODE:"): row for row in _dict_rows(civ, """
                SELECT * FROM civ_social_state
                WHERE year=2226 AND subject_id LIKE 'NODE:CER-P%'
                ORDER BY subject_id
            """)}
            governance = {row["subject_id"].removeprefix("NODE:"): row for row in _dict_rows(civ, """
                SELECT * FROM civ_governance_profile
                WHERE year=2226 AND subject_id LIKE 'NODE:CER-P%'
                ORDER BY subject_id
            """)}
            pressures = _dict_rows(civ, """
                SELECT subject_id, year, pressure_type, intensity, direction,
                       affected_groups, trigger_basis, derivation_id
                FROM civ_social_pressure
                WHERE year=2226 AND subject_id LIKE 'NODE:CER-P%'
                ORDER BY subject_id, pressure_type
            """)
            zones = _dict_rows(civ, """
                SELECT s.subject_id, s.display_name, d.year, d.biological_population,
                       d.synthetic_population, d.transient_population,
                       d.working_age_population, d.median_age, d.derivation_id
                FROM civ_subject s
                LEFT JOIN civ_demographic_state d
                  ON d.subject_id=s.subject_id AND d.year=2226
                WHERE s.parent_subject_id='BODY:CERES:CERES' AND s.subject_class='CENSUS_ZONE'
                ORDER BY s.subject_id
            """)
            census_relations = _dict_rows(civ, """
                SELECT node_subject_id, zone_subject_id, year, relationship_type,
                       primary_relation, confidence, basis_code, basis_text, derivation_id
                FROM civ_census_node_relation
                WHERE year=2226 AND node_subject_id LIKE 'NODE:CER-P%'
                ORDER BY node_subject_id, zone_subject_id
            """)
            influence = _dict_rows(civ, """
                SELECT subject_id, actor_subject_id, actor_name, actor_node_key AS actor_noun_id, year,
                       influence_domain, influence_weight, control_class, basis, derivation_id
                FROM v_graph_civstate_influence_edges
                WHERE year=2226 AND subject_id LIKE 'NODE:CER-P%'
                  AND actor_node_key IS NOT NULL
                  AND influence_domain IN ('GOVERNANCE','OPERATIONS','SECURITY','SUPPLY')
                ORDER BY subject_id, influence_domain, actor_subject_id
            """)
            institution_subjects = {row["subject_id"]: row for row in _dict_rows(civ, """
                SELECT subject_id, subject_class, display_name, navigator_noun_id,
                       aggregation_class, active_2226
                FROM civ_subject WHERE subject_id LIKE 'NOUN:%' AND active_2226=1
            """)}

        facilities = {}
        pressure_by_facility = {node: [] for node in expected}
        for row in pressures:
            pressure_by_facility.setdefault(row["subject_id"].removeprefix("NODE:"), []).append(row)
        relations_by_facility = {node: [] for node in expected}
        institutions: dict[str, dict] = {}
        for edge in influence:
            node_id = edge["subject_id"].removeprefix("NODE:")
            subject = institution_subjects.get(edge["actor_subject_id"])
            if not subject or subject["subject_id"] != edge["actor_noun_id"]:
                continue
            relation = {
                "institution_id": subject["subject_id"],
                "name": subject["display_name"],
                "institution_class": subject["subject_class"],
                "domain": edge["influence_domain"],
                "relationship": edge["basis"],
                "control_class": edge["control_class"],
                "weight": edge["influence_weight"],
                "derivation_id": edge["derivation_id"],
            }
            relations_by_facility.setdefault(node_id, []).append(relation)
            dossier = institutions.setdefault(subject["subject_id"], {
                "id": subject["subject_id"], "name": subject["display_name"],
                "institution_class": subject["subject_class"],
                "navigator_noun_id": subject["navigator_noun_id"], "facilities": [],
            })
            dossier["facilities"].append({"facility_id": node_id, **relation})

        for identity in world_facilities:
            node_id = identity["node_id"]
            facilities[node_id] = {
                "id": node_id,
                "subject_id": f"NODE:{node_id}",
                "identity": identity,
                "runtime_context": place_context.get(node_id),
                "infrastructure": infrastructure.get(node_id),
                "social": social.get(node_id),
                "governance": governance.get(node_id),
                "social_pressures": pressure_by_facility.get(node_id, []),
                "institutions": relations_by_facility.get(node_id, []),
            }
        return {
            "schema_version": 1,
            "epoch": 2226,
            "world": world_body,
            "body": {"demographic": demographic, "economy": economy, "workforce": workforce},
            "facilities": facilities,
            "institutions": institutions,
            "zones": zones,
            "census_relations": census_relations,
            "provenance": {
                "world": {"database": "WORLD", "tables": ["entities", "celestial_properties", "celestial_dynamics"], "row_key": "entity_id=CER", "grain": "BODY", "units": {"gm_km3_s2": "km3/s2", "mean_radius_km": "km", "rotation_period_s": "s"}},
                "body_people": {"database": "CIVSTATE", "table": "civ_demographic_state", "row_key": "subject_id=BODY:CERES:CERES;year=2226", "grain": "BODY", "units": "persons"},
                "body_economy": {"database": "CIVSTATE", "table": "civ_economic_state", "row_key": "subject_id=BODY:CERES:CERES;year=2226", "grain": "BODY", "units": "model monetary units unless field is a ratio/index"},
                "facilities": {"database": "CIVSTATE", "tables": ["civ_infrastructure_state", "civ_social_state", "civ_governance_profile", "civ_social_pressure"], "view": "civ_runtime_place_context", "row_key": "NODE:<WORLD node_id>;year=2226", "grain": "FACILITY_NODE"},
                "institutions": {"database": "CIVSTATE", "tables": ["civ_subject", "civ_influence_state"], "view": "v_graph_civstate_influence_edges", "grain": "TYPED_FACILITY_INSTITUTION_EDGE"},
                "media": {"database": "MEDIA", "table": "media_assets", "delivery": "verified original_blob via allowlisted HTTP paths"},
            },
            "support": {
                "world_environment": "LIVE",
                "world_resources": "UNSUPPORTED",
                "world_history": "UNSUPPORTED",
                "people": "LIVE",
                "economy": "LIVE",
                "transit_nodes": "LIVE",
                "transit_od_corridors": "UNSUPPORTED_PENDING_ENDPOINT_VALIDATION",
                "systems": "LIVE",
                "institutions": "LIVE_TYPED_INFLUENCE_RELATIONSHIPS",
                "society": "LIVE",
            },
        }
    except sqlite3.Error as error:
        raise ValueError("Atlas database could not be queried") from error


class ReadOnlyAtlasQueryAdapter:
    """Typed boundary for the two fixed analytical database projections."""

    __slots__ = ("world_db", "civstate_db")

    def __init__(self, world_db: Path, civstate_db: Path) -> None:
        self.world_db = world_db
        self.civstate_db = civstate_db

    def load(self) -> dict[str, object]:
        return _load_atlas_data(self.world_db, self.civstate_db)


def load_atlas_data(world_db: Path, civstate_db: Path) -> dict[str, object]:
    return ReadOnlyAtlasQueryAdapter(Path(world_db), Path(civstate_db)).load()


def create_server(port: int = 8768, root: Path = ROOT, world_db: Path | None = None,
                  civstate_db: Path | None = None, media_db: Path | None = None) -> ThreadingHTTPServer:
    root = root.resolve()
    world_db = Path(world_db) if world_db else root / "data/LOOM_2226.sqlite3"
    civstate_db = Path(civstate_db) if civstate_db else root / "data/LOOM_2226_CIVSTATE.sqlite3"
    media_db = Path(media_db) if media_db else root / "data/LOOM_2226_media.sqlite3"
    manifest = load_manifest(root)
    payload = json.dumps(manifest, ensure_ascii=False).encode("utf-8")
    images = {"/images/" + r["filename"]: r for r in manifest["facilities"]}

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status: int, content_type: str, content: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(content)

        def do_GET(self) -> None:
            # Reject foreign Host headers (including DNS rebinding); no CORS grant.
            allowed_hosts = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            if self.headers.get("Host") not in allowed_hosts:
                self.respond(403, "text/plain", b"Loopback access only")
                return
            path = urlsplit(self.path).path
            try:
                if path == "/atlas-data.json":
                    data = json.dumps(load_atlas_data(world_db, civstate_db), ensure_ascii=False).encode("utf-8")
                    self.respond(200, "application/json; charset=utf-8", data)
                elif path == "/manifest.json":
                    self.respond(200, "application/json; charset=utf-8", payload)
                elif path == BODY_HERO_PATH:
                    mime, content = read_media_blob(world_db, media_db, BODY_HERO)
                    self.respond(200, mime, content)
                elif path in STATIC:
                    filename, mime = STATIC[path]
                    directory = root / "web/ceres-atlas"
                    file = directory / filename
                    if file.is_symlink() or directory.resolve() not in file.resolve().parents:
                        raise ValueError("Application file must be local")
                    self.respond(200, mime, file.read_bytes())
                elif path in images:
                    mime, content = read_media_blob(world_db, media_db, images[path])
                    self.respond(200, mime, content)
                else:
                    self.respond(404, "text/plain", b"Not found")
            except (OSError, ValueError):
                self.respond(404, "text/plain", b"Local resource unavailable or unverified")

        do_HEAD = do_GET

        def log_message(self, *_args) -> None:
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--world-db", type=Path, default=ROOT / "data/LOOM_2226.sqlite3")
    parser.add_argument("--civstate-db", type=Path, default=ROOT / "data/LOOM_2226_CIVSTATE.sqlite3")
    parser.add_argument("--media-db", type=Path, default=ROOT / "data/LOOM_2226_media.sqlite3")
    args = parser.parse_args()
    try:
        server = create_server(args.port, world_db=args.world_db, civstate_db=args.civstate_db, media_db=args.media_db)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Cannot start Ceres Atlas: {error}\n")
    print(f"Private Ceres Atlas: http://127.0.0.1:{server.server_port}/", flush=True)
    print("Offline local use. Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
