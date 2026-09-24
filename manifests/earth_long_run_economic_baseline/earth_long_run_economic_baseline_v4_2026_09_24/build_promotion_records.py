"""Build hash-pinned Earth v4 promotion records without rerunning economics."""
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent / "earth_long_run_economic_baseline_v4_candidate_2026_09_24"
PERMANENT = Path("/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24")
V3 = Path("/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v3_repaired_2026_09_23")
HISTORIC_QUALIFIER = Path("/home/ubuntu/loom_earth_2026_2035/earth_repair_successor_2026_09_22/qualify.py")
DESIGNATION = "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24"
MODEL = "v0.6.1-d1-c1-h1-r1-alpha060-national-gfcf1"
POLICY = "WDI_NATIONAL_GFCF_GDP_LATEST_2024_2025_MEDIAN_2024_FALLBACK_v1"


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path):
    path = Path(path)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}


def verify(path, expected):
    path = Path(path)
    if not path.is_file() or path.stat().st_size != expected["bytes"] or sha(path) != expected["sha256"]:
        raise ValueError(f"hash or size mismatch: {path}")


def rows(path):
    with Path(path).open() as stream:
        for line in stream:
            yield json.loads(line)


def write_both(name, value):
    content = json.dumps(value, sort_keys=True, indent=2) + "\n"
    (HERE / name).write_text(content)
    (PERMANENT / name).write_text(content)
    if (HERE / name).read_bytes() != (PERMANENT / name).read_bytes():
        raise ValueError(f"repository and permanent copies differ: {name}")


