#!/usr/bin/env python3
"""Locked executable baseline for CIVPROP Engine V1.

Runner V1.13 keeps the selected HYBRID_V1 propagation architecture and closed
GAP-001 through GAP-013 boundaries, including Facility/Site Materialization and Asset Lifecycle V1
V1 as a deterministic post-engine projection from generated infrastructure modules
to stable sites, materialized facilities, orbitals, settlement candidates and
Atlas-facing facility classifications. Later gaps remain explicit.
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
from engineering.civprop.contracts.project_economics_v1 import ProjectEconomicsRuntime
from engineering.civprop.contracts.facility_site_materialization_v1 import (
    FacilitySiteMaterializerV1,
)
from engineering.civprop.contracts.asset_lifecycle_v1 import (
    AssetLifecycleRuntimeV1, load_asset_lifecycle_data, to_dicts as lifecycle_to_dicts,
    project_production_through_lifecycle,
)
from engineering.civprop.method_lab.prototypes.common import (
    project_capital_unit,
    resolved_project,
)


OUTPUT_FORMAT = "CIVPROP_ENGINE_V1_OUTPUT"
OUTPUT_CONTRACT_VERSION = "1.13.0"
RUNNER_ID = "CIVPROP_ENGINE_V1_RUNNER"
RUNNER_VERSION = "1.13.0"
DEFAULT_PARAMETER_SET_ID = "METHOD_LAB_SYNTHETIC_V1"
PROJECT_ECONOMICS_PARAMETER_PATH = (
    _CIVPROP_DIR / "contracts" / "project_economics_v1.json"
)
MISSION_KNOWLEDGE_PARAMETER_PATH = (
    _CIVPROP_DIR / "contracts" / "mission_knowledge_v1.json"
)
PRESSURE_OBSERVABILITY_PARAMETER_PATH = (
    _CIVPROP_DIR / "contracts" / "pressure_observability_v1.json"
)
RESOURCE_MASS_BALANCE_PARAMETER_PATH = (
    _CIVPROP_DIR / "contracts" / "resource_mass_balance_v1.json"
)
PRODUCTION_ACCOUNTING_PARAMETER_PATH = (
    _CIVPROP_DIR / "contracts" / "production_accounting_v1.json"
)
POWER_BALANCE_PARAMETER_PATH = (
    _CIVPROP_DIR / "contracts" / "power_balance_v1.json"
)
TRAFFIC_FLEET_PARAMETER_PATH = (
    _CIVPROP_DIR / "contracts" / "traffic_fleet_v1.json"
)
ASSET_LIFECYCLE_PARAMETER_PATH = _CIVPROP_DIR / "contracts" / "asset_lifecycle_v1.json"
FACILITY_SITE_MATERIALIZATION_PARAMETER_PATH = (
    _CIVPROP_DIR
    / "contracts"
    / "facility_site_materialization_v1.json"
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
        mission_knowledge_v1,
        pressure_observability_v1,
        resource_mass_balance_v1,
        production_accounting_v1,
        power_balance_v1,
        traffic_fleet_v1,
        facility_site_materialization_v1,
        asset_lifecycle_v1,
    )
    from engineering.civprop.method_lab import (
        contracts,
        mission_lane_v1,
        pressure_lane_v1,
        resource_lane_v1,
        production_lane_v1,
        power_lane_v1,
        traffic_lane_v1,
    )
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
        "mission_knowledge_contract_sha256": _module_sha256(
            mission_knowledge_v1
        ),
        "mission_knowledge_parameter_set_sha256": _sha256(
            MISSION_KNOWLEDGE_PARAMETER_PATH
        ),
        "mission_lane_sha256": _module_sha256(mission_lane_v1),
        "pressure_observability_contract_sha256": _module_sha256(
            pressure_observability_v1
        ),
        "pressure_observability_parameter_set_sha256": _sha256(
            PRESSURE_OBSERVABILITY_PARAMETER_PATH
        ),
        "pressure_lane_sha256": _module_sha256(pressure_lane_v1),
        "resource_mass_balance_contract_sha256": _module_sha256(
            resource_mass_balance_v1
        ),
        "resource_mass_balance_parameter_set_sha256": _sha256(
            RESOURCE_MASS_BALANCE_PARAMETER_PATH
        ),
        "resource_lane_sha256": _module_sha256(resource_lane_v1),
        "production_accounting_contract_sha256": _module_sha256(
            production_accounting_v1
        ),
        "production_accounting_parameter_set_sha256": _sha256(
            PRODUCTION_ACCOUNTING_PARAMETER_PATH
        ),
        "production_lane_sha256": _module_sha256(production_lane_v1),
        "power_balance_contract_sha256": _module_sha256(
            power_balance_v1
        ),
        "power_balance_parameter_set_sha256": _sha256(
            POWER_BALANCE_PARAMETER_PATH
        ),
        "power_lane_sha256": _module_sha256(power_lane_v1),
        "traffic_fleet_contract_sha256": _module_sha256(
            traffic_fleet_v1
        ),
        "traffic_fleet_parameter_set_sha256": _sha256(
            TRAFFIC_FLEET_PARAMETER_PATH
        ),
        "traffic_lane_sha256": _module_sha256(traffic_lane_v1),
        "facility_site_materialization_contract_sha256": _module_sha256(
            facility_site_materialization_v1
        ),
        "asset_lifecycle_contract_sha256": _module_sha256(asset_lifecycle_v1),
        "asset_lifecycle_parameter_set_sha256": _sha256(ASSET_LIFECYCLE_PARAMETER_PATH),
        "facility_site_materialization_parameter_set_sha256": _sha256(
            FACILITY_SITE_MATERIALIZATION_PARAMETER_PATH
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
        "actor_knowledge": (
            "VERSIONED_ACTOR_SCOPED_BELIEF_UPDATED_ONLY_BY_RECEIVED_OBSERVATIONS"
        ),
        "resource_truth": (
            "EVALUATOR_ONLY_HIDDEN_REALIZATION_BOUNDED_RUNTIME_LANES_ONLY"
        ),
        "mission_knowledge": (
            "GENERAL_MISSION_ACTION_CONTRACT_WITH_BINARY_RESOURCE_OBSERVATION_V1"
        ),
        "observation_noise": (
            "KEYED_SEED_EVIDENCE_MISSION_AND_MODEL_INSERTION_ORDER_INDEPENDENT"
        ),
        "knowledge_update": (
            "DETERMINISTIC_BAYESIAN_UPDATE_WITH_DUPLICATE_SCOPE_AND_CHRONOLOGY_GUARDS"
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
            "VERSIONED_IMMUTABLE_ANNUAL_LEDGER_WITH_RECONSTRUCTABLE_TRANSITIONS"
        ),
        "pressure_contributions": (
            "QUANTIFIED_CAUSAL_REQUIREMENT_AND_CAPACITY_COMPONENTS_WITH_STABLE_IDS"
        ),
        "pressure_qualification": (
            "PER_OPPORTUNITY_RATIO_TRACE_WITH_SELECTED_DECISION_PROVENANCE"
        ),
        "pressure_observability_effect": (
            "READ_ONLY_INSTRUMENTATION_DECISIONS_AND_RANDOM_DRAWS_UNCHANGED"
        ),
        "resource_mass_balance": (
            "EVALUATOR_ONLY_STOCK_FEED_GRADE_RECOVERY_TAILINGS_INVENTORY_DEPLETION"
        ),
        "resource_physical_state": (
            "SEPARATE_FROM_ACTOR_VISIBLE_RESOURCE_KNOWLEDGE"
        ),
        "resource_unknown": (
            "PRESENT_UNQUANTIFIED_OR_UNKNOWN_ABUNDANCE_NEVER_COERCED_TO_ZERO_OR_INVENTORY"
        ),
        "production_accounting": (
            "PHYSICAL_OUTPUT_FEASIBILITY_SEPARATE_FROM_MONETARY_VALUATION_AND_CAPITAL_STOCK"
        ),
        "production_constraints": (
            "MISSING_REQUIRED_POWER_LABOR_MATERIAL_TRANSPORT_CONSTRAINTS_PROPAGATE_UNKNOWN"
        ),
        "value_added": (
            "GROSS_OUTPUT_MINUS_INTERMEDIATE_CONSUMPTION_OPERATING_COST_IS_DISTINCT"
        ),
        "productive_capital": (
            "GROSS_COMMISSIONED_PROJECT_CAPITAL_WITH_EXPLICIT_GAP013_LIFECYCLE_PROJECTION"
        ),
        "power_balance": (
            "INSTALLED_MW_SEPARATE_FROM_AVERAGE_GENERATION_PEAK_LOAD_AND_ANNUAL_MWH"
        ),
        "power_energy_interval": (
            "GREGORIAN_CALENDAR_YEAR_8760_OR_8784_HOURS"
        ),
        "power_unknowns": (
            "AVERAGE_LOAD_GENERATOR_AVAILABILITY_FIRMNESS_FACILITY_LOADS_AND_RESERVE_REMAIN_UNKNOWN_UNLESS_QUALIFIED"
        ),
        "power_timeline": (
            "R03_AND_ENE_MOD_INDUSTRIAL_ARE_CONTEXT_ONLY_NO_AUTO_UNLOCK"
        ),
        "atlas_power_metrics": (
            "POWER_AVERAGE_MW_AND_POWER_PEAK_MW_ARE_RUNTIME_ELECTRICAL_LOAD_DEMAND_METRICS"
        ),
        "traffic_fleet": (
            "EXPLICIT_OD_ASSIGNMENT_ACCESSIBILITY_SERVICE_FLEET_VOYAGE_BACKLOG_ACCOUNTING"
        ),
        "transport_capacity": (
            "LOCAL_HANDLING_CAPACITY_IS_NOT_REALIZED_OD_MOVEMENT"
        ),
        "traffic_timeline": (
            "TRN_MOD_HEAVY_AND_TRN_MOD_NEP_ARE_CONTEXT_ONLY_NO_AUTO_FLEET_SPAWN"
        ),
        "atlas_traffic_metrics": (
            "CARGO_PASSENGER_SHIP_CALL_FIELDS_ARE_ANNUAL_MODELED_NODE_INCIDENCE"
        ),
        "facility_site_materialization": (
            "POST_ENGINE_EXPLICIT_ONLY_COLOCATION_STABLE_IDENTITY_NO_CAUSAL_FEEDBACK"
        ),
        "materialization_spatial_authority": (
            "LOCATION_CLASS_ONLY_UNLESS_EXACT_SURFACE_OR_ORBITAL_AUTHORITY_IS_EXPLICIT"
        ),
        "materialization_ownership": (
            "MODULE_OWNER_PRESERVED_OPERATOR_NEVER_INFERRED_FROM_OWNER"
        ),
        "materialization_naming": (
            "PRESENTATION_ONLY_NAMES_DO_NOT_CHANGE_SITE_OR_FACILITY_IDENTITY"
        ),
        "atlas_facility_types": (
            "DERIVED_FROM_MODULE_COMPOSITION_STRATEGIC_PORT_DEFERRED_TO_GAP015"
        ),
        "asset_lifecycle": (
            "EXPLICIT_PARAMETERS_AND_EVENTS_ONLY_UNKNOWN_LIFECYCLE_NEVER_INVENTED"
        ),
        "asset_lifecycle_effect": (
            "RUNNER_PROJECTION_ONLY_HYBRID_V1_CAUSAL_BEHAVIOR_UNCHANGED_IN_INITIAL_INTEGRATION"
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
        "atlas_role": (
            "ENGINE_STATE_PLUS_DETERMINISTIC_GAP012_MATERIALIZATION_"
            "DERIVED_STRATEGIC_METRICS_REMAIN_GAP015"
        ),
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
            "meaning": "Mission/Knowledge V1 separates mission actions from infrastructure, actor-visible belief from evaluator truth, keyed noisy observations from physical realization, and deterministic Bayesian knowledge updates from later decisions.",
        },
        {
            "gap_id": "GAP-007",
            "name": "PRESSURE_OBSERVABILITY",
            "status": "OPEN",
            "meaning": "Pressure Observability V1 emits immutable annual pressure transitions, quantified causal contributions and per-opportunity qualification traces with stable IDs; selected project decisions link to the exact qualifying record without changing Hybrid behavior.",
        },
        {
            "gap_id": "GAP-008",
            "name": "RESOURCE_MASS_BALANCE",
            "status": "OPEN",
            "meaning": "Resource Mass Balance V1 separates actor-visible evidence/belief from evaluator-only physical realization and conserves in-situ stock, extracted feed, grade, recovery, tailings, product inventory and depletion; unquantified abundance remains UNKNOWN rather than zero or invented inventory.",
        },
        {
            "gap_id": "GAP-009",
            "name": "PRODUCTION_AND_VALUE_ADDED",
            "status": "OPEN",
            "meaning": "Production Accounting V1 separates physical output feasibility from monetary valuation and gross productive-capital accounting; unresolved required constraints remain UNKNOWN, value added is gross output minus intermediate consumption, and operating cost is distinct.",
        },
        {
            "gap_id": "GAP-010",
            "name": "POWER_BALANCE",
            "status": "OPEN",
            "meaning": "Power Balance V1 separates installed generation capacity from average/firm generation, explicit population/facility load, peak and average demand, annual MWh, reserve/storage assumptions, unserved/curtailed energy and runtime-derived Atlas average/peak load metrics; timeline power milestones never auto-unlock capacity.",
        },
        {
            "gap_id": "GAP-011",
            "name": "TRAFFIC_AND_FLEET",
            "status": "OPEN",
            "meaning": "Traffic/Fleet V1 separates local transport handling capacity from realized OD movement and generates explicit cargo/passenger demand assignment, scoped service state, fleet trip capacity, annual voyages, ship calls, backlog, route utilization and node-incidence metrics; unassigned demand remains UNASSIGNED_OD and timeline transport milestones never auto-spawn fleet.",
        },
        {
            "gap_id": "GAP-012",
            "name": "FACILITY_AND_SITE_MATERIALIZATION",
            "status": "OPEN",
            "meaning": "Facility/Site Materialization V1 deterministically projects generated infrastructure modules into stable sites, materialized facilities, orbital/site projections, habitat settlement candidates and Atlas-facing facility classifications. Colocation is explicit-only; inherited off-world initial state remains UNQUALIFIED_COMPATIBILITY and is never materialized without module provenance; exact spatial values require admitted authority; owner/operator remain distinct; names are presentation-only.",
        },
        {
            "gap_id": "GAP-013",
            "name": "MAINTENANCE_DEPRECIATION_RETIREMENT",
            "status": "OPEN",
            "meaning": "Asset Lifecycle V1 projects explicit age, maintenance, depreciation, failure, retirement, abandonment, restoration and replacement into usable capacity and a post-engine production projection; missing lifecycle authority remains UNKNOWN rather than inferred.",
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
        {
            "gap_id": "GAP-016",
            "name": "GENERIC_PHYSICAL_TRANSPORT_SERVICE",
            "status": "OPEN",
            "meaning": "Generalized trajectory, vehicle, propulsion, power, propellant/remass, payload and infrastructure coupling has not yet earned physical transport service feasibility or capacity.",
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


def _apply_demographic_output_semantics(result_dict: dict[str, Any], bundle) -> dict[str, Any]:
    """Fail closed for Earth fields not governed by GAP-014 demographic authority.

    The promoted Earth lane governs biological population only.  The legacy
    Method-Lab fixture also carries 2026 workforce and habitat numbers; carrying
    those unchanged beside a moving 2026-2226 population makes stale values look
    authoritative.  Earth is excluded from V1 demand/pressure, so this boundary
    changes publication semantics without changing Hybrid decisions.
    """
    authority = bundle.scenario.demographic_authority_v1
    if authority is None:
        return result_dict
    for row in result_dict.get("annual_states", []):
        if row.get("location_id") != "EARTH_SURFACE":
            continue
        row["workforce"] = None
        capacities = row.get("capacities") or {}
        capacities["habitat"] = None
        row["state_authority"] = {
            "biological_population": "EARTH_PROMOTED_DEMOGRAPHIC_AUTHORITY",
            "workforce": "UNKNOWN_NOT_GOVERNED_BY_DEMOGRAPHIC_AUTHORITY",
            "habitat": "UNKNOWN_NOT_GOVERNED_BY_DEMOGRAPHIC_AUTHORITY",
        }
    return result_dict


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

    # Immutable replay indexes. Preserve source order within each year while
    # avoiding repeated full-history scans across the 201-year projection.
    budget_events_by_year = {}
    capability_events_by_actor_year = {}
    for event in package.events:
        if event.event_type == "BUDGET_ALLOCATION_SET":
            budget_events_by_year.setdefault(event.year, []).append(event)
        elif event.event_type == "CAPABILITY_SET":
            capability_events_by_actor_year.setdefault(
                (event.actor_id, event.year), []
            ).append(event)

    committed_projects_by_year = {}
    for decision in result.decisions:
        if decision.action == "COMMIT_PROJECT" and decision.status == "COMMITTED":
            committed_projects_by_year.setdefault(decision.year, []).append(decision)

    committed_missions_by_year = {}
    for decision in result.mission_decisions:
        if decision.action == "COMMIT_MISSION" and decision.status == "COMMITTED":
            committed_missions_by_year.setdefault(decision.year, []).append(decision)

    base_capability_ids = {
        actor_id: {
            record.capability_id
            for facts in (actor.installed_capability, actor.acquired_capability)
            for record in facts.records
            if record.capability_id is not None
        }
        for actor_id, actor in actors.items()
    }
    cumulative_capability_ids = {
        actor_id: set(ids) for actor_id, ids in base_capability_ids.items()
    }

    mission_by_id = (
        {x.mission_archetype_id: x for x in bundle.scenario.mission_knowledge_v1.missions}
        if bundle.scenario.mission_knowledge_v1 is not None else {}
    )
    economics = (
        ProjectEconomicsRuntime(bundle.scenario.project_economics_v1)
        if bundle.scenario.mission_knowledge_v1 is not None
        and bundle.scenario.project_economics_v1 is not None else None
    )
    legacy_projects = projects

    for year in range(bundle.scenario.start_year, bundle.scenario.end_year + 1):
        for event in budget_events_by_year.get(year, ()):
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

        for decision in committed_projects_by_year.get(year, ()):
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

        if bundle.scenario.mission_knowledge_v1 is not None:
            for decision in committed_missions_by_year.get(year, ()):
                mission = mission_by_id[decision.mission_archetype_id]
                if economics is not None:
                    resolved = economics.resolve(
                        mission.project_economics_id,
                        year=year,
                    )
                    mission_cost = resolved.capital_cost
                    required_unit = resolved.capital_unit
                else:
                    project = legacy_projects[mission.project_economics_id]
                    mission_cost = project.capital_cost
                    required_unit = bundle.scenario.units["capital"]

                budget = budgets[decision.actor_id]
                if (
                    budget["status"] != "KNOWN"
                    or budget["amount"] is None
                    or budget["unit"] != required_unit
                    or budget["amount"] + 1e-9 < mission_cost
                ):
                    raise ValueError(
                        "mission commitment cannot be replayed from actor budget"
                    )
                budget["amount"] -= mission_cost
                transaction_counter += 1
                transactions.append(
                    {
                        "transaction_id": f"at{transaction_counter:05d}",
                        "year": year,
                        "actor_id": decision.actor_id,
                        "transaction_type": "MISSION_COMMITMENT",
                        "amount": mission_cost,
                        "unit": required_unit,
                        "scope": (
                            f"{decision.mission_archetype_id}@"
                            f"{decision.target_location_id}"
                        ),
                        "provenance_ref": (
                            f"mission_decision:{decision.decision_id}"
                        ),
                    }
                )

        for actor_id, actor in sorted(actors.items()):
            cumulative_capability_ids[actor_id].update(
                str(event.payload["capability_id"])
                for event in capability_events_by_actor_year.get((actor_id, year), ())
            )
            capability_ids = cumulative_capability_ids[actor_id]
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
    trace_decisions: bool = False,
) -> dict[str, Any]:
    input_dir = Path(input_dir).resolve()
    infrastructure_catalog_path = Path(infrastructure_catalog_path).resolve()

    bundle = load_bundle(input_dir)
    catalog = load_infrastructure_catalog(infrastructure_catalog_path)
    parameterized_archetypes = _validate_infrastructure_crosswalk(bundle, catalog)

    engine = HybridEngineV1()
    result = engine.run(bundle, seed, trace_decisions=trace_decisions)
    validate_result(result, bundle)
    result_dict = json.loads(canonical_json(result))
    result_dict = _apply_demographic_output_semantics(result_dict, bundle)
    if bundle.scenario.facility_site_materialization_v1 is None:
        materialization = None
        materialization_dict = {
            "compatibility_states": [],
            "modules": [],
            "sites": [],
            "facilities": [],
            "orbitals": [],
            "settlements": [],
            "atlas_facilities": [],
        }
    else:
        materialization = FacilitySiteMaterializerV1(
            bundle.scenario.facility_site_materialization_v1,
            catalog,
            bundle.scenario.locations,
        ).materialize(result.facilities)
        materialization_dict = json.loads(
            canonical_json(materialization)
        )
    if bundle.scenario.asset_lifecycle_v1 is None:
        raise ValueError("compiled scenario missing required GAP-013 asset_lifecycle_v1 package")
    lifecycle_policies, lifecycle_events, lifecycle_boundary = load_asset_lifecycle_data(
        bundle.scenario.asset_lifecycle_v1
    )
    lifecycle_states = AssetLifecycleRuntimeV1(lifecycle_policies, lifecycle_events).project(
        result.facilities, bundle.scenario.start_year, bundle.scenario.end_year
    )
    lifecycle_production_states = project_production_through_lifecycle(
        result.facility_production_states, lifecycle_states
    )

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
                "mission_observation_truth_consumed": bool(
                    result.observations
                ),
                "resource_physical_realization_consumed": bool(
                    bundle.scenario.resource_mass_balance_v1 is not None
                    and result.resource_states
                ),
                "evaluator_truth_consumed_by_engine": bool(
                    result.observations or result.resource_states
                ),
                "evaluator_truth_access_policy": (
                    "OBSERVATION_RUNTIME_AND_RESOURCE_MASS_BALANCE_LANE_ONLY_NOT_ACTOR_INPUT"
                ),
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
        "asset_lifecycle_boundary": lifecycle_boundary,
        "asset_lifecycle_states": lifecycle_to_dicts(lifecycle_states),
        "lifecycle_production_states": lifecycle_to_dicts(lifecycle_production_states),
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
        "mission_knowledge_boundary": (
            None
            if bundle.scenario.mission_knowledge_v1 is None
            else json.loads(canonical_json(bundle.scenario.mission_knowledge_v1))
        ),
        "pressure_observability_boundary": (
            None
            if bundle.scenario.pressure_observability_v1 is None
            else json.loads(
                canonical_json(bundle.scenario.pressure_observability_v1)
            )
        ),
        "resource_mass_balance_boundary": (
            None
            if bundle.scenario.resource_mass_balance_v1 is None
            else json.loads(
                canonical_json(bundle.scenario.resource_mass_balance_v1)
            )
        ),
        "production_accounting_boundary": (
            None
            if bundle.scenario.production_accounting_v1 is None
            else json.loads(
                canonical_json(bundle.scenario.production_accounting_v1)
            )
        ),
        "power_balance_boundary": (
            None
            if bundle.scenario.power_balance_v1 is None
            else json.loads(canonical_json(bundle.scenario.power_balance_v1))
        ),
        "traffic_fleet_boundary": (
            None
            if bundle.scenario.traffic_fleet_v1 is None
            else json.loads(canonical_json(bundle.scenario.traffic_fleet_v1))
        ),
        "facility_site_materialization_boundary": (
            None
            if bundle.scenario.facility_site_materialization_v1 is None
            else json.loads(
                canonical_json(
                    bundle.scenario.facility_site_materialization_v1
                )
            )
        ),
        "actor_states": actor_states,
        "actor_transactions": actor_transactions,
        "actor_state_events": actor_state_events,
        "annual_states": result_dict["annual_states"],
        "facilities": result_dict["facilities"],
        "decisions": result_dict["decisions"],
        "mission_decisions": result_dict.get("mission_decisions", []),
        "mission_opportunity_dispositions": result_dict.get("mission_opportunity_dispositions", []),
        "missions": result_dict.get("missions", []),
        "observations": result_dict.get("observations", []),
        "knowledge_states": result_dict.get("knowledge_states", []),
        "pressure_states": result_dict.get("pressure_states", []),
        "pressure_contributions": result_dict.get(
            "pressure_contributions",
            [],
        ),
        "pressure_qualifications": result_dict.get(
            "pressure_qualifications",
            [],
        ),
        "resource_states": result_dict.get("resource_states", []),
        "resource_flows": result_dict.get("resource_flows", []),
        "facility_production_states": result_dict.get(
            "facility_production_states",
            [],
        ),
        "sector_production_states": result_dict.get(
            "sector_production_states",
            [],
        ),
        "location_production_states": result_dict.get(
            "location_production_states",
            [],
        ),
        "body_production_states": result_dict.get(
            "body_production_states",
            [],
        ),
        "power_states": result_dict.get("power_states", []),
        "power_flows": result_dict.get("power_flows", []),
        "atlas_power_metrics": [
            {
                "year": row["year"],
                "location_id": row["location_id"],
                "power_state_id": row["power_state_id"],
                "power_average_mw": row["atlas_power_average_mw"],
                "power_peak_mw": row["atlas_power_peak_mw"],
                "measurement_basis": (
                    "ANNUAL_AVERAGE_AND_PEAK_ELECTRICAL_LOAD_DEMAND"
                ),
            }
            for row in result_dict.get("power_states", [])
        ],
        "traffic_demand_states": result_dict.get(
            "traffic_demand_states", []
        ),
        "traffic_service_states": result_dict.get(
            "traffic_service_states", []
        ),
        "fleet_states": result_dict.get("fleet_states", []),
        "voyage_states": result_dict.get("voyage_states", []),
        "route_traffic_states": result_dict.get(
            "route_traffic_states", []
        ),
        "location_traffic_states": result_dict.get(
            "location_traffic_states", []
        ),
        "traffic_pressure_overrides": result_dict.get(
            "traffic_pressure_overrides", []
        ),
        "atlas_traffic_metrics": [
            {
                "year": row["year"],
                "location_id": row["location_id"],
                "location_traffic_state_id": (
                    row["location_traffic_state_id"]
                ),
                "cargo_throughput_tonnes_year": (
                    row["cargo_throughput_tonnes_year"]
                ),
                "passenger_movements_year": (
                    row["passenger_movements_year"]
                ),
                "ship_calls_year": row["ship_calls_year"],
                "measurement_basis": (
                    "ANNUAL_MODELED_NODE_TRAFFIC_INCIDENCE"
                ),
                "metric_scope": row["metric_scope"],
            }
            for row in result_dict.get(
                "location_traffic_states", []
            )
        ],
        "materialization_compatibility_states": (
            materialization_dict["compatibility_states"]
        ),
        "materialized_modules": materialization_dict["modules"],
        "sites": materialization_dict["sites"],
        "materialized_facilities": materialization_dict["facilities"],
        "orbitals": materialization_dict["orbitals"],
        "settlements": materialization_dict["settlements"],
        "atlas_facilities": materialization_dict["atlas_facilities"],
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
        help="Compatible frozen input directory (defaults to the current compiled CIVPROP qualification fixture).",
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
