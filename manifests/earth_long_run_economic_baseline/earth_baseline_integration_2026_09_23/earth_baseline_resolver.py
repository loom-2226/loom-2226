"""Resolve the local Earth long-run economic baseline, failing closed on stale files.

This module reads the current-baseline pointer; it never selects a versioned run
on its own. Historical designations remain resolvable for explicit rollback.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


BASELINE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
CURRENT_POINTER = BASELINE_ROOT / "EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json"
DEMOGRAPHIC_POINTER = BASELINE_ROOT / "EARTH_DEMOGRAPHIC_AUTHORITY_CURRENT.json"


class BaselineResolutionError(ValueError):
    """The designated baseline or one of its pinned artifacts is unavailable."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise BaselineResolutionError(f"Cannot read {path}: {exc}") from exc
    return digest.hexdigest()


def _json(path: Path) -> dict:
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BaselineResolutionError(f"Cannot parse {path}: {exc}") from exc
    if not isinstance(content, dict):
        raise BaselineResolutionError(f"Expected JSON object: {path}")
    return content


def _check(path: Path, expected_hash: str, expected_bytes: int | None = None) -> None:
    actual_hash = _sha256(path)
    if actual_hash != expected_hash:
        raise BaselineResolutionError(f"SHA-256 mismatch: {path}")
    if expected_bytes is not None and path.stat().st_size != expected_bytes:
        raise BaselineResolutionError(f"Byte-size mismatch: {path}")


def _registered(rows: list[dict]) -> None:
    for item in rows:
        _check(Path(item["path"]), item["sha256"], item["bytes"])


