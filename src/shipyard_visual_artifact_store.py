from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STORE_VERSION = "LOOM_SHIPYARD_VISUAL_ARTIFACT_STORE_v0.1"
STORE_AUTHORITY = "DERIVED_VISUAL_ARTIFACT_STORAGE_ONLY"
GLB_KIND = "ASSEMBLED_SEMANTIC_GLB"
GLB_MIME = "model/gltf-binary"


class VisualArtifactStoreError(ValueError):
    pass


@dataclass(frozen=True)
class StoredVisualArtifact:
    artifact_id: str
    artifact_kind: str
    mime_type: str
    artifact_sha256: str
    source_design_candidate_id: str
    source_design_candidate_hash: str
    source_governed_package_hash: str
    source_semantic_package_hash: str
    authority_status: str
    payload: bytes
    manifest: dict[str, Any]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hex64(value: str, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
        raise VisualArtifactStoreError(f"{label} must be a 64-character hex digest")
    return value.lower()


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VisualArtifactStoreError(f"{label} must be a non-empty string")
    return value.strip()


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS visual_artifact_blob(
            artifact_id TEXT PRIMARY KEY,
            artifact_kind TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            artifact_sha256 TEXT NOT NULL,
            source_design_candidate_id TEXT NOT NULL,
            source_design_candidate_hash TEXT NOT NULL,
            source_governed_package_hash TEXT NOT NULL,
            source_semantic_package_hash TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            manifest_json TEXT NOT NULL,
            payload BLOB NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(artifact_kind, source_semantic_package_hash, artifact_sha256)
        );
        CREATE INDEX IF NOT EXISTS idx_visual_artifact_candidate
            ON visual_artifact_blob(source_design_candidate_id, artifact_kind);
        """
    )


def artifact_id_for(manifest: dict[str, Any]) -> str:
    semantic_hash = _hex64(_text(manifest.get("source_semantic_package_hash"), "source_semantic_package_hash"), "source_semantic_package_hash")
    glb_hash = _hex64(_text(manifest.get("glb_sha256"), "glb_sha256"), "glb_sha256")
    return f"VISUAL::GLB::{semantic_hash[:16]}::{glb_hash[:16]}"


def store_semantic_glb(db_path: str | Path, glb: bytes, manifest: dict[str, Any]) -> StoredVisualArtifact:
    if not isinstance(glb, (bytes, bytearray)) or not glb:
        raise VisualArtifactStoreError("GLB payload must be non-empty bytes")
    payload = bytes(glb)
    actual = _sha256(payload)
    expected = _hex64(_text(manifest.get("glb_sha256"), "glb_sha256"), "glb_sha256")
    if actual != expected:
        raise VisualArtifactStoreError("GLB payload digest does not match manifest")
    if manifest.get("flight_dynamics_authority") or manifest.get("canon_changed") or manifest.get("production_shipclasses_changed"):
        raise VisualArtifactStoreError("visual artifact may not escalate engineering authority")

    candidate_id = _text(manifest.get("source_design_candidate_id"), "source_design_candidate_id")
    candidate_hash = _hex64(_text(manifest.get("source_design_candidate_hash"), "source_design_candidate_hash"), "source_design_candidate_hash")
    governed_hash = _hex64(_text(manifest.get("source_governed_package_hash"), "source_governed_package_hash"), "source_governed_package_hash")
    semantic_hash = _hex64(_text(manifest.get("source_semantic_package_hash"), "source_semantic_package_hash"), "source_semantic_package_hash")
    artifact_id = artifact_id_for(manifest)
    manifest_json = json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False)

    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise VisualArtifactStoreError(f"Shipyard design ledger not found: {path}")
    con = sqlite3.connect(str(path))
    try:
        ensure_schema(con)
        con.execute(
            """INSERT INTO visual_artifact_blob(
                artifact_id,artifact_kind,mime_type,artifact_sha256,
                source_design_candidate_id,source_design_candidate_hash,
                source_governed_package_hash,source_semantic_package_hash,
                authority_status,manifest_json,payload
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(artifact_id) DO UPDATE SET
                artifact_kind=excluded.artifact_kind,
                mime_type=excluded.mime_type,
                artifact_sha256=excluded.artifact_sha256,
                source_design_candidate_id=excluded.source_design_candidate_id,
                source_design_candidate_hash=excluded.source_design_candidate_hash,
                source_governed_package_hash=excluded.source_governed_package_hash,
                source_semantic_package_hash=excluded.source_semantic_package_hash,
                authority_status=excluded.authority_status,
                manifest_json=excluded.manifest_json,
                payload=excluded.payload
            """,
            (artifact_id, GLB_KIND, GLB_MIME, actual, candidate_id, candidate_hash,
             governed_hash, semantic_hash, STORE_AUTHORITY, manifest_json, sqlite3.Binary(payload)),
        )
        con.commit()
    finally:
        con.close()
    return load_artifact(db_path, artifact_id)


def load_artifact(db_path: str | Path, artifact_id: str) -> StoredVisualArtifact:
    path = Path(db_path).expanduser().resolve()
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    try:
        ensure_schema(con)
        row = con.execute("SELECT * FROM visual_artifact_blob WHERE artifact_id=?", (_text(artifact_id, "artifact_id"),)).fetchone()
        if row is None:
            raise VisualArtifactStoreError(f"visual artifact not found: {artifact_id}")
        payload = bytes(row["payload"])
        actual = _sha256(payload)
        if actual != row["artifact_sha256"]:
            raise VisualArtifactStoreError("stored visual artifact digest mismatch")
        manifest = json.loads(row["manifest_json"])
        if manifest.get("glb_sha256") != actual:
            raise VisualArtifactStoreError("stored manifest/payload digest mismatch")
        if row["authority_status"] != STORE_AUTHORITY:
            raise VisualArtifactStoreError("stored visual artifact authority escalation")
        return StoredVisualArtifact(
            artifact_id=row["artifact_id"], artifact_kind=row["artifact_kind"], mime_type=row["mime_type"],
            artifact_sha256=row["artifact_sha256"], source_design_candidate_id=row["source_design_candidate_id"],
            source_design_candidate_hash=row["source_design_candidate_hash"], source_governed_package_hash=row["source_governed_package_hash"],
            source_semantic_package_hash=row["source_semantic_package_hash"], authority_status=row["authority_status"],
            payload=payload, manifest=manifest,
        )
    finally:
        con.close()
