from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path
from typing import Any, Dict, Mapping

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from physical_design_core import DesignVariable  # noqa: E402
from physical_design_search import DeterministicGridSearch, SearchResult  # noqa: E402
from wayfarer_s1_adapter import build_candidate, evaluate_candidate  # noqa: E402

SOLVER_VERSION = "LOOM_WAYFARER_S1_DETERMINISTIC_GRID_v0.1"
DEFAULT_SEED = 2226

# The relational equivalent body is 16 m long inside x=18..34, so its center
# has one admitted value in S1 v0.1. Launch and tank station are real choices.
S1_VARIABLES = (
    DesignVariable("relational_x_m", 26.0, 26.0, 1.0, "m"),
    DesignVariable("launch_x_m", 21.25, 22.75, 0.25, "m"),
    DesignVariable("tank_x_m", 18.0, 32.0, 0.5, "m"),
)


def _builder(candidate_id: str, seed: int, values: Mapping[str, float]):
    return build_candidate(
        candidate_id=candidate_id,
        seed=seed,
        relational_x_m=values["relational_x_m"],
        launch_x_m=values["launch_x_m"],
        tank_x_m=values["tank_x_m"],
        solver_version=SOLVER_VERSION,
    )


def make_solver() -> DeterministicGridSearch:
    return DeterministicGridSearch(
        solver_version=SOLVER_VERSION,
        variables=S1_VARIABLES,
        candidate_builder=_builder,
        evaluator=evaluate_candidate,
    )


def solve(seed: int = DEFAULT_SEED) -> SearchResult:
    return make_solver().solve(int(seed))


def _geometry_dict(geometry: Any) -> Dict[str, Any]:
    if hasattr(geometry, "length_m") and hasattr(geometry, "diameter_m"):
        return {
            "type": "CYLINDER_X",
            "length_m": float(geometry.length_m),
            "diameter_m": float(geometry.diameter_m),
        }
    if hasattr(geometry, "x_m") and hasattr(geometry, "y_m") and hasattr(geometry, "z_m"):
        return {
            "type": "BOX",
            "x_m": float(geometry.x_m),
            "y_m": float(geometry.y_m),
            "z_m": float(geometry.z_m),
        }
    raise TypeError(f"Unsupported geometry {type(geometry).__name__}")


def result_payload(result: SearchResult) -> Dict[str, Any]:
    candidate = result.candidate
    evaluation = result.evaluation
    type_map = {row.type_id: row for row in candidate.component_types}
    admitted_bodies = []
    component_transforms = []
    for instance in candidate.component_instances:
        component_transforms.append(
            {
                "instance_id": instance.instance_id,
                "component_type_id": instance.component_type_id,
                "active": bool(instance.active),
                "translation_m": list(instance.transform.translation_m),
                "quaternion_wxyz": list(instance.transform.quaternion_wxyz),
            }
        )
        ctype = type_map[instance.component_type_id]
        if ctype.admitted_geometry is not None:
            admitted_bodies.append(
                {
                    "instance_id": instance.instance_id,
                    "mass_kg": float(ctype.mass_kg),
                    "geometry": _geometry_dict(ctype.admitted_geometry),
                    "authority_status": ctype.authority_status,
                    "provenance": ctype.provenance,
                }
            )

    tank_points = [
        {
            "source_id": point.source_id,
            "mass_kg": float(point.mass_kg),
            "centroid_m": list(point.centroid_m),
            "authority_status": point.authority_status,
            "provenance": point.provenance,
        }
        for point in candidate.point_masses
        if point.source_id.startswith("normal_remass_tank_")
    ]

    return {
        "schema": "LOOM_2226_WAYFARER_S1_CANDIDATE",
        "schema_version": "0.1",
        "status": ["ENGINEERING", "RESEARCH", "QUALIFICATION_CANDIDATE", "NON_CANON", "NON_PRODUCTION"],
        "PROCEDURAL_LAYOUT_FEASIBILITY": "PASS",
        "candidate_id": candidate.candidate_id,
        "seed": candidate.seed,
        "solver_version": result.solver_version,
        "selector": result.selector,
        "search": {
            "examined_count": result.examined_count,
            "legal_count": result.legal_count,
            "rejected_count": result.rejected_count,
            "variables": [dataclasses.asdict(v) for v in S1_VARIABLES],
        },
        "component_transforms": component_transforms,
        "component_active_states": dict(candidate.active_states),
        "store_decomposition_kg": dict(candidate.store_decomposition_kg),
        "admitted_equivalent_bodies": admitted_bodies,
        "abstract_placement_keep_out_objects": [dataclasses.asdict(row) for row in candidate.keep_outs],
        "tank_point_mass_decomposition": tank_points,
        "mass_kg": float(evaluation.mass_kg),
        "center_of_mass_m": list(evaluation.center_of_mass_m),
        "parallel_axis_tensor_kg_m2": [list(row) for row in evaluation.parallel_axis_tensor_kg_m2],
        "admitted_centroidal_tensor_kg_m2": [list(row) for row in evaluation.admitted_centroidal_tensor_kg_m2],
        "candidate_aggregate_tensor_kg_m2": [list(row) for row in evaluation.candidate_aggregate_tensor_kg_m2],
        "unresolved_inertia_mass_fraction": float(evaluation.unresolved_inertia_mass_fraction),
        "hard_constraints": [dataclasses.asdict(row) for row in evaluation.hard_constraints],
        "objective_vector": [dataclasses.asdict(row) for row in evaluation.objective_vector],
        "provenance_map": dict(candidate.provenance_map),
        "input_hashes": dict(candidate.input_hashes),
        "flight_dynamics_authority": False,
        "wayfarer_flight_inertia_qualified": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
        "surrogate_full_inertia_used": False,
    }


def canonical_json(result: SearchResult) -> str:
    return json.dumps(result_payload(result), sort_keys=True, separators=(",", ":"), allow_nan=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="LOOM Wayfarer S1 deterministic procedural-layout feasibility solver")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)
    try:
        result = solve(args.seed)
        print(json.dumps(result_payload(result), indent=2, sort_keys=True, allow_nan=False))
        return 0
    except Exception as exc:
        print("PROCEDURAL_LAYOUT_FEASIBILITY = FAIL")
        print(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
