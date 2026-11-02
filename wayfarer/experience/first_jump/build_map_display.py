"""OFFLINE display-only compiler. No Navigator import, no flight integration.

FQ11's original EA/MA source-epoch ephemeris is propagated with its
already-used Sun-only planetary_state function. Result is fixed screen
coordinates for a read-only Pixel map. Never used as flight authority.
Requires numpy/scipy only when generating this committed file.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FQ11_INPUT = ROOT / "wayfarer/lab/flight_qual/fq11_calc_metric_energy_b_20261101/FQ11_INPUT.json"
RESULT = ROOT / "wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101/FQ11_RESULT.json"
TARGET = HERE / "map_display.json"
sys.path.insert(0, str(ROOT / "wayfarer/lab/flight"))
from metric_arrival_v1 import planetary_state, AU_KM  # existing FQ11 model; NOT Navigator

def build():
    source_bytes = FQ11_INPUT.read_bytes()
    data = json.loads(source_bytes)
    if data["epoch_utc"] != "2226-08-29T05:00:00Z" or data["bodies"].keys() != {"EA", "MA"}:
        raise ValueError("FQ11 solar display source epoch/planet set changed")
    actual = json.loads(RESULT.read_text())
    if actual["fq"] != "FQ11" or actual["status"] != "PASS":
        raise ValueError("Accepted FQ11 required")
    # No new flight duration. Only FQ11's measured phase boundaries.
    cases = {}
    for case in actual["measured_cases"]:
        phases = case["phase_evidence"]
        coast = sum(p["duration_s"] for p in phases["preburn"] if p["kind"] == "coast")
        elapsed = [
            case["preburn_actual_duration_s"] + coast,
            case["metric_timing_s"],
            phases["rcs_reorientation"][0]["duration_s"],
            case["trim_actual_torch_duration_s"],
        ]
        cases[case["case"]] = {
            "phase_durations_s": {
                k: v for k, v in zip(("preburn", "metric", "turn", "trim"), elapsed)
            },
            "source": "FQ11_RESULT.json#/measured_cases/" +
                      str(actual["measured_cases"].index(case)),
        }
    end = max(sum(x["phase_durations_s"].values()) for x in cases.values())
    # Precompiled, 30 s sampling. No FQ11 spacecraft coordinates are implied.
    sample_times = sorted(set([0.0, end] + [float(x) for x in range(0, math.ceil(end), 30)]))
    screen_scale_px_per_au = 135.0   # graphical mapping only
    projected = []
    for seconds in sample_times:
        row = {"elapsed_s": round(seconds, 4)}
        for key in ("EA", "MA"):
            p, _ = planetary_state(data["bodies"][key], float(data["sun_gm_km3_s2"]), seconds)
            row[key] = [round(float(p[0] / AU_KM * screen_scale_px_per_au), 7),
                        round(float(p[1] / AU_KM * screen_scale_px_per_au), 7)]
        projected.append(row)
    # Orbit guides are propagated FQ11 snapshot context, NOT guessed circles.
    traces = {}
    for key, period_days in (("EA", 366), ("MA", 690)):
        coords = []
        for i in range(121):
            p, _ = planetary_state(data["bodies"][key], float(data["sun_gm_km3_s2"]),
                                   period_days * 86400.0 * i / 120)
            coords.append([round(float(p[0] / AU_KM * screen_scale_px_per_au), 5),
                           round(float(p[1] / AU_KM * screen_scale_px_per_au), 5)])
        traces[key] = coords
    return {
        "schema": "FIRST_JUMP_SOLAR_DISPLAY_v0.3",
        "role": "READ_ONLY_DISPLAY_CONTEXT_NOT_FLIGHT_OR_CAPTURE_POSITION",
        "epoch_utc": data["epoch_utc"],
        "source_input": FQ11_INPUT.relative_to(ROOT).as_posix(),
        "source_input_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "source_fq11_result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "ephemeris_method": "FQ11 metric_arrival_v1.planetary_state Sun-only propagation; no Navigator core",
        "projection": "Sun-centered, ecliptic XY, 135 display px/AU; no ship path",
        "body_labels": {"EA": "Earth", "MA": "Mars"},
        "cases": cases,
        "samples": projected,
        "orbit_context": traces,
        "ship_locations": {"preburn": "EA", "metric_departure": "EA",
                           "metric_arrival": "MA", "turn": "MA", "trim": "MA"},
        "metric_path": None,
        "mars_approach_range": None
    }

def main():
    TARGET.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n")
    print("Map display written from FQ11 input snapshot:", TARGET)

if __name__ == "__main__":
    main()