def qualification_boundary():
    spec = importlib.util.spec_from_file_location("historical_earth_qualification", HISTORIC_QUALIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    stage = PERMANENT / "stage_2031_2060"
    result = module.historical_boundary_gate(
        list(rows(stage / "country_sectors_2031_2060.ndjson")),
        list(rows(stage / "country_sector_assets_2031_2060.ndjson")),
    )
    if result["source_gate_sha256"] != "8e11ff09894a0796885a34390d418a8fdaea42e323efad813f4b1a27c650ae51":
        raise ValueError("historical boundary rule changed")
    if not result["passed"]:
        raise ValueError("existing post-transition boundary qualification did not pass")
    original = json.loads((stage / "report.json").read_text())
    if original["status"] != "REVIEW" or original["qualification"]["passed"]:
        raise ValueError("the original all-years REVIEW is missing")
    if original["qualification"]["max_annual_sector_investment_share_move"] != 0.04009355027507272:
        raise ValueError("the observed 4.009355 pp diagnostic changed")
    return {"schema": "earth-v4-inherited-boundary-qualification-v1",
            "all_years_diagnostic": {"status": "REVIEW_RETAINED",
                                     "maximum_total_sector_investment_share_move_pp": 100 * 0.04009355027507272,
                                     "threshold_pp": 3.0,
                                     "report": record(stage / "report.json")},
            "existing_post_transition_qualification": result,
            "qualifier_source": record(HISTORIC_QUALIFIER),
            "disposition": "Investigated replacement-driven first transition; v0.2 boundary qualification PASS; original v0.5 REVIEW unchanged"}


def scope(candidate_manifest):
    evidence = json.loads((CANDIDATE / "COUNTRY_EVIDENCE.json").read_text())["economies"]
    if len(evidence) != 237 or len({x["iso3"] for x in evidence}) != 237:
        raise ValueError("demographic identity universe is not 237 unique areas")
    economic = sorted(x["iso3"] for x in evidence if x["v3_economic_model"])
    demographic_only = sorted(x["iso3"] for x in evidence if not x["v3_economic_model"])
    if len(economic) != 80 or len(demographic_only) != 157:
        raise ValueError("economic versus demographic-only partition mismatch")
    for row in evidence:
        if row["identity_geography"]["class"] != "DIRECT" or row["demography"]["class"] != "DIRECT":
            raise ValueError(f"unqualified identity or demography: {row['iso3']}")
        for layer in ("labor", "productivity_tfp", "factor_shares", "investment_capital",
                      "sector_decomposition", "asset_decomposition", "trade_network_topology"):
            expected = "DERIVED_FROM_QUALIFIED_METHOD" if row["v3_economic_model"] else "UNAVAILABLE"
            if row[layer]["class"] != expected:
                raise ValueError(f"incorrect {layer} qualification for {row['iso3']}")
    endpoint = list(rows(PERMANENT / "successor_80_2226/results/countries_2226.ndjson"))
    if len(endpoint) != 80 or sorted(x["iso3"] for x in endpoint) != economic or {x["year"] for x in endpoint} != {2226}:
        raise ValueError("economic endpoint does not match qualified 80")
    sensitivity = json.loads((CANDIDATE / "DEMOGRAPHIC_SENSITIVITY.json").read_text())
    for name, scenario in sensitivity["scenarios"].items():
        if len(scenario["country_population_2226"]) != 237:
            raise ValueError(f"incomplete demographic scenario {name}")
    coverage = json.loads((CANDIDATE / "COVERAGE_REPORT.json").read_text())
    if coverage["target_economies"] != 237 or coverage["v3_modeled_economies"] != 80:
        raise ValueError("coverage report contradicts scope")
    return {"schema": "earth-v4-promotion-scope-v1", "designation": DESIGNATION,
            "decision_authority": "Kevin, explicit 2026-09-24 Earth v4 promotion-scope decision",
            "economic_qualification": {"count": 80, "iso3": economic,
                                       "status": "QUALIFIED_MODEL_TRAJECTORY_2026_2226"},
            "identity_demography": {"count": 237, "iso3": sorted(x["iso3"] for x in evidence),
                                      "population_time_basis": "UN_WPP_2024_MEDIUM_TPopulation1Jan"},
            "demographic_only": {"count": 157, "iso3": demographic_only,
                                 "status": "NO_QUALIFIED_ECONOMIC_TRAJECTORY"},
            "deferred": ["SUCCESSOR_FULL", "B_TO_C", "A_TO_C", "FULL_EARTH_ECONOMIC_TAIL_SENSITIVITY"],
            "country_evidence": record(PERMANENT / "candidate_git_record/COUNTRY_EVIDENCE.json"),
            "coverage_report": record(PERMANENT / "candidate_git_record/COVERAGE_REPORT.json"),
            "demographic_sensitivity": record(PERMANENT / "candidate_git_record/DEMOGRAPHIC_SENSITIVITY.json"),
            "candidate_manifest_sha256": sha(CANDIDATE / "CANDIDATE_RUN_MANIFEST.json")}


def main():
    if not PERMANENT.is_dir() or not (PERMANENT / "candidate_git_record").is_dir():
        raise ValueError("permanent candidate copy missing")
    candidate_manifest = json.loads((CANDIDATE / "CANDIDATE_RUN_MANIFEST.json").read_text())
    if candidate_manifest["status"] != "HOLD_NOT_PROMOTED":
        raise ValueError("candidate's historical status changed")
    local = {}
    for name, source in candidate_manifest["candidate_local_artifacts"].items():
        verify(source["path"], source)
        target = PERMANENT / name
        verify(target, source)
        local[name] = record(target)
    snapshot = {}
    for path in sorted((PERMANENT / "candidate_git_record").rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            original = CANDIDATE / path.relative_to(PERMANENT / "candidate_git_record")
            if not original.is_file() or sha(original) != sha(path):
                raise ValueError(f"candidate Git snapshot differs: {path}")
            snapshot[str(path.relative_to(PERMANENT / "candidate_git_record"))] = record(path)
    decision = HERE / "BASELINE_DECISION.md"
    (PERMANENT / "BASELINE_DECISION.md").write_bytes(decision.read_bytes())
    write_both("BOUNDARY_QUALIFICATION.json", qualification_boundary())
    write_both("PROMOTION_SCOPE.json", scope(candidate_manifest))
    forward = json.loads((PERMANENT / "successor_80_2226/trajectory_report.json").read_text())
    validation = json.loads((PERMANENT / "INDEPENDENT_VALIDATION.json").read_text())
    if not forward["qualification"]["passed"] or forward["qualification"]["final_year_reached"] != 2226:
        raise ValueError("forward annual gates did not qualify")
    if validation["status"] != "PASS" or validation["reconstructed_nodes"] != [["TWN", "ENERGY"]]:
        raise ValueError("independent validation or Taiwan repair failed")
    v3_manifest = V3 / "BASELINE_MANIFEST.json"
    pointer = json.loads((HERE.parent / "EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json").read_text())
    if pointer["active_designation"] != "EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23" or sha(v3_manifest) != pointer["active_manifest_sha256"]:
        raise ValueError("previous current v3 baseline is not verified")
    selected_names = ("successor_80_2226/results/countries_2060_2226.ndjson",
                      "successor_80_2226/results/country_sectors_2060_2226.ndjson",
                      "successor_80_2226/results/country_sector_assets_2060_2226.ndjson",
                      "successor_80_2226/results/countries_2226.ndjson",
                      "successor_80_2226/results/country_sectors_2226.ndjson",
                      "successor_80_2226/results/country_sector_assets_2226.ndjson",
                      "successor_80_2226/complete_checkpoints/earth_2226.checkpoint.zip")
    selected = {name: local[name] for name in selected_names}
    inherited = Path("/home/ubuntu/loom_earth_2026_2035/earth_repair_successor_2026_09_22")
    dependencies = {"stage_bridge.py": record(inherited / "stage_bridge.py"),
                    "stage_mid.py": record(inherited / "stage_mid.py"),
                    "v3_runner.py": record(V3 / "runner.py"),
                    "v3_checkpoint_io.py": record(V3 / "checkpoint_io.py"),
                    "v3_horizon_checkpoint.py": record(V3 / "horizon_checkpoint.py"),
                    "existing_boundary_qualifier.py": record(HISTORIC_QUALIFIER)}
    if dependencies["stage_bridge.py"]["sha256"] != "50fc8d9b38bf0336e34cd9214158120a3177df207fa3bcd977adf5eeea96b0a7":
        raise ValueError("inherited bridge code changed")
    if dependencies["stage_mid.py"]["sha256"] != "fb944c8d29e35bcd010d39e149604010dfdd89ab832764f87560844ef19947da":
        raise ValueError("inherited mid-stage code changed")
    if dependencies["v3_runner.py"]["sha256"] != "32e927276fff88652780d041169d8e216fa2ecea1f0e34babb8f0b155a5b9c37":
        raise ValueError("inherited forward runner changed")
    with zipfile.ZipFile(PERMANENT / selected_names[-1]) as archive:
        checkpoint = json.loads(archive.read("manifest.json"))
    if checkpoint["runner_sha256"] != dependencies["v3_runner.py"]["sha256"] or checkpoint["current_year"] != 2226:
        raise ValueError("completed checkpoint does not match executed numerical runner")
    run = {"schema": "loom-earth-v4-promoted-run-manifest-v1", "baseline_id": DESIGNATION,
           "source_candidate_branch_head": "84910307b5f0b6aa905dc53f14ed2a982d6e4d3e",
           "source_candidate_manifest": record(CANDIDATE / "CANDIDATE_RUN_MANIFEST.json"),
           "main_sha_at_candidate_start": "fbc3818648cd9cdf54629281f52b5eb928b4f877",
           "inherited_runtime_model_version": MODEL, "investment_policy_id": POLICY,
           "scope": record(PERMANENT / "PROMOTION_SCOPE.json"),
           "boundary_qualification": record(PERMANENT / "BOUNDARY_QUALIFICATION.json"),
           "independent_validation": local["INDEPENDENT_VALIDATION.json"],
           "forward_trajectory_report": local["successor_80_2226/trajectory_report.json"],
           "candidate_local_artifacts": local, "candidate_git_snapshot": snapshot,
           "inherited_code_dependencies": dependencies,
           "selected_outputs": selected,
           "qualification": {"economic_80_forward": "PASS", "identity_demography_237": "PASS",
                             "all_years_2031_2060": "REVIEW_RETAINED",
                             "existing_post_transition_boundary": "PASS",
                             "successor_full": "DEFERRED_BY_AUTHORIZED_SCOPE"},
           "previous_current_baseline": record(v3_manifest)}
    write_both("RUN_MANIFEST.json", run)
    baseline = {"schema": "loom-earth-local-economic-baseline-designation-v3",
                "designation": DESIGNATION,
                "status": "PROMOTED_WITH_DISCLOSED_2031_2060_REVIEW",
                "epistemic_status": "qualified 80-economy economic model plus 237-area identity/demography; scenario, not canon or physical capacity",
                "decision": record(PERMANENT / "BASELINE_DECISION.md"),
                "run_manifest": record(PERMANENT / "RUN_MANIFEST.json"),
                "promotion_scope": record(PERMANENT / "PROMOTION_SCOPE.json"),
                "boundary_qualification": record(PERMANENT / "BOUNDARY_QUALIFICATION.json"),
                "selected_outputs": selected,
                "previous_current_baseline": record(v3_manifest),
                "model_behavior_changed_by_promotion": False,
                "simulation_executed_by_promotion": False}
    write_both("BASELINE_MANIFEST.json", baseline)
    print(f"pinned {len(local)} copied local artifacts, {len(snapshot)} Git source files; "
          f"baseline manifest SHA-256 {sha(HERE / 'BASELINE_MANIFEST.json')}")


if __name__ == "__main__":
    main()
