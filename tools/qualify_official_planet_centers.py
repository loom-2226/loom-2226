#!/usr/bin/env python3
"""Qualify official JPL/NAIF physical planet-center sources for LOOM."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError
from src.loom_spice_ephemeris_adapter import SpiceEphemerisAdapter, registry_from_manifest


DEFAULT_MANIFEST = ROOT / "manifests/solar/OFFICIAL_PLANET_CENTER_KERNELS_V1.json"
DEFAULT_OUTPUT = ROOT / "docs/qualification/OFFICIAL_PLANET_CENTERS_V1_evidence.json"
DEFAULT_ASSET_ROOT = Path("/home/ubuntu/loom_solar_assets")
EPOCHS = ("2026-01-01T00:00:00Z", "2226-01-01T00:00:00Z", "2250-01-01T00:00:00Z")
CENTERS = {
    "MARS": {"naif_id": 499, "source_id": "JPL_MAR099", "barycenter": "MARS_SYSTEM_BARYCENTER", "barycenter_naif_id": 4},
    "SATURN": {"naif_id": 699, "source_id": "JPL_SAT441", "barycenter": "SATURN_SYSTEM_BARYCENTER", "barycenter_naif_id": 6},
    "URANUS": {"naif_id": 799, "source_id": "JPL_URA184_PART_3", "barycenter": "URANUS_SYSTEM_BARYCENTER", "barycenter_naif_id": 7},
    "NEPTUNE": {"naif_id": 899, "source_id": "JPL_NEP097", "barycenter": "NEPTUNE_SYSTEM_BARYCENTER", "barycenter_naif_id": 8},
}


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_epoch(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def segment_inventory(spice: Any, path: Path, target: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    handle = spice.dafopr(str(path))
    try:
        spice.dafbfs(handle)
        while spice.daffna():
            doubles, integers = spice.dafus(spice.dafgs(), 2, 6)
            if int(integers[0]) != target:
                continue
            records.append({
                "target_naif_id": int(integers[0]),
                "center_naif_id": int(integers[1]),
                "frame_id": int(integers[2]),
                "spk_data_type": int(integers[3]),
                "coverage_et": [float(doubles[0]), float(doubles[1])],
                "coverage_utc": [
                    spice.et2utc(float(doubles[0]), "ISOC", 6) + "Z",
                    spice.et2utc(float(doubles[1]), "ISOC", 6) + "Z",
                ],
            })
    finally:
        spice.dafcls(handle)
    return sorted(records, key=lambda record: record["coverage_et"])


def norm(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values))


def qualify(manifest_path: Path, asset_root: Path) -> dict[str, Any]:
    import spiceypy as spice

    spice.kclear()
    manifest = json.loads(manifest_path.read_text())
    assets = {record["asset_id"]: record for record in manifest["assets"]}
    asset_results: dict[str, Any] = {}
    for asset_id, record in assets.items():
        path = asset_root / record["local_path"]
        actual_size = path.stat().st_size
        actual_hash = sha256(path)
        if actual_size != record["byte_count"] or actual_hash != record["sha256"]:
            raise RuntimeError(f"asset integrity mismatch: {asset_id}")
        asset_results[asset_id] = {
            "path": str(path),
            "byte_count": actual_size,
            "sha256": actual_hash,
            "source_url": record["source_url"],
            "acquired_at": record["acquired_at"],
        }

    lsk_path = asset_root / assets["NAIF0012_LSK"]["local_path"]
    spice.furnsh(str(lsk_path))
    inventory_results: dict[str, Any] = {}
    for record in manifest["selected_kernel_inventory"]:
        asset_id = record["asset_id"]
        target = int(record["selected_target"]["naif_id"])
        path = asset_root / assets[asset_id]["local_path"]
        actual_targets = list(spice.spkobj(str(path)))
        if actual_targets != record["spk_target_ids"]:
            raise RuntimeError(f"SPK target inventory mismatch: {asset_id}")
        window = spice.spkcov(str(path), target)
        if spice.wncard(window) != 1:
            raise RuntimeError(f"selected target coverage is not one continuous interval: {asset_id}")
        start, stop = spice.wnfetd(window, 0)
        coverage_utc = [spice.et2utc(start, "ISOC", 6) + "Z", spice.et2utc(stop, "ISOC", 6) + "Z"]
        expected = record["selected_target"]
        if [start, stop] != expected["coverage_et"] or coverage_utc != expected["coverage_utc"]:
            raise RuntimeError(f"SPK coverage mismatch: {asset_id}")
        segments = segment_inventory(spice, path, target)
        if {segment["center_naif_id"] for segment in segments} != {expected["center_naif_id"]}:
            raise RuntimeError(f"SPK center mismatch: {asset_id}")
        if {segment["frame_id"] for segment in segments} != {expected["segment_frame_id"]}:
            raise RuntimeError(f"SPK segment frame mismatch: {asset_id}")
        inventory_results[asset_id] = {
            "spk_target_ids": actual_targets,
            "selected_target_naif_id": target,
            "selected_target_center_naif_id": expected["center_naif_id"],
            "coverage_et": [start, stop],
            "coverage_utc": coverage_utc,
            "segments": segments,
        }
    spice.kclear()

    registry = registry_from_manifest(manifest_path, asset_root)
    adapter = SpiceEphemerisAdapter(registry)
    service = adapter.service()
    cases: list[dict[str, Any]] = []
    boundaries: dict[str, Any] = {}
    for body, expected in CENTERS.items():
        identifier = registry.body_identifier(body)
        barycenter_identifier = registry.body_identifier(expected["barycenter"])
        if int(identifier.identifier_value) != expected["naif_id"]:
            raise RuntimeError(f"physical-center identity mismatch: {body}")
        if int(barycenter_identifier.identifier_value) != expected["barycenter_naif_id"]:
            raise RuntimeError(f"barycenter identity mismatch: {body}")
        for epoch in EPOCHS:
            state = service.resolve(body, epoch)
            replay = service.resolve(body, epoch)
            barycenter = service.resolve(expected["barycenter"], epoch)
            if state != replay:
                raise RuntimeError(f"non-deterministic replay: {body} {epoch}")
            provenance = state.provenance
            required = {
                "ephemeris_source_id": expected["source_id"],
                "naif_identifier": str(expected["naif_id"]),
                "spice_frame": "ECLIPJ2000",
                "aberration_correction": "NONE",
                "request_time_scale": "UTC",
                "time_scale_internal": "SPICE ET/TDB",
                "units": "km,km/s",
            }
            if any(provenance.get(key) != value for key, value in required.items()):
                raise RuntimeError(f"state contract mismatch: {body} {epoch}")
            if state.reference_frame != CANONICAL_FRAME or not state.navigation_grade:
                raise RuntimeError(f"typed authority mismatch: {body} {epoch}")
            if barycenter.provenance["naif_identifier"] != str(expected["barycenter_naif_id"]):
                raise RuntimeError(f"barycenter substitution: {body} {epoch}")
            position_delta = [
                state.position_km[index] - barycenter.position_km[index]
                for index in range(3)
            ]
            velocity_delta = [
                state.velocity_km_s[index] - barycenter.velocity_km_s[index]
                for index in range(3)
            ]
            position_separation = norm(position_delta)
            if position_separation <= 1e-8:
                raise RuntimeError(f"center not measurably distinct from barycenter: {body} {epoch}")
            cases.append({
                "body_id": body,
                "naif_id": expected["naif_id"],
                "barycenter_body_id": expected["barycenter"],
                "barycenter_naif_id": expected["barycenter_naif_id"],
                "epoch_utc": epoch,
                "ephemeris_source_id": expected["source_id"],
                "position_km": list(state.position_km),
                "velocity_km_s": list(state.velocity_km_s),
                "center_barycenter_position_separation_km": position_separation,
                "center_barycenter_velocity_separation_km_s": norm(velocity_delta),
                "deterministic_replay": "PASS",
                "contract": "PASS",
            })

        source, coverage = registry.source_for(body, EPOCHS[-1])
        boundary_states = []
        for boundary in (coverage.valid_from, coverage.valid_until):
            state = service.resolve(body, boundary)
            boundary_states.append({
                "epoch_utc": state.epoch_utc,
                "ephemeris_source_id": state.provenance["ephemeris_source_id"],
                "result": "PASS",
            })
        fail_closed = []
        for outside in (
            iso(parse_epoch(coverage.valid_from) - timedelta(microseconds=1)),
            iso(parse_epoch(coverage.valid_until) + timedelta(microseconds=1)),
        ):
            try:
                service.resolve(body, outside)
            except CelestialStateError:
                fail_closed.append({"epoch_utc": outside, "result": "PASS_FAIL_CLOSED"})
            else:
                raise RuntimeError(f"out-of-coverage request did not fail closed: {body} {outside}")
        boundaries[body] = {
            "source_id": source.ephemeris_source_id,
            "valid_from": coverage.valid_from,
            "valid_until": coverage.valid_until,
            "exact_boundaries": boundary_states,
            "outside_boundaries": fail_closed,
        }

    spice.kclear()
    return {
        "qualification": "OFFICIAL_PLANET_CENTERS_V1",
        "result": "PASS",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "manifest": str(manifest_path.relative_to(ROOT)),
        "manifest_sha256": sha256(manifest_path),
        "classification": "OFFICIAL JPL/NAIF INPUT / QUALIFIED SUPPLEMENTARY",
        "does_not_establish": [
            "Jupiter 599 authority",
            "Pluto 999 authority",
            "derived ephemeris authority",
            "barycenter substitution for a physical center",
        ],
        "assets": asset_results,
        "kernel_inventory": inventory_results,
        "epochs": list(EPOCHS),
        "cases": cases,
        "coverage_boundaries": boundaries,
        "contract": manifest["authority_policy"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ASSET_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    evidence = qualify(args.manifest.resolve(), args.asset_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(f"{evidence['qualification']}: {evidence['result']}")
    print(f"evidence: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
