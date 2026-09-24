#!/usr/bin/env python3
"""Materialize the bounded v0.1 parameter grid from explicit overrides."""

import argparse
import copy
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--sensitivity", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    base = json.loads(args.base.read_text(encoding="utf-8"))
    sensitivity = json.loads(args.sensitivity.read_text(encoding="utf-8"))
    args.output_root.mkdir(parents=True, exist_ok=True)
    records = []
    for med_name, med in sensitivity["medical_scenarios"].items():
        for synth_name, synth in sensitivity["synthetic_scenarios"].items():
            value = copy.deepcopy(base)
            value["schema"] = "loom-earth-lean-biosynthetic-parameters-v0.1-scenario"
            value["scenario"] = {"medical": med_name, "synthetic": synth_name}
            value["status"] = "V0_1_SENSITIVITY_NON_CANON_NOT_ENDPOINT_FITTED"
            value["medicine"].update({key: item for key, item in med.items() if key != "description"})
            value["synthetic_persons"].update(synth)
            value["allocation_repair"] = sensitivity["allocation_repair"]
            name = f"{med_name}__{synth_name}.json"
            path = args.output_root / name
            path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            records.append({"medical": med_name, "synthetic": synth_name, "path": str(path)})
    (args.output_root / "grid_manifest.json").write_text(
        json.dumps({"schema": "LOOM_EARTH_BIOSYNTHETIC_V0_1_GRID", "runs": records},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"scenarios": len(records), "output_root": str(args.output_root)}, sort_keys=True))


if __name__ == "__main__":
    main()
