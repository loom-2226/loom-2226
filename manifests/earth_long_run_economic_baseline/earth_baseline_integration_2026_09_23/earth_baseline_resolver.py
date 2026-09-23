"""Resolve the local Earth long-run economic baseline, failing closed on stale files.

This module reads the current-baseline pointer; it never selects a versioned run
on its own. Historical designations remain resolvable for explicit rollback.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


CURRENT_POINTER = Path(__file__).resolve().parents[1] / "EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json"


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
