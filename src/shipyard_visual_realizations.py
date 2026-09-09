from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from shipyard_visual_library import _require_design_ledger, load_asset

REALIZATION_STORE_VERSION = "LOOM_SHIPYARD_VISUAL_REALIZATION_STORE_v0.1"
REALIZATION_AUTHORITY = "NON_AUTHORITATIVE_VISUAL_REALIZATION_ONLY"
_ALLOWED_YARDS = frozenset({"ASTERIA", "KELDRIN", "SHIKARI", "TASCHEN"})
_ALLOWED_MIME = frozenset({"image/png", "image/jpeg", "image/webp"})


class VisualRealizationError(ValueError):
    pass


@dataclass(frozen=True)
class VisualRealization:
    realization_id: str
    source_asset_id: str
    source_glb_sha256: str
    yard_id: str
    packet_hash: str
    display_name: str
    mime_type: str
    image_sha256: str
    authority_status: str
    payload: bytes


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VisualRealizationError(f"{label} must be a non-empty string")
    return value.strip()


def ensure_schema(connection: sqlite3.Connection) -> None:
    _require_design_ledger(connection)
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS visual_realization(
            realization_id TEXT PRIMARY KEY,
            source_asset_id TEXT NOT NULL,
            source_glb_sha256 TEXT NOT NULL,
            yard_id TEXT NOT NULL,
            packet_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            image_sha256 TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            payload BLOB NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_asset_id, yard_id, image_sha256)
        );
        CREATE INDEX IF NOT EXISTS idx_visual_realization_source
            ON visual_realization(source_asset_id, yard_id, created_at);
        """
    )


def _id(source_asset_id: str, yard_id: str, image_sha256: str) -> str:
    seed = f"{source_asset_id}|{yard_id}|{image_sha256}".encode("utf-8")
    return "REALIZATION::" + hashlib.sha256(seed).hexdigest()[:24]


def store_realization(
    db_path: str | Path,
    *,
    source_asset_id: str,
    yard_id: str,
    packet_hash: str,
    display_name: str,
    mime_type: str,
    payload: bytes,
) -> VisualRealization:
    source = load_asset(db_path, _text(source_asset_id, "source_asset_id"))
    yard = _text(yard_id, "yard_id").upper()
    if yard not in _ALLOWED_YARDS:
        raise VisualRealizationError(f"unsupported yard_id {yard}")
    mime = _text(mime_type, "mime_type").lower()
    if mime not in _ALLOWED_MIME:
        raise VisualRealizationError(f"unsupported image mime_type {mime}")
    packet = _text(packet_hash, "packet_hash")
    if len(packet) != 64 or any(ch not in "0123456789abcdef" for ch in packet.lower()):
        raise VisualRealizationError("packet_hash must be a SHA-256 hex digest")
    image = bytes(payload)
    if not image:
        raise VisualRealizationError("image payload must be non-empty")
    if len(image) > 40 * 1024 * 1024:
        raise VisualRealizationError("image payload exceeds 40 MiB library limit")
    digest = _sha256(image)
    rid = _id(source.asset_id, yard, digest)
    path = Path(db_path).expanduser().resolve()
    con = sqlite3.connect(str(path))
    try:
        ensure_schema(con)
        con.execute(
            """INSERT INTO visual_realization(
                realization_id,source_asset_id,source_glb_sha256,yard_id,packet_hash,
                display_name,mime_type,image_sha256,authority_status,payload
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(realization_id) DO UPDATE SET
                display_name=excluded.display_name,
                packet_hash=excluded.packet_hash,
                payload=excluded.payload
            """,
            (
                rid, source.asset_id, source.sha256, yard, packet,
                _text(display_name, "display_name"), mime, digest,
                REALIZATION_AUTHORITY, sqlite3.Binary(image),
            ),
        )
        con.commit()
    finally:
        con.close()
    return load_realization(db_path, rid)


def list_realizations(db_path: str | Path, source_asset_id: str | None = None) -> list[dict]:
    path = Path(db_path).expanduser().resolve()
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    try:
        ensure_schema(con)
        if source_asset_id:
            rows = con.execute(
                """SELECT realization_id,source_asset_id,source_glb_sha256,yard_id,packet_hash,
                          display_name,mime_type,image_sha256,authority_status,created_at
                   FROM visual_realization WHERE source_asset_id=?
                   ORDER BY yard_id, created_at DESC""",
                (_text(source_asset_id, "source_asset_id"),),
            ).fetchall()
        else:
            rows = con.execute(
                """SELECT realization_id,source_asset_id,source_glb_sha256,yard_id,packet_hash,
                          display_name,mime_type,image_sha256,authority_status,created_at
                   FROM visual_realization ORDER BY source_asset_id, yard_id, created_at DESC"""
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def load_realization(db_path: str | Path, realization_id: str) -> VisualRealization:
    path = Path(db_path).expanduser().resolve()
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    try:
        ensure_schema(con)
        row = con.execute(
            "SELECT * FROM visual_realization WHERE realization_id=?",
            (_text(realization_id, "realization_id"),),
        ).fetchone()
        if row is None:
            raise VisualRealizationError(f"visual realization not found: {realization_id}")
        image = bytes(row["payload"])
        if _sha256(image) != row["image_sha256"]:
            raise VisualRealizationError("stored realization image digest mismatch")
        source = load_asset(db_path, row["source_asset_id"])
        if source.sha256 != row["source_glb_sha256"]:
            raise VisualRealizationError("source GLB hash no longer matches realization provenance")
        if row["authority_status"] != REALIZATION_AUTHORITY:
            raise VisualRealizationError("realization authority mismatch")
        return VisualRealization(
            realization_id=row["realization_id"], source_asset_id=row["source_asset_id"],
            source_glb_sha256=row["source_glb_sha256"], yard_id=row["yard_id"],
            packet_hash=row["packet_hash"], display_name=row["display_name"],
            mime_type=row["mime_type"], image_sha256=row["image_sha256"],
            authority_status=row["authority_status"], payload=image,
        )
    finally:
        con.close()
