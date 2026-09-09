from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shipyard_glb_viewer import inspect_glb

LIBRARY_VERSION = "LOOM_SHIPYARD_VISUAL_LIBRARY_v0.1"
GLB_MIME = "model/gltf-binary"
_REQUIRED_LEDGER_TABLES = frozenset({"ledger_meta", "design_state", "derived_artifact"})
ARTIFACT_CLASSES = frozenset({"GOVERNED_SEMANTIC", "VISUAL_REFERENCE", "EXTERNAL_FIXTURE"})
AUTHORITY_BY_CLASS = {
    "GOVERNED_SEMANTIC": "DERIVED_ENGINEERING_TRACEABLE_GLB_ONLY",
    "VISUAL_REFERENCE": "NON_AUTHORITATIVE_VISUAL_REFERENCE_ONLY",
    "EXTERNAL_FIXTURE": "VISUAL_FIXTURE_ONLY",
}


class VisualLibraryError(ValueError):
    pass


@dataclass(frozen=True)
class VisualLibraryAsset:
    asset_id: str
    display_name: str
    ship_name: str
    artifact_class: str
    authority_status: str
    sha256: str
    generator: str
    mesh_count: int
    node_count: int
    semantic_node_count: int
    source_candidate_id: str | None
    source_candidate_hash: str | None
    metadata: dict[str, Any]
    payload: bytes


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VisualLibraryError(f"{label} must be a non-empty string")
    return value.strip()


def _require_design_ledger(connection: sqlite3.Connection) -> None:
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not _REQUIRED_LEDGER_TABLES.issubset(tables):
        raise VisualLibraryError("target is not a LOOM Shipyard design ledger")
    row = connection.execute("SELECT value FROM ledger_meta WHERE key='ledger_version'").fetchone()
    if row is None or not isinstance(row[0], str) or not row[0].startswith("LOOM_DESIGN_LEDGER_"):
        raise VisualLibraryError("missing LOOM design-ledger identity")


