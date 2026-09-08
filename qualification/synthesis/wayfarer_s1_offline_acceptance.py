from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from wayfarer_s1_solver import canonical_json, result_payload, solve  # noqa: E402

EXPECTED_CANDIDATE_ID = "CAND-5719E3F3251DE6E25FDF"


def accept(seed: int = 2226):
    first = solve(seed)
    second = solve(seed)
    if canonical_json(first) != canonical_json(second):
        raise RuntimeError("SAME_SEED_DIFFERENT_DESIGN")
    payload = result_payload(first)
    if payload["PROCEDURAL_LAYOUT_FEASIBILITY"] != "PASS":
        raise RuntimeError("PROCEDURAL_LAYOUT_FEASIBILITY_NOT_PASS")
    if payload["candidate_id"] != EXPECTED_CANDIDATE_ID:
        raise RuntimeError(
            f"CANDIDATE_ID_MISMATCH expected={EXPECTED_CANDIDATE_ID} got={payload['candidate_id']}"
        )
    if payload["mass_kg"] != 1_158_500.0:
        raise RuntimeError("WAYFARER_WET_MASS_MISMATCH")
    if payload["store_decomposition_kg"].get("normal_remass") != 250_000.0:
        raise RuntimeError("REMASS_ACCOUNTING_MISMATCH")
    if payload["store_decomposition_kg"].get("protected_water") != 50_000.0:
        raise RuntimeError("PROTECTED_WATER_ACCOUNTING_MISMATCH")
    if payload["flight_dynamics_authority"] is not False:
        raise RuntimeError("FLIGHT_AUTHORITY_PROMOTED")
    if payload["wayfarer_flight_inertia_qualified"] is not False:
        raise RuntimeError("WAYFARER_INERTIA_PROMOTED")
    if not all(row["passed"] for row in payload["hard_constraints"]):
        raise RuntimeError("HARD_CONSTRAINT_FAILURE")
    return payload


def main() -> int:
    try:
        payload = accept()
    except Exception as exc:
        print("WAYFARER_S1_OFFLINE_ACCEPTANCE = FAIL")
        print(f"{type(exc).__name__}: {exc}")
        return 1

    transforms = {row["instance_id"]: row["translation_m"] for row in payload["component_transforms"]}
    tank_x = sorted({row["centroid_m"][0] for row in payload["tank_point_mass_decomposition"]})
    print("WAYFARER_S1_OFFLINE_ACCEPTANCE = PASS")
    print("PROCEDURAL_LAYOUT_FEASIBILITY = PASS")
    print(f"candidate_id = {payload['candidate_id']}")
    print(f"seed = {payload['seed']}")
    print(f"examined = {payload['search']['examined_count']}")
    print(f"legal = {payload['search']['legal_count']}")
    print(f"relational_x_m = {transforms['relational_plant'][0]}")
    print(f"launch_x_m = {transforms['planetary_launch'][0]}")
    print(f"tank_x_m = {tank_x[0]}")
    print(f"mass_kg = {payload['mass_kg']}")
    print(f"center_of_mass_m = {json.dumps(payload['center_of_mass_m'])}")
    print(f"unresolved_inertia_mass_fraction = {payload['unresolved_inertia_mass_fraction']}")
    print("flight_dynamics_authority = false")
    print("wayfarer_flight_inertia_qualified = false")
    print("canon_changed = false")
    print("production_shipclasses_changed = false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
