from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from wayfarer_s1_adapter import build_candidate, evaluate_candidate  # noqa: E402
from wayfarer_s1_solver import DEFAULT_SEED, solve  # noqa: E402

S2_VERSION = "LOOM_WAYFARER_S2_COMMON_MODEL_COMPARE_v0.1"
HAND_AUTHORED_TUPLE = {
    "relational_x_m": 26.0,
    "launch_x_m": 21.8,
    "tank_x_m": 25.0,
}
REFERENCE_DOCKED_MASS_KG = 1_158_500.0
REFERENCE_DOCKED_COM_M = (26.676650841605525, 0.0, 0.14812257229175657)
EXPECTED_GENERATED_CANDIDATE_ID = "CAND-5719E3F3251DE6E25FDF"


class WayfarerS2Error(ValueError):
    pass


def _tensor_delta(a, b):
    return tuple(tuple(float(a[i][j]) - float(b[i][j]) for j in range(3)) for i in range(3))


def _vector_delta(a, b):
    return tuple(float(a[i]) - float(b[i]) for i in range(3))


def _objective_map(evaluation) -> Dict[str, Any]:
    return {row.objective_id: row for row in evaluation.objective_vector}


def _constraint_map(evaluation) -> Dict[str, bool]:
    return {row.constraint_id: bool(row.passed) for row in evaluation.hard_constraints}


def _tank_x(candidate) -> float:
    xs = [
        float(row.centroid_m[0])
        for row in candidate.point_masses
        if row.source_id.startswith("normal_remass_tank_")
    ]
    if len(xs) != 4 or max(xs) - min(xs) > 1e-12:
        raise WayfarerS2Error("Expected four tanks at one common station")
    return sum(xs) / len(xs)


def _placement_tuple(candidate) -> Dict[str, float]:
    instances = {row.instance_id: row for row in candidate.component_instances}
    return {
        "relational_x_m": float(instances["relational_plant"].transform.translation_m[0]),
        "launch_x_m": float(instances["planetary_launch"].transform.translation_m[0]),
        "tank_x_m": _tank_x(candidate),
    }


def _layout_payload(candidate, evaluation) -> Dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "placement_tuple_m": _placement_tuple(candidate),
        "mass_kg": float(evaluation.mass_kg),
        "center_of_mass_m": list(evaluation.center_of_mass_m),
        "parallel_axis_tensor_kg_m2": [list(row) for row in evaluation.parallel_axis_tensor_kg_m2],
        "admitted_centroidal_tensor_kg_m2": [list(row) for row in evaluation.admitted_centroidal_tensor_kg_m2],
        "aggregate_partial_tensor_kg_m2": [list(row) for row in evaluation.candidate_aggregate_tensor_kg_m2],
        "unresolved_inertia_mass_fraction": float(evaluation.unresolved_inertia_mass_fraction),
        "hard_constraints": [dataclasses.asdict(row) for row in evaluation.hard_constraints],
        "objective_vector": [dataclasses.asdict(row) for row in evaluation.objective_vector],
        "flight_dynamics_authority": False,
    }


