"""Run the selected CIVPROP Hybrid Engine V1 reference against the frozen Method Lab."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .contracts import canonical_json, load_bundle, validate_result
from .prototypes.hybrid_v1 import HybridEngineV1
from .run_prototypes import summarize_result


def run_selected(directory: Path, seed: int = 42):
    bundle = load_bundle(Path(directory))
    engine = HybridEngineV1()
    result = engine.run(bundle, seed)
    validate_result(result, bundle)
    summary = summarize_result(result, bundle.scenario.end_year)
    summary.update(
        {
            "format": "CIVPROP_HYBRID_V1_SUMMARY",
            "engine_id": engine.engine_id,
            "engine_version": engine.engine_version,
            "input_bundle_sha256": bundle.bundle_sha256,
            "seed": seed,
            "full_result_sha256": hashlib.sha256(
                canonical_json(result).encode()
            ).hexdigest(),
        }
    )
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    directory = Path(__file__).resolve().parent
    summary = run_selected(directory, args.seed)
    text = json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
