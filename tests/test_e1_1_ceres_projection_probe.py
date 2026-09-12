from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "spikes" / "e1_1_ceres_projection_probe.py"


def load_probe():
    spec = importlib.util.spec_from_file_location("e1_1_ceres_projection_probe", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute("CREATE TABLE places (id TEXT PRIMARY KEY, name TEXT, role TEXT)")
        conn.execute("CREATE TABLE edges (src TEXT, dst TEXT, relation TEXT)")
        conn.execute(
            "INSERT INTO places VALUES (?, ?, ?)",
            ("CERES", "Ceres", "Belt civic/network hub"),
        )
        conn.execute(
            "INSERT INTO places VALUES (?, ?, ?)",
            ("MARS", "Mars", "planetary node"),
        )
        conn.execute(
            "INSERT INTO edges VALUES (?, ?, ?)",
            ("CERES", "VESTA", "commercial"),
        )
        conn.commit()
    finally:
        conn.close()


def test_probe_finds_entity_without_mutating_database(tmp_path: Path):
    probe = load_probe()
    db = tmp_path / "world.sqlite3"
    build_db(db)
    before = probe.sha256_file(db)

    result = probe.inspect_database("WORLD", db, "Ceres")

    after = probe.sha256_file(db)
    assert before == after
    assert result["mode"] == "READ_ONLY"
    assert result["matching_relation_count"] >= 1
    names = {x["relation"] for x in result["matching_relations"]}
    assert "places" in names


def test_probe_is_case_insensitive(tmp_path: Path):
    probe = load_probe()
    db = tmp_path / "civ.sqlite3"
    build_db(db)

    result = probe.inspect_database("CIVSTATE", db, "ceres")

    assert result["sampled_matching_rows"] >= 1


def test_missing_database_fails_closed_as_absent(tmp_path: Path):
    probe = load_probe()
    missing = tmp_path / "missing.sqlite3"

    result = probe.inspect_database("WORLD", missing, "Ceres")

    assert result["exists"] is False
    assert result["relations_scanned"] == 0
    assert result["matching_relations"] == []