def resolve(pointer_path: Path = CURRENT_POINTER) -> dict:
    """Return verified baseline identity and artifact paths; never fall back."""
    pointer = _json(Path(pointer_path))
    if pointer.get("schema") != "loom-earth-local-economic-baseline-pointer-v1":
        raise BaselineResolutionError("Unsupported baseline-pointer schema")
    manifest_path = Path(pointer["active_manifest"])
    _check(manifest_path, pointer["active_manifest_sha256"])
    manifest = _json(manifest_path)

    # The rollback target is checked independently. It is never a substitute
    # for a missing or corrupt active manifest.
    _check(Path(pointer["rollback_manifest"]), pointer["rollback_manifest_sha256"])

    if manifest.get("schema") == "loom-earth-local-economic-baseline-designation-v3":
        if manifest["designation"] != pointer["active_designation"] or manifest["designation"] != "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24":
            raise BaselineResolutionError("V4 designation mismatch")
        decision = manifest["decision"]
        _check(Path(decision["path"]), decision["sha256"], decision["bytes"])
        _check(manifest_path.parent / "BASELINE_DECISION.md", pointer["active_decision_sha256"])
        if decision["sha256"] != pointer["active_decision_sha256"]:
            raise BaselineResolutionError("V4 decision hash mismatch")
        previous = manifest["previous_current_baseline"]
        _check(Path(previous["path"]), previous["sha256"], previous["bytes"])
        if (previous["path"] != pointer["rollback_manifest"] or
                previous["sha256"] != pointer["rollback_manifest_sha256"] or
                pointer["previous_formal_designation"] != "EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23"):
            raise BaselineResolutionError("V4 rollback identity mismatch")
        run_ref = manifest["run_manifest"]
        _check(Path(run_ref["path"]), run_ref["sha256"], run_ref["bytes"])
        run = _json(Path(run_ref["path"]))
        if (run.get("schema") != "loom-earth-v4-promoted-run-manifest-v1" or
                run["baseline_id"] != manifest["designation"] or
                run["inherited_runtime_model_version"] != "v0.6.1-d1-c1-h1-r1-alpha060-national-gfcf1" or
                run["investment_policy_id"] != "WDI_NATIONAL_GFCF_GDP_LATEST_2024_2025_MEDIAN_2024_FALLBACK_v1"):
            raise BaselineResolutionError("V4 run identity mismatch")
        checked = 0
        for group in ("candidate_local_artifacts", "candidate_git_snapshot", "inherited_code_dependencies"):
            for item in run[group].values():
                _check(Path(item["path"]), item["sha256"], item["bytes"])
                checked += 1
        for name in ("source_candidate_manifest", "scope", "boundary_qualification",
                     "independent_validation", "forward_trajectory_report", "previous_current_baseline"):
            item = run[name]
            _check(Path(item["path"]), item["sha256"], item["bytes"])
            checked += 1
        if (manifest["promotion_scope"] != run["scope"] or
                manifest["boundary_qualification"] != run["boundary_qualification"] or
                manifest["selected_outputs"] != run["selected_outputs"] or
                manifest["previous_current_baseline"] != run["previous_current_baseline"]):
            raise BaselineResolutionError("V4 designation/run records disagree")
        for name, item in run["selected_outputs"].items():
            if run["candidate_local_artifacts"].get(name) != item:
                raise BaselineResolutionError("V4 selected output is not run-pinned")
        scope = _json(Path(run["scope"]["path"]))
        economic = set(scope["economic_qualification"]["iso3"])
        demographic = set(scope["identity_demography"]["iso3"])
        demographic_only = set(scope["demographic_only"]["iso3"])
        if (len(economic) != 80 or len(demographic) != 237 or len(demographic_only) != 157 or
                economic & demographic_only or economic | demographic_only != demographic or
                scope["identity_demography"]["population_time_basis"] != "UN_WPP_2024_MEDIUM_TPopulation1Jan"):
            raise BaselineResolutionError("V4 coverage partition invalid")
        for name in ("country_evidence", "coverage_report", "demographic_sensitivity"):
            item = scope[name]
            _check(Path(item["path"]), item["sha256"], item["bytes"])
            checked += 1
        evidence = _json(Path(scope["country_evidence"]["path"]))["economies"]
        if (len(evidence) != 237 or {row["iso3"] for row in evidence} != demographic or
                {row["iso3"] for row in evidence if row["v3_economic_model"]} != economic or
                any(row["demography"]["class"] != "DIRECT" or row["identity_geography"]["class"] != "DIRECT"
                    for row in evidence)):
            raise BaselineResolutionError("V4 country evidence contradicts scope")
        for row in evidence:
            expected = "DERIVED_FROM_QUALIFIED_METHOD" if row["iso3"] in economic else "UNAVAILABLE"
            for layer in ("labor", "productivity_tfp", "factor_shares", "investment_capital",
                          "sector_decomposition", "asset_decomposition", "trade_network_topology"):
                if row[layer]["class"] != expected:
                    raise BaselineResolutionError(f"V4 {layer} evidence contradicts economic coverage")
        coverage = _json(Path(scope["coverage_report"]["path"]))
        if coverage["target_economies"] != 237 or coverage["v3_modeled_economies"] != 80:
            raise BaselineResolutionError("V4 coverage report contradicts scope")
        sensitivity = _json(Path(scope["demographic_sensitivity"]["path"]))
        if sensitivity.get("status") != "SCENARIOS_NOT_SELECTED_CENTRAL_UNCHANGED":
            raise BaselineResolutionError("V4 demographic sensitivity authority status invalid")
        if any(set(scenario["country_population_2226"]) != demographic
               for scenario in sensitivity["scenarios"].values()):
            raise BaselineResolutionError("V4 demographic envelope incomplete")

        # PR #267 made the aggregate half-life tail non-authoritative. The
        # additive v4.1 supplement selects a 2226 endpoint without rewriting
        # the immutable promoted-v4 records or inventing an annual trajectory.
        demographic_pointer = _json(DEMOGRAPHIC_POINTER)
        if (demographic_pointer.get("schema") != "loom-earth-demographic-authority-pointer-v1" or
                demographic_pointer.get("status") != "ACTIVE" or
                demographic_pointer.get("economic_baseline_designation") != manifest["designation"] or
                demographic_pointer.get("selected_year") != 2226):
            raise BaselineResolutionError("V4 demographic authority pointer invalid")
        correction_manifest_path = REPO_ROOT / demographic_pointer["active_manifest"]
        _check(correction_manifest_path, demographic_pointer["active_manifest_sha256"])
        correction_manifest = _json(correction_manifest_path)
        if (correction_manifest.get("schema") != "loom-earth-v4-demographic-correction-manifest-v1" or
                correction_manifest.get("status") != "ACTIVE_DATA_INTEGRATION_SUPPLEMENT" or
                correction_manifest.get("target_baseline") != manifest["designation"] or
                correction_manifest.get("selected_year") != 2226):
            raise BaselineResolutionError("V4 demographic correction manifest invalid")
        correction_files = correction_manifest.get("files", {})
        required_correction_files = {
            "DEMOGRAPHIC_CORRECTION_DECISION.md",
            "EARTH_2226_COUNTRY_POPULATION.csv",
            "EARTH_2226_DEMOGRAPHIC_AUTHORITY.json",
            "build_demographic_correction.py",
        }
        if set(correction_files) != required_correction_files:
            raise BaselineResolutionError("V4 demographic correction file register invalid")
        correction_paths = {}
        for name, item in correction_files.items():
            path = REPO_ROOT / item["path"]
            _check(path, item["sha256"], item["bytes"])
            correction_paths[name] = path
            checked += 1
        correction = _json(correction_paths["EARTH_2226_DEMOGRAPHIC_AUTHORITY.json"])
        if (correction.get("schema") != "loom-earth-v4-demographic-authority-correction-v1" or
                correction.get("status") != "SELECTED_2226_CANON_CONSTRAINED_COUNTRY_ALLOCATION"):
            raise BaselineResolutionError("V4 demographic correction authority invalid")
        authority = correction["authority"]
        method = correction["method"]
        checks = correction["checks"]
        rows = correction["countries"]
        if (authority["wpp_authority_through_year"] != 2100 or
                authority["cohort_detail_status"] != "NOT_REPROMOTED_BY_THIS_CORRECTION" or
                method["free_parameters_added"] != 0 or
                checks["country_area_count"] != 237 or
                checks["economic_80_count"] != 80 or
                checks["demographic_only_count"] != 157 or
                len(rows) != 237 or
                len({row["iso3"] for row in rows}) != 237 or
                {row["iso3"] for row in rows} != demographic or
                any(row["population_2226"] <= 0 for row in rows)):
            raise BaselineResolutionError("V4 selected demographic endpoint failed structural checks")
        selected_total = sum(row["population_2226"] for row in rows)
        canon_total = authority["canon_earth_biological_population_2226"]
        if (abs(selected_total - canon_total) > 1e-3 or
                abs(checks["selected_population_sum"] - canon_total) > 1e-3 or
                abs(checks["canon_parent_difference"]) > 1e-3 or
                abs(canon_total - 8312538895.185726) > 1e-6):
            raise BaselineResolutionError("V4 selected demographic endpoint does not reconcile to canon Earth")
        if (sum(row["allocation_class"] == "RECOVERED_V2_1_NAMED_80_RENORMALIZED" for row in rows) != 80 or
                sum(row["allocation_class"] == "WPP_2100_SHARE_OF_RECOVERED_V2_1_ROW_RESIDUAL" for row in rows) != 157):
            raise BaselineResolutionError("V4 selected demographic allocation classes invalid")
        for source_key, hash_key in (
                ("canon_source", "canon_source_sha256"),
                ("recovered_allocator_source", "recovered_allocator_source_sha256")):
            source_path = REPO_ROOT / (authority[source_key] if source_key == "canon_source" else method[source_key])
            expected = authority[hash_key] if source_key == "canon_source" else method[hash_key]
            _check(source_path, expected)
        _check(Path(method["wpp_source"]), method["wpp_source_sha256"])
        checked += 3

        boundary = _json(Path(run["boundary_qualification"]["path"]))
        if (boundary["all_years_diagnostic"]["status"] != "REVIEW_RETAINED" or
                not boundary["existing_post_transition_qualification"]["passed"] or
                not 4.0093 < boundary["all_years_diagnostic"]["maximum_total_sector_investment_share_move_pp"] < 4.0094):
            raise BaselineResolutionError("V4 REVIEW disposition invalid")
        source = boundary["existing_post_transition_qualification"]
        _check(Path(source["source_gate_path"]), source["source_gate_sha256"])
        validation = _json(Path(run["independent_validation"]["path"]))
        report = _json(Path(run["forward_trajectory_report"]["path"]))
        if (validation["status"] != "PASS" or validation["reconstructed_nodes"] != [["TWN", "ENERGY"]] or
                not report["qualification"]["passed"] or report["qualification"]["final_year_reached"] != 2226):
            raise BaselineResolutionError("V4 numerical qualification failed")
        endpoint = Path(run["selected_outputs"]["successor_80_2226/results/countries_2226.ndjson"]["path"])
        try:
            with endpoint.open() as stream:
                endpoint_rows = [json.loads(line) for line in stream]
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise BaselineResolutionError("Cannot read V4 economic endpoint") from exc
        if (len(endpoint_rows) != 80 or {row["iso3"] for row in endpoint_rows} != economic or
                {row["year"] for row in endpoint_rows} != {2226}):
            raise BaselineResolutionError("V4 endpoint/economic coverage mismatch")
        checkpoint = Path(run["selected_outputs"]["successor_80_2226/complete_checkpoints/earth_2226.checkpoint.zip"]["path"])
        try:
            with zipfile.ZipFile(checkpoint) as archive:
                checkpoint_manifest = json.loads(archive.read("manifest.json"))
        except (OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
            raise BaselineResolutionError("Cannot inspect V4 checkpoint") from exc
        if checkpoint_manifest["runner_sha256"] != run["inherited_code_dependencies"]["v3_runner.py"]["sha256"]:
            raise BaselineResolutionError("V4 checkpoint runner hash mismatch")
        outputs = run["selected_outputs"]
        return {"designation": manifest["designation"], "model_version": run["inherited_runtime_model_version"] + "+earth-v4-seed",
                "policy": run["investment_policy_id"], "manifest": manifest_path,
                "coverage": {"economic_economies": 80, "identity_demographic_areas": 237,
                             "demographic_only_areas": 157},
                "demographic_authority": {
                    "wpp_authority_through_year": 2100,
                    "post_2100_selected_state": "EARTH_2226_CANON_CONSTRAINED_COUNTRY_ALLOCATION",
                    "post_2100_status": "SELECTED_ENDPOINT_ONLY_NO_ANNUAL_COHORT_TRAJECTORY",
                    "selected_year": 2226,
                    "earth_biological_population_2226": canon_total,
                    "selected_country_area_count": len(rows),
                    "allocation_method": method["id"],
                    "cohort_detail_status": authority["cohort_detail_status"],
                    "medical_longevity_lineage_status": authority["medical_longevity_lineage_status"],
                    "recovered_cohort_control_2226": 8442000000,
                    "recovered_control_status": "PROVISIONAL_PROPAGATION_DEPENDENT_NOT_GOVERNING"},
                "artifacts": {"annual_countries": Path(outputs["successor_80_2226/results/countries_2060_2226.ndjson"]["path"]),
                              "annual_sectors": Path(outputs["successor_80_2226/results/country_sectors_2060_2226.ndjson"]["path"]),
                              "annual_assets": Path(outputs["successor_80_2226/results/country_sector_assets_2060_2226.ndjson"]["path"]),
                              "endpoint_countries": endpoint,
                              "endpoint_sectors": Path(outputs["successor_80_2226/results/country_sectors_2226.ndjson"]["path"]),
                              "endpoint_assets": Path(outputs["successor_80_2226/results/country_sector_assets_2226.ndjson"]["path"]),
                              "complete_checkpoint_2226": checkpoint,
                              "country_evidence": Path(scope["country_evidence"]["path"]),
                              "demographic_sensitivity": Path(scope["demographic_sensitivity"]["path"]),
                              "demographic_authority_2226": correction_paths["EARTH_2226_DEMOGRAPHIC_AUTHORITY.json"],
                              "demographic_country_population_2226": correction_paths["EARTH_2226_COUNTRY_POPULATION.csv"],
                              "demographic_correction_decision": correction_paths["DEMOGRAPHIC_CORRECTION_DECISION.md"]},
                "verified_registered_files": checked}

    if manifest.get("schema") == "loom-earth-local-economic-baseline-designation-v2":
        if manifest["designation"] != pointer["active_designation"]:
            raise BaselineResolutionError("Active designation does not match manifest")
        _check(manifest_path.parent / "BASELINE_DECISION.md", pointer["active_decision_sha256"])
        run_ref = manifest["run_manifest"]
        _check(Path(run_ref["path"]), run_ref["sha256"], run_ref["bytes"])
        run = _json(Path(run_ref["path"]))
        if run["baseline_id"] != manifest["designation"]:
            raise BaselineResolutionError("Run designation mismatch")
        if run["inherited_runtime_model_version"] != "v0.6.1-d1-c1-h1-r1-alpha060-national-gfcf1":
            raise BaselineResolutionError("Runtime model identity mismatch")
        if run["investment_policy_id"] != "WDI_NATIONAL_GFCF_GDP_LATEST_2024_2025_MEDIAN_2024_FALLBACK_v1":
            raise BaselineResolutionError("Investment policy mismatch")
        count = 0
        for section in ("sources", "code", "outputs", "validation", "smoke_2061"):
            for item in run[section].values():
                _check(Path(item["path"]), item["sha256"], item["bytes"])
                count += 1
        summary = run["compact_summary"]
        _check(Path(summary["path"]), summary["sha256"], summary["bytes"])
        count += 1
        for item in manifest["compact_record"].values():
            _check(Path(item["path"]), item["sha256"], item["bytes"])
        for name, item in manifest["selected_outputs"].items():
            if run["outputs"].get(name) != item:
                raise BaselineResolutionError("Selected output is not pinned by the run manifest")
        if run["outputs"]["results/active_boundary_repairs.json"] != manifest["taiwan_evidence"]:
            raise BaselineResolutionError("Taiwan evidence is not pinned by the run manifest")
        checkpoint = Path(run["outputs"]["complete_checkpoints/earth_2226.checkpoint.zip"]["path"])
        try:
            with zipfile.ZipFile(checkpoint) as archive:
                checkpoint_manifest = json.loads(archive.read("manifest.json"))
        except (OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
            raise BaselineResolutionError("Cannot inspect completed checkpoint manifest") from exc
        if checkpoint_manifest["runner_sha256"] != run["code"]["runner_executed.py"]["sha256"]:
            raise BaselineResolutionError("Executed runner does not match checkpoint")
        report = _json(Path(run["outputs"]["trajectory_report.json"]["path"]))
        if not report["qualification"]["passed"] or report["qualification"]["final_year_reached"] != 2226:
            raise BaselineResolutionError("Repaired run is not qualified through 2226")
        artifacts = {
            "annual_countries": Path(run["outputs"]["results/countries_2060_2226.ndjson"]["path"]),
            "annual_sectors": Path(run["outputs"]["results/country_sectors_2060_2226.ndjson"]["path"]),
            "annual_assets": Path(run["outputs"]["results/country_sector_assets_2060_2226.ndjson"]["path"]),
            "endpoint_countries": Path(run["outputs"]["results/countries_2226.ndjson"]["path"]),
            "endpoint_sectors": Path(run["outputs"]["results/country_sectors_2226.ndjson"]["path"]),
            "endpoint_assets": Path(run["outputs"]["results/country_sector_assets_2226.ndjson"]["path"]),
            "complete_checkpoint_2226": Path(run["outputs"]["complete_checkpoints/earth_2226.checkpoint.zip"]["path"]),
        }
        return {"designation": manifest["designation"],
                "model_version": run["inherited_runtime_model_version"] + "+long-run-repair-v3",
                "policy": run["investment_policy_id"], "manifest": manifest_path,
                "artifacts": artifacts, "verified_registered_files": count}

    if manifest.get("schema") == "loom-earth-local-economic-baseline-designation-v1":
        if manifest["designation"] != pointer["active_designation"]:
            raise BaselineResolutionError("Active designation does not match manifest")
        if "active_decision_sha256" in pointer:
            _check(manifest_path.parent / "BASELINE_DECISION.md", pointer["active_decision_sha256"])
        source = manifest["qualified_successor_run_manifest"]
        source_path = Path(source["path"])
        _check(source_path, source["sha256"])
        run = _json(source_path)
        if run["model_version"] != manifest["model_version"] or run["policy_id"] != manifest["calibration_policy_id"]:
            raise BaselineResolutionError("Model or policy identity mismatch")
        if run["alpha_ceiling"] != manifest["alpha_ceiling"] or not run["qualification"]["passed"]:
            raise BaselineResolutionError("Alpha ceiling or qualification mismatch")
        for section in ("inputs", "code", "outputs", "evidence"):
            _registered(run[section])
        registered = {row["path"]: row["sha256"] for section in ("inputs", "code", "outputs", "evidence") for row in run[section]}
        for item in manifest["selected_outputs"].values():
            if registered.get(item["path"]) != item["sha256"]:
                raise BaselineResolutionError("Selected output is not pinned by the run manifest")
        artifacts = {name: Path(item["path"]) for name, item in manifest["selected_outputs"].items()}
        return {"designation": manifest["designation"], "model_version": run["model_version"],
                "policy": run["policy_id"], "manifest": manifest_path, "artifacts": artifacts,
                "verified_registered_files": sum(len(run[section]) for section in ("inputs", "code", "outputs", "evidence"))}

    if manifest.get("freeze_id") == pointer["active_designation"]:
        _registered(manifest["verified_file_register"])
        refs = manifest["reference_outputs"]
        registered_paths = {row["path"] for row in manifest["verified_file_register"]}
        if not set(refs.values()).issubset(registered_paths):
            raise BaselineResolutionError("Rollback output is not pinned by its file register")
        return {"designation": manifest["freeze_id"], "model_version": manifest["model_version"],
                "policy": manifest["calibration_policy_id"], "manifest": manifest_path,
                "artifacts": {"annual_countries": Path(refs["annual_countries_2060_2226"]),
                              "endpoint_countries": Path(refs["country_2226"]),
                              "complete_checkpoint_2226": Path(refs["complete_checkpoint_2226"])},
                "verified_registered_files": len(manifest["verified_file_register"])}

    raise BaselineResolutionError("Unsupported or inconsistent baseline manifest")


def load_endpoint_countries(pointer_path: Path = CURRENT_POINTER) -> list[dict]:
    """Read the verified current endpoint for a downstream data consumer."""
    endpoint = resolve(pointer_path)["artifacts"]["endpoint_countries"]
    try:
        with endpoint.open(encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BaselineResolutionError(f"Cannot load endpoint {endpoint}: {exc}") from exc
    if len(rows) != 80 or len({row["iso3"] for row in rows}) != 80 or {row["year"] for row in rows} != {2226}:
        raise BaselineResolutionError("Endpoint coverage or year mismatch")
    return rows
