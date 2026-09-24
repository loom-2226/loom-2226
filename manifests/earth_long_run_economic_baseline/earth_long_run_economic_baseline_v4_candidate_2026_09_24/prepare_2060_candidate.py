"""Register the repaired 2060 candidate boundary without calling it qualified."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.candidate_root
    stage = root / "stage_2031_2060"
    report_path = stage / "report.json"
    report = json.loads(report_path.read_text())
    rows = [json.loads(line) for line in (stage / "countries_2060.ndjson").open()]
    if len(rows) != 80 or len({r["iso3"] for r in rows}) != 80:
        raise ValueError("candidate 2060 country identity invalid")
    vector = [[r["iso3"], r["capital_share_alpha"], r["investment"] / r["value_added"]]
              for r in sorted(rows, key=lambda r: r["iso3"])]
    fingerprint = hashlib.sha256(json.dumps(vector, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    files = {}
    for name in ("countries_2060.ndjson", "country_sectors_2060.ndjson", "country_sector_assets_2060.ndjson"):
        path = stage / name
        files[name] = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}
    manifest = {"schema": "loom-earth-v4-candidate-2060-boundary-v1",
                "status": "CANDIDATE_REVIEW_GATE_NOT_QUALIFIED" if not report["qualification"]["passed"] else "CANDIDATE_GATE_PASSED",
                "boundary_year": 2060, "country_count": 80, "sector_row_count": 800, "asset_row_count": 3200,
                "qualification": report["qualification"],
                "economic_policy": {"id": "UNTREATED_FROZEN_2060_EXPLICIT_v1",
                                    "interpretation": "Inherited source PWT capital shares and derived 2060 investment/VA; candidate 2026 repair, no clipping",
                                    "ordered_vector": vector,
                                    "ordered_vector_sha256": fingerprint},
                "files": files, "source_stage_report": str(report_path), "source_stage_report_sha256": sha(report_path)}
    path = root / "CANDIDATE_2060_MANIFEST.json"
    path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print(path, manifest["status"], fingerprint)


if __name__ == "__main__":
    main()
