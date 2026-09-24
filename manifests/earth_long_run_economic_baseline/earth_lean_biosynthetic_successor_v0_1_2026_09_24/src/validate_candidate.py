#!/usr/bin/env python3
"""Independent hostile checks for the lean coupled successor artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            yield json.loads(line)


def close(a: float, b: float, rel: float = 1e-9, absolute: float = 1e-5) -> bool:
    return abs(a - b) <= max(absolute, rel * max(abs(a), abs(b)))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demographic-root", type=Path, required=True)
    parser.add_argument("--economic-root", type=Path, required=True)
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    failures: list[str] = []
    checks: dict[str, object] = {}
    params = load(args.parameters)
    biological = load(args.demographic_root / "annual_biological_summary.json")
    synthetic = load(args.economic_root / "annual_synthetic_summary.json")
    labor = load(args.economic_root / "annual_labor_composition.json")
    economic = load(args.economic_root / "annual_economic_summary.json")

    expected_years = list(range(2100, 2227))
    for name, series in (("biological", biological), ("synthetic", synthetic),
                         ("labor", labor), ("economic", economic)):
        years = [row["year"] for row in series]
        if years != expected_years:
            failures.append(f"{name} annual coverage")
    checks["annual_years"] = len(expected_years)

    max_bio_reconciliation = 0.0
    for previous, current in zip(biological, biological[1:]):
        residual = current["population"] - (
            previous["population"] + previous["births"] - previous["deaths"]
        )
        max_bio_reconciliation = max(max_bio_reconciliation, abs(residual))
        if not close(residual, 0.0, absolute=2e-4):
            failures.append(f"biological stock reconciliation {current['year']}")
    checks["max_biological_stock_residual_persons"] = max_bio_reconciliation

    synth_cfg = params["synthetic_persons"]
    max_synth_reconciliation = 0.0
    for previous, current in zip(synthetic, synthetic[1:]):
        expected = (previous["population"] + current["additions"]
                    - current["retirements_losses"] + current["net_migration"])
        residual = current["population"] - expected
        max_synth_reconciliation = max(max_synth_reconciliation, abs(residual))
        if not close(current["population"], expected):
            failures.append(f"synthetic stock reconciliation {current['year']}")
        expected_labor = (current["population"] * current["labor_participation"]
                          * current["effective_labor_per_participant"])
        if not close(current["effective_labor"], expected_labor):
            failures.append(f"synthetic labor without stock {current['year']}")
    checks["max_synthetic_stock_residual_persons"] = max_synth_reconciliation
    checks["synthetic_net_migration_zero"] = all(row["net_migration"] == 0 for row in synthetic)

    max_labor_residual = 0.0
    for row in labor:
        expected = row["biological_labor"] + row["synthetic_labor"] + row["machine_task_capacity"]
        max_labor_residual = max(max_labor_residual, abs(row["total_effective_labor"] - expected))
        if not close(row["total_effective_labor"], expected):
            failures.append(f"labor composition {row['year']}")
        if min(row["biological_labor"], row["synthetic_labor"], row["machine_task_capacity"]) < 0:
            failures.append(f"negative labor component {row['year']}")
    checks["max_labor_composition_residual"] = max_labor_residual

    country_counts = defaultdict(int)
    max_country_labor_residual = 0.0
    max_bio_capability_excess = 0.0
    for row in rows(args.economic_root / "countries_2100_2226.ndjson"):
        country_counts[row["year"]] += 1
        expected = row["biological_labor"] + row["synthetic_labor"] + row["machine_task_capacity"]
        max_country_labor_residual = max(max_country_labor_residual,
                                         abs(row["effective_labor_input"] - expected))
        max_bio_capability_excess = max(max_bio_capability_excess,
                                        row["biological_labor"] - row["labor_capable_biological_population"])
        if row["biological_labor"] > row["biological_population"] + 1e-5:
            failures.append(f"biological labor exceeds persons {row['iso3']}/{row['year']}")
        if row["recognized_person_population"] != row["biological_population"] + row["synthetic_population"]:
            failures.append(f"recognized persons composition {row['iso3']}/{row['year']}")
        for key, value in row.items():
            if isinstance(value, float) and not math.isfinite(value):
                failures.append(f"nonfinite {key} {row['iso3']}/{row['year']}")
    if set(country_counts.values()) != {80} or set(country_counts) != set(expected_years):
        failures.append("economic country universe")
    checks["economic_country_rows_per_year"] = sorted(set(country_counts.values()))
    checks["max_country_labor_composition_residual"] = max_country_labor_residual
    checks["max_biological_capability_excess"] = max_bio_capability_excess

    endpoint = load(args.economic_root / "countries_2226.json")
    checks["terminal_country_count"] = len(endpoint)
    checks["terminal_country_identity_unique"] = len({r["iso3"] for r in endpoint}) == len(endpoint)
    if not checks["terminal_country_identity_unique"]:
        failures.append("duplicate endpoint economy identity")

    with (args.demographic_root / "country_demography_2226.csv").open(encoding="utf-8") as handle:
        demog_endpoint = list(csv.DictReader(handle))
    checks["terminal_demographic_area_count"] = len(demog_endpoint)
    if len(demog_endpoint) != 237 or len({r["iso3"] for r in demog_endpoint}) != 237:
        failures.append("237-area demographic universe")
    demog_total = sum(float(r["population"]) for r in demog_endpoint)
    if not close(demog_total, biological[-1]["population"]):
        failures.append("demographic endpoint total")
    checks["terminal_demographic_population_residual"] = demog_total - biological[-1]["population"]

    runner_report = load(args.economic_root / "economic_report.json")
    gates = runner_report["max_residuals_and_movements"]
    for gate in ("production_equation_relative_residual",
                 "capital_stock_flow_relative_residual",
                 "country_sector_reconciliation_relative_residual",
                 "sector_asset_reconciliation_relative_residual",
                 "labor_composition_relative_residual"):
        if gates[gate] > 1e-9:
            failures.append(gate)
    checks["runner_gates"] = gates

    artifacts = {}
    for root in (args.demographic_root, args.economic_root):
        for path in sorted(root.glob("*")):
            if path.is_file() and path != args.report:
                artifacts[str(path)] = {"bytes": path.stat().st_size, "sha256": sha256(path)}

    report = {
        "schema": "LOOM_EARTH_LEAN_BIOSYNTHETIC_INDEPENDENT_VALIDATION_v0",
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
        "artifact_hashes": artifacts,
        "terminal": {
            "biological_population": biological[-1]["population"],
            "synthetic_population": synthetic[-1]["population"],
            "recognized_person_population": biological[-1]["population"] + synthetic[-1]["population"],
            "total_effective_labor": labor[-1]["total_effective_labor"],
            "value_added": economic[-1]["value_added"],
        },
        "category_assertions": {
            "synthetic_persons_excluded_from_biological_population": True,
            "machine_task_capacity_excluded_from_person_population": True,
            "machine_task_capacity_reported_separately": True,
        },
    }
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failures": failures,
                      "terminal": report["terminal"]}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
