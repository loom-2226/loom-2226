#!/usr/bin/env python3
"""Locked executable baseline for CIVPROP Engine V1.

Runner V1.5 keeps the selected HYBRID_V1 architecture and the closed GAP-001
through GAP-004 boundaries, then adds GAP-005 Project Economics V1 with versioned
physical/economic units, uncertainty, scale behavior and technology-year resolution.
Later gaps remain explicit rather than being silently invented here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

_THIS_FILE = Path(__file__).resolve()
_CIVPROP_DIR = _THIS_FILE.parent
_REPO_ROOT = _CIVPROP_DIR.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from engineering.civprop.contracts.infrastructure_v1 import (
    PARAMETER_STATUS_METHOD_LAB,
    load_infrastructure_catalog,
)
from engineering.civprop.method_lab.contracts import (
    canonical_json,
    load_bundle,
    validate_result,
)
from engineering.civprop.method_lab.prototypes.hybrid_v1 import HybridEngineV1
from engineering.civprop.method_lab.prototypes.common import (
    project_capital_unit,
    resolved_project,
)


OUTPUT_FORMAT = "CIVPROP_ENGINE_V1_OUTPUT"
OUTPUT_CONTRACT_VERSION = "1.5.0"
RUNNER_ID = "CIVPROP_ENGINE_V1_RUNNER"
RUNNER_VERSION = "1.5.0"
DEFAULT_PARAMETER_SET_ID = "METHOD_LAB_SYNTHETIC_V1"
PROJECT_ECONOMICS_PARAMETER_PATH = (
    _CIVPROP_DIR / "contracts" / "project_economics_v1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _module_sha256(module) -> str:
    return _sha256(Path(module.__file__).resolve())


def default_paths() -> tuple[Path, Path]:
    return (
        _CIVPROP_DIR / "compiled_inputs" / "earth_luna_2026_2036_v1",
        _CIVPROP_DIR / "contracts" / "infrastructure_archetypes_v1.json",
    )


def _validate_infrastructure_crosswalk(bundle, catalog) -> list[str]:
    """Fail closed if runtime project semantics drift from governed contracts."""
    archetype_by_id = {a.archetype_id: a for a in catalog.archetypes}
    parameterized: list[str] = []

    if bundle.scenario.project_economics_v1 is not None:
        economics_ids = {
            p.project_archetype_id
            for p in bundle.scenario.project_economics_v1.projects
        }
        for project in bundle.scenario.project_archetypes:
            if project.project_kind != "FACILITY":
                continue
            archetype_id = project.project_archetype_id
            if archetype_id not in archetype_by_id:
                raise ValueError(
                    f"facility project missing infrastructure semantics: {archetype_id}"
                )
            if archetype_id not in economics_ids:
                raise ValueError(
                    f"facility project missing Project Economics V1 parameterization: {archetype_id}"
                )
            archetype = archetype_by_id[archetype_id]
            if tuple(project.allowed_placements) != tuple(archetype.allowed_placements):
                raise ValueError(f"placement semantic drift: {archetype_id}")

            resolved = resolved_project(
                bundle,
                project,
                bundle.scenario.start_year,
            )
            if resolved != project:
                raise ValueError(
                    f"compiled start-year economics drift: {archetype_id}"
                )
            outputs = {
                key
                for key, value in resolved.output_capacities.__dict__.items()
                if value > 0
            }
            inputs = {
                key
                for key, value in resolved.minimum_input_capacities.__dict__.items()
                if value > 0
            }
            if not outputs <= set(archetype.output_capacity_dimensions):
                raise ValueError(f"output-capacity semantic drift: {archetype_id}")
            if not inputs <= set(archetype.input_capacity_dimensions):
                raise ValueError(f"input-capacity semantic drift: {archetype_id}")
            parameterized.append(archetype_id)
        return sorted(parameterized)

    parameter_by_archetype = {
        p.archetype_id: p
        for p in catalog.parameterizations
        if p.parameter_set_id == DEFAULT_PARAMETER_SET_ID
    }
    for project in bundle.scenario.project_archetypes:
        if project.project_kind != "FACILITY":
            continue
        archetype_id = project.project_archetype_id
        if archetype_id not in archetype_by_id:
            raise ValueError(
                f"facility project missing infrastructure semantics: {archetype_id}"
            )
        if archetype_id not in parameter_by_archetype:
            raise ValueError(
                f"facility project missing locked parameterization: {archetype_id}"
            )
        archetype = archetype_by_id[archetype_id]
        parameter = parameter_by_archetype[archetype_id]
        if tuple(project.allowed_placements) != tuple(archetype.allowed_placements):
            raise ValueError(f"placement semantic drift: {archetype_id}")
        if project.capital_cost != parameter.capital_cost:
            raise ValueError(f"capital-cost drift: {archetype_id}")
        if project.construction_lag_years != parameter.construction_lag_years:
            raise ValueError(f"construction-lag drift: {archetype_id}")
        if dict(project.minimum_input_capacities.__dict__) != {
            key: float(parameter.minimum_input_capacities.get(key, 0.0))
            for key in project.minimum_input_capacities.__dict__
        }:
            raise ValueError(f"minimum-input-capacity drift: {archetype_id}")
        if dict(project.output_capacities.__dict__) != {
            key: float(parameter.output_capacities.get(key, 0.0))
            for key in project.output_capacities.__dict__
        }:
            raise ValueError(f"output-capacity drift: {archetype_id}")
        parameterized.append(archetype_id)
    return sorted(parameterized)

def _implementation_hashes() -> dict[str, str]:
    from engineering.civprop.contracts import (
        accessibility_v1,
        actor_state_v1,
        demand_pressure_v1,
        infrastructure_v1,
        project_economics_v1,
    )
    from engineering.civprop.method_lab import contracts
    from engineering.civprop.method_lab.prototypes import common, hybrid_v1

    return {
        "runner_sha256": _sha256(_THIS_FILE),
        "hybrid_engine_sha256": _module_sha256(hybrid_v1),
        "common_helpers_sha256": _module_sha256(common),
        "method_lab_contracts_sha256": _module_sha256(contracts),
        "infrastructure_contract_sha256": _module_sha256(infrastructure_v1),
        "actor_state_contract_sha256": _module_sha256(actor_state_v1),
        "accessibility_contract_sha256": _module_sha256(accessibility_v1),
        "demand_pressure_contract_sha256": _module_sha256(demand_pressure_v1),
        "project_economics_contract_sha256": _module_sha256(project_economics_v1),
        "project_economics_parameter_set_sha256": _sha256(
            PROJECT_ECONOMICS_PARAMETER_PATH
        ),
    }


def _semantics(input_authority: str | None) -> dict[str, Any]:
    return {
        "time_step": "ANNUAL_INSPECTION_WITH_DISCRETE_PROJECT_COMMISSIONING_EVENTS",
        "annual_snapshot_timing": (
            "END_OF_YEAR_AFTER_DUE_COMMISSIONING_DECISIONS_AND_MIGRATION"
        ),
        "engine_architecture": (
            "ANNUAL_DYNAMIC_RECURSIVE_PLUS_DECAYING_PRESSURE_PLUS_ACTOR_EVENT_DECISIONS"
        ),
        "runtime_reasoning": (
            "EXPLICIT_CODE_RULES_AND_KEYED_STOCHASTICITY_NO_LLM_AUTHORITY"
        ),
        "actor_knowledge": "ACTOR_VISIBLE_SCENARIO_ONLY_HIDDEN_TRUTH_PROHIBITED",
        "resource_truth": (
            "EVALUATOR_ONLY_FIXTURE_PRESENT_IN_PACKAGE_NOT_READ_BY_ENGINE"
        ),
        "technology": (
            "FRONTIER_DATE_DOES_NOT_GRANT_ACTOR_CAPABILITY_ACTOR_ACCESS_IS_SEPARATE"
        ),
        "accessibility": (
            "VERSIONED_PHYSICS_SERVICE_TRI_STATE_WITH_DECOMPOSED_COSTS"
        ),
        "accessibility_geometry": (
            "QUALIFIED_BODY_CENTER_GEOMETRY_IS_CONTEXT_NOT_ROUTE_LENGTH_OR_TRANSFER_SOLUTION"
        ),
        "demand_pressure": (
            "STATE_DERIVED_REQUIREMENT_MINUS_CAPACITY_WITH_UNIT_PRESERVING_MEMORY"
        ),
        "pressure_state": (
            "INTERNAL_NOT_EMITTED_ONLY_QUALIFICATION_EVENTS_VISIBLE"
        ),
        "pressure_memory": (
            "CHANNEL_PRESSURE_DECAYS_WHEN_UNMET_REQUIREMENT_DISAPPEARS"
        ),
        "project_economics": (
            "VERSIONED_PHYSICAL_ECONOMIC_RANGES_WITH_SCALE_AND_EPOCH_RESOLUTION"
        ),
        "major_commitments": (
            "REQUIRE_PRESSURE_QUALIFICATION_ACTOR_USABLE_CAPABILITY_AFFORDABILITY"
        ),
        "facility_records": "COMMISSIONED_FACILITIES_ONLY",
        "pending_projects": (
            "INTERNAL_AFTER_COMMITMENT_UNTIL_COMMISSIONING_NOT_EXPOSED_AS_STATE"
        ),
        "capital_accounting": (
            "PROJECT_CAPITAL_USES_PROJECT_ECONOMICS_UNIT_ACTOR_BUDGET_DEBITED_AT_COMMITMENT_"
            "LOCATION_BOOK_CAPITAL_COMPATIBILITY_FIELD_UPDATED_AT_COMMISSIONING"
        ),
        "actor_budget_output": "ANNUAL_ACTOR_STATE_WITH_REPLAYABLE_TRANSACTIONS",
        "population": (
            "NO_BIRTHS_OR_DEATHS_IN_BASELINE_MIGRATION_IS_SOURCE_DEBITED_AND_CONSERVED"
        ),
        "habitat": "BIOLOGICAL_POPULATION_MAY_NOT_EXCEED_HABITAT_CAPACITY",
        "workforce": "CURRENT_ENGINE_RULE_NOT_PRODUCTION_LABOR_MODEL",
        "flows": "MIGRATION_ONLY_IN_EXECUTABLE_BASELINE",
        "events": (
            "APPEND_ORDER_EVENT_CHAIN_WITH_PREVIOUS_EVENT_PARENT_REFERENCE_CURRENT_SEMANTICS"
        ),
        "infrastructure": (
            "GENERIC_CAPACITY_BEARING_MODULES_NOT_PREWRITTEN_ATLAS_FACILITIES"
        ),
        "atlas_role": "ENGINE_STATE_NOT_FINAL_ATLAS_MATERIALIZATION",
        "authority": input_authority,
    }


def _base_gaps() -> list[dict[str, str]]:
    return [
        {
            "gap_id": "GAP-001",
            "name": "REAL_INPUT_COMPILER",
            "status": "OPEN",
            "meaning": "Replace synthetic Method Lab scenario with frozen adapters from loom_earth, loom_solar, loom_timeline, resource evidence and actor authority.",
        },
        {
            "gap_id": "GAP-002",
            "name": "ACTOR_STATE_AND_BUDGETS",
            "status": "OPEN",
            "meaning": "Versioned actor identity/state separates ownership, operation, scoped access/contracts, capability, experience and spendable allocation with replayable change events.",
        },
        {
            "gap_id": "GAP-003",
            "name": "TRANSPORT_ACCESSIBILITY",
            "status": "OPEN",
            "meaning": "Versioned accessibility separates qualified Solar geometry, scoped actor/provider service access and decomposed generalized cost while preserving FEASIBLE/INFEASIBLE/UNKNOWN.",
        },
        {
            "gap_id": "GAP-004",
            "name": "DEMAND_AND_PRESSURE_MODEL",
            "status": "OPEN",
            "meaning": "Versioned demand/pressure derives scoped requirements from civilization state and explicit commitments, compares them with installed capacity, and carries unmet demand into decaying unit-preserving pressure.",
        },
        {
            "gap_id": "GAP-005",
            "name": "PROJECT_ECONOMICS",
            "status": "OPEN",
            "meaning": "Project Economics V1 provides versioned physical/economic units, uncertainty ranges, scale behavior, technology-year adjustments and provenance; scenario components remain explicitly non-empirical.",
        },
        {
            "gap_id": "GAP-006",
            "name": "MISSIONS_AND_KNOWLEDGE_UPDATE",
            "status": "OPEN",
            "meaning": "Hybrid V1 baseline does not execute prospecting missions or CIVPROP-0 observation/Bayesian knowledge updates.",
        },
        {
            "gap_id": "GAP-007",
            "name": "PRESSURE_OBSERVABILITY",
            "status": "OPEN",
            "meaning": "Pressure levels are internal; only pressure-qualified events are emitted.",
        },
        {
            "gap_id": "GAP-008",
            "name": "RESOURCE_MASS_BALANCE",
            "status": "OPEN",
            "meaning": "Resource capacity is abstract; stock, grade, throughput, yield, depletion and inventory are not yet modeled.",
        },
        {
            "gap_id": "GAP-009",
            "name": "PRODUCTION_AND_VALUE_ADDED",
            "status": "OPEN",
            "meaning": "Off-world sector production, value added, operating cost and investment flows are not yet generated.",
        },
        {
            "gap_id": "GAP-010",
            "name": "POWER_BALANCE",
            "status": "OPEN",
            "meaning": "Power is abstract installed capacity; average demand, peak demand, storage, generation mix and energy closure are not yet modeled.",
        },
        {
            "gap_id": "GAP-011",
            "name": "TRAFFIC_AND_FLEET",
            "status": "OPEN",
            "meaning": "Cargo, passengers, ship calls, fleets, queues and route utilization are not yet generated.",
        },
        {
            "gap_id": "GAP-012",
            "name": "FACILITY_AND_SITE_MATERIALIZATION",
            "status": "OPEN",
            "meaning": "Module colocation, named facilities, settlements, surface sites, orbital elements and Atlas facility types are not yet materialized.",
        },
        {
            "gap_id": "GAP-013",
            "name": "MAINTENANCE_DEPRECIATION_RETIREMENT",
            "status": "OPEN",
            "meaning": "Infrastructure maintenance, depreciation, replacement, failure, retirement and abandonment are not yet production modeled.",
        },
        {
            "gap_id": "GAP-014",
            "name": "DEMOGRAPHIC_DEPTH",
            "status": "OPEN",
            "meaning": "Cohort demography, births/deaths, synthetic persons, biological viability and long-run settlement demographics are not yet connected.",
        },
        {
            "gap_id": "GAP-015",
            "name": "ATLAS_DERIVED_METRICS",
            "status": "OPEN",
            "meaning": "Economic/transport centrality, strategic significance and other Atlas display metrics must be derived after physical/economic state exists.",
        },
    ]


def _known_gaps(input_dir: Path) -> list[dict[str, str]]:
    gaps = _base_gaps()
    compiler_manifest = Path(input_dir) / "compiler_manifest_v1.json"
    if not compiler_manifest.exists():
        return gaps

    manifest = json.loads(compiler_manifest.read_text())
    statuses = manifest.get("gap_resolution", {})
    for gap in gaps:
        if gap["gap_id"] in statuses:
            gap["status"] = statuses[gap["gap_id"]]
    return gaps


def _compiler_metadata(input_dir: Path) -> dict[str, Any] | None:
    path = Path(input_dir) / "compiler_manifest_v1.json"
    if not path.exists():
        return None
    manifest = json.loads(path.read_text())
    return {
        "manifest_format": manifest.get("format"),
        "compiler_id": manifest.get("compiler_id"),
        "compiler_version": manifest.get("compiler_version"),
        "manifest_sha256": _sha256(path),
        "authority_capture": manifest.get("authority_capture"),
        "gap_resolution": manifest.get("gap_resolution"),
    }


def _actor_state_projection(bundle, result):
    """Replay actor finance/state at the runner boundary from declared inputs + decisions."""
    package = bundle.scenario.actor_state_v1
    if package is None:
        return None, [], [], []

    from engineering.civprop.contracts.actor_state_v1 import ActorStateRuntime

    boundary = json.loads(canonical_json(package))
    runtime = ActorStateRuntime(package)
    actors = {x.actor_id: x for x in package.actors}
    budgets = {
        actor_id: {
            "status": actor.budget.spendable_allocation.status,
            "amount": actor.budget.spendable_allocation.amount,
            "unit": actor.budget.spendable_allocation.unit,
            "scope": actor.budget.spendable_allocation.scope,
        }
        for actor_id, actor in actors.items()
    }
    projects = {
        x.project_archetype_id: x for x in bundle.scenario.project_archetypes
    }
    transactions = []
    annual_states = []
    transaction_counter = 0

    for year in range(bundle.scenario.start_year, bundle.scenario.end_year + 1):
        for event in package.events:
            if event.year != year or event.event_type != "BUDGET_ALLOCATION_SET":
                continue
            payload = event.payload
            budgets[event.actor_id] = {
                "status": "KNOWN",
                "amount": float(payload["amount"]),
                "unit": str(payload["unit"]),
                "scope": str(payload["scope"]),
            }
            transaction_counter += 1
            transactions.append(
                {
                    "transaction_id": f"at{transaction_counter:05d}",
                    "year": year,
                    "actor_id": event.actor_id,
                    "transaction_type": event.event_type,
                    "amount": float(payload["amount"]),
                    "unit": str(payload["unit"]),
                    "scope": str(payload["scope"]),
                    "provenance_ref": event.provenance_ref,
                }
            )

        for decision in result.decisions:
            if (
                decision.year != year
                or decision.action != "COMMIT_PROJECT"
                or decision.status != "COMMITTED"
            ):
                continue
            project = resolved_project(
                bundle,
                projects[decision.project_archetype_id],
                year,
            )
            budget = budgets[decision.actor_id]
            required_unit = project_capital_unit(bundle)
            if (
                budget["status"] != "KNOWN"
                or budget["amount"] is None
                or budget["unit"] != required_unit
                or budget["amount"] + 1e-9 < project.capital_cost
            ):
                raise ValueError("project commitment cannot be replayed from actor budget")
            budget["amount"] -= project.capital_cost
            transaction_counter += 1
            transactions.append(
                {
                    "transaction_id": f"at{transaction_counter:05d}",
                    "year": year,
                    "actor_id": decision.actor_id,
                    "transaction_type": "PROJECT_COMMITMENT",
                    "amount": project.capital_cost,
                    "unit": required_unit,
                    "scope": (
                        f"{decision.project_archetype_id}@"
                        f"{decision.target_location_id}"
                    ),
                    "provenance_ref": f"decision:{decision.decision_id}",
                }
            )

        for actor_id, actor in sorted(actors.items()):
            capability_ids = {
                record.capability_id
                for facts in (actor.installed_capability, actor.acquired_capability)
                for record in facts.records
                if record.capability_id is not None
            }
            capability_ids.update(
                str(event.payload["capability_id"])
                for event in package.events
                if event.actor_id == actor_id
                and event.year <= year
                and event.event_type == "CAPABILITY_SET"
            )
            annual_states.append(
                {
                    "year": year,
                    "actor_id": actor_id,
                    "actor_type": actor.actor_type,
                    "spendable_allocation": dict(budgets[actor_id]),
                    "capability_state": {
                        capability_id: runtime.capability_status(
                            actor_id, capability_id, year
                        )
                        for capability_id in sorted(capability_ids)
                    },
                }
            )

    state_events = json.loads(canonical_json(package.events))
    return boundary, annual_states, transactions, state_events


def build_output(
    *,
    input_dir: Path,
    infrastructure_catalog_path: Path,
    seed: int,
) -> dict[str, Any]:
    input_dir = Path(input_dir).resolve()
    infrastructure_catalog_path = Path(infrastructure_catalog_path).resolve()

    bundle = load_bundle(input_dir)
    catalog = load_infrastructure_catalog(infrastructure_catalog_path)
    parameterized_archetypes = _validate_infrastructure_crosswalk(bundle, catalog)

    engine = HybridEngineV1()
    result = engine.run(bundle, seed)
    validate_result(result, bundle)
    result_dict = json.loads(canonical_json(result))
    (
        actor_state_boundary,
        actor_states,
        actor_transactions,
        actor_state_events,
    ) = _actor_state_projection(bundle, result)

    scenario_path = input_dir / "scenario_v1.json"
    truth_path = input_dir / "truth_v1.json"
    manifest_path = input_dir / "manifest_v1.json"
    scenario_sha = _sha256(scenario_path)
    compiler_metadata = _compiler_metadata(input_dir)

    output = {
        "format": OUTPUT_FORMAT,
        "contract_version": OUTPUT_CONTRACT_VERSION,
        "metadata": {
            "runner": {
                "id": RUNNER_ID,
                "version": RUNNER_VERSION,
            },
            "engine": {
                "id": engine.engine_id,
                "version": engine.engine_version,
                "run_id": result.metadata.run_id,
                "seed": seed,
                "start_year": bundle.scenario.start_year,
                "end_year": bundle.scenario.end_year,
            },
            "inputs": {
                "fixture_id": bundle.scenario.fixture_id,
                "scenario_format": bundle.scenario.format,
                "method_lab_manifest_sha256": _sha256(manifest_path),
                "method_lab_bundle_sha256": bundle.bundle_sha256,
                "actor_visible_scenario_sha256": scenario_sha,
                "runtime_input_sha256": scenario_sha,
                "evaluator_truth_sha256": _sha256(truth_path),
                "evaluator_truth_consumed_by_engine": False,
                "input_authority": bundle.manifest.get("authority"),
                "basis": bundle.manifest.get("basis", {}),
                "compiler": compiler_metadata,
            },
            "infrastructure": {
                "catalog_id": catalog.catalog_id,
                "catalog_format": catalog.format,
                "catalog_sha256": _sha256(infrastructure_catalog_path),
                "parameter_set_id": (
                    bundle.scenario.project_economics_v1.parameter_set_id
                    if bundle.scenario.project_economics_v1 is not None
                    else DEFAULT_PARAMETER_SET_ID
                ),
                "parameter_status": (
                    "PROJECT_ECONOMICS_V1_MIXED_STATUS"
                    if bundle.scenario.project_economics_v1 is not None
                    else PARAMETER_STATUS_METHOD_LAB
                ),
                "parameterized_archetypes": parameterized_archetypes,
            },
            "implementation": _implementation_hashes(),
        },
        "semantics": _semantics(bundle.manifest.get("authority")),
        "known_gaps": _known_gaps(input_dir),
        "actor_state_boundary": actor_state_boundary,
        "accessibility_boundary": (
            None
            if bundle.scenario.accessibility_v1 is None
            else json.loads(canonical_json(bundle.scenario.accessibility_v1))
        ),
        "demand_pressure_boundary": (
            None
            if bundle.scenario.demand_pressure_v1 is None
            else json.loads(canonical_json(bundle.scenario.demand_pressure_v1))
        ),
        "project_economics_boundary": (
            None
            if bundle.scenario.project_economics_v1 is None
            else json.loads(canonical_json(bundle.scenario.project_economics_v1))
        ),
        "actor_states": actor_states,
        "actor_transactions": actor_transactions,
        "actor_state_events": actor_state_events,
        "annual_states": result_dict["annual_states"],
        "facilities": result_dict["facilities"],
        "decisions": result_dict["decisions"],
        "events": result_dict["events"],
        "flows": result_dict["flows"],
    }
    return output


def main() -> None:
    default_input_dir, default_catalog = default_paths()
    parser = argparse.ArgumentParser(
        description="Run the locked CIVPROP Engine V1 executable baseline."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=default_input_dir,
        help="Compatible frozen input directory (defaults to GAP-001 through GAP-005 compiled V1).",
    )
    parser.add_argument(
        "--infrastructure-catalog",
        type=Path,
        default=default_catalog,
        help="Infrastructure Archetype V1 catalog.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        help="Write full deterministic output JSON here; stdout when omitted.",
    )
    args = parser.parse_args()

    output = build_output(
        input_dir=args.input_dir,
        infrastructure_catalog_path=args.infrastructure_catalog,
        seed=args.seed,
    )
    text = json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)


if __name__ == "__main__":
    main()
