"""Descriptive and controlled A/B audit; all monetary values are model proxies."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
V3_LOCAL = Path("/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v3_repaired_2026_09_23")
V3_PRE = Path("/home/ubuntu/loom_earth_2026_2035/earth_repair_successor_2026_09_22")


def read(path, year=None):
    with Path(path).open() as handle:
        return [r for r in (json.loads(line) for line in handle) if year is None or r["year"] == year]


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def quantiles(values):
    values = sorted(values)
    if not values:
        return None
    def percentile(p):
        pos = (len(values)-1) * p
        lo, hi = math.floor(pos), math.ceil(pos)
        return values[lo] + (pos-lo) * (values[hi]-values[lo])
    return {"min": values[0], "p05": percentile(.05), "p25": percentile(.25),
            "median": percentile(.5), "p75": percentile(.75), "p95": percentile(.95),
            "max": values[-1], "mean": statistics.fmean(values)}


def ranks(rows, field):
    ordered = sorted(rows, key=lambda r: (-r[field], r["iso3"]))
    return {r["iso3"]: n for n, r in enumerate(ordered, 1)}


def concentration(rows, field):
    values = sorted((r[field] for r in rows), reverse=True)
    total = math.fsum(values)
    shares = [v/total for v in values]
    hhi = math.fsum(s*s for s in shares)
    n = len(values)
    ascending = list(reversed(values))
    gini = sum((2*i-n-1)*v for i, v in enumerate(ascending, 1)) / (n*total)
    return {"top_1_share": sum(shares[:1]), "top_5_share": sum(shares[:5]),
            "top_10_share": sum(shares[:10]), "top_20_share": sum(shares[:20]),
            "hhi": hhi, "effective_economies": 1/hhi, "gini_economy_totals": gini}


def aggregate(rows):
    fields = ("population", "demographic_working_age_population", "labor_force", "employment",
              "value_added", "capital", "investment")
    total = {field: math.fsum(r[field] for r in rows) for field in fields}
    total["capital_per_va"] = total["capital"] / total["value_added"]
    total["investment_per_va"] = total["investment"] / total["value_added"]
    total["va_per_capita_proxy"] = total["value_added"] / total["population"]
    return total


def metrics(row):
    return {"population": row["population"], "value_added": row["value_added"],
            "va_per_capita_proxy": row["value_added"] / row["population"],
            "capital_per_va": row["capital"] / row["value_added"],
            "investment_per_va": row["investment"] / row["value_added"],
            "working_age_share": row["demographic_working_age_population"] / row["population"],
            "labor_force_participation": row["labor_force"] / row["labor_market_working_age_population"],
            "employment_per_labor_force": row["employment"] / row["labor_force"],
            "real_va_growth": row["real_value_added_growth"],
            "tfp_growth": row["country_tfp_growth"], "tfp_multiplier": row["country_tfp_multiplier"]}


def describe(rows, initial):
    by_iso = {r["iso3"]: r for r in rows}
    initial_by_iso = {r["iso3"]: r for r in initial}
    if set(by_iso) != set(initial_by_iso):
        raise ValueError("rank baseline economy universe differs")
    m = {iso: metrics(row) for iso, row in by_iso.items()}
    fields = list(next(iter(m.values())))
    r0_pop, r1_pop = ranks(initial, "population"), ranks(rows, "population")
    r0_va, r1_va = ranks(initial, "value_added"), ranks(rows, "value_added")
    n = len(rows)
    def spearman(a, b):
        return 1 - 6*sum((a[i]-b[i])**2 for i in a) / (n*(n*n-1))
    change_pop = {iso: r0_pop[iso]-r1_pop[iso] for iso in by_iso}
    change_va = {iso: r0_va[iso]-r1_va[iso] for iso in by_iso}
    cagr = {iso: {field: (m[iso][field] / (initial_by_iso[iso]["value_added"] / initial_by_iso[iso]["population"]
                                 if field == "va_per_capita_proxy" else initial_by_iso[iso][field])) ** (1/200)-1
                  for field in ("population", "value_added", "va_per_capita_proxy")}
            for iso in by_iso}
    distributions = {field: quantiles([m[iso][field] for iso in m]) for field in fields}
    outliers = {field: {"highest": sorted(({"iso3": iso, "value": m[iso][field]} for iso in m),
                                            key=lambda r: (-r["value"], r["iso3"]))[:10],
                        "lowest": sorted(({"iso3": iso, "value": m[iso][field]} for iso in m),
                                           key=lambda r: (r["value"], r["iso3"]))[:10]}
                for field in fields}
    return {"country_distributions_2226": distributions,
            "concentration_2026": {f: concentration(initial, f) for f in ("population", "value_added")},
            "concentration_2226": {f: concentration(rows, f) for f in ("population", "value_added")},
            "rank_stability": {"population_spearman": spearman(r0_pop, r1_pop),
                               "va_spearman": spearman(r0_va, r1_va),
                               "population_risers": sorted(change_pop.items(), key=lambda kv: -kv[1])[:10],
                               "population_fallers": sorted(change_pop.items(), key=lambda kv: kv[1])[:10],
                               "va_risers": sorted(change_va.items(), key=lambda kv: -kv[1])[:10],
                               "va_fallers": sorted(change_va.items(), key=lambda kv: kv[1])[:10]},
            "cagr_distributions_2026_2226": {field: quantiles([v[field] for v in cagr.values()])
                                               for field in ("population", "value_added", "va_per_capita_proxy")},
            "outliers": outliers,
            "negative_terminal_va_growth": sorted(r["iso3"] for r in rows if r["real_value_added_growth"] < 0),
            "replacement_coverage_below_one": sorted(r["iso3"] for r in rows if r.get("replacement_coverage_ratio", 1) < 1-1e-12),
            "country_ranks_2226": {iso: {"population": r1_pop[iso], "va": r1_va[iso]} for iso in sorted(by_iso)}}


def composition(rows, group, fields):
    totals = {field: math.fsum(r[field] for r in rows if r.get(field) is not None) for field in fields}
    groups = defaultdict(list)
    for row in rows:
        groups[row[group]].append(row)
    result = {}
    for key, members in sorted(groups.items()):
        result[key] = {field: (math.fsum(r[field] for r in members) / totals[field]
                               if totals[field] and all(r.get(field) is not None for r in members) else None)
                       for field in fields}
    return result


def arm(root, pre):
    rows = {2026: read(pre / "stage_2026_2031/countries_2026_2031.ndjson", 2026),
            2060: read(pre / "stage_2031_2060/countries_2060.ndjson"),
            2100: read(root / "results/countries_2060_2226.ndjson", 2100),
            2226: read(root / "results/countries_2226.ndjson")}
    sector_2026 = read(pre / "stage_2026_2031/country_sectors_2026_2031.ndjson", 2026)
    sector_2226 = read(root / "results/country_sectors_2226.ndjson")
    asset_2026 = read(pre / "stage_2026_2031/country_sector_assets_2026_2031.ndjson", 2026)
    asset_2226 = read(root / "results/country_sector_assets_2226.ndjson")
    return {"boundaries": {str(year): aggregate(values) for year, values in rows.items()},
            "country_rows": rows,
            "descriptives": describe(rows[2226], rows[2026]),
            "sector_composition": {"2026": composition(sector_2026, "sector", ("value_added", "employment", "capital", "investment")),
                                   "2226": composition(sector_2226, "sector", ("value_added", "employment", "capital", "investment"))},
            "asset_composition": {"2026": composition(asset_2026, "asset_class", ("capital", "investment")),
                                  "2226": composition(asset_2226, "asset_class", ("capital", "investment"))}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", required=True, type=Path)
    args = parser.parse_args()
    v3 = arm(V3_LOCAL / "full_2226", V3_PRE)
    successor = arm(args.candidate_root / "successor_80_2226", args.candidate_root)
    write(HERE / "DESCRIPTIVE_STATISTICS.json", {"schema": "loom-earth-v4-descriptives-v1",
           "status": "PROVISIONAL_SUCCESSOR_80_REVIEW_GATE", "v3_control": v3["descriptives"],
           "successor_80": successor["descriptives"], "successor_80_boundaries": successor["boundaries"]})
    write(HERE / "STRUCTURE_REPORT.json", {"schema": "loom-earth-v4-structure-v1",
           "asset_2026_investment_note": "2026 asset rows have null investment; asset-class investment shares are unavailable, not zero",
           "v3_control": {"sectors": v3["sector_composition"], "assets": v3["asset_composition"]},
           "successor_80": {"sectors": successor["sector_composition"], "assets": successor["asset_composition"]}})
    v3_end = {r["iso3"]: r for r in v3["country_rows"][2226]}
    suc_end = {r["iso3"]: r for r in successor["country_rows"][2226]}
    if set(v3_end) != set(suc_end):
        raise ValueError("A/B 80-economy universe differs")
    diff = {iso: {"va_delta": suc_end[iso]["value_added"]-v3_end[iso]["value_added"],
                  "va_relative_change": suc_end[iso]["value_added"]/v3_end[iso]["value_added"]-1,
                  "va_share_delta_pp": 100*(suc_end[iso]["value_added"]/successor["boundaries"]["2226"]["value_added"]
                                             - v3_end[iso]["value_added"]/v3["boundaries"]["2226"]["value_added"]),
                  "population_delta": suc_end[iso]["population"]-v3_end[iso]["population"]}
            for iso in sorted(v3_end)}
    comparison = {"schema": "loom-earth-v4-controlled-comparison-v1",
                  "V3_CONTROL": v3["boundaries"], "SUCCESSOR_80": successor["boundaries"],
                  "A_to_B_2226_country_effects": diff,
                  "A_to_B_2226_global_delta": {field: successor["boundaries"]["2226"][field]-v3["boundaries"]["2226"][field]
                                               for field in ("population", "value_added", "capital", "investment")},
                  "SUCCESSOR_FULL": {"status": "NOT_RUN_UNQUALIFIED_ECONOMIC_INPUTS",
                                     "reason": "157 WPP areas lack jointly qualified sector/asset/factor/trade inputs"},
                  "B_to_C": None, "A_to_C": None,
                  "interpretation": {"A_to_B": "2026 accounting-boundary repair and inherited model interactions on exactly the v3 80",
                                     "B_to_C": "Unavailable until expanded-economy economic qualification",
                                     "A_to_C": "Unavailable until expanded-economy economic qualification"}}
    write(HERE / "CONTROLLED_COMPARISON.json", comparison)
    print("V3_CONTROL and SUCCESSOR_80 analyzed; SUCCESSOR_FULL held")


if __name__ == "__main__":
    main()
