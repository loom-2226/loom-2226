"""Build an isolated, source-preserving 2026 successor seed for the original 80.

The old current-price observation is never edited. The candidate copies only
qualified model inputs and makes the modeled production reconstruction explicit.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from successor import qualifying_nodes, repair_seed

HERE = Path(__file__).resolve().parent
EARTH = Path("/home/ubuntu/LOOM_Earth2026")
ROOT = Path("/home/ubuntu/loom_earth_2026_2035")
V3 = HERE.parent / "earth_long_run_economic_baseline_v3_repaired_2026_09_23" / "RUN_MANIFEST.json"


def load(path):
    return [json.loads(line) for line in Path(path).open() if line.strip()]


def write(path, rows):
    with Path(path).open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_root
    output.mkdir(parents=True, exist_ok=False)
    inputs = output / "qualified_inputs"
    inputs.mkdir()
    qualified = EARTH / "earth2026_2031_cobb_douglas_v0.2"
    asset_path = EARTH / "earth2026_sector_capital_asset_reconstruction_v0.2/country_sector_assets_2026.ndjson"
    country_path = qualified / "countries_2026_2031.ndjson"
    sector_path = qualified / "country_sectors_2026_2031.ndjson"
    countries_all = load(country_path)
    sectors_all = load(sector_path)
    asset_rows = load(asset_path)
    countries = {r["iso3"]: r for r in countries_all if r["year"] == 2026}
    sectors = {(r["iso3"], r["sector"]): r for r in sectors_all if r["year"] == 2026}
    assets = {(r["iso3"], r["sector"], r["asset_class"]): r for r in asset_rows}
    if len(countries) != 80 or len(sectors) != 800 or len(assets) != 3200:
        raise ValueError("qualified 2026 input shape changed")
    v3 = json.loads(V3.read_text())
    v3_countries = {r["iso3"]: r for r in load(v3["sources"]["seed_2026_countries"]["path"]) if r["year"] == 2026}
    v3_sectors = {(r["iso3"], r["sector"]): r for r in load(v3["sources"]["seed_2026_sectors"]["path"]) if r["year"] == 2026}
    if set(countries) != set(v3_countries) or set(sectors) != set(v3_sectors):
        raise ValueError("2026 source universe differs from v3 control")
    for iso, row in countries.items():
        for key in ("population", "employment", "value_added", "capital", "investment"):
            if not math.isclose(row[key], v3_countries[iso][key], rel_tol=1e-12):
                raise ValueError(f"2026 source/control mismatch {iso} {key}")
    for node, row in sectors.items():
        for key in ("employment", "value_added", "gross_output", "investment"):
            if not math.isclose(row[key], v3_sectors[node][key], rel_tol=1e-12):
                raise ValueError(f"2026 sector/control mismatch {node} {key}")
    oecd = ROOT / "oecd_ten_sector_2024"
    source = {}
    source_files = {}
    for basis, key, field in (("current", "current_va", "value_added"),
                              ("current", "current_go", "gross_output"),
                              ("pyp", "pyp_va", "value_added"),
                              ("pyp", "pyp_go", "gross_output")):
        path = oecd / f"{basis}_country_sector_{field}_2024.ndjson"
        source_files[key] = str(path)
        for row in load(path):
            source.setdefault((row["country"], row["sector"]), {})[key] = row[field]
    nodes = qualifying_nodes(source, sectors)
    repaired_sectors, repaired_assets, trace = repair_seed(source, sectors, assets, countries)
    if len(nodes) != len(trace):
        raise ValueError("qualifying-node trace incomplete")
    for row in sectors_all:
        if row["year"] == 2026:
            row.update(repaired_sectors[(row["iso3"], row["sector"])])
            if "raw_value_added_before_country_tfp" in row:
                row["raw_value_added_before_country_tfp"] = row["value_added"] / row["country_tfp_multiplier"]
            if (row["iso3"], row["sector"]) in nodes:
                row["reconstruction_method_id"] = trace[nodes.index((row["iso3"], row["sector"]))]["method_id"]
                row["source_current_price_va_2024_signed"] = source[(row["iso3"], row["sector"])]["current_va"]
    asset_class_totals = {}
    for (iso, _, cls), item in repaired_assets.items():
        asset_class_totals[(iso, cls)] = asset_class_totals.get((iso, cls), 0) + item["capital"]
    for row in asset_rows:
        updated = repaired_assets[(row["iso3"], row["sector"], row["asset_class"])]
        row["capital"] = updated["capital"]
        row["share_of_sector_capital"] = row["capital"] / repaired_sectors[(row["iso3"], row["sector"])]["capital"]
        class_total = asset_class_totals[(row["iso3"], row["asset_class"])]
        row["share_of_country_asset_class"] = row["capital"] / class_total if class_total > 0 else 0.0
        row["modeled_2026_reconstruction"] = (row["iso3"], row["sector"]) in nodes
        if row["modeled_2026_reconstruction"]:
            row["reconstruction_method_id"] = trace[nodes.index((row["iso3"], row["sector"]))]["method_id"]
    write(inputs / "countries_2026_2031.ndjson", countries_all)
    write(inputs / "country_sectors_2026_2031.ndjson", sectors_all)
    write(output / "seed_assets_2026.ndjson", asset_rows)
    (output / "RECONSTRUCTION_TRACE.json").write_text(json.dumps({"schema": "loom-earth-v4-accounting-boundary-trace-v1",
        "qualified_nodes": trace, "source_observation_preserved": True, "v3_original_80_unchanged": True}, sort_keys=True, indent=2) + "\n")
    paths = [country_path, sector_path, asset_path, *map(Path, source_files.values()),
             inputs / "countries_2026_2031.ndjson", inputs / "country_sectors_2026_2031.ndjson",
             output / "seed_assets_2026.ndjson", output / "RECONSTRUCTION_TRACE.json"]
    (output / "SEED_MANIFEST.json").write_text(json.dumps({"schema": "loom-earth-v4-seed-manifest-v1",
        "input_v3_run_manifest_sha256": sha(V3), "files": {str(p): {"sha256": sha(p), "bytes": p.stat().st_size} for p in paths}},
        sort_keys=True, indent=2) + "\n")
    print(f"2026 qualifying nodes: {nodes}; seed written: {output}")


if __name__ == "__main__":
    main()
