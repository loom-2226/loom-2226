"""Run all three CIVPROP Method Lab prototype engines against one frozen bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .contracts import canonical_json, load_bundle, validate_result
from .prototypes.actor_event import ActorEventEngine
from .prototypes.dynamic_recursive import DynamicRecursiveEngine
from .prototypes.system_dynamics import SystemDynamicsEngine


ENGINE_TYPES = (
    DynamicRecursiveEngine,
    SystemDynamicsEngine,
    ActorEventEngine,
)


def _final_location_summary(result, end_year):
    rows = {}
    for state in result.annual_states:
        if state.year != end_year:
            continue
        rows[state.location_id] = {
            "biological_population": state.biological_population,
            "transient_population": state.transient_population,
            "workforce": state.workforce,
            "capital": state.capital,
            "capacities": {
                "power": state.capacities.power,
                "resource": state.capacities.resource,
                "industrial": state.capacities.industrial,
                "habitat": state.capacities.habitat,
                "shipyard": state.capacities.shipyard,
                "transport": state.capacities.transport,
            },
        }
    return dict(sorted(rows.items()))


def summarize_result(result, end_year):
    payload = canonical_json(result).encode()
    facilities_by_location = {}
    facilities_by_type = {}
    for facility in result.facilities:
        facilities_by_location[facility.location_id] = (
            facilities_by_location.get(facility.location_id, 0) + 1
        )
        facilities_by_type[facility.project_archetype_id] = (
            facilities_by_type.get(facility.project_archetype_id, 0) + 1
        )
    return {
        "result_sha256": hashlib.sha256(payload).hexdigest(),
        "facility_count": len(result.facilities),
        "decision_count": len(result.decisions),
        "event_count": len(result.events),
        "flow_count": len(result.flows),
        "facilities_by_location": dict(sorted(facilities_by_location.items())),
        "facilities_by_type": dict(sorted(facilities_by_type.items())),
        "final_locations": _final_location_summary(result, end_year),
    }


def run_all(directory: Path, seed: int = 42):
    bundle = load_bundle(Path(directory))
    engines = {}
    for engine_type in ENGINE_TYPES:
        engine = engine_type()
        result = engine.run(bundle, seed)
        validate_result(result, bundle)
        engines[engine.engine_id] = summarize_result(
            result,
            bundle.scenario.end_year,
        )
    return {
        "format": "CIVPROP_METHOD_LAB_PROTOTYPE_SUMMARY_V1",
        "input_bundle_sha256": bundle.bundle_sha256,
        "seed": seed,
        "horizon": {
            "start_year": bundle.scenario.start_year,
            "end_year": bundle.scenario.end_year,
        },
        "engines": dict(sorted(engines.items())),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    directory = Path(__file__).resolve().parent
    summary = run_all(directory, args.seed)
    text = json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
