"""Read frozen sources and build the candidate Earth coverage and tail audit.

No network and no economic simulation. Output is experiment-local, never the
governed current pointer. Run from this directory with Python 3.12.
"""
import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

from successor import demographic_tail, wpp_identity

HERE = Path(__file__).resolve().parent
V3_MANIFEST = HERE.parent / "earth_long_run_economic_baseline_v3_repaired_2026_09_23" / "RUN_MANIFEST.json"
MACRO_ENVELOPE = Path("/home/ubuntu/LOOM_Earth2026/Earth2026_country_macro_envelope_WEO2026_v0.1.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value, compact=False):
    path.write_text(json.dumps(value, sort_keys=True, indent=None if compact else 2,
                               separators=(",", ":") if compact else None,
                               ensure_ascii=False, allow_nan=False) + "\n")


def wpp_rows(path):
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def load_wpp(manifest):
    total = Path(manifest["sources"]["wpp_total"]["path"])
    age = Path(manifest["sources"]["wpp_age"]["path"])
    for name, path in (("wpp_total", total), ("wpp_age", age)):
        if sha(path) != manifest["sources"][name]["sha256"]:
            raise ValueError(f"source hash mismatch: {name}")
    identity, world = wpp_identity(wpp_rows(total))
    isos = set(identity)
    years = set(range(2091, 2101)) | {2026}
    pop = {year: {} for year in years}
    for row in wpp_rows(total):
        if row["Variant"] == "Medium" and row["ISO3_code"] in isos:
            year = int(row["Time"])
            if year in years:
                pop[year][row["ISO3_code"]] = float(row["TPopulation1Jan"]) * 1000
    pct = {year: {} for year in years}
    for row in wpp_rows(age):
        if row["Variant"] == "Medium" and row["ISO3_code"] in isos:
            year = int(row["Time"])
            if year in years and 15 <= int(row["AgeGrpStart"]) <= 60:
                iso = row["ISO3_code"]
                pct[year][iso] = pct[year].get(iso, 0) + float(row["PopTotal"])
    share = {year: {iso: v / 100 for iso, v in values.items()} for year, values in pct.items()}
    for year in sorted(years):
        if set(pop[year]) != isos or set(share[year]) != isos:
            raise ValueError(f"incomplete WPP population/age coverage {year}")
        if any(not 0 < value < 1 for value in share[year].values()):
            raise ValueError(f"invalid WPP age share {year}")
    return identity, world, pop, share


def load_v3_ids(manifest):
    source = manifest["sources"]["seed_2026_countries"]
    path = Path(source["path"])
    if sha(path) != source["sha256"]:
        raise ValueError("v3 2026 seed hash mismatch")
    rows = [json.loads(line) for line in path.open() if line.strip()]
    result = {row["iso3"] for row in rows if row["year"] == 2026}
    if sum(row["year"] == 2026 for row in rows) != len(result):
        raise ValueError("duplicate v3 2026 economy")
    return result


def pwt_raw_presence(path):
    """Raw field inventory only; presence does not qualify model calibration."""
    v3_code = HERE.parent / "earth_long_run_economic_baseline_v3_repaired_2026_09_23"
    sys.path.insert(0, str(v3_code))
    spec = importlib.util.spec_from_file_location("v3_pwt_reader", v3_code / "runner.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.read_xlsx_rows(path, "Data")
    header = next(data)
    index = {name: n for n, name in enumerate(header)}
    columns = ("ctfp", "rtfpna", "ck", "labsh", "emp", "avh", "hc")
    present = {}
    for row in data:
        if len(row) <= max(index["year"], index["countrycode"]):
            continue
        iso = row[index["countrycode"]]
        try:
            year = int(float(row[index["year"]]))
        except (ValueError, TypeError):
            continue
        if not iso or year < 2019 or year > 2023:
            continue
        rec = present.setdefault(iso, {name: False for name in columns})
        for name in columns:
            if index[name] < len(row):
                try:
                    value = float(row[index[name]])
                    rec[name] |= math.isfinite(value)
                except (ValueError, TypeError):
                    pass
    return present


def coverage(identity, model_ids, macro_rows, pwt_presence):
    by_iso = {row["iso3"]: row for row in macro_rows}
    evidence = []
    for iso, info in identity.items():
        m = by_iso.get(iso, {})
        modeled = iso in model_ids
        macro = m.get("real_gdp_constant_2015_usd")
        labor = m.get("employment_total")
        row = {
            **info,
            "v3_economic_model": modeled,
            "raw_source_availability": {"pwt11_2019_2023_fields_present": pwt_presence.get(iso),
                                        "ilostat_employment_envelope_present": labor is not None,
                                        "oecd_ten_sector_model_registered": modeled,
                                        "note": "Raw presence is not model qualification"},
            "identity_geography": {"class": "DIRECT", "source": "UN_WPP_2024_MEDIUM", "method_id": None},
            "demography": {"class": "DIRECT", "source": "UN_WPP_2024_MEDIUM", "method_id": "WPP_JAN1_AND_15_64"},
            "labor": {"class": "DERIVED_FROM_QUALIFIED_METHOD" if modeled else "UNAVAILABLE",
                      "source": "V3_2026_MODEL_SEED" if modeled else "ILOSTAT_EMPLOYMENT_ENVELOPE_ONLY" if labor is not None else None,
                      "method_id": "V3_2026_LABOR_BRIDGE" if modeled else None,
                      "employment_envelope_present": labor is not None,
                      "employment_source_year": m.get("employment_source_year"),
                      "reason": None if modeled else "Working-age/labor-force/employment model state not jointly qualified"},
            "macroeconomic_envelope": {"class": "DERIVED_FROM_QUALIFIED_METHOD" if macro is not None else "UNAVAILABLE",
                                       "source": "WDI_CONSTANT_2015_USD_PLUS_IMF_WEO" if macro is not None else None,
                                       "method_id": m.get("real_gdp_bridge_method") if macro is not None else None,
                                       "gdp_2026_constant_2015_usd": macro,
                                       "reason": None if macro is not None else m.get("real_gdp_bridge_method") or "No qualified 2026 GDP"},
        }
        for layer, source_name, method in (
            ("productivity_tfp", "V3_PWT11_TFP", "V3_PWT_TFP_CALIBRATION"),
            ("factor_shares", "V3_PWT11_FACTOR", "V3_FACTOR_SHARE_CLOSURE"),
            ("investment_capital", "V3_PWT11_WDI_ASSET_BRIDGE", "V3_FOUR_ASSET_RECONSTRUCTION"),
            ("sector_decomposition", "OECD_ICIO_2024_TEN_SECTOR", "V3_OECD_SECTOR_REDUCER"),
            ("asset_decomposition", "PWT11_FOUR_ASSET", "V3_FOUR_ASSET_RECONSTRUCTION"),
            ("trade_network_topology", "OECD_ICIO_2024", "V3_OECD_BILATERAL_TOPOLOGY"),
        ):
            row[layer] = {"class": "DERIVED_FROM_QUALIFIED_METHOD" if modeled else "UNAVAILABLE",
                          "source": source_name if modeled else None,
                          "method_id": method if modeled else None,
                          "reason": None if modeled else "No qualified economy-specific full-model input"}
        evidence.append(row)
    return evidence


def summarize_coverage(evidence, world):
    layers = ("identity_geography", "demography", "labor", "macroeconomic_envelope", "productivity_tfp",
              "factor_shares", "investment_capital", "sector_decomposition", "asset_decomposition", "trade_network_topology")
    out = {}
    for layer in layers:
        counts, population = {}, {}
        for row in evidence:
            kind = row[layer]["class"]
            counts[kind] = counts.get(kind, 0) + 1
            population[kind] = population.get(kind, 0) + row["population_2026"]
        out[layer] = {"economies_by_class": counts, "population_by_class": population}
    model_pop = sum(row["population_2026"] for row in evidence if row["v3_economic_model"])
    macro_rows = [row for row in evidence if row["macroeconomic_envelope"]["gdp_2026_constant_2015_usd"] is not None]
    macro_total = sum(row["macroeconomic_envelope"]["gdp_2026_constant_2015_usd"] for row in macro_rows)
    macro_model = sum(row["macroeconomic_envelope"]["gdp_2026_constant_2015_usd"] for row in macro_rows if row["v3_economic_model"])
    return {"target_economies": len(evidence), "v3_modeled_economies": sum(r["v3_economic_model"] for r in evidence),
            "wpp_world_population_2026_jan1": world, "v3_modeled_population_2026_jan1": model_pop,
            "v3_population_coverage": model_pop / world, "excluded_population_from_v3": world-model_pop,
            "layers": out,
            "macro_2026_coverage": {"method": "WDI_2015_USD_LEVEL_PLUS_IMF_WEO_2026_GROWTH_AVAILABLE_SOURCE_DENOMINATOR",
                                    "source_economies": len(macro_rows), "source_denominator": macro_total,
                                    "v3_80_numerator_on_same_source_basis": macro_model,
                                    "v3_share_of_available_source_denominator": macro_model/macro_total,
                                    "limitation": "Available-source denominator is not a complete world GDP observation"}}


def demographic_sensitivity(pop, share, model_ids, parameters):
    scenarios = {}
    central_rank = None
    for name, p in parameters["demographic_scenarios"].items():
        pp, ss = demographic_tail(pop, share, p["population_growth_half_life_years"],
                                  p["working_age_share_delta_half_life_years"], 2226)
        final = pp[2226]
        ranked = sorted(final, key=lambda iso: (-final[iso], iso))
        if name == "CENTRAL":
            central_rank = {iso: n for n, iso in enumerate(ranked, 1)}
        scenarios[name] = {"global_population_2100": sum(pp[2100].values()),
                           "global_population_2226": sum(final.values()),
                           "v3_80_population_2226": sum(final[iso] for iso in model_ids),
                           "top_20_population_2226": [{"iso3": iso, "population": final[iso]} for iso in ranked[:20]],
                           "country_population_2226": final,
                           "country_working_age_share_2226": ss[2226],
                           "country_population_change_2100_2226": {iso: final[iso]/pp[2100][iso]-1 for iso in sorted(final)}}
    for name, data in scenarios.items():
        rank = {iso: n for n, iso in enumerate(sorted(data["country_population_2226"],
                                                     key=lambda iso: (-data["country_population_2226"][iso], iso)), 1)}
        data["rank_change_vs_central"] = {iso: rank[iso] - central_rank[iso] for iso in sorted(rank)}
    return scenarios


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=HERE)
    args = parser.parse_args()
    manifest = json.loads(V3_MANIFEST.read_text())
    params = json.loads((HERE / "parameters.json").read_text())
    identity, world, pop, share = load_wpp(manifest)
    model_ids = load_v3_ids(manifest)
    if not model_ids <= set(identity):
        raise ValueError("v3 economy absent from WPP identity universe")
    macro = json.loads(MACRO_ENVELOPE.read_text())
    macro_rows = macro["countries"]
    if len({r["iso3"] for r in macro_rows}) != len(macro_rows):
        raise ValueError("duplicate macro envelope identity")
    pwt_source = manifest["sources"]["pwt_11"]
    if sha(pwt_source["path"]) != pwt_source["sha256"]:
        raise ValueError("PWT 11 source hash mismatch")
    pwt_presence = pwt_raw_presence(Path(pwt_source["path"]))
    evidence = coverage(identity, model_ids, macro_rows, pwt_presence)
    out = args.output_root
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "COUNTRY_EVIDENCE.json", {"schema": "loom-earth-v4-country-evidence-v1", "economies": evidence}, compact=True)
    write_json(out / "COVERAGE_REPORT.json", {"schema": "loom-earth-v4-coverage-v1", **summarize_coverage(evidence, world)})
    write_json(out / "DEMOGRAPHIC_SENSITIVITY.json", {"schema": "loom-earth-v4-demographic-sensitivity-v1",
                                                     "status": "SCENARIOS_NOT_SELECTED_CENTRAL_UNCHANGED",
                                                     "parameters_sha256": sha(HERE / "parameters.json"),
                                                     "scenarios": demographic_sensitivity(pop, share, model_ids, params)}, compact=True)
    write_json(out / "SOURCE_PROVENANCE.json", {"schema": "loom-earth-v4-source-provenance-v1",
                                                "v3_run_manifest_sha256": sha(V3_MANIFEST),
                                                "wpp_total_sha256": sha(manifest["sources"]["wpp_total"]["path"]),
                                                "wpp_age_sha256": sha(manifest["sources"]["wpp_age"]["path"]),
                                                "pwt_11_sha256": sha(pwt_source["path"]),
                                                "v3_seed_2026_countries_sha256": sha(manifest["sources"]["seed_2026_countries"]["path"]),
                                                "macro_envelope_path": str(MACRO_ENVELOPE),
                                                "macro_envelope_sha256": sha(MACRO_ENVELOPE)})
    print(f"WPP Country/Area identities: {len(identity)}; v3 economic IDs: {len(model_ids)}; Jan-1 coverage: {sum(identity[i]['population_2026'] for i in model_ids)/world:.6%}")


if __name__ == "__main__":
    main()
