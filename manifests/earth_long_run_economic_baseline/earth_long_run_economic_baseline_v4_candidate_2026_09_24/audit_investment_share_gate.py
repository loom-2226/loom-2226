"""Read-only, independent audit of the inherited 2031–2060 investment-share gate."""
import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CANDIDATE = Path("/home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24")
DEFAULT_CONTROL = Path("/home/ubuntu/loom_earth_2026_2035/earth_repair_successor_2026_09_22")


def read_rows(path):
    with path.open() as handle:
        for line in handle:
            yield json.loads(line)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_stage(root):
    base = root / "stage_2031_2060"
    report = json.loads((base / "report.json").read_text())
    sectors_path = base / "country_sectors_2031_2060.ndjson"
    if sha256(sectors_path) != report["output_files"]["sectors_all"]["sha256"]:
        raise ValueError("stage sector bytes do not match their own report")
    rows = list(read_rows(sectors_path))
    by_key = {}
    totals = {}
    for row in rows:
        key = row["iso3"], row["sector"], row["year"]
        if key in by_key:
            raise ValueError(f"duplicate sector-year {key}")
        by_key[key] = row
        cy = row["iso3"], row["year"]
        totals[cy] = totals.get(cy, 0.0) + row["investment"]
    moves = []
    for (iso, sector, year), row in by_key.items():
        previous = by_key.get((iso, sector, year - 1))
        if previous is None:
            continue
        before = previous["investment"] / totals[(iso, year - 1)]
        after = row["investment"] / totals[(iso, year)]
        if not math.isclose(after, row["investment_share_of_country"], rel_tol=1e-12):
            raise ValueError(f"reported share does not match investment: {iso}/{sector}/{year}")
        moves.append({"iso3": iso, "sector": sector, "from_year": year - 1, "to_year": year,
                      "share_before": before, "share_after": after, "move_pp": 100 * (after - before),
                      "absolute_move_pp": 100 * abs(after - before),
                      "sector_investment_before": previous["investment"],
                      "sector_investment_after": row["investment"],
                      "country_investment_before": totals[(iso, year - 1)],
                      "country_investment_after": totals[(iso, year)]})
    moves.sort(key=lambda x: (-x["absolute_move_pp"], x["iso3"], x["sector"], x["to_year"]))
    maximum = moves[0]
    if not math.isclose(maximum["absolute_move_pp"] / 100,
                        report["qualification"]["max_annual_sector_investment_share_move"], rel_tol=1e-12):
        raise ValueError("independent maximum differs from stage report")
    return base, report, by_key, totals, moves


def normalized(values):
    total = sum(values.values())
    return {key: value / total for key, value in values.items()}


