"""Build the deterministic Git authority manifest for this promoted package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[2]
OUTPUT = PACKAGE / "PROMOTION_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    files = []
    for path in sorted(PACKAGE.rglob("*")):
        if (not path.is_file() or path == OUTPUT or "__pycache__" in path.parts or
                path.suffix in {".pyc", ".pyo"}):
            continue
        files.append({
            "path": path.relative_to(REPO).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "schema": "loom-earth-biosynthetic-promotion-manifest-v1",
        "designation": "EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24",
        "status": "ACTIVE_SELECTED_EARTH_AUTHORITY",
        "authority_boundary": {
            "empirical_demography_through_year": 2100,
            "selected_modeled_successor_start_year": 2101,
            "selected_modeled_successor_end_year": 2226,
            "demographic_areas": 237,
            "economic_economies": 80,
        },
        "selected_scenario": "MED_CENTRAL__SYNTH_CENTRAL",
        "research_source": {
            "repository": "loom-2226/loom-research-lab",
            "pull_request": 75,
            "candidate_commit": "d9f5065e390a1ce0c1cca78f68a14317dc03d723",
            "merged_commit": "cb4e63554f8ecfaf35a8c3b70275fea479959fbd",
            "candidate_manifest_sha256": "508580bfe37877d796da1ad74f92b8bcba4a6857cdab5cc25e4cc55d5fff3653",
        },
        "selection": {
            "rule": "EXPLICIT_PARAMETER_MIDDLE_CASE_AFTER_ALL_NINE_RUNS_QUALIFIED",
            "endpoint_fitted": False,
            "sensitivity_grid_runs": 9,
            "qualification": "PASS",
        },
        "category_contract": {
            "biological_humans_are_synthetic_persons": False,
            "synthetic_persons_are_machine_tasks": False,
            "machine_tasks_count_as_population": False,
        },
        "supersedes": {
            "demographic_authority": "EARTH_2226_CANON_CONSTRAINED_COUNTRY_ALLOCATION",
            "economic_authority_after_2100": "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24",
        },
        "preserved_provenance": [
            "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24",
            "EARTH_2226_CANON_CONSTRAINED_COUNTRY_ALLOCATION",
            "EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23",
        ],
        "rollback": {
            "designation": "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24",
            "economic_manifest": "manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_2026_09_24/BASELINE_MANIFEST.json",
            "demographic_manifest": "manifests/earth_long_run_economic_baseline/earth_demographic_correction_v4_1_2026_09_24/CORRECTION_MANIFEST.json",
        },
        "files": files,
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
