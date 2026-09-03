#!/usr/bin/env python3
"""LOOM 2226 JPL Horizons provider probe.

Purpose
-------
Run on an internet-connected qualification host (not inside the LOOM runtime)
and acquire authoritative JPL Horizons vectors for fixed LOOM epochs. The
script does not perform navigation physics and is not a runtime ephemeris
provider. It emits a deterministic normalized JSON artifact plus SHA-256 so
provider reachability and source data can be independently qualified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://ssd.jpl.nasa.gov/api/horizons.api"
DEFAULT_EPOCH = "2226-08-22 00:00"
TARGETS = {
    "CERES": "1;",      # asteroid 1 Ceres
    "MARS": "499",
    "NEPTUNE": "899",
}


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_obj(obj) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()


def horizons_url(command: str, epoch: str) -> str:
    # One-hour interval with one-hour step yields a compact, machine-readable
    # vector table while retaining the exact request parameters in the output.
    from datetime import datetime, timedelta
    start = datetime.strptime(epoch, "%Y-%m-%d %H:%M")
    stop = start + timedelta(hours=1)
    params = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "OBJ_DATA": "'YES'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'VECTORS'",
        "CENTER": "'500@10'",
        "START_TIME": f"'{start:%Y-%m-%d %H:%M}'",
        "STOP_TIME": f"'{stop:%Y-%m-%d %H:%M}'",
        "STEP_SIZE": "'1 h'",
        "OUT_UNITS": "'KM-S'",
        "REF_PLANE": "'ECLIPTIC'",
        "REF_SYSTEM": "'ICRF'",
        "VEC_TABLE": "'2'",
        "CSV_FORMAT": "'YES'",
        "VEC_CORR": "'NONE'",
    }
    return API + "?" + urllib.parse.urlencode(params)


def fetch_text(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "LOOM-2226-GitHub-Qualification/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8")


def parse_horizons_result(payload_text: str) -> dict:
    payload = json.loads(payload_text)
    result = payload.get("result")
    if not isinstance(result, str):
        raise RuntimeError("Horizons response missing textual result")
    if "$$SOE" not in result or "$$EOE" not in result:
        raise RuntimeError("Horizons response contains no vector table")
    body = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0].strip()
    rows = list(csv.reader(io.StringIO(body)))
    rows = [[cell.strip() for cell in row] for row in rows if row]
    if not rows:
        raise RuntimeError("Horizons vector table is empty")

    # VEC_TABLE=2 CSV columns begin with JD/calendar then X,Y,Z,VX,VY,VZ.
    row = rows[0]
    if len(row) < 8:
        raise RuntimeError(f"Unexpected Horizons vector row width: {len(row)}")
    try:
        x, y, z, vx, vy, vz = map(float, row[2:8])
    except ValueError as exc:
        raise RuntimeError(f"Unable to parse Horizons vector row: {row}") from exc

    return {
        "provider": "JPL_HORIZONS",
        "provider_signature": payload.get("signature", {}),
        "calendar": row[1],
        "julian_date": row[0],
        "position_km": [x, y, z],
        "velocity_km_s": [vx, vy, vz],
    }


def acquire(target: str, command: str, epoch: str) -> dict:
    url = horizons_url(command, epoch)
    parsed = parse_horizons_result(fetch_text(url))
    parsed.update({
        "target": target,
        "command": command,
        "requested_epoch": epoch,
        "center": "500@10",
        "frame": "ICRF/ECLIPTIC",
        "units": "KM-S",
        "request_url": url,
    })
    parsed["record_sha256"] = sha256_obj({k: v for k, v in parsed.items() if k != "record_sha256"})
    return parsed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epoch", default=DEFAULT_EPOCH)
    ap.add_argument("--output", default="artifacts/horizons_provider_probe.json")
    args = ap.parse_args()

    records = [acquire(name, command, args.epoch) for name, command in TARGETS.items()]
    artifact = {
        "schema": "LOOM_HORIZONS_PROVIDER_PROBE_V1",
        "epoch": args.epoch,
        "records": records,
    }
    artifact["artifact_sha256"] = sha256_obj({k: v for k, v in artifact.items() if k != "artifact_sha256"})

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))
    print("ARTIFACT:", out)
    print("SHA256:", artifact["artifact_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
