#!/usr/bin/env python3
from __future__ import annotations

"""Retain a passed E1 Neptune disposable qualification sandbox.

This wrapper does not implement or modify flight behavior. It invokes the existing
`e1_neptune_disposable_campaign.py` harness unchanged, substitutes only that
harness's temporary-directory provider, and retains the resulting campaign copy
iff the existing qualification passes and the retained restart state independently
matches the qualified Neptune arrival.

The real campaign remains the source input and must remain bit-identical according
to the underlying qualification result.
"""

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping

SCRIPT_PATH = Path(__file__).resolve()
QUAL_DIR = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[3]
ANDROID_ROOT = Path("/storage/emulated/0/Download")
DEFAULT_ROOT = ANDROID_ROOT if ANDROID_ROOT.exists() else Path.cwd()
DEFAULT_SANDBOX = DEFAULT_ROOT / "LOOM_E1_NEPTUNE_QUALIFIED"
DEFAULT_RESULT = DEFAULT_ROOT / "E1_NEPTUNE_RETAINED_QUALIFICATION_RESULT.json"
STATE_FILE = "LOOM_STATE_V1.json"
MARKER_FILE = "E1_RETAINED_SANDBOX.json"


def _load_existing_harness():
    if str(QUAL_DIR) not in sys.path:
        sys.path.insert(0, str(QUAL_DIR))
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    path = QUAL_DIR / "e1_neptune_disposable_campaign.py"
    spec = importlib.util.spec_from_file_location("loom_e1_existing_disposable_harness", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import existing qualification harness: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _RetainedDirectory:
    def __init__(self, root: Path) -> None:
        self.root = root

    def __enter__(self) -> str:
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True, exist_ok=False)
        return str(self.root)

    def __exit__(self, exc_type, exc, tb) -> bool:
        # The wrapper decides whether to retain or remove after the underlying
        # harness returns. Never suppress an exception.
        return False


def _tempfile_proxy(root: Path) -> SimpleNamespace:
    return SimpleNamespace(TemporaryDirectory=lambda *a, **k: _RetainedDirectory(root))


def validate_retained_sandbox(root: Path, result: Mapping[str, Any]) -> dict[str, Any]:
    if result.get("qualification_pass") is not True:
        raise RuntimeError("underlying E1 Neptune qualification did not PASS")
    if result.get("real_campaign_unchanged_pass") is not True:
        raise RuntimeError("real campaign unchanged gate did not PASS")
    if result.get("restart_destination_pass") is not True:
        raise RuntimeError("qualified restart destination gate did not PASS")

    state_path = root / STATE_FILE
    if not state_path.exists():
        raise RuntimeError("retained sandbox is missing authoritative campaign state")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise RuntimeError("retained sandbox state is not a JSON object")

    state_id = str(state.get("state_id") or "")
    location = str(state.get("location_token") or "").upper()
    epoch = str(state.get("epoch_utc") or "")
    expected_state = str(result.get("restart_state_id") or "")
    expected_location = str(result.get("restart_location") or "").upper()

    if not state_id or state_id != expected_state:
        raise RuntimeError("retained sandbox state_id does not match qualified restart state")
    if location not in {"NEPTUNE", "NEPTUNE_SYSTEM"}:
        raise RuntimeError(f"retained sandbox is not at Neptune: {location!r}")
    if expected_location and location != expected_location:
        raise RuntimeError("retained sandbox location does not match qualified restart location")
    if not epoch or epoch != str(result.get("restart_epoch_utc") or epoch):
        raise RuntimeError("retained sandbox epoch does not match qualified restart epoch")

    return {
        "schema": "LOOM_E1_RETAINED_SANDBOX_V1",
        "authority": "QUALIFIED_DISPOSABLE_CAMPAIGN_COPY",
        "source_harness": "e1_neptune_disposable_campaign.py",
        "qualification_pass": True,
        "real_campaign_unchanged_pass": True,
        "state_id": state_id,
        "location_token": location,
        "epoch_utc": epoch,
        "remass_t": state.get("ship", {}).get("remass_t"),
        "wet_mass_t": state.get("ship", {}).get("wet_mass_t"),
        "hud_safe_read_only": True,
        "production_campaign": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--sandbox", type=Path, default=DEFAULT_SANDBOX)
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--epoch", default=None)
    args = parser.parse_args()

    harness = _load_existing_harness()
    sandbox = args.sandbox.resolve()
    result_path = args.out.resolve()

    original_tempfile = harness.tempfile
    original_argv = sys.argv[:]
    harness.tempfile = _tempfile_proxy(sandbox)

    harness_args = [
        str(harness.SCRIPT_PATH),
        "--root", str(args.root.resolve()),
        "--out", str(result_path),
    ]
    # `--epoch` belongs to the outer Pixel runner, not the disposable harness;
    # retained qualification therefore consumes the same campaign epoch already
    # present in the authoritative source state.
    try:
        sys.argv = harness_args
        rc = int(harness.main())
    except Exception:
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=True)
        raise
    finally:
        sys.argv = original_argv
        harness.tempfile = original_tempfile

    try:
        if rc != 0:
            raise RuntimeError(f"underlying E1 Neptune qualification returned {rc}")
        if not result_path.exists():
            raise RuntimeError("underlying qualification result was not written")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        summary = validate_retained_sandbox(sandbox, result)
        marker = sandbox / MARKER_FILE
        marker.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    except Exception:
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=True)
        raise

    print(json.dumps({
        "retained_sandbox_pass": True,
        "sandbox": str(sandbox),
        "qualification_result": str(result_path),
        **summary,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
