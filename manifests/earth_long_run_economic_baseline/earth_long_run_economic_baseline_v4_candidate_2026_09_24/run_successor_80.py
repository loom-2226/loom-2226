"""Forward diagnostic from the repaired candidate boundary.

The inherited 2031-2060 REVIEW gate is retained in the candidate manifest.
Even a completed 2226 run remains unqualified until that gate is resolved.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
V3 = HERE.parent / "earth_long_run_economic_baseline_v3_repaired_2026_09_23"
EXPECTED_RUNNER = "32e927276fff88652780d041169d8e216fa2ecea1f0e34babb8f0b155a5b9c37"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", required=True, type=Path)
    parser.add_argument("--output-name", default="smoke_2061")
    parser.add_argument("--end-year", type=int, choices=(2061, 2226), default=2061)
    parser.add_argument("--allow-review-input", action="store_true", required=True)
    args = parser.parse_args()
    root = args.candidate_root
    manifest = json.loads((root / "CANDIDATE_2060_MANIFEST.json").read_text())
    if manifest["status"] == "CANDIDATE_REVIEW_GATE_NOT_QUALIFIED" and not args.allow_review_input:
        raise ValueError("2060 boundary not qualified")
    runner_path = V3 / "runner.py"
    if hashlib.sha256(runner_path.read_bytes()).hexdigest() != EXPECTED_RUNNER:
        raise ValueError("inherited v3 numerical runner changed")
    sys.path.insert(0, str(V3))
    spec = importlib.util.spec_from_file_location("candidate_v3_numerical_runner", runner_path)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.FREEZE = root / "stage_2031_2060"
    runner.COUNTRIES_2060_SRC = runner.FREEZE / "countries_2060.ndjson"
    runner.SECTORS_2060_SRC = runner.FREEZE / "country_sectors_2060.ndjson"
    runner.ASSETS_2060_SRC = runner.FREEZE / "country_sector_assets_2060.ndjson"
    runner.FREEZE_MANIFEST = root / "CANDIDATE_2060_MANIFEST.json"
    runner.POLICY_FINGERPRINT = manifest["economic_policy"]["ordered_vector_sha256"]
    previous = sys.argv
    sys.argv = [str(runner_path), "--output-dir", str(root / args.output_name), "--alpha-ceiling", "0.60"]
    if args.end_year == 2061:
        sys.argv.extend(("--stop-after", "2061"))
    try:
        runner._options, runner._checkpoint_dir, runner._output_year = runner._configure_checkpoint_run()
    finally:
        sys.argv = previous
    runner.main()


if __name__ == "__main__":
    main()
