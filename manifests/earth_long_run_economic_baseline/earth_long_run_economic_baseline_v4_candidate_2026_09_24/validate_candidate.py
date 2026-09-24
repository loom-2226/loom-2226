"""Independent candidate accounting and production validation (read only)."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path


def rows(path):
    with path.open() as handle:
        for line in handle:
            yield json.loads(line)


def close(a, b):
    return math.isclose(a, b, rel_tol=3e-12, abs_tol=1e-8)


def validate(root):
    output = root / "successor_80_2226/results"
    countries = {}
    for row in rows(output / "countries_2060_2226.ndjson"):
        key = (row["iso3"], row["year"])
        if key in countries:
            raise ValueError(f"duplicate economy-year {key}")
        countries[key] = row
    if len(countries) != 80 * 167:
        raise ValueError("incomplete annual country universe")
    sums = defaultdict(lambda: defaultdict(list))
    sector_capital = {}
    historical_A = {}
    count = 0
    reconstructed = {(row["iso3"], row["sector"]) for row in
                     json.loads((root / "RECONSTRUCTION_TRACE.json").read_text())["qualified_nodes"]}
    for row in rows(output / "country_sectors_2060_2226.ndjson"):
        key = (row["iso3"], row["sector"])
        cy = (row["iso3"], row["year"])
        for field in ("value_added", "capital", "investment", "employment", "gross_output"):
            value = row[field]
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"invalid modeled sector {cy} {field}")
            sums[cy][field].append(value)
        sector_capital[(row["iso3"], row["sector"], row["year"])] = row["capital"]
        if key in historical_A and row["cobb_douglas_A_2026"] != historical_A[key]:
            raise ValueError(f"2026 historical A mutated {key}")
        historical_A[key] = row["cobb_douglas_A_2026"]
        if row["year"] > 2060:
            if not close(row["capital_share_alpha"] + row["labor_exponent_effective"], 1):
                raise ValueError(f"factor exponents {key} {row['year']}")
            modeled = (row["country_tfp_multiplier"] * row["technology_productivity_multiplier"]
                       * row["A"] * row["capital"] ** row["capital_share_alpha"]
                       * row["effective_labor_input"] ** row["labor_exponent_effective"])
            if not close(modeled, row["value_added"]):
                raise ValueError(f"operative production {key} {row['year']}")
        if key in reconstructed and min(row["value_added"], row["gross_output"], row["capital"], row["A"]) <= 0:
            raise ValueError(f"reconstructed sector failed {key} {row['year']}")
        count += 1
    if count != 80 * 10 * 167:
        raise ValueError("incomplete sector rows")
    for key, fields in sums.items():
        for field, values in fields.items():
            if not close(math.fsum(values), countries[key][field]):
                raise ValueError(f"country-sector reconciliation {key} {field}")
    asset_capital = defaultdict(list)
    prior = {}
    count_assets = 0
    for row in rows(output / "country_sector_assets_2060_2226.ndjson"):
        key = (row["iso3"], row["sector"], row["asset_class"])
        if key in prior:
            old = prior[key]
            if row["year"] != old["year"] + 1:
                raise ValueError(f"asset year gap {key}")
            predicted = (1-row["asset_depreciation_rate"]) * old["capital"] + old["investment"]
            if not close(predicted, row["capital"]):
                raise ValueError(f"asset stock-flow {key} {row['year']}")
        prior[key] = row
        asset_capital[(row["iso3"], row["sector"], row["year"])].append(row["capital"])
        count_assets += 1
    if count_assets != 80 * 10 * 4 * 167:
        raise ValueError("incomplete asset rows")
    for key, values in asset_capital.items():
        if not close(math.fsum(values), sector_capital[key]):
            raise ValueError(f"sector-asset capital reconciliation {key}")
    return {"status": "PASS", "country_year_rows": len(countries), "sector_year_rows": count,
            "asset_year_rows": count_assets, "reconstructed_nodes": sorted([list(node) for node in reconstructed]),
            "checks": ["unique economy-year", "finite nonnegative modeled sector state", "country-sector accounting",
                       "sector-asset capital", "annual asset stock-flow", "factor exponents", "operative production",
                       "immutable 2026 historical A", "reconstructed sector positive"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", required=True, type=Path)
    args = parser.parse_args()
    result = validate(args.candidate_root)
    (args.candidate_root / "INDEPENDENT_VALIDATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
