#!/usr/bin/env python3
"""Reproduce only the promoted v4 economic prefix needed for a 2100 checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v4-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads((args.v4_root / "RUN_MANIFEST.json").read_text())
    runner_record = manifest["inherited_code_dependencies"]["v3_runner.py"]
    runner_path = Path(runner_record["path"])
    if sha256(runner_path) != runner_record["sha256"]:
        raise ValueError("promoted v4 runner hash mismatch")
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)

    sys.path.insert(0, str(runner_path.parent))
    spec = importlib.util.spec_from_file_location("v4_promoted_prefix_runner", runner_path)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)

    candidate_manifest_path = args.v4_root / "CANDIDATE_2060_MANIFEST.json"
    candidate_manifest = json.loads(candidate_manifest_path.read_text())
    first_registered_input = Path(next(iter(candidate_manifest["files"].values()))["path"])
    runner.FREEZE = first_registered_input.parent
    runner.COUNTRIES_2060_SRC = runner.FREEZE / "countries_2060.ndjson"
    runner.SECTORS_2060_SRC = runner.FREEZE / "country_sectors_2060.ndjson"
    runner.ASSETS_2060_SRC = runner.FREEZE / "country_sector_assets_2060.ndjson"
    runner.FREEZE_MANIFEST = candidate_manifest_path
    runner.POLICY_FINGERPRINT = candidate_manifest["economic_policy"]["ordered_vector_sha256"]

    previous = sys.argv
    sys.argv = [str(runner_path), "--output-dir", str(args.output_dir),
                "--stop-after", "2100", "--alpha-ceiling", "0.60"]
    try:
        runner._options, runner._checkpoint_dir, runner._output_year = runner._configure_checkpoint_run()
    finally:
        sys.argv = previous
    runner.main()

    checkpoint = args.output_dir / "complete_checkpoints/earth_2100.checkpoint.zip"
    if not checkpoint.is_file():
        raise RuntimeError("2100 checkpoint not produced")
    print(json.dumps({"status": "V4_2100_PREFIX_REPRODUCED", "checkpoint": str(checkpoint),
                      "checkpoint_sha256": sha256(checkpoint)}, sort_keys=True))


if __name__ == "__main__":
    main()
