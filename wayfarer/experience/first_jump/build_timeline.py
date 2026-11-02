"""Build read-only presentation facts from the exact accepted FQ11 result.

No physical simulation, interpolation, or imported flight-calculation modules.
Each flight number carries its JSON-pointer provenance.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101/FQ11_RESULT.json"
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "timeline.json"

FIELDS = {
    "preburn_s": "preburn_actual_duration_s",
    "preburn_kg": "preburn_measured_remass_kg",
    "preburn_peak_g": "preburn_peak_g",
    "metric_s": "metric_timing_s",
    "arrival_mismatch_m_s": "forward_arrival_mismatch_m_s",
    "turn_s": "phase_evidence/rcs_reorientation/0/duration_s",
    "turn_deg": "RCS_point_turn_deg",
    "turn_hz": "rcs_control_min_hz_derived",
    "turn_remass_kg": "RCS_turn_measured_remass_kg",
    "trim_s": "trim_actual_torch_duration_s",
    "trim_kg": "trim_measured_remass_kg",
    "final_mismatch_m_s": "trim_post_velocity_error_m_s",
    "total_remass_kg": "total_remass_kg",
    "remass_remaining_kg": "remass_remaining_kg",
}
SOURCE_REL = SOURCE.relative_to(ROOT).as_posix()

def build():
    raw = SOURCE.read_bytes()
    fq = json.loads(raw)
    if fq.get("fq") != "FQ11" or fq.get("status") != "PASS":
        raise ValueError("Accepted FQ11 PASS result required")
    if sorted(c["case"] for c in fq["measured_cases"]) != ["NOMINAL", "UNDERBURN_1_PERCENT"]:
        raise ValueError("Unexpected FQ11 case set")
    cases = {}
    for i, case in enumerate(fq["measured_cases"]):
        if case["status"] != "PASS":
            raise ValueError("FQ11 case not accepted")
        entries = {}
        for label, key in FIELDS.items():
            value = case
            for part in key.split("/"):
                value = value[int(part)] if part.isdecimal() else value[part]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError("Invalid FQ11 numeric evidence: " + label)
            entries[label] = {
                "value": value,
                "source": f"{SOURCE_REL}#/measured_cases/{i}/{key}"
            }
        cases[case["case"]] = entries
    return {
        "schema": "LOOM_FIRST_JUMP_FQ11_TIMELINE_v0.1",
        "source": SOURCE_REL,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "scope": "FQ11 accepted finite lab result; playback, not flight execution",
        "geometry": "Mars approach shell (Option A placeholder; no position/distance)",
        "unavailable": ["preburn_delta_v_km_s", "certified_collapse_position", "orbital_capture"],
        "cases": cases,
    }

def main():
    OUTPUT.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} from {SOURCE_REL}")

if __name__ == "__main__":
    main()
