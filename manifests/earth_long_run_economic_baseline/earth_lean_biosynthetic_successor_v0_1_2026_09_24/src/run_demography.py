#!/usr/bin/env python3
"""Build the 2100-2226 biological cohort and biological-labor candidate."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from pathlib import Path

from model import (
    interpolate_records,
    labor_from_cohorts,
    medicine_access,
    medicine_mortality_multiplier,
    propagate_one_year,
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_ndjson(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def load_wpp(total_path: Path, age_path: Path):
    totals = {}
    names = {}
    life = {}
    vital_2100 = {}
    world_total = {}
    world_life = {}
    with gzip.open(total_path, "rt", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["Variant"] != "Medium" or row["Time"] not in {"2095", "2100"}:
                continue
            year = int(row["Time"])
            if row["LocTypeName"] == "World" and row["Location"] == "World":
                world_total[year] = float(row["TPopulation1Jan"]) * 1000.0
                if year == 2100:
                    world_life = {"M": float(row["LExMale"]), "F": float(row["LExFemale"])}
            if row["LocTypeName"] != "Country/Area" or year != 2100:
                continue
            iso = row["ISO3_code"].strip()
            totals[iso] = float(row["TPopulation1Jan"]) * 1000.0
            names[iso] = row["Location"]
            life[iso] = {"M": float(row["LExMale"]), "F": float(row["LExFemale"])}
            vital_2100[iso] = {
                "births": float(row["Births"]) * 1000.0,
                "deaths": float(row["Deaths"]) * 1000.0,
            }

    country_pct = {}
    world_pct = {2095: {}, 2100: {}}
    with gzip.open(age_path, "rt", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["Variant"] != "Medium" or row["Time"] not in {"2095", "2100"}:
                continue
            year = int(row["Time"])
            age = int(row["AgeGrpStart"])
            if row["Location"] == "World":
                world_pct[year][age] = {"M": float(row["PopMale"]), "F": float(row["PopFemale"])}
            elif year == 2100 and row["LocTypeName"] == "Country/Area":
                iso = row["ISO3_code"].strip()
                country_pct.setdefault(iso, {})[age] = {
                    "M": float(row["PopMale"]), "F": float(row["PopFemale"])
                }
    if len(totals) != 237 or set(country_pct) != set(totals):
        raise ValueError(f"WPP Country/Area coverage mismatch: totals={len(totals)} ages={len(country_pct)}")
    if set(world_total) != {2095, 2100} or not world_life:
        raise ValueError("WPP world mortality anchors missing")
    return totals, names, life, vital_2100, world_total, world_life, country_pct, world_pct


def initial_cohorts(total: float, percentages: dict[int, dict[str, float]], age_starts) -> dict:
    """Normalize rounded WPP percentages to the Jan-1 country total.

    WPP publishes 100+ as one open group. The bounded model places that mass in
    100-104 at the boundary and leaves older five-year groups empty.
    """
    cohorts = {sex: {age: 0.0 for age in age_starts} for sex in ("M", "F")}
    source_sum = sum(values[sex] for values in percentages.values() for sex in ("M", "F"))
    if source_sum <= 0:
        raise ValueError("empty WPP age-sex distribution")
    for age, values in percentages.items():
        target_age = 100 if age >= 100 else age
        for sex in ("M", "F"):
            cohorts[sex][target_age] += total * values[sex] / source_sum
    return cohorts


def world_baseline_mortality(world_total, world_pct, age_starts, parameters):
    mortality = {sex: {} for sex in ("M", "F")}
    for sex in ("M", "F"):
        for age in age_starts:
            if age <= 90:
                start = world_total[2095] * world_pct[2095][age][sex] / 100.0
                end = world_total[2100] * world_pct[2100][age + 5][sex] / 100.0
                survival5 = min(0.99995, max(0.001, end / start))
                mortality[sex][age] = 1.0 - survival5 ** 0.2
            elif age < age_starts[-1]:
                steps = (age - 90) / 5.0
                mortality[sex][age] = min(0.75, mortality[sex][90] * (1.55 ** steps))
            else:
                mortality[sex][age] = float(parameters["mortality"]["terminal_age_annual_probability"])
    return mortality


def country_mortality(iso, year, baseline, life, world_life, parameters, calibration=1.0):
    settings = parameters["mortality"]
    result = {sex: {} for sex in ("M", "F")}
    for sex in ("M", "F"):
        country_scale = math.exp(
            -float(settings["country_life_expectancy_elasticity"])
            * (life[iso][sex] - world_life[sex])
        )
        for age, base_q in baseline[sex].items():
            q = (base_q * country_scale * calibration
                 * medicine_mortality_multiplier(age, year, parameters))
            result[sex][age] = min(
                float(settings["annual_probability_ceiling"]),
                max(float(settings["annual_probability_floor"]), q),
            )
    return result


def calibrate_mortality(cohorts, iso, target_deaths, baseline, life, world_life, parameters):
    """Calibrate mortality level to the WPP 2100 country death total."""
    low, high = 0.0, 10.0
    for _ in range(80):
        middle = (low + high) / 2.0
        q = country_mortality(iso, 2100, baseline, life, world_life, parameters, middle)
        deaths = sum(cohorts[sex][age] * q[sex][age]
                     for sex in ("M", "F") for age in cohorts[sex])
        if deaths < target_deaths:
            low = middle
        else:
            high = middle
    scale = (low + high) / 2.0
    q = country_mortality(iso, 2100, baseline, life, world_life, parameters, scale)
    deaths = sum(cohorts[sex][age] * q[sex][age]
                 for sex in ("M", "F") for age in cohorts[sex])
    if not math.isclose(deaths, target_deaths, rel_tol=1e-10, abs_tol=1e-3):
        raise ValueError(f"WPP mortality boundary calibration failed {iso}")
    return scale


def cohort_metrics(cohorts):
    ages = sorted(cohorts["M"])
    by_age = {age: cohorts["M"][age] + cohorts["F"][age] for age in ages}
    population = sum(by_age.values())

    def share_at(minimum=0, maximum=None):
        value = sum(pop for age, pop in by_age.items()
                    if age >= minimum and (maximum is None or age <= maximum))
        return value, value / population

    cumulative = 0.0
    median = ages[-1] + 2.5
    for age in ages:
        if cumulative + by_age[age] >= population / 2.0:
            within = (population / 2.0 - cumulative) / max(by_age[age], 1e-30)
            median = age + min(5.0, max(0.0, 5.0 * within))
            break
        cumulative += by_age[age]
    fields = {
        "population": population,
        "median_age_approx": median,
    }
    for name, minimum, maximum in (
        ("under_20", 0, 15), ("age_20_64", 20, 60), ("age_65_plus", 65, None),
        ("age_80_plus", 80, None), ("age_100_plus", 100, None),
        ("age_120_plus", 120, None), ("age_150_plus", 150, None),
    ):
        value, share = share_at(minimum, maximum)
        fields[name] = value
        fields[f"{name}_share"] = share
    return fields


def load_v4_boundary(v4_root: Path, economic_isos: set[str]):
    scope = read_json(v4_root / "PROMOTION_SCOPE.json")
    registered = set(scope["economic_qualification"]["iso3"])
    if registered != economic_isos:
        raise ValueError("v4 economic roster mismatch")
    rows = {}
    path = v4_root / "successor_80_2226/results/countries_2060_2226.ndjson"
    for row in read_ndjson(path):
        if row["year"] == 2100:
            rows[row["iso3"]] = row
    if set(rows) != economic_isos:
        raise ValueError("v4 2100 boundary coverage mismatch")
    return rows


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def run(parameters: dict, total_path: Path, age_path: Path, v4_root: Path, output_root: Path):
    output_root.mkdir(parents=True, exist_ok=True)
    totals, names, life, vital, world_total, world_life, percentages, world_pct = load_wpp(total_path, age_path)
    age_starts = tuple(parameters["age_groups"]["starts"])
    cohorts = {iso: initial_cohorts(totals[iso], percentages[iso], age_starts) for iso in sorted(totals)}
    boundary_total = sum(cohort_metrics(value)["population"] for value in cohorts.values())
    if not math.isclose(boundary_total, world_total[2100], rel_tol=2e-6):
        raise ValueError(f"country totals do not reconcile to WPP world: {boundary_total} vs {world_total[2100]}")

    economic_isos = set(read_json(v4_root / "PROMOTION_SCOPE.json")["economic_qualification"]["iso3"])
    v4_boundary = load_v4_boundary(v4_root, economic_isos)
    labor_calibration = {}
    labor_boundary_repairs = []
    for iso in sorted(economic_isos):
        raw = labor_from_cohorts(cohorts[iso], 2100, parameters, 1.0)
        legacy_employment = v4_boundary[iso]["employment"]
        selected_labor = min(legacy_employment, raw["labor_capable_population"])
        calibration = selected_labor / raw["effective_biological_labor"]
        if not 0 < calibration:
            raise ValueError(f"invalid 2100 biological labor calibration {iso}: {calibration}")
        labor_from_cohorts(cohorts[iso], 2100, parameters, calibration)
        labor_calibration[iso] = calibration
        if selected_labor < legacy_employment:
            labor_boundary_repairs.append({
                "iso3": iso,
                "legacy_v4_employment_2100": legacy_employment,
                "health_capable_biological_population_2100": raw["labor_capable_population"],
                "selected_biological_labor_2100": selected_labor,
                "method": "CAP_AT_HEALTH_CAPABLE_BIOLOGICAL_POPULATION_AND_REBASE_PRODUCTION_A",
            })

    baseline_q = world_baseline_mortality(world_total, world_pct, age_starts, parameters)
    mortality_calibration = {
        iso: calibrate_mortality(cohorts[iso], iso, vital[iso]["deaths"], baseline_q,
                                 life, world_life, parameters)
        for iso in sorted(cohorts)
    }
    fertility = parameters["fertility"]
    annual_summary = []
    country_endpoint = []
    country_path = output_root / "biological_country_2100_2226.ndjson"
    cohort_path = output_root / "biological_cohorts_2100_2226.ndjson"
    labor_path = output_root / "biological_labor_80_2100_2226.ndjson"
    with country_path.open("w", encoding="utf-8") as country_file, \
            cohort_path.open("w", encoding="utf-8") as cohort_file, \
            labor_path.open("w", encoding="utf-8") as labor_file:
        for year in range(parameters["years"]["start"], parameters["years"]["end"] + 1):
            tfr = interpolate_records(fertility["anchors"], year, "tfr")
            mean_age = interpolate_records(fertility["anchors"], year, "mean_age")
            sd_age = interpolate_records(fertility["anchors"], year, "sd_age")
            global_totals = {key: 0.0 for key in (
                "population", "births", "deaths", "under_20", "age_20_64", "age_65_plus",
                "age_80_plus", "age_100_plus", "age_120_plus", "age_150_plus")}
            median_weight = 0.0
            year_next = {}
            for iso in sorted(cohorts):
                current = cohorts[iso]
                metrics = cohort_metrics(current)
                mortality = country_mortality(
                    iso, year, baseline_q, life, world_life, parameters,
                    mortality_calibration[iso])
                advanced = propagate_one_year(current, mortality, tfr, mean_age, sd_age,
                                              fertility["male_birth_share"])
                births, deaths = advanced["births"], advanced["deaths"]
                row = {"iso3": iso, "name": names[iso], "year": year, **metrics,
                       "births": births, "deaths": deaths,
                       "natural_change": births - deaths,
                       "tfr": tfr, "mean_childbearing_age": mean_age, "fertility_sd": sd_age,
                       "migration": 0.0, "source": "WPP_2100_BOUNDARY" if year == 2100 else "LEAN_COHORT_SUCCESSOR"}
                if year == 2100:
                    row["wpp_reported_births_2100"] = vital[iso]["births"]
                    row["wpp_reported_deaths_2100"] = vital[iso]["deaths"]
                if year == parameters["years"]["end"]:
                    country_endpoint.append(row)
                country_file.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
                cohort_file.write(json.dumps({"iso3": iso, "year": year, "cohorts": current}, sort_keys=True, allow_nan=False) + "\n")
                if iso in economic_isos:
                    labor = labor_from_cohorts(current, year, parameters, labor_calibration[iso])
                    labor_file.write(json.dumps({"iso3": iso, "year": year, **labor,
                                                 "population": metrics["population"],
                                                 "age_20_64": metrics["age_20_64"]},
                                                sort_keys=True, allow_nan=False) + "\n")
                for key in global_totals:
                    if key in metrics:
                        global_totals[key] += metrics[key]
                median_weight += metrics["median_age_approx"] * metrics["population"]
                global_totals["births"] += births
                global_totals["deaths"] += deaths
                if year < parameters["years"]["end"]:
                    year_next[iso] = advanced["cohorts"]
            population = global_totals["population"]
            summary = {
                "year": year, **global_totals,
                "natural_change": global_totals["births"] - global_totals["deaths"],
                "median_age_approx_country_weighted": median_weight / population,
                "tfr": tfr, "mean_childbearing_age": mean_age, "fertility_sd": sd_age,
                "medicine_access": medicine_access(year, parameters),
            }
            for key in ("under_20", "age_20_64", "age_65_plus", "age_80_plus",
                        "age_100_plus", "age_120_plus", "age_150_plus"):
                summary[f"{key}_share"] = summary[key] / population
            annual_summary.append(summary)
            if year < parameters["years"]["end"]:
                cohorts = year_next

    write_json(output_root / "annual_biological_summary.json", annual_summary)
    write_json(output_root / "labor_calibration_2100.json", labor_calibration)
    write_json(output_root / "mortality_calibration_2100.json", mortality_calibration)
    write_json(output_root / "labor_boundary_repairs_2100.json", labor_boundary_repairs)
    with (output_root / "country_demography_2226.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["iso3", "name", "population", "median_age_approx", "under_20_share",
                  "age_20_64_share", "age_65_plus_share", "age_80_plus_share", "age_100_plus_share",
                  "age_120_plus_share", "age_150_plus_share"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(country_endpoint, key=lambda row: row["iso3"]))
    report = {
        "status": "DEMOGRAPHY_AND_BIOLOGICAL_LABOR_COMPLETE",
        "country_area_count": len(totals),
        "economic_labor_country_count": len(economic_isos),
        "labor_boundary_repair_count": len(labor_boundary_repairs),
        "labor_boundary_repairs": labor_boundary_repairs,
        "boundary_population_2100": annual_summary[0]["population"],
        "terminal_population_2226": annual_summary[-1]["population"],
        "terminal": annual_summary[-1],
        "age_source_open_100_plus_treatment": "ALL_WPP_100_PLUS_MASS_ASSIGNED_TO_100_104_AT_2100_BOUNDARY",
        "migration": "ZERO_AFTER_2100",
        "files": {
            "annual_summary": str(output_root / "annual_biological_summary.json"),
            "country_path": str(country_path),
            "cohort_path": str(cohort_path),
            "labor_path": str(labor_path),
            "country_endpoint": str(output_root / "country_demography_2226.csv"),
        },
    }
    write_json(output_root / "demography_report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--wpp-total", type=Path, required=True)
    parser.add_argument("--wpp-age", type=Path, required=True)
    parser.add_argument("--v4-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    report = run(read_json(args.parameters), args.wpp_total, args.wpp_age, args.v4_root, args.output_root)
    print(json.dumps({"status": report["status"], "countries": report["country_area_count"],
                      "population_2226": report["terminal_population_2226"]}, sort_keys=True))


if __name__ == "__main__":
    main()
