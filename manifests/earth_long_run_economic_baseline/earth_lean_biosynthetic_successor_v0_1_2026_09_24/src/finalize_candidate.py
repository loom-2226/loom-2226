#!/usr/bin/env python3
"""Create compact, reviewable reports from the validated local candidate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


DESIGNATION = "EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_CANDIDATE_2026_09_24"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def ndjson(path: Path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def top(rows, key, count=20):
    return [{"rank": rank, **row} for rank, row in enumerate(
        sorted(rows, key=lambda item: item[key], reverse=True)[:count], 1)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--demographic-root", type=Path, required=True)
    parser.add_argument("--economic-root", type=Path, required=True)
    parser.add_argument("--v4-root", type=Path, required=True)
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--authority-root", type=Path, required=True)
    args = parser.parse_args()
    results = args.project / "results"
    results.mkdir(exist_ok=True)

    validation = load(args.demographic_root / "independent_validation.json")
    if validation["status"] != "PASS":
        raise ValueError("candidate must pass independent validation")
    demography = load(args.demographic_root / "annual_biological_summary.json")
    synthetic = load(args.economic_root / "annual_synthetic_summary.json")
    labor = load(args.economic_root / "annual_labor_composition.json")
    economy = load(args.economic_root / "annual_economic_summary.json")
    candidate_countries = load(args.economic_root / "countries_2226.json")
    v4_countries = ndjson(args.v4_root / "successor_80_2226/results/countries_2226.ndjson")
    with (args.demographic_root / "country_demography_2226.csv").open(encoding="utf-8") as handle:
        demographic_countries = [dict(row, population=float(row["population"])) for row in csv.DictReader(handle)]
    with args.bridge.open(encoding="utf-8") as handle:
        bridge = [dict(row, population_2226=float(row["population_2226"])) for row in csv.DictReader(handle)]

    v4_by_iso = {row["iso3"]: row for row in v4_countries}
    cand_by_iso = {row["iso3"]: row for row in candidate_countries}
    v4_va = sum(row["value_added"] for row in v4_countries)
    comparisons = []
    v4_rank = {row["iso3"]: rank for rank, row in enumerate(
        sorted(v4_countries, key=lambda x: x["value_added"], reverse=True), 1)}
    cand_rank = {row["iso3"]: rank for rank, row in enumerate(
        sorted(candidate_countries, key=lambda x: x["value_added"], reverse=True), 1)}
    for iso in sorted(cand_by_iso):
        old, new = v4_by_iso[iso], cand_by_iso[iso]
        comparisons.append({
            "iso3": iso,
            "v4_value_added": old["value_added"],
            "candidate_value_added": new["value_added"],
            "value_added_change_fraction": new["value_added"] / old["value_added"] - 1.0,
            "v4_rank": v4_rank[iso], "candidate_rank": cand_rank[iso],
            "rank_change_positive_is_rise": v4_rank[iso] - cand_rank[iso],
        })

    comparison = {
        "schema": "LOOM_EARTH_LEAN_BIOSYNTHETIC_COMPARISON_v0",
        "designation": DESIGNATION,
        "current_promoted_bridge_v4": {
            "biological_population_2226": sum(row["population_2226"] for row in bridge),
            "synthetic_population_2226": None,
            "recognized_person_population_2226": None,
            "biological_age_structure": None,
            "biological_labor": None,
            "synthetic_labor": None,
            "machine_task_capacity": None,
            "total_effective_labor": sum(row["effective_labor_input"] for row in v4_countries),
            "value_added": v4_va,
            "note": "Null means the promoted bridge/v4 does not model the category; it is not zero.",
        },
        "candidate_2226": {
            "biological_population": demography[-1]["population"],
            "synthetic_population": synthetic[-1]["population"],
            "recognized_person_population": demography[-1]["population"] + synthetic[-1]["population"],
            "median_biological_age_approx": demography[-1]["median_age_approx_country_weighted"],
            "age_structure": {key: demography[-1][key] for key in (
                "under_20", "age_20_64", "age_65_plus", "age_80_plus",
                "age_100_plus", "age_120_plus", "age_150_plus")},
            "biological_labor": labor[-1]["biological_labor"],
            "synthetic_labor": labor[-1]["synthetic_labor"],
            "machine_task_capacity": labor[-1]["machine_task_capacity"],
            "total_effective_labor": labor[-1]["total_effective_labor"],
            "value_added": economy[-1]["value_added"],
        },
        "candidate_minus_v4": {
            "biological_population": demography[-1]["population"] - sum(row["population_2226"] for row in bridge),
            "total_effective_labor": labor[-1]["total_effective_labor"] - sum(row["effective_labor_input"] for row in v4_countries),
            "value_added": economy[-1]["value_added"] - v4_va,
            "value_added_fraction": economy[-1]["value_added"] / v4_va - 1.0,
        },
        "economy_rank_changes": sorted(comparisons, key=lambda x: abs(x["rank_change_positive_is_rise"]), reverse=True),
    }
    write(results / "COMPARISON_CURRENT_V4_TO_CANDIDATE.json", comparison)

    outliers = {
        "top_20_biological_populations": top(demographic_countries, "population"),
        "top_20_qualified_economies_by_value_added": top(candidate_countries, "value_added"),
        "largest_biological_labor_shares": top([
            {"iso3": r["iso3"], "share": r["biological_labor"] / r["effective_labor_input"]}
            for r in candidate_countries], "share"),
        "largest_synthetic_labor_shares": top([
            {"iso3": r["iso3"], "share": r["synthetic_labor"] / r["effective_labor_input"]}
            for r in candidate_countries], "share"),
        "largest_automation_shares": top([
            {"iso3": r["iso3"], "share": r["machine_task_capacity"] / r["effective_labor_input"]}
            for r in candidate_countries], "share"),
        "largest_value_added_changes": sorted(comparisons, key=lambda x: abs(x["value_added_change_fraction"]), reverse=True)[:20],
        "boundary_repairs": load(args.demographic_root / "labor_boundary_repairs_2100.json"),
    }
    write(results / "OUTLIER_REVIEW.json", outliers)

    source_paths = {
        "wpp_age_sex": Path("/home/ubuntu/LOOM_Earth2026/raw/WPP2024_PopulationByAge5GroupSex_Percentage_Medium.csv.gz"),
        "wpp_indicators": Path("/home/ubuntu/LOOM_Earth2026/raw/WPP2024_Demographic_Indicators_Medium.csv.gz"),
        "recovered_v03": args.project / "sources/recovered/LOOM_2226_Earth_Demographic_and_Social_Propagation_Model_v0.3-1.md",
        "recovered_v04": args.project / "sources/recovered/LOOM_2226_Earth_Demographic_Model_v0.4_social_scenarios.csv",
        "technology_timeline": args.authority_root / "docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md",
        "demography_lineage": args.authority_root / "manifests/earth_long_run_economic_baseline/EARTH_DEMOGRAPHY_LINEAGE_RECOVERY_2026_09_24.md",
        "current_bridge": args.bridge,
        "v4_manifest": args.v4_root / "BASELINE_MANIFEST.json",
        "v4_2100_checkpoint": args.demographic_root / "v4_control_to_2100/complete_checkpoints/earth_2100.checkpoint.zip",
    }
    provenance = {
        "schema": "LOOM_EARTH_LEAN_BIOSYNTHETIC_SOURCE_MANIFEST_v0",
        "designation": DESIGNATION,
        "authority_main_sha": "817103d9d8640b6400047a1d02fd479633e8323d",
        "source_files": {name: {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}
                         for name, path in source_paths.items()},
        "authority_roles": {
            "wpp": "EMPIRICAL_DEMOGRAPHY_THROUGH_2100",
            "recovered_lineage": "SETTING_CALIBRATION_AND_PROVENANCE",
            "technology_timeline": "TECHNOLOGY_BOUNDARY; OFF_EARTH_MED_EVENTS_NOT_USED_AS_EARTH_MULTIPLIERS",
            "current_bridge": "PROMOTED_COMPARATOR_ONLY",
            "v4": "QUALIFIED_80_ECONOMY_BOUNDARY_AND_ENGINE",
        },
    }
    write(results / "SOURCE_PROVENANCE.json", provenance)

    compact_files = {
        "annual_biological_summary.json": args.demographic_root / "annual_biological_summary.json",
        "annual_synthetic_summary.json": args.economic_root / "annual_synthetic_summary.json",
        "annual_labor_composition.json": args.economic_root / "annual_labor_composition.json",
        "annual_economic_summary.json": args.economic_root / "annual_economic_summary.json",
        "country_demography_2226.csv": args.demographic_root / "country_demography_2226.csv",
        "countries_2226.json": args.economic_root / "countries_2226.json",
        "country_sectors_2226.json": args.economic_root / "country_sectors_2226.json",
        "country_sector_assets_2226.json": args.economic_root / "country_sector_assets_2226.json",
        "demography_report.json": args.demographic_root / "demography_report.json",
        "economic_report.json": args.economic_root / "economic_report.json",
        "independent_validation.json": args.demographic_root / "independent_validation.json",
    }
    for name, source in compact_files.items():
        (results / name).write_bytes(source.read_bytes())

    all_local = {}
    for path in sorted(args.demographic_root.glob("*")):
        if path.is_file():
            all_local[str(path)] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    for path in sorted(args.economic_root.glob("*")):
        if path.is_file():
            all_local[str(path)] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    manifest = {
        "schema": "LOOM_EARTH_LEAN_BIOSYNTHETIC_CANDIDATE_MANIFEST_v0",
        "designation": DESIGNATION,
        "status": "RESEARCH_CANDIDATE_NOT_PROMOTED",
        "validation": "PASS",
        "scope": {"demographic_areas": 237, "economic_economies": 80, "years": [2100, 2226]},
        "terminal": validation["terminal"],
        "local_artifacts": all_local,
        "git_results": {},
    }
    write(results / "CANDIDATE_MANIFEST.json", manifest)
    manifest["git_results"] = {
        path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
        for path in sorted(results.iterdir()) if path.is_file() and path.name != "CANDIDATE_MANIFEST.json"
    }
    write(results / "CANDIDATE_MANIFEST.json", manifest)
    print(json.dumps({"designation": DESIGNATION, "validation": "PASS",
                      "results": len(list(results.iterdir()))}, sort_keys=True))


if __name__ == "__main__":
    main()
