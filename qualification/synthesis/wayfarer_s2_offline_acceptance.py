from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from wayfarer_s2_compare import canonical_json, compare  # noqa: E402

EXPECTED_CANDIDATE = "CAND-5719E3F3251DE6E25FDF"
EXPECTED_BASELINE = {"relational_x_m": 26.0, "launch_x_m": 21.8, "tank_x_m": 25.0}
EXPECTED_GENERATED = {"relational_x_m": 26.0, "launch_x_m": 21.75, "tank_x_m": 26.5}


def run() -> int:
    a = canonical_json(2226)
    b = canonical_json(2226)
    if a != b:
        raise RuntimeError("S2 comparison is not byte-deterministic")

    payload = compare(2226)
    if payload["S2_COMMON_MODEL_COMPARISON"] != "PASS":
        raise RuntimeError("S2 comparison did not pass")
    if payload["generated"]["candidate_id"] != EXPECTED_CANDIDATE:
        raise RuntimeError("Generated candidate drift")
    if payload["baseline"]["placement_tuple_m"] != EXPECTED_BASELINE:
        raise RuntimeError("Baseline placement drift")
    if payload["generated"]["placement_tuple_m"] != EXPECTED_GENERATED:
        raise RuntimeError("Generated placement drift")
    if payload["baseline"]["mass_kg"] != 1_158_500.0 or payload["generated"]["mass_kg"] != 1_158_500.0:
        raise RuntimeError("Mass drift")
    firewall = payload["authority_firewall"]
    if any(firewall.values()):
        raise RuntimeError("Authority firewall promotion detected")

    delta = payload["deltas_generated_minus_baseline"]
    print("WAYFARER_S2_OFFLINE_ACCEPTANCE = PASS")
    print("S2_COMMON_MODEL_COMPARISON = PASS")
    print("candidate_id =", payload["generated"]["candidate_id"])
    print("seed =", payload["seed"])
    print("baseline_relational_x_m =", payload["baseline"]["placement_tuple_m"]["relational_x_m"])
    print("baseline_launch_x_m =", payload["baseline"]["placement_tuple_m"]["launch_x_m"])
    print("baseline_tank_x_m =", payload["baseline"]["placement_tuple_m"]["tank_x_m"])
    print("generated_relational_x_m =", payload["generated"]["placement_tuple_m"]["relational_x_m"])
    print("generated_launch_x_m =", payload["generated"]["placement_tuple_m"]["launch_x_m"])
    print("generated_tank_x_m =", payload["generated"]["placement_tuple_m"]["tank_x_m"])
    print("com_x_delta_m =", delta["center_of_mass_m"][0])
    objectives = {row["objective_id"]: row for row in delta["objective_vector"]}
    print("j4_delta_m =", objectives["J4_REMASS_FEED_DISTANCE_SURROGATE"]["generated_minus_baseline"])
    print("j7_delta_m =", objectives["J7_LAUNCH_EXTRACTION_PENALTY"]["generated_minus_baseline"])
    print("flight_dynamics_authority = false")
    print("wayfarer_flight_inertia_qualified = false")
    print("canon_changed = false")
    print("production_shipclasses_changed = false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except Exception as exc:
        print("WAYFARER_S2_OFFLINE_ACCEPTANCE = FAIL")
        print(f"{type(exc).__name__}: {exc}")
        raise SystemExit(1)
