"""Record every altered 2026 sector and asset cell with method provenance."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = Path("/home/ubuntu/LOOM_Earth2026")
METHOD = "PROPORTIONAL_COUNTRY_RESIDUAL_ASSET_CLASS_PRESERVING_2026"


def rows(path, key):
    with Path(path).open() as handle:
        return {tuple(row[k] for k in key): row for row in (json.loads(line) for line in handle)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.candidate_root
    original_sector = ORIGINAL / "earth2026_2031_cobb_douglas_v0.2/country_sectors_2026_2031.ndjson"
    candidate_sector = root / "qualified_inputs/country_sectors_2026_2031.ndjson"
    original_assets = ORIGINAL / "earth2026_sector_capital_asset_reconstruction_v0.2/country_sector_assets_2026.ndjson"
    candidate_assets = root / "seed_assets_2026.ndjson"
    before_s = rows(original_sector, ("iso3", "sector", "year"))
    after_s = rows(candidate_sector, ("iso3", "sector", "year"))
    before_a = rows(original_assets, ("iso3", "sector", "asset_class"))
    after_a = rows(candidate_assets, ("iso3", "sector", "asset_class"))
    if set(before_s) != set(after_s) or set(before_a) != set(after_a):
        raise ValueError("successor changed model node identities")
    source = json.loads((root / "RECONSTRUCTION_TRACE.json").read_text())
    targets = {(r["iso3"], r["sector"]): r["method_id"] for r in source["qualified_nodes"]}
    sector_changes = []
    for key in sorted(before_s):
        if key[2] != 2026:
            continue
        fields = ("value_added", "gross_output", "capital", "investment", "employment")
        changed = {field: {"original": before_s[key][field], "candidate": after_s[key][field]}
                   for field in fields if before_s[key][field] != after_s[key][field]}
        if changed:
            sector_changes.append({"iso3": key[0], "sector": key[1], "year": 2026,
                                   "role": "ACCOUNTING_ANOMALY_TARGET" if key[:2] in targets else "WITHIN_COUNTRY_DONOR",
                                   "method_id": targets[key[:2]] if key[:2] in targets else METHOD,
                                   "changed_modeled_fields": changed})
    asset_changes = []
    for key in sorted(before_a):
        if before_a[key]["capital"] != after_a[key]["capital"]:
            asset_changes.append({"iso3": key[0], "sector": key[1], "asset_class": key[2],
                                  "role": "ACCOUNTING_ANOMALY_TARGET" if key[:2] in targets else "WITHIN_COUNTRY_DONOR",
                                  "method_id": METHOD,
                                  "original_modeled_capital": before_a[key]["capital"],
                                  "candidate_modeled_capital": after_a[key]["capital"]})
    result = {"schema": "loom-earth-v4-2026-redistribution-provenance-v1",
              "source_observations_untouched": True,
              "method": "Target PYP ratio, country VA/K/I residual donated proportionally; donor asset-class mixes and national asset-class capital conserved",
              "source_sha256": {str(path): sha(path) for path in (original_sector, original_assets)},
              "candidate_sha256": {str(path): sha(path) for path in (candidate_sector, candidate_assets)},
              "sector_changes": sector_changes, "asset_changes": asset_changes,
              "sector_change_count": len(sector_changes), "asset_change_count": len(asset_changes)}
    (HERE / "REDISTRIBUTION_PROVENANCE.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("2026 sector changes", len(sector_changes), "asset changes", len(asset_changes))


if __name__ == "__main__":
    main()
