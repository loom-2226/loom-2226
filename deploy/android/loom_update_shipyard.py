#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
DEPLOY = HERE.parents[1]
APP_ROOT = HERE.parents[2]
BASE_UPDATER = DEPLOY / "loom_update.py"
MIGRATOR = APP_ROOT / "src" / "shipyard_migrate.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not BASE_UPDATER.is_file():
        raise RuntimeError(f"Base LOOM updater not installed: {BASE_UPDATER}")
    updater = _load("loom_update_runtime", BASE_UPDATER)
    rc = int(updater.main(argv))
    if rc != 0:
        print("SHIPYARD MIGRATION SKIPPED: base LOOM update did not complete cleanly")
        return rc
    if "--dry-run" in argv or (argv and argv[0] in {"status", "validate"}):
        print("SHIPYARD MIGRATION SKIPPED: non-mutating updater mode")
        return 0
    if not MIGRATOR.is_file():
        raise RuntimeError(f"Shipyard migrator not installed: {MIGRATOR}")
    migrator = _load("shipyard_migrate_runtime", MIGRATOR)
    result = migrator.apply_phase2()
    print("\nSHIPYARD LOCAL MIGRATION")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("\nLOOM + SHIPYARD UPDATE COMPLETE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"SHIPYARD UPDATE FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