def compare(seed: int = DEFAULT_SEED) -> Dict[str, Any]:
    baseline = build_candidate(
        candidate_id="HAND_AUTHORED_WAYFARER_BASELINE",
        seed=int(seed),
        relational_x_m=HAND_AUTHORED_TUPLE["relational_x_m"],
        launch_x_m=HAND_AUTHORED_TUPLE["launch_x_m"],
        tank_x_m=HAND_AUTHORED_TUPLE["tank_x_m"],
        solver_version=S2_VERSION,
    )
    baseline_eval = evaluate_candidate(baseline)

    generated_result = solve(int(seed))
    generated = generated_result.candidate
    generated_eval = generated_result.evaluation

    if generated.candidate_id != EXPECTED_GENERATED_CANDIDATE_ID:
        raise WayfarerS2Error(
            f"Generated candidate drift: {generated.candidate_id} != {EXPECTED_GENERATED_CANDIDATE_ID}"
        )
    if abs(baseline_eval.mass_kg - REFERENCE_DOCKED_MASS_KG) > 1e-9:
        raise WayfarerS2Error("Hand-authored baseline mass no longer reproduces qualified DOCKED mass")
    if max(abs(baseline_eval.center_of_mass_m[i] - REFERENCE_DOCKED_COM_M[i]) for i in range(3)) > 1e-12:
        raise WayfarerS2Error("Hand-authored baseline CoM no longer reproduces qualified DOCKED CoM")

    baseline_obj = _objective_map(baseline_eval)
    generated_obj = _objective_map(generated_eval)
    if baseline_obj.keys() != generated_obj.keys():
        raise WayfarerS2Error("Objective-vector schema mismatch")

    baseline_constraints = _constraint_map(baseline_eval)
    generated_constraints = _constraint_map(generated_eval)
    if baseline_constraints.keys() != generated_constraints.keys():
        raise WayfarerS2Error("Hard-constraint schema mismatch")
    if not all(baseline_constraints.values()) or not all(generated_constraints.values()):
        raise WayfarerS2Error("S2 requires both compared layouts to be legal under the common admitted model")

    baseline_place = _placement_tuple(baseline)
    generated_place = _placement_tuple(generated)
    objective_deltas = []
    for key in baseline_obj:
        b = baseline_obj[key]
        g = generated_obj[key]
        objective_deltas.append(
            {
                "objective_id": key,
                "baseline_value": float(b.value),
                "generated_value": float(g.value),
                "generated_minus_baseline": float(g.value - b.value),
                "units": b.units,
                "semantics": b.semantics,
            }
        )

    payload = {
        "schema": "LOOM_2226_WAYFARER_S2_COMPARISON",
        "schema_version": "0.1",
        "status": ["ENGINEERING", "RESEARCH", "QUALIFICATION_COMPARISON", "NON_CANON", "NON_PRODUCTION"],
        "S2_COMMON_MODEL_COMPARISON": "PASS",
        "comparison_version": S2_VERSION,
        "seed": int(seed),
        "baseline": _layout_payload(baseline, baseline_eval),
        "generated": _layout_payload(generated, generated_eval),
        "deltas_generated_minus_baseline": {
            "placement_m": {k: generated_place[k] - baseline_place[k] for k in baseline_place},
            "mass_kg": float(generated_eval.mass_kg - baseline_eval.mass_kg),
            "center_of_mass_m": list(_vector_delta(generated_eval.center_of_mass_m, baseline_eval.center_of_mass_m)),
            "parallel_axis_tensor_kg_m2": [
                list(row) for row in _tensor_delta(generated_eval.parallel_axis_tensor_kg_m2, baseline_eval.parallel_axis_tensor_kg_m2)
            ],
            "admitted_centroidal_tensor_kg_m2": [
                list(row) for row in _tensor_delta(generated_eval.admitted_centroidal_tensor_kg_m2, baseline_eval.admitted_centroidal_tensor_kg_m2)
            ],
            "aggregate_partial_tensor_kg_m2": [
                list(row) for row in _tensor_delta(generated_eval.candidate_aggregate_tensor_kg_m2, baseline_eval.candidate_aggregate_tensor_kg_m2)
            ],
            "unresolved_inertia_mass_fraction": float(
                generated_eval.unresolved_inertia_mass_fraction - baseline_eval.unresolved_inertia_mass_fraction
            ),
            "objective_vector": objective_deltas,
        },
        "common_model_limitations": [
            "FULL_WAYFARER_CENTROIDAL_INERTIA_OPEN_NOT_QUALIFIED",
            "PRINCIPAL_AXES_OPEN_WITHOUT_FULL_INERTIA",
            "RADIATOR_PANEL_GEOMETRY_OPEN_NOT_COMPARED",
            "DOCKING_GEOMETRY_OPEN_NOT_COMPARED",
            "TANK_AXIAL_GEOMETRY_OPEN_NOT_COMPARED",
            "NO_GLOBAL_SCALAR_WINNER_DECLARED",
        ],
        "authority_firewall": {
            "flight_dynamics_authority": False,
            "wayfarer_flight_inertia_qualified": False,
            "canon_changed": False,
            "production_shipclasses_changed": False,
        },
    }
    return payload


def canonical_json(seed: int = DEFAULT_SEED) -> str:
    return json.dumps(compare(seed), sort_keys=True, separators=(",", ":"), allow_nan=False)


def main(argv: Iterable[str] | None = None) -> int:
    try:
        payload = compare(DEFAULT_SEED)
        print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except Exception as exc:
        print("S2_COMMON_MODEL_COMPARISON = FAIL")
        print(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
