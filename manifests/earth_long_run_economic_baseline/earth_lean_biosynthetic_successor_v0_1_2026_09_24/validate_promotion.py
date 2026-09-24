"""Fail-closed validation for the promoted lean biosynthetic Earth successor."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[2]
MANIFEST = PACKAGE / "PROMOTION_MANIFEST.json"


class PromotionValidationError(ValueError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(manifest_path: Path = MANIFEST) -> dict:
    manifest = load_json(manifest_path)
    if manifest.get("schema") != "loom-earth-biosynthetic-promotion-manifest-v1":
        raise PromotionValidationError("Unsupported promotion manifest")
    if manifest.get("designation") != "EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24":
        raise PromotionValidationError("Wrong promoted designation")
    if manifest.get("selected_scenario") != "MED_CENTRAL__SYNTH_CENTRAL":
        raise PromotionValidationError("Wrong selected scenario")
    if manifest.get("research_source", {}).get("candidate_commit") != "d9f5065e390a1ce0c1cca78f68a14317dc03d723":
        raise PromotionValidationError("Wrong Research Lab candidate source")
    if manifest.get("research_source", {}).get("merged_commit") != "cb4e63554f8ecfaf35a8c3b70275fea479959fbd":
        raise PromotionValidationError("Wrong Research Lab merge source")

    for item in manifest.get("files", []):
        path = REPO / item["path"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            raise PromotionValidationError(f"Artifact mismatch: {item['path']}")

    source_manifest = PACKAGE / "v0_1/results/CANDIDATE_MANIFEST.json"
    if sha256(source_manifest) != "508580bfe37877d796da1ad74f92b8bcba4a6857cdab5cc25e4cc55d5fff3653":
        raise PromotionValidationError("Research candidate manifest mismatch")

    selected = load_json(PACKAGE / "v0_1/results/selected_scenario.json")
    endpoint = selected["endpoint"]
    expected = {
        "biological_population": 7163281708.265873,
        "synthetic_population": 9672505.78986048,
        "recognized_person_population": 7172954214.055734,
        "biological_labor": 1455527766.770138,
        "synthetic_labor": 10881569.013593039,
        "machine_task_capacity": 52627339.05102448,
        "total_effective_labor": 1519036674.8347554,
        "value_added_80": 241453886085432.44,
    }
    if selected.get("selection") != manifest["selected_scenario"] or endpoint.get("qualification") != "PASS":
        raise PromotionValidationError("Selected scenario is not qualified")
    for field, value in expected.items():
        if not math.isclose(endpoint[field], value, rel_tol=1e-13, abs_tol=1e-6):
            raise PromotionValidationError(f"Selected endpoint mismatch: {field}")
    if not math.isclose(endpoint["recognized_person_population"],
                        endpoint["biological_population"] + endpoint["synthetic_population"],
                        rel_tol=1e-13, abs_tol=1e-6):
        raise PromotionValidationError("Recognized-person identity failed")
    if not math.isclose(endpoint["total_effective_labor"],
                        endpoint["biological_labor"] + endpoint["synthetic_labor"] + endpoint["machine_task_capacity"],
                        rel_tol=1e-13, abs_tol=1e-6):
        raise PromotionValidationError("Labor composition identity failed")
    if endpoint["machine_task_capacity"] == endpoint["synthetic_population"]:
        raise PromotionValidationError("Machine tasks were mixed with synthetic persons")

    grid = load_json(PACKAGE / "v0_1/results/sensitivity_grid.json")
    if (grid.get("qualification") != "PASS" or grid.get("failures") or len(grid.get("runs", [])) != 9 or
            len({r["medical"] for r in grid["runs"]}) != 3 or
            len({r["synthetic"] for r in grid["runs"]}) != 3):
        raise PromotionValidationError("Sensitivity grid is incomplete or failed")

    countries = load_json(PACKAGE / "v0_1/results/selected_countries_2226.json")
    if len(countries) != 80 or len({row["iso3"] for row in countries}) != 80:
        raise PromotionValidationError("Economic roster mismatch")
    violations = [row["iso3"] for row in countries
                  if not (row["biological_labor"] <= row["labor_capable_biological_population"]
                          <= row["biological_population"])]
    if violations:
        raise PromotionValidationError(f"Workforce/population invariant failed: {violations}")
    if any(row["synthetic_labor"] > 0 and row["synthetic_population"] <= 0 for row in countries):
        raise PromotionValidationError("Synthetic labor lacks supporting persons")
    if any(not math.isclose(row["recognized_person_population"],
                            row["biological_population"] + row["synthetic_population"],
                            rel_tol=1e-12, abs_tol=1e-5) for row in countries):
        raise PromotionValidationError("Country recognized-person identity failed")

    with (PACKAGE / "v0_1/results/selected_country_demography_2226.csv").open(encoding="utf-8") as stream:
        demographic_rows = list(csv.DictReader(stream))
    if len(demographic_rows) != 237 or len({row["iso3"] for row in demographic_rows}) != 237:
        raise PromotionValidationError("Demographic roster mismatch")

    annual = {
        "biological": load_json(PACKAGE / "v0_1/results/selected_annual_biological_summary.json"),
        "synthetic": load_json(PACKAGE / "v0_1/results/selected_annual_synthetic_summary.json"),
        "labor": load_json(PACKAGE / "v0_1/results/selected_annual_labor_composition.json"),
        "economic": load_json(PACKAGE / "v0_1/results/selected_annual_economic_summary.json"),
    }
    years = list(range(2100, 2227))
    if any([row["year"] for row in rows] != years for rows in annual.values()):
        raise PromotionValidationError("Annual trajectory coverage mismatch")
    for row in annual["labor"]:
        if not math.isclose(row["total_effective_labor"],
                            row["biological_labor"] + row["synthetic_labor"] + row["machine_task_capacity"],
                            rel_tol=1e-12, abs_tol=1e-6):
            raise PromotionValidationError(f"Annual labor composition failed in {row['year']}")

    return {
        "status": "PASS",
        "designation": manifest["designation"],
        "selected_scenario": manifest["selected_scenario"],
        "verified_files": len(manifest["files"]),
        "demographic_areas": len(demographic_rows),
        "economic_economies": len(countries),
        "workforce_invariant_passed": len(countries),
        "workforce_invariant_failed": 0,
        "endpoint": expected,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
