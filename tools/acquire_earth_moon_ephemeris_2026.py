#!/usr/bin/env python3
"""Acquire a bounded Earth-centered Moon vector ephemeris from JPL Horizons.

This is an explicit external-data acquisition tool for HUD qualification. It
writes a local JSON cache and does not mutate LOOM canonical SQLite authority.
The cache remains source-labelled JPL_HORIZONS_DIRECT and is consumed read-only.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import argparse
import csv
import io
import json
import os

API = "https://ssd.jpl.nasa.gov/api/horizons.api"
DEFAULT_START = "2026-09-10"
DEFAULT_STOP = "2026-10-10"
DEFAULT_STEP = "1 h"
DEFAULT_RELATIVE = Path("qualification/earth_moon_2026_hourly.json")


def _default_output() -> Path:
    root = Path(os.environ.get("LOOM_DATA_ROOT") or "/storage/emulated/0/Documents/LOOM/data")
    return root / DEFAULT_RELATIVE


def _request_url(start: str, stop: str, step: str) -> str:
    params = {
        "format": "json",
        "COMMAND": "'301'",          # Moon
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'VECTORS'",
        "CENTER": "'500@399'",      # Earth center
        "START_TIME": f"'{start}'",
        "STOP_TIME": f"'{stop}'",
        "STEP_SIZE": f"'{step}'",
        "REF_PLANE": "'ECLIPTIC'",
        "REF_SYSTEM": "'J2000'",
        "VEC_TABLE": "'2'",
        "VEC_CORR": "'NONE'",
        "OUT_UNITS": "'KM-S'",
        "CSV_FORMAT": "'YES'",
    }
    return API + "?" + urlencode(params)


def _iso_from_horizons_calendar(text: str) -> str:
    # Example: A.D. 2026-Sep-10 00:00:00.0000
    value = text.strip().replace("A.D. ", "")
    dt = datetime.strptime(value.split(".")[0], "%Y-%b-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def parse_horizons_result(result: str) -> list[dict]:
    if "$$SOE" not in result or "$$EOE" not in result:
        raise RuntimeError("Horizons response did not contain an ephemeris block")
    block = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    anchors = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("!"):
            continue
        row = next(csv.reader(io.StringIO(line), skipinitialspace=True))
        # VEC_TABLE=2 CSV: JD, calendar, X,Y,Z,VX,VY,VZ,...
        if len(row) < 8:
            continue
        try:
            position = [float(row[2]), float(row[3]), float(row[4])]
            velocity = [float(row[5]), float(row[6]), float(row[7])]
        except ValueError:
            continue
        anchors.append({
            "epoch_utc": _iso_from_horizons_calendar(row[1]),
            "position_km": position,
            "velocity_km_s": velocity,
        })
    if len(anchors) < 2:
        raise RuntimeError("Horizons response yielded fewer than two usable vector anchors")
    return anchors


def acquire(output: Path, *, start: str, stop: str, step: str) -> Path:
    url = _request_url(start, stop, step)
    print("SOURCE: JPL Horizons API")
    print("TARGET: Moon (301)")
    print("CENTER: Earth (399)")
    print("FRAME: J2000 / ECLIPTIC")
    print(f"WINDOW: {start} -> {stop} @ {step}")
    with urlopen(url, timeout=90) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(f"Horizons API error: {payload['error']}")
    anchors = parse_horizons_result(str(payload.get("result") or ""))
    document = {
        "contract": "LOOM_EXTERNAL_EPHEMERIS_CACHE_V1",
        "status": "EXTERNAL_SOURCE_CACHE",
        "source": "JPL_HORIZONS_DIRECT",
        "target": {"entity_id": "LU", "horizons_command": "301", "name": "Moon"},
        "center": {"entity_id": "EA", "horizons_center": "500@399", "name": "Earth"},
        "reference_frame": "J2000/ECLIPTIC",
        "corrections": "NONE_GEOMETRIC",
        "units": "KM-S",
        "requested_step": step,
        "requested_start": start,
        "requested_stop": stop,
        "anchor_count": len(anchors),
        "anchors": anchors,
        "authority_note": "Direct external ephemeris samples; cache is not LOOM canonical SQLite authority.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"ANCHORS: {len(anchors)}")
    print(f"OUTPUT: {output}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=_default_output())
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--stop", default=DEFAULT_STOP)
    parser.add_argument("--step", default=DEFAULT_STEP)
    args = parser.parse_args()
    acquire(args.output.expanduser().resolve(), start=args.start, stop=args.stop, step=args.step)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