def causal_trace(base, report, by_key, totals, maximum):
    iso, year = maximum["iso3"], maximum["to_year"]
    country_path = base / "countries_2031_2060.ndjson"
    if sha256(country_path) != report["output_files"]["countries_all"]["sha256"]:
        raise ValueError("stage country bytes do not match their own report")
    country_rows = {row["year"]: row for row in read_rows(country_path)
                    if row["iso3"] == iso and row["year"] in (year - 1, year)}
    investment_rate = country_rows[year - 1]["investment"] / country_rows[year - 1]["value_added"]
    if not math.isclose(investment_rate * country_rows[year]["value_added"],
                        country_rows[year]["investment"], rel_tol=1e-12):
        raise ValueError("country investment-rate rule does not reproduce the transition")
    sectors = sorted(sector for country, sector, y in by_key if country == iso and y == year)
    prior = {sector: by_key[(iso, sector, year - 1)]["investment"] / totals[(iso, year - 1)]
             for sector in sectors}
    pressure = {sector: by_key[(iso, sector, year)]["io_demand_pressure"] for sector in sectors}
    productivity = {sector: by_key[(iso, sector, year)]["capital_productivity"] for sector in sectors}
    prod_ref = sorted(productivity.values())
    prod_ref = (prod_ref[4] + prod_ref[5]) / 2
    params = report["parameters"]
    raw = {sector: prior[sector] ** params["investment_inertia_exponent"]
           * pressure[sector] ** params["demand_elasticity_expansion"]
           * (productivity[sector] / prod_ref) ** params["productivity_elasticity_expansion"]
           for sector in sectors}
    desired = normalized(raw)
    speed = params["investment_adjust_speed"]
    blended = normalized({sector: (1 - speed) * prior[sector] + speed * desired[sector]
                          for sector in sectors})
    asset_path = base / "country_sector_assets_2031_2060.ndjson"
    if sha256(asset_path) != report["output_files"]["assets_all"]["sha256"]:
        raise ValueError("stage asset bytes do not match their own report")
    previous_assets = [row for row in read_rows(asset_path) if row["iso3"] == iso and row["year"] == year - 1]
    replacement = {sector: 0.0 for sector in sectors}
    for asset in previous_assets:
        evolved_capital = ((1 - asset["asset_depreciation_rate"]) * asset["capital"]
                           + asset["investment"])
        replacement[asset["sector"]] += asset["asset_depreciation_rate"] * evolved_capital
    replacement_total = sum(replacement.values())
    country_investment = totals[(iso, year)]
    coverage = min(1.0, country_investment / replacement_total)
    expansion_total = country_investment - coverage * replacement_total
    reconstructed = {sector: coverage * replacement[sector] + expansion_total * blended[sector]
                     for sector in sectors}
    for sector in sectors:
        observed = by_key[(iso, sector, year)]["investment"]
        if not math.isclose(reconstructed[sector], observed, rel_tol=1e-12):
            raise ValueError(f"allocation formula does not reproduce {iso}/{sector}/{year}")
    target = maximum["sector"]
    replacement_weight = coverage * replacement_total / country_investment
    return {"country_investment_rule": "prior country investment/VA rate times current modeled country VA",
            "frozen_country_investment_per_va": investment_rate,
            "country_value_added_before": country_rows[year - 1]["value_added"],
            "country_value_added_after": country_rows[year]["value_added"],
            "country_investment": country_investment, "replacement_requirement": replacement_total,
            "replacement_coverage": coverage, "expansion_budget": expansion_total,
            "parameters": params, "io_demand_pressure": pressure[target],
            "capital_productivity": productivity[target], "prior_total_share": prior[target],
            "desired_expansion_share": desired[target], "blended_expansion_share": blended[target],
            "replacement_investment": coverage * replacement[target],
            "replacement_share_of_replacement_budget": replacement[target] / replacement_total,
            "expansion_investment": expansion_total * blended[target],
            "reconstructed_sector_investment": reconstructed[target],
            "replacement_contribution_to_move_pp": 100 * replacement_weight
                * (replacement[target] / replacement_total - prior[target]),
            "expansion_contribution_to_move_pp": 100 * (1 - replacement_weight)
                * (blended[target] - prior[target])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--v3-stage-root", type=Path, default=DEFAULT_CONTROL)
    parser.add_argument("--output", type=Path, default=HERE / "INVESTMENT_SHARE_GATE_AUDIT.json")
    args = parser.parse_args()
    base, report, rows, totals, moves = load_stage(args.candidate_root)
    old_base, old_report, old_rows, old_totals, old_moves = load_stage(args.v3_stage_root)
    maximum = moves[0]
    key = maximum["iso3"], maximum["sector"], maximum["to_year"]
    for y in range(2031, 2035):
        a, b = rows[(key[0], key[1], y)], old_rows[(key[0], key[1], y)]
        if y <= 2032 and (a["investment"] != b["investment"] or
                          a["investment_share_of_country"] != b["investment_share_of_country"]):
            raise ValueError("v3/v4 initial excursion differs")
    top20_keys = [(x["iso3"], x["sector"], x["from_year"], x["to_year"]) for x in moves[:20]]
    old_top20_keys = [(x["iso3"], x["sector"], x["from_year"], x["to_year"]) for x in old_moves[:20]]
    if top20_keys != old_top20_keys:
        raise ValueError("v3/v4 top-20 movement identities differ")
    by_year = {}
    for move in moves:
        by_year[move["to_year"]] = max(by_year.get(move["to_year"], 0), move["absolute_move_pp"])
    result = {"schema": "earth-v4-sector-investment-share-gate-audit-v1",
              "status": "REVIEW_UNCHANGED", "candidate_stage_report_sha256": sha256(base / "report.json"),
              "v3_stage_report_sha256": sha256(old_base / "report.json"),
              "candidate_stage_source_sha256": report["output_files"]["sectors_all"]["sha256"],
              "v3_stage_source_sha256": old_report["output_files"]["sectors_all"]["sha256"],
              "annual_moves_examined": len(moves), "maximum": maximum,
              "top_20": moves[:20], "moves_above_3pp": sum(x["absolute_move_pp"] > 3 for x in moves),
              "year_maxima_pp": by_year, "maximum_after_2032_pp": max(v for y, v in by_year.items() if y > 2032),
              "v3_maximum": old_moves[0], "v3_v4_maximum_node_2031_2032_equal": True,
              "v3_v4_top_20_identities_equal": True,
              "causal_trace": causal_trace(base, report, rows, totals, maximum),
              "classification": "LEGITIMATE_MODEL_DYNAMICS",
              "disposition": "The modeled allocation is internally valid. No threshold, model behavior or qualification result changed; existing governance provides no automatic conversion of REVIEW to PASS."}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"audited {len(moves)} annual moves; maximum {maximum['absolute_move_pp']:.12f} pp; "
          f"above 3 pp: {result['moves_above_3pp']}; reproduced v3: {result['v3_v4_maximum_node_2031_2032_equal']}")


if __name__ == "__main__":
    main()