def ensure_schema(connection: sqlite3.Connection) -> None:
    _require_design_ledger(connection)
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS visual_library_asset(
            asset_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            ship_name TEXT NOT NULL,
            artifact_class TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            generator TEXT NOT NULL,
            mesh_count INTEGER NOT NULL,
            node_count INTEGER NOT NULL,
            semantic_node_count INTEGER NOT NULL,
            source_candidate_id TEXT,
            source_candidate_hash TEXT,
            metadata_json TEXT NOT NULL,
            payload BLOB NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(artifact_class, sha256)
        );
        CREATE INDEX IF NOT EXISTS idx_visual_library_ship
            ON visual_library_asset(ship_name, artifact_class, created_at);
        """
    )


def _asset_id(artifact_class: str, digest: str) -> str:
    return f"GLBLIB::{artifact_class}::{digest[:20]}"


def add_glb_asset(
    db_path: str | Path,
    glb: bytes,
    *,
    display_name: str,
    ship_name: str,
    artifact_class: str,
    source_candidate_id: str | None = None,
    source_candidate_hash: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> VisualLibraryAsset:
    if artifact_class not in ARTIFACT_CLASSES:
        raise VisualLibraryError(f"unsupported artifact_class {artifact_class}")
    payload = bytes(glb)
    if not payload:
        raise VisualLibraryError("GLB payload must be non-empty")
    info = inspect_glb(payload)
    extras = info.get("asset_extras") or {}
    if extras.get("flight_dynamics_authority") or extras.get("canon_changed") or extras.get("production_shipclasses_changed"):
        raise VisualLibraryError("visual-library asset may not escalate engineering authority")
    if artifact_class == "GOVERNED_SEMANTIC" and info["semantic_node_count"] <= 0:
        raise VisualLibraryError("GOVERNED_SEMANTIC asset must carry semantic nodes")

    digest = _sha256(payload)
    asset_id = _asset_id(artifact_class, digest)
    authority = AUTHORITY_BY_CLASS[artifact_class]
    merged_metadata = dict(metadata or {})
    merged_metadata.update({
        "library_version": LIBRARY_VERSION,
        "asset_extras": extras,
        "viewer_authority": info.get("viewer_authority"),
    })
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise VisualLibraryError(f"Shipyard design ledger not found: {path}")
    con = sqlite3.connect(str(path))
    try:
        ensure_schema(con)
        con.execute(
            """INSERT INTO visual_library_asset(
                asset_id,display_name,ship_name,artifact_class,authority_status,mime_type,
                sha256,generator,mesh_count,node_count,semantic_node_count,
                source_candidate_id,source_candidate_hash,metadata_json,payload
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(asset_id) DO UPDATE SET
                display_name=excluded.display_name,
                ship_name=excluded.ship_name,
                metadata_json=excluded.metadata_json,
                payload=excluded.payload
            """,
            (
                asset_id, _text(display_name, "display_name"), _text(ship_name, "ship_name"),
                artifact_class, authority, GLB_MIME, digest, str(info.get("generator") or "UNKNOWN"),
                int(info["mesh_count"]), int(info["node_count"]), int(info["semantic_node_count"]),
                source_candidate_id, source_candidate_hash,
                json.dumps(merged_metadata, sort_keys=True, separators=(",", ":"), allow_nan=False),
                sqlite3.Binary(payload),
            ),
        )
        con.commit()
    finally:
        con.close()
    return load_asset(db_path, asset_id)


def import_glb_file(
    db_path: str | Path,
    glb_path: str | Path,
    *,
    display_name: str,
    ship_name: str = "Wayfarer",
    artifact_class: str = "VISUAL_REFERENCE",
) -> VisualLibraryAsset:
    path = Path(glb_path).expanduser().resolve()
    if not path.is_file():
        raise VisualLibraryError(f"GLB file not found: {path}")
    return add_glb_asset(
        db_path, path.read_bytes(), display_name=display_name, ship_name=ship_name,
        artifact_class=artifact_class,
        metadata={"imported_from_filename": path.name, "external_file_path_not_authoritative": True},
    )


def list_assets(db_path: str | Path) -> list[dict[str, Any]]:
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise VisualLibraryError(f"Shipyard design ledger not found: {path}")
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    try:
        ensure_schema(con)
        rows = con.execute(
            """SELECT asset_id,display_name,ship_name,artifact_class,authority_status,sha256,
                      generator,mesh_count,node_count,semantic_node_count,source_candidate_id,
                      source_candidate_hash,created_at
               FROM visual_library_asset
               ORDER BY ship_name, display_name, created_at"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        con.close()


def load_asset(db_path: str | Path, asset_id: str) -> VisualLibraryAsset:
    path = Path(db_path).expanduser().resolve()
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    try:
        ensure_schema(con)
        row = con.execute("SELECT * FROM visual_library_asset WHERE asset_id=?", (_text(asset_id, "asset_id"),)).fetchone()
        if row is None:
            raise VisualLibraryError(f"visual library asset not found: {asset_id}")
        payload = bytes(row["payload"])
        if _sha256(payload) != row["sha256"]:
            raise VisualLibraryError("stored visual-library GLB digest mismatch")
        info = inspect_glb(payload)
        if int(info["mesh_count"]) != int(row["mesh_count"]):
            raise VisualLibraryError("stored visual-library metadata mismatch")
        return VisualLibraryAsset(
            asset_id=row["asset_id"], display_name=row["display_name"], ship_name=row["ship_name"],
            artifact_class=row["artifact_class"], authority_status=row["authority_status"],
            sha256=row["sha256"], generator=row["generator"], mesh_count=int(row["mesh_count"]),
            node_count=int(row["node_count"]), semantic_node_count=int(row["semantic_node_count"]),
            source_candidate_id=row["source_candidate_id"], source_candidate_hash=row["source_candidate_hash"],
            metadata=json.loads(row["metadata_json"]), payload=payload,
        )
    finally:
        con.close()
