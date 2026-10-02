#!/usr/bin/env python3
"""Create an ephemeral MEDIA database for Atlas tests from approved test fixtures."""
import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BODY = {
    "asset_id": "0e516224-6345-4e97-b6d1-569bf193f495",
    "media_key": "2c6211b6-6cd2-4b62-89f7-cb795fdbac51",
    "filename": ROOT / "web/ceres-atlas/assets/ceres-world-hero.png",
    "sha256": "fa5fc5876d8f66631837ce498d77e139444b9247e8b2a66ff6dd8ad611e1f08e",
    "byte_length": 1261154,
}


def create_fixture(path: Path) -> None:
    rows = [BODY]
    for record in json.loads((ROOT / "docs/ceres/manifest.json").read_text()):
        rows.append({
            "asset_id": record["asset_id"], "media_key": record["media_key"],
            "filename": ROOT / "docs/ceres" / record["filename"],
            "sha256": record["sha256"], "byte_length": record["byte_length"],
        })
    with sqlite3.connect(path) as connection:
        connection.execute("""CREATE TABLE media_assets (
            media_key TEXT PRIMARY KEY, asset_id TEXT NOT NULL, mime_type TEXT NOT NULL,
            original_blob BLOB, original_byte_length INTEGER, original_sha256 TEXT
        )""")
        for row in rows:
            content = Path(row["filename"]).read_bytes()
            connection.execute("INSERT INTO media_assets VALUES (?,?,?,?,?,?)", (
                row["media_key"], row["asset_id"], "image/png", content,
                row["byte_length"], row["sha256"],
            ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    create_fixture(parser.parse_args().output)
