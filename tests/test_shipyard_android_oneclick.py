from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "deploy" / "android" / "loom_update_shipyard.py"
MIGRATOR = ROOT / "src" / "shipyard_migrate.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_overlay_manifest_is_bounded_and_pinned() -> None:
    manifest = json.loads((ROOT / "manifests" / "release_manifest.json").read_text(encoding="utf-8"))
    assert manifest["release_state"] == "staging"
    assert manifest["source_ref"] == "research/computational-shipyard-android-oneclick-v0.1-2026-09-08"
    paths = [row["path"] for row in manifest["artifacts"]]
    assert paths == [
        "deploy/loom_update.py",
        "src/shipyard_migrate.py",
        "deploy/android/loom_update_shipyard.py",
    ]
    assert all(row["install_group"] == "code" for row in manifest["artifacts"])
    assert all(row.get("git_blob_sha1") for row in manifest["artifacts"])


def test_wrapper_paths_match_runtime_install_layout() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    assert 'DEPLOY / "loom_update.py"' in text
    assert 'APP_ROOT / "src" / "shipyard_migrate.py"' in text
    assert "migrator.apply_phase2()" in text


def test_migrator_refuses_empty_sqlite(tmp_path: Path) -> None:
    module = _load(MIGRATOR, "shipyard_migrate_oneclick_test")
    db = tmp_path / "wrong.sqlite3"
    sqlite3.connect(db).close()
    try:
        module.apply_phase2(db)
    except RuntimeError as exc:
        assert "not a LOOM Shipyard" in str(exc)
    else:
        raise AssertionError("standalone migrator accepted non-Shipyard SQLite")
