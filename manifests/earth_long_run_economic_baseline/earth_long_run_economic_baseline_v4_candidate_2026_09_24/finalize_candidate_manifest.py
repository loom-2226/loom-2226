"""Pin the local candidate bytes from Git without changing the active pointer."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
POINTER = HERE.parent / "EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json"
V3_MANIFEST = HERE.parent / "earth_long_run_economic_baseline_v3_repaired_2026_09_23/BASELINE_MANIFEST.json"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def record(path):
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.candidate_root
    pointer = json.loads(POINTER.read_text())
    if pointer["active_designation"] != "EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23":
        raise ValueError("governed current baseline moved")
    if sha(pointer["active_manifest"]) != pointer["active_manifest_sha256"]:
        raise ValueError("v3 immutable reference hash mismatch")
    report = json.loads((root / "successor_80_2226/trajectory_report.json").read_text())
    stage_report = json.loads((root / "stage_2031_2060/report.json").read_text())
    if not report["qualification"]["passed"]:
        raise ValueError("provisional successor 80 annual gate failed")
    if stage_report["qualification"]["passed"]:
        raise ValueError("this HOLD manifest expects unresolved inherited mid-stage REVIEW")
    local = {str(path.relative_to(root)): record(path) for path in sorted(root.rglob("*")) if path.is_file()}
    code = {path.name: record(path) for path in sorted(HERE.glob("*.py"))}
    files = {name: record(HERE / name) for name in (
        "CHANGE_IMPACT.md", "COUNTRY_EVIDENCE.json", "COVERAGE_REPORT.json", "DATA_DICTIONARY.md",
        "DEMOGRAPHIC_SENSITIVITY.json", "MODEL_SPEC.md", "README.md", "RECONSTRUCTION_TRACE.json",
        "REDISTRIBUTION_PROVENANCE.json", "REJECTED_ATTEMPTS.md",
        "SOURCE_PROVENANCE.json", "QUALIFICATION_COVERAGE.md",
        "STRUCTURE_REPORT.json", "DESCRIPTIVE_STATISTICS.json", "CONTROLLED_COMPARISON.json",
        "OUTLIER_EXPLANATIONS.md", "PROMOTION_RECOMMENDATION.md", "QUALIFICATION_RESULTS.md",
        "parameters.json", "review_economies.json")}
    manifest = {"schema": "loom-earth-v4-candidate-run-manifest-v1",
                "designation": "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_CANDIDATE_2026_09_24",
                "status": "HOLD_NOT_PROMOTED",
                "base_main_sha": "fbc3818648cd9cdf54629281f52b5eb928b4f877",
                "v3_current_pointer": record(POINTER), "v3_baseline_manifest": record(V3_MANIFEST),
                "candidate_root": str(root), "candidate_local_artifacts": local,
                "candidate_repo_code": code, "candidate_repo_reports": files,
                "qualification": {"successor_80_forward_annual_gates": report["qualification"]["passed"],
                                  "pre2060_stage_review": stage_report["qualification"],
                                  "successor_full_economic": "NOT_RUN_UNQUALIFIED_INPUTS",
                                  "promotion": "HOLD"},
                "failed_attempt_note": "Two rejected local construction attempts are retained outside the candidate root and documented in REJECTED_ATTEMPTS.md. The final candidate root contains only the corrected seed, stages, smoke and full diagnostic."}
    (HERE / "CANDIDATE_RUN_MANIFEST.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print("pinned", len(local), "candidate local files and", len(code), "code files")


if __name__ == "__main__":
    main()
