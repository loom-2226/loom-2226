#!/usr/bin/env python3
"""Summarize and independently qualify the bounded v0.1 nine-run grid."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


DESIGNATION = "EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_CANDIDATE_2026_09_24"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def concentration(rows, key):
    values = sorted((float(row[key]) for row in rows), reverse=True)
    total = sum(values)
    shares = [value / total for value in values]
    return {"top_1_share": shares[0], "top_5_share": sum(shares[:5]),
            "hhi": sum(share * share for share in shares)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid-root", type=Path, required=True)
    parser.add_argument("--v0-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    failures = []
    records = []
    medical_names = ("MED_CONSERVATIVE", "MED_CENTRAL", "MED_HIGH")
    synth_names = ("SYNTH_LOW", "SYNTH_CENTRAL", "SYNTH_HIGH")
    for medical in medical_names:
        demographic_root = args.grid_root / "demography" / medical
        biological = load(demographic_root / "annual_biological_summary.json")
        with (demographic_root / "country_demography_2226.csv").open(encoding="utf-8") as handle:
            bio_countries = list(csv.DictReader(handle))
        for synthetic in synth_names:
            scenario = f"{medical}__{synthetic}"
            run_root = args.grid_root / "runs_repaired" / scenario
            report = load(run_root / "economic_report.json")
            countries = load(run_root / "countries_2226.json")
            labor = load(run_root / "annual_labor_composition.json")
            synth = load(run_root / "annual_synthetic_summary.json")
            economy = load(run_root / "annual_economic_summary.json")
            scenario_failures = []
            if len(countries) != 80 or len({row["iso3"] for row in countries}) != 80:
                scenario_failures.append("economic identity universe")
            if len(bio_countries) != 237 or len({row["iso3"] for row in bio_countries}) != 237:
                scenario_failures.append("demographic identity universe")
            expected_years = list(range(2100, 2227))
            for name, series in (("biological", biological), ("synthetic", synth),
                                 ("labor", labor), ("economic", economy)):
                if [row["year"] for row in series] != expected_years:
                    scenario_failures.append(f"{name} annual coverage")
            for previous, current in zip(biological, biological[1:]):
                expected = previous["population"] + previous["births"] - previous["deaths"]
                if not math.isclose(current["population"], expected, rel_tol=1e-10, abs_tol=2e-4):
                    scenario_failures.append("biological stock reconciliation")
                    break
            for row in labor:
                expected = row["biological_labor"] + row["synthetic_labor"] + row["machine_task_capacity"]
                if not math.isclose(row["total_effective_labor"], expected, rel_tol=1e-12, abs_tol=1e-6):
                    scenario_failures.append("labor composition")
                    break
            gates = report["max_residuals_and_movements"]
            for gate in ("capital_stock_flow_relative_residual",
                         "country_sector_reconciliation_relative_residual",
                         "sector_asset_reconciliation_relative_residual",
                         "production_equation_relative_residual",
                         "labor_composition_relative_residual"):
                if gates[gate] > 1e-9:
                    scenario_failures.append(gate)
            if not report["economic_level_continuity_2100"]:
                scenario_failures.append("2100 handoff")
            if any(row["biological_labor"] > row["labor_capable_biological_population"] + 1e-5
                   or row["biological_labor"] > row["biological_population"] + 1e-5
                   for row in countries):
                scenario_failures.append("biological labor bound")
            if scenario_failures:
                failures.extend(f"{scenario}: {failure}" for failure in scenario_failures)
            biological_terminal = biological[-1]
            labor_terminal = labor[-1]
            synth_concentration = concentration(countries, "synthetic_population")
            machine_concentration = concentration(countries, "machine_task_capacity")
            records.append({
                "scenario": scenario, "medical": medical, "synthetic": synthetic,
                "qualification": "PASS" if not scenario_failures else "FAIL",
                "biological_population": biological_terminal["population"],
                "synthetic_population": synth[-1]["population"],
                "recognized_person_population": biological_terminal["population"] + synth[-1]["population"],
                "median_biological_age": biological_terminal["median_age_approx_country_weighted"],
                "age_65_plus_share": biological_terminal["age_65_plus_share"],
                "age_80_plus_share": biological_terminal["age_80_plus_share"],
                "age_100_plus_share": biological_terminal["age_100_plus_share"],
                "age_120_plus_share": biological_terminal["age_120_plus_share"],
                "age_150_plus_share": biological_terminal["age_150_plus_share"],
                "biological_labor": labor_terminal["biological_labor"],
                "synthetic_labor": labor_terminal["synthetic_labor"],
                "machine_task_capacity": labor_terminal["machine_task_capacity"],
                "total_effective_labor": labor_terminal["total_effective_labor"],
                "value_added_80": economy[-1]["value_added"],
                "synthetic_concentration": synth_concentration,
                "automation_concentration": machine_concentration,
                "maximum_country_synthetic_labor_share": max(
                    row["synthetic_labor"] / row["effective_labor_input"] for row in countries),
                "maximum_country_automation_share": max(
                    row["machine_task_capacity"] / row["effective_labor_input"] for row in countries),
                "top_20_biological_population": [
                    {"rank": rank, "iso3": row["iso3"], "name": row["name"],
                     "population": float(row["population"])}
                    for rank, row in enumerate(sorted(
                        bio_countries, key=lambda value: float(value["population"]), reverse=True)[:20], 1)],
                "top_20_economies_by_va": [
                    {"rank": rank, "iso3": row["iso3"], "value_added": row["value_added"]}
                    for rank, row in enumerate(sorted(
                        countries, key=lambda value: value["value_added"], reverse=True)[:20], 1)],
                "country_synthetic_labor_shares": {
                    row["iso3"]: row["synthetic_labor"] / row["effective_labor_input"] for row in countries},
                "country_automation_shares": {
                    row["iso3"]: row["machine_task_capacity"] / row["effective_labor_input"] for row in countries},
                "max_gate_residual": max(gates[key] for key in (
                    "capital_stock_flow_relative_residual",
                    "country_sector_reconciliation_relative_residual",
                    "sector_asset_reconciliation_relative_residual",
                    "production_equation_relative_residual",
                    "labor_composition_relative_residual")),
            })

    selected_name = "MED_CENTRAL__SYNTH_CENTRAL"
    selected = next(record for record in records if record["scenario"] == selected_name)
    v0_countries = load(args.v0_root / "countries_2226.json")
    before_after = {
        "v0_before": {
            "synthetic": concentration(v0_countries, "synthetic_population"),
            "automation": concentration(v0_countries, "machine_task_capacity"),
            "maximum_country_synthetic_labor_share": max(
                row["synthetic_labor"] / row["effective_labor_input"] for row in v0_countries),
            "maximum_country_automation_share": max(
                row["machine_task_capacity"] / row["effective_labor_input"] for row in v0_countries),
        },
        "v0_1_selected_after": {
            "synthetic": selected["synthetic_concentration"],
            "automation": selected["automation_concentration"],
            "maximum_country_synthetic_labor_share": selected["maximum_country_synthetic_labor_share"],
            "maximum_country_automation_share": selected["maximum_country_automation_share"],
        },
    }
    write(args.output_root / "sensitivity_grid.json", {
        "schema": "LOOM_EARTH_BIOSYNTHETIC_V0_1_SENSITIVITY_GRID",
        "designation": DESIGNATION, "runs": records, "failures": failures,
        "qualification": "PASS" if not failures and len(records) == 9 else "FAIL",
    })
    columns = [key for key in records[0] if not isinstance(records[0][key], (dict, list))]
    with (args.output_root / "sensitivity_grid.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow({key: record[key] for key in columns})
    write(args.output_root / "selected_scenario.json", {
        "schema": "LOOM_EARTH_BIOSYNTHETIC_V0_1_SELECTED_SCENARIO",
        "designation": DESIGNATION, "status": "WORKING_CENTRAL_RESEARCH_CANDIDATE_NOT_PROMOTED",
        "selection": selected_name,
        "selection_reason": "Explicit parameter-middle case; all nine runs qualify and no evidence establishes another case as uniquely superior.",
        "endpoint": selected,
    })
    write(args.output_root / "allocation_concentration_before_after.json", before_after)
    selected_run_root = args.grid_root / "runs_repaired" / selected_name
    selected_demographic_root = args.grid_root / "demography" / "MED_CENTRAL"
    compact_selected = {
        "selected_annual_biological_summary.json": selected_demographic_root / "annual_biological_summary.json",
        "selected_annual_synthetic_summary.json": selected_run_root / "annual_synthetic_summary.json",
        "selected_annual_labor_composition.json": selected_run_root / "annual_labor_composition.json",
        "selected_annual_economic_summary.json": selected_run_root / "annual_economic_summary.json",
        "selected_countries_2226.json": selected_run_root / "countries_2226.json",
        "selected_country_demography_2226.csv": selected_demographic_root / "country_demography_2226.csv",
        "selected_economic_report.json": selected_run_root / "economic_report.json",
    }
    for name, source in compact_selected.items():
        (args.output_root / name).write_bytes(source.read_bytes())
    manifest_files = sorted(args.output_root.glob("*"))
    write(args.output_root / "CANDIDATE_MANIFEST.json", {
        "schema": "LOOM_EARTH_BIOSYNTHETIC_V0_1_CANDIDATE_MANIFEST",
        "designation": DESIGNATION, "status": "RESEARCH_CANDIDATE_NOT_PROMOTED",
        "grid_runs": 9, "qualification": "PASS" if not failures else "FAIL",
        "selected_scenario": selected_name,
        "local_grid_root": str(args.grid_root),
        "local_run_artifacts": {
            str(path): {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in sorted(args.grid_root.rglob("*")) if path.is_file()
        },
        "checked_in_results": {
            path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in manifest_files
            if path.is_file() and path.name != "CANDIDATE_MANIFEST.json"
        },
    })
    print(json.dumps({"qualification": "PASS" if not failures else "FAIL",
                      "runs": len(records), "selected": selected_name,
                      "biological_population": selected["biological_population"],
                      "synthetic_population": selected["synthetic_population"]}, sort_keys=True))
    if failures or len(records) != 9:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
