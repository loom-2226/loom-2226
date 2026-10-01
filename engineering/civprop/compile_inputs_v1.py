#!/usr/bin/env python3
"""GAP-001 CIVPROP real-authority input compiler V1.

The compiler does two distinct things:

1. capture promoted/read-only authority into one frozen evidence artifact;
2. compile that frozen artifact into the currently locked CIVPROP runner envelope.

GAP-002 adds a versioned actor-state boundary: real scoped AUS evidence is mapped
where semantics match, generic spendable allocation remains UNKNOWN, and the old
scenario-credit/generic-capability placeholders are removed. GAP-003 replaces the
synthetic accessibility table with a versioned physics + scoped-service boundary.
GAP-004 replaces exogenous demand with causal state-derived pressure. GAP-005 adds
a versioned hybrid project-economics parameter boundary with physical/economic units,
uncertainty, scale behavior and technology-year dependence. GAP-006 promotes missions,
observations and actor-visible Bayesian knowledge updates behind a hidden-truth
firewall. GAP-007 adds read-only, reconstructable pressure-state and qualification
provenance. Later compatibility values remain explicit assumptions owned by their
registered gaps.

This keeps input assembly deterministic without laundering unresolved model
assumptions into authority.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any

_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT_FOR_IMPORT = _THIS_FILE.parents[2]
if str(_REPO_ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORT))

from engineering.civprop.contracts.project_economics_v1 import (
    ProjectEconomicsRuntime,
    load_project_economics_package,
)
from engineering.civprop.contracts.mission_knowledge_v1 import (
    load_mission_knowledge_package,
)
from engineering.civprop.contracts.pressure_observability_v1 import (
    load_pressure_observability_package,
)
from engineering.civprop.contracts.resource_mass_balance_v1 import (
    load_resource_mass_balance_package,
    load_resource_physical_realization,
)
from engineering.civprop.contracts.production_accounting_v1 import (
    load_production_accounting_package,
)
from engineering.civprop.contracts.power_balance_v1 import (
    load_power_balance_package,
)
from engineering.civprop.contracts.traffic_fleet_v1 import (
    load_traffic_fleet_package,
)


AUTHORITY_CAPTURE_FORMAT = "CIVPROP_AUTHORITY_CAPTURE_V1"
COMPILER_MANIFEST_FORMAT = "CIVPROP_INPUT_COMPILER_MANIFEST_V1"
COMPILED_FIXTURE_ID = "EARTH_LUNA_COMPILED_AUTHORITY_V1_2026_2036"
COMPILED_AUTHORITY = "COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1"

EARTH_SNAPSHOT_ID = "earth-v0-1-9934d0ac-20260925"
TIMELINE_SNAPSHOT_ID = "timeline-v0-1-0232bf23494f-20260925"
START_YEAR = 2026
END_YEAR = 2036

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
METHOD_LAB_DIR = HERE / "method_lab"
INPUT_ROOT = HERE / "inputs"
COMPILED_ROOT = HERE / "compiled_inputs" / "earth_luna_2026_2036_v1"
CANONICAL_CAPTURE_REPO_PATH = "engineering/civprop/inputs/authority_capture_v1.json"

RESOURCE_PATH = REPO_ROOT / "dev/solar_civprop_m4b/campaign_assertions.json"
FLEET_ACCESS_PATH = HERE / "civprop0/actor_access_evidence.json"
AUS_GOV_ACCESS_PATH = HERE / "civprop0/aus_government_access_evidence.json"
ROOVER_PATH = HERE / "civprop0/roover_service_envelope.json"
ROOVER_TRANSPORT_RUN_PATH = HERE / "civprop0/runs/roover_transport_mid2030_v1.json"
PROJECT_ECONOMICS_PATH = HERE / "contracts/project_economics_v1.json"
MISSION_KNOWLEDGE_PATH = HERE / "contracts/mission_knowledge_v1.json"
PRESSURE_OBSERVABILITY_PATH = (
    HERE / "contracts/pressure_observability_v1.json"
)
RESOURCE_MASS_BALANCE_PATH = (
    HERE / "contracts/resource_mass_balance_v1.json"
)
PRODUCTION_ACCOUNTING_PATH = (
    HERE / "contracts/production_accounting_v1.json"
)
EARTH_SECTOR_SCHEMA_PATH = (
    REPO_ROOT / "data/postgres/migrations/004_earth_temporal_authority.sql"
)
POWER_BALANCE_PATH = HERE / "contracts/power_balance_v1.json"
TRAFFIC_FLEET_PATH = HERE / "contracts/traffic_fleet_v1.json"
ATLAS_POWER_QUALIFICATION_PATH = (
    REPO_ROOT
    / "data/postgres/evidence/LOOM_CERES_MVP_A_FIELD_QUALIFICATION_v0.1.json"
)
RESOURCE_COVERAGE_CONTRACT_PATH = (
    REPO_ROOT
    / "dev/solar_civprop_resource_contract/RESOURCE_COVERAGE_CONTRACT_V1.json"
)
RESOURCE_STATE_CONTRACT_PATH = (
    REPO_ROOT
    / "dev/solar_civprop_resource_contract/RESOURCE_STATE_CONTRACT_V1.sql"
)
DORRINGTON_CONTRACT_PATH = (
    REPO_ROOT
    / "dev/resource_economics/dorrington_olsen/m2/DORRINGTON_OLSEN_CIVPROP_INPUT_CONTRACT.json"
)
DORRINGTON_ASSESSMENT_PATH = (
    REPO_ROOT / "reports/solar_civprop/DORRINGTON_OLSEN_M2_CIVPROP_ASSESSMENT.md"
)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def _write_json(path: Path, value: Any) -> bytes:
    payload = _json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return payload


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def default_capture_path() -> Path:
    return INPUT_ROOT / "authority_capture_v1.json"


def default_output_dir() -> Path:
    return COMPILED_ROOT


def _git_head() -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()


def _psql_json_records(database: str, queries: dict[str, str]) -> dict[str, list[dict[str, Any]]]:
    sql = ["BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;"]
    for key, query in queries.items():
        safe_key = key.replace("'", "''")
        sql.append(
            "SELECT json_build_object("
            f"'key','{safe_key}','rows',COALESCE(json_agg(t),'[]'::json))::jsonb::text "
            f"FROM ({query}) t;"
        )
    sql.append("COMMIT;")
    output = subprocess.check_output(
        [
            "psql",
            "-X",
            "-qAt",
            "-v",
            "ON_ERROR_STOP=1",
            "-d",
            database,
            "-c",
            "\n".join(sql),
        ],
        text=True,
    )
    rows: dict[str, list[dict[str, Any]]] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if "key" in item:
            rows[item["key"]] = item["rows"]
    missing = set(queries) - set(rows)
    if missing:
        raise RuntimeError(f"missing PostgreSQL capture blocks: {sorted(missing)}")
    return rows


def _validated_transport_reference(solar: dict[str, Any]) -> dict[str, Any]:
    """Admit the frozen Roo-ver transport screen as geometry/service evidence."""
    raw = ROOVER_TRANSPORT_RUN_PATH.read_bytes()
    document = json.loads(raw)
    assessment = document["assessment"]
    context = assessment["solar_context"]
    epoch = assessment["reference_epoch_utc"]

    if assessment["authority_class"] != "BOUNDED_MISSION_TRANSPORT_SCREEN":
        raise ValueError("unexpected Roo-ver transport authority class")
    if assessment["status"] != "UNKNOWN":
        raise ValueError("Roo-ver end-to-end transport screen must remain UNKNOWN")
    if epoch != "2030-07-01T00:00:00Z":
        raise ValueError("unexpected Roo-ver geometry reference epoch")
    if context["reference_epoch_utc"] != epoch:
        raise ValueError("Roo-ver Solar context epoch mismatch")

    states = (context["earth"], context["moon"])
    expected_sha = solar["ephemeris_source"]["sha256"]
    for state in states:
        provenance = state["provenance"]
        if state["epoch_utc"] != epoch:
            raise ValueError("Roo-ver state epoch mismatch")
        if state["reference_frame"] != "J2000/ECLIPTIC":
            raise ValueError("Roo-ver state frame is not qualified canonical frame")
        if state["navigation_grade"] is not True:
            raise ValueError("Roo-ver geometry state is not navigation grade")
        if provenance.get("state_source") != "LOCAL_SPICE":
            raise ValueError("Roo-ver geometry is not from qualified local SPICE")
        if provenance.get("ephemeris_source_id") != "DE440":
            raise ValueError("Roo-ver geometry is not DE440")
        if provenance.get("asset_sha256") != expected_sha:
            raise ValueError("Roo-ver DE440 hash does not match captured Solar authority")
        if provenance.get("units") != "km,km/s":
            raise ValueError("Roo-ver state units are not km,km/s")

    separation = math.dist(states[0]["position_km"], states[1]["position_km"])
    relative_speed = math.dist(states[0]["velocity_km_s"], states[1]["velocity_km_s"])
    if not math.isclose(separation, assessment["earth_moon_distance_km"], rel_tol=0, abs_tol=1e-6):
        raise ValueError("Roo-ver Earth/Moon separation does not reproduce")
    if not math.isclose(relative_speed, assessment["earth_moon_relative_speed_km_s"], rel_tol=0, abs_tol=1e-12):
        raise ValueError("Roo-ver Earth/Moon relative speed does not reproduce")

    return {
        "source_path": str(ROOVER_TRANSPORT_RUN_PATH.relative_to(REPO_ROOT)),
        "source_sha256": _sha256_bytes(raw),
        "document": document,
    }


def capture_live_authority(
    output_path: Path | None = None,
    *,
    database: str = "loom_dev",
) -> dict[str, Any]:
    """Capture the current promoted authority without writing any database."""
    output_path = Path(output_path or default_capture_path())
    queries = {
        "earth_snapshot": (
            "SELECT * FROM loom_control.snapshot "
            f"WHERE snapshot_id='{EARTH_SNAPSHOT_ID}'"
        ),
        "timeline_snapshot": (
            "SELECT * FROM loom_control.snapshot "
            f"WHERE snapshot_id='{TIMELINE_SNAPSHOT_ID}'"
        ),
        "aus_area": (
            "SELECT * FROM loom_earth.earth_area "
            f"WHERE snapshot_id='{EARTH_SNAPSHOT_ID}' AND iso3='AUS'"
        ),
        "aus_demographic": (
            "SELECT * FROM loom_earth.earth_demographic_year "
            f"WHERE snapshot_id='{EARTH_SNAPSHOT_ID}' AND iso3='AUS' "
            f"AND year BETWEEN {START_YEAR} AND {END_YEAR} ORDER BY year"
        ),
        "aus_economic": (
            "SELECT * FROM loom_earth.earth_economic_year "
            f"WHERE snapshot_id='{EARTH_SNAPSHOT_ID}' AND iso3='AUS' "
            f"AND year BETWEEN {START_YEAR} AND {END_YEAR} ORDER BY year"
        ),
        "global_2026": (
            "SELECT "
            "d.biological_population, l.legacy_employment, "
            "e.value_added AS economic_value_added, "
            "e.gross_output AS economic_gross_output, "
            "e.investment AS economic_investment, "
            "e.capital AS economic_capital "
            "FROM "
            f"(SELECT SUM(biological_population)::double precision AS biological_population "
            f" FROM loom_earth.earth_demographic_year WHERE snapshot_id='{EARTH_SNAPSHOT_ID}' AND year={START_YEAR}) d, "
            f"(SELECT SUM(legacy_employment)::double precision AS legacy_employment "
            f" FROM loom_earth.earth_legacy_labor_year WHERE snapshot_id='{EARTH_SNAPSHOT_ID}' AND year={START_YEAR}) l, "
            f"(SELECT SUM(value_added)::double precision AS value_added, "
            f"        SUM(gross_output)::double precision AS gross_output, "
            f"        SUM(investment)::double precision AS investment, "
            f"        SUM(capital)::double precision AS capital "
            f" FROM loom_earth.earth_economic_year WHERE snapshot_id='{EARTH_SNAPSHOT_ID}' AND year={START_YEAR}) e"
        ),
        "solar_bodies": (
            "SELECT * FROM loom_solar.body "
            "WHERE body_id IN ('EARTH','MOON') ORDER BY body_id"
        ),
        "solar_identifiers": (
            "SELECT * FROM loom_solar.body_identifier "
            "WHERE body_id IN ('EARTH','MOON') AND status='ACTIVE' "
            "ORDER BY body_id,authority,identifier_type"
        ),
        "ephemeris_source": (
            "SELECT * FROM loom_solar.ephemeris_source "
            "WHERE ephemeris_source_id='DE440'"
        ),
        "ephemeris_coverage": (
            "SELECT * FROM loom_solar.ephemeris_coverage "
            "WHERE body_id IN ('EARTH','MOON') "
            "AND ephemeris_source_id='DE440' ORDER BY body_id"
        ),
        "timeline_rules": (
            "SELECT * FROM loom_timeline.interpretation_rule "
            f"WHERE snapshot_id='{TIMELINE_SNAPSHOT_ID}' ORDER BY rule_key"
        ),
        "timeline_milestones": (
            "SELECT milestone_id,family,timeline_kind,authority_class,"
            "epistemic_status,reference_period,start_year,end_year,"
            "temporal_precision,capability_change_md,threshold_gate_md,"
            "basis_uncertainty_md,source_section,sort_order,notes_md "
            "FROM loom_timeline.milestone "
            f"WHERE snapshot_id='{TIMELINE_SNAPSHOT_ID}' "
            f"AND COALESCE(start_year,9999) BETWEEN {START_YEAR} AND {END_YEAR} "
            "ORDER BY sort_order,milestone_id"
        ),
    }
    rows = _psql_json_records(database, queries)

    if len(rows["earth_snapshot"]) != 1 or rows["earth_snapshot"][0]["state"] != "VALIDATED":
        raise RuntimeError("Earth snapshot is not uniquely VALIDATED")
    if len(rows["timeline_snapshot"]) != 1 or rows["timeline_snapshot"][0]["state"] != "VALIDATED":
        raise RuntimeError("Timeline snapshot is not uniquely VALIDATED")
    if len(rows["aus_area"]) != 1:
        raise RuntimeError("AUS Earth area identity not unique")
    if len(rows["aus_demographic"]) != END_YEAR - START_YEAR + 1:
        raise RuntimeError("AUS demographic horizon incomplete")
    if len(rows["aus_economic"]) != END_YEAR - START_YEAR + 1:
        raise RuntimeError("AUS economic horizon incomplete")
    if len(rows["global_2026"]) != 1:
        raise RuntimeError("global 2026 aggregate capture failed")
    if {x["body_id"] for x in rows["solar_bodies"]} != {"EARTH", "MOON"}:
        raise RuntimeError("Earth/Moon Solar body identity incomplete")
    if len(rows["ephemeris_source"]) != 1:
        raise RuntimeError("DE440 source not unique")
    if rows["ephemeris_source"][0]["status"] != "QUALIFIED":
        raise RuntimeError("DE440 source is not QUALIFIED")
    if not rows["ephemeris_source"][0]["navigation_grade"]:
        raise RuntimeError("DE440 source is not navigation grade")

    campaign = json.loads(RESOURCE_PATH.read_text())
    assertion = next(
        x for x in campaign["evidence_assertions"]
        if x["key"] == "MOON_POLAR_WATER_ICE"
    )
    fleet_access = json.loads(FLEET_ACCESS_PATH.read_text())
    aus_government_access = json.loads(AUS_GOV_ACCESS_PATH.read_text())
    roover = json.loads(ROOVER_PATH.read_text())
    solar_capture = {
        "bodies": rows["solar_bodies"],
        "identifiers": rows["solar_identifiers"],
        "ephemeris_source": rows["ephemeris_source"][0],
        "ephemeris_coverage": rows["ephemeris_coverage"],
    }
    transport_reference = _validated_transport_reference(solar_capture)
    project_economics = json.loads(PROJECT_ECONOMICS_PATH.read_text())
    load_project_economics_package(project_economics)
    mission_knowledge = json.loads(MISSION_KNOWLEDGE_PATH.read_text())
    load_mission_knowledge_package(mission_knowledge)
    pressure_observability = json.loads(
        PRESSURE_OBSERVABILITY_PATH.read_text()
    )
    load_pressure_observability_package(pressure_observability)
    resource_mass_balance = json.loads(
        RESOURCE_MASS_BALANCE_PATH.read_text()
    )
    load_resource_mass_balance_package(resource_mass_balance)
    production_accounting = json.loads(
        PRODUCTION_ACCOUNTING_PATH.read_text()
    )
    load_production_accounting_package(production_accounting)
    power_balance = json.loads(POWER_BALANCE_PATH.read_text())
    load_power_balance_package(power_balance)
    traffic_fleet = json.loads(TRAFFIC_FLEET_PATH.read_text())
    load_traffic_fleet_package(traffic_fleet)

    source_paths = [
        RESOURCE_PATH,
        FLEET_ACCESS_PATH,
        AUS_GOV_ACCESS_PATH,
        ROOVER_PATH,
        ROOVER_TRANSPORT_RUN_PATH,
        PROJECT_ECONOMICS_PATH,
        MISSION_KNOWLEDGE_PATH,
        PRESSURE_OBSERVABILITY_PATH,
        RESOURCE_MASS_BALANCE_PATH,
        PRODUCTION_ACCOUNTING_PATH,
        EARTH_SECTOR_SCHEMA_PATH,
        POWER_BALANCE_PATH,
        TRAFFIC_FLEET_PATH,
        ATLAS_POWER_QUALIFICATION_PATH,
        RESOURCE_COVERAGE_CONTRACT_PATH,
        RESOURCE_STATE_CONTRACT_PATH,
        DORRINGTON_CONTRACT_PATH,
        DORRINGTON_ASSESSMENT_PATH,
        METHOD_LAB_DIR / "scenario_v1.json",
        METHOD_LAB_DIR / "truth_v1.json",
        REPO_ROOT / "data/postgres/earth_temporal_projection_manifest.json",
        REPO_ROOT / "data/postgres/timeline_projection_manifest.json",
        REPO_ROOT / "docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md",
    ]
    source_hashes = {
        str(path.relative_to(REPO_ROOT)): _sha256_path(path)
        for path in source_paths
    }
    query_hashes = {
        key: _sha256_bytes(query.encode())
        for key, query in queries.items()
    }

    capture = {
        "format": AUTHORITY_CAPTURE_FORMAT,
        "capture_id": "EARTH_LUNA_AUTHORITY_CAPTURE_V1_2026_2036",
        "captured_for_gap": (
            "GAP-001_REAL_INPUT_COMPILER_PLUS_GAP-002_ACTOR_STATE_AND_BUDGETS"
            "_PLUS_GAP-003_TRANSPORT_ACCESSIBILITY_PLUS_GAP-004_DEMAND_PRESSURE"
            "_PLUS_GAP-005_PROJECT_ECONOMICS_PLUS_GAP-006_MISSIONS_KNOWLEDGE"
            "_PLUS_GAP-007_PRESSURE_OBSERVABILITY"
            "_PLUS_GAP-008_RESOURCE_MASS_BALANCE"
            "_PLUS_GAP-009_PRODUCTION_ACCOUNTING"
            "_PLUS_GAP-010_POWER_BALANCE"
            "_PLUS_GAP-011_TRAFFIC_FLEET"
        ),
        "capture_semantics": (
            "READ_ONLY_PROMOTED_AUTHORITY_PLUS_REPOSITORY_EVIDENCE_NO_DATABASE_WRITES"
        ),
        "source_basis_commit": _git_head(),
        "postgres_database": database,
        "postgres_query_sha256": query_hashes,
        "source_file_sha256": source_hashes,
        "earth": {
            "snapshot": rows["earth_snapshot"][0],
            "aus_area": rows["aus_area"][0],
            "global_2026": rows["global_2026"][0],
            "aus_demographic_2026_2036": rows["aus_demographic"],
            "aus_economic_2026_2036": rows["aus_economic"],
        },
        "solar": solar_capture,
        "transport": {
            "roover_reference": transport_reference,
        },
        "model_parameters": {
            "project_economics_v1": project_economics,
            "project_economics_source": {
                "path": str(PROJECT_ECONOMICS_PATH.relative_to(REPO_ROOT)),
                "sha256": _sha256_path(PROJECT_ECONOMICS_PATH),
            },
            "mission_knowledge_v1": mission_knowledge,
            "mission_knowledge_source": {
                "path": str(MISSION_KNOWLEDGE_PATH.relative_to(REPO_ROOT)),
                "sha256": _sha256_path(MISSION_KNOWLEDGE_PATH),
            },
            "pressure_observability_v1": pressure_observability,
            "pressure_observability_source": {
                "path": str(
                    PRESSURE_OBSERVABILITY_PATH.relative_to(REPO_ROOT)
                ),
                "sha256": _sha256_path(PRESSURE_OBSERVABILITY_PATH),
            },
            "resource_mass_balance_v1": resource_mass_balance,
            "resource_mass_balance_source": {
                "path": str(
                    RESOURCE_MASS_BALANCE_PATH.relative_to(REPO_ROOT)
                ),
                "sha256": _sha256_path(RESOURCE_MASS_BALANCE_PATH),
            },
            "production_accounting_v1": production_accounting,
            "production_accounting_source": {
                "path": str(
                    PRODUCTION_ACCOUNTING_PATH.relative_to(REPO_ROOT)
                ),
                "sha256": _sha256_path(PRODUCTION_ACCOUNTING_PATH),
            },
            "earth_accounting_semantics": {
                "path": str(
                    EARTH_SECTOR_SCHEMA_PATH.relative_to(REPO_ROOT)
                ),
                "sha256": _sha256_path(EARTH_SECTOR_SCHEMA_PATH),
                "transfer_scope": (
                    "FIELD_NAMES_AND_ACCOUNTING_IDENTITIES_ONLY_"
                    "NO_OFFWORLD_PRICE_PRODUCTIVITY_OR_UTILIZATION_COPY"
                ),
            },
            "power_balance_v1": power_balance,
            "power_balance_source": {
                "path": str(POWER_BALANCE_PATH.relative_to(REPO_ROOT)),
                "sha256": _sha256_path(POWER_BALANCE_PATH),
            },
            "atlas_power_field_semantics": {
                "path": str(
                    ATLAS_POWER_QUALIFICATION_PATH.relative_to(REPO_ROOT)
                ),
                "sha256": _sha256_path(
                    ATLAS_POWER_QUALIFICATION_PATH
                ),
                "transfer_scope": (
                    "FIELD_IDENTITIES_ONLY_RUNTIME_POWER_BALANCE_"
                    "NOW_DEFINES_AVERAGE_AND_PEAK_LOAD"
                ),
            },
            "traffic_fleet_v1": traffic_fleet,
            "traffic_fleet_source": {
                "path": str(
                    TRAFFIC_FLEET_PATH.relative_to(REPO_ROOT)
                ),
                "sha256": _sha256_path(TRAFFIC_FLEET_PATH),
            },
            "atlas_traffic_field_semantics": {
                "path": str(
                    ATLAS_POWER_QUALIFICATION_PATH.relative_to(REPO_ROOT)
                ),
                "sha256": _sha256_path(
                    ATLAS_POWER_QUALIFICATION_PATH
                ),
                "transfer_scope": (
                    "NODE_INCIDENCE_FIELD_IDENTITIES_ONLY_NO_2026_"
                    "TRAFFIC_OR_FLEET_VALUES_IMPORTED"
                ),
            },
            "resource_state_contracts": {
                "coverage_path": str(
                    RESOURCE_COVERAGE_CONTRACT_PATH.relative_to(REPO_ROOT)
                ),
                "coverage_sha256": _sha256_path(
                    RESOURCE_COVERAGE_CONTRACT_PATH
                ),
                "state_view_path": str(
                    RESOURCE_STATE_CONTRACT_PATH.relative_to(REPO_ROOT)
                ),
                "state_view_sha256": _sha256_path(
                    RESOURCE_STATE_CONTRACT_PATH
                ),
            },
            "dorrington_olsen_boundary": {
                "contract_path": str(DORRINGTON_CONTRACT_PATH.relative_to(REPO_ROOT)),
                "contract_sha256": _sha256_path(DORRINGTON_CONTRACT_PATH),
                "assessment_path": str(DORRINGTON_ASSESSMENT_PATH.relative_to(REPO_ROOT)),
                "assessment_sha256": _sha256_path(DORRINGTON_ASSESSMENT_PATH),
            },
        },
        "timeline": {
            "snapshot": rows["timeline_snapshot"][0],
            "interpretation_rules": rows["timeline_rules"],
            "milestones_2026_2036": rows["timeline_milestones"],
        },
        "resource": {
            "assertion": assertion,
            "source_path": str(RESOURCE_PATH.relative_to(REPO_ROOT)),
            "source_sha256": _sha256_path(RESOURCE_PATH),
        },
        "actor": {
            "earth_area": rows["aus_area"][0],
            "fleet_access": fleet_access,
            "aus_government_access": aus_government_access,
            "roover_service": roover,
            "source_paths": {
                "fleet_access": str(FLEET_ACCESS_PATH.relative_to(REPO_ROOT)),
                "aus_government_access": str(AUS_GOV_ACCESS_PATH.relative_to(REPO_ROOT)),
                "roover_service": str(ROOVER_PATH.relative_to(REPO_ROOT)),
            },
        },
    }
    _write_json(output_path, capture)
    return capture


def _assumption_register() -> list[dict[str, str]]:
    return [
        {
            "assumption_id": "ASSUME-GAP012-OFFWORLD-INITIAL-STATE",
            "gap_id": "GAP-012",
            "status": "EXPLICIT_PLACEHOLDER",
            "semantics": (
                "Initial Earth-orbit/Luna/cislunar engine capacities remain compatibility "
                "values inherited from the Method Lab and migrated into explicit physical units; "
                "the unit adapter does not make them a compiled empirical 2026 infrastructure inventory."
            ),
        },
        {
            "assumption_id": "ASSUME-GAP014-EARTH-HABITAT-FLOOR",
            "gap_id": "GAP-014",
            "status": "COMPATIBILITY_BOUNDARY",
            "semantics": (
                "EARTH_SURFACE habitat is set equal to compiled 2026 biological population "
                "so the engine does not reject its inherited terrestrial population. This "
                "is a boundary-capacity floor, not an inventory of terrestrial beds/housing."
            ),
        },
    ]


def _compile_actor_state(capture: dict[str, Any]) -> dict[str, Any]:
    """Compile only actor facts supported by admitted AUS evidence; unknowns stay unknown."""
    actor = capture["actor"]
    government = actor["aus_government_access"]["case"]
    roover = actor["roover_service"]
    source_ids = [x["id"] for x in government["sources"]]
    area = actor["earth_area"]

    return {
        "format": "CIVPROP_ACTOR_STATE_V1",
        "contract_version": "1.0.0",
        "as_of_year": START_YEAR,
        "actors": [
            {
                "actor_id": "AUS",
                "actor_type": "STATE",
                "identity": {
                    "display_name": area["display_name"],
                    "provenance_refs": [
                        f"loom_earth:{area['snapshot_id']}:earth_area:AUS"
                    ],
                },
                "budget": {
                    "spendable_allocation": {
                        "status": "UNKNOWN",
                        "amount": None,
                        "unit": None,
                        "scope": "GENERAL_CIVPROP_PROJECT_DECISION_BUDGET",
                        "provenance_refs": [],
                    },
                    "committed_funds": [
                        {
                            "commitment_id": "AUS_ROOVER_42M_COMMITMENT",
                            "status": "OBSERVED_COMMITTED",
                            "amount": 42000000,
                            "unit": "AUD",
                            "scope": "ROO_VER_DEVELOPMENT_BUILD_OPERATION",
                            "provenance_refs": [
                                "AUS_GOV_2025_08_29_ROO_VER_MISSION"
                            ],
                        }
                    ],
                },
                "ownership": {"status": "UNKNOWN", "records": []},
                "operation": {
                    "status": "KNOWN_RECORDS",
                    "records": [
                        {
                            "record_id": "AUS_ROOVER_OPERATION_RELATIONSHIP",
                            "subject_id": "ROO_VER",
                            "status": "OBSERVED_OPERATOR_RELATIONSHIP",
                            "scope": "ROO_VER_DEVELOPMENT_AND_REMOTE_SURFACE_OPERATION",
                            "counterparty_id": "ELO2",
                            "valid_from": 2025,
                            "valid_to": None,
                            "provenance_refs": [
                                "AUS_GOV_2025_08_29_ROO_VER_MISSION"
                            ],
                        }
                    ],
                },
                "access_rights": {
                    "status": "KNOWN_RECORDS",
                    "records": [
                        {
                            "record_id": "AUS_ROOVER_CLPS_ACCESS",
                            "subject_id": "ROO_VER",
                            "status": "OBSERVED_SCOPED_ACCESS",
                            "scope": government["scope"],
                            "counterparty_id": government["partner_id"],
                            "provider_id": government["provider_id"],
                            "capability_id": government["capability"],
                            "valid_from": int(government["observed_from"][:4]),
                            "valid_to": None,
                            "provenance_refs": source_ids,
                        }
                    ],
                },
                "contracts": {
                    "status": "KNOWN_RECORDS",
                    "records": [
                        {
                            "record_id": "AUS_NASA_ROVER_AGREEMENT",
                            "subject_id": "ROO_VER",
                            "status": "OBSERVED_ROVER_SPECIFIC_AGREEMENT",
                            "scope": "ROVER_SPECIFIC_FUTURE_LUNAR_MISSION",
                            "counterparty_id": "NASA",
                            "valid_from": 2021,
                            "valid_to": None,
                            "provenance_refs": [
                                "NASA_2021_10_12_AUSTRALIA_ROVER_AGREEMENT"
                            ],
                        }
                    ],
                },
                "provider_service_access": {
                    "status": "KNOWN_RECORDS",
                    "records": [
                        {
                            "record_id": "AUS_ROOVER_IM5_PROVIDER_PATH",
                            "subject_id": roover["payload_id"],
                            "status": "OBSERVED_INDIRECT_PROVIDER_SERVICE_PATH",
                            "scope": roover["service_path"],
                            "counterparty_id": "NASA",
                            "provider_id": government["provider_id"],
                            "capability_id": government["capability"],
                            "valid_from": START_YEAR,
                            "valid_to": None,
                            "provenance_refs": source_ids,
                            "target_landing_year": roover["target_landing_year"],
                        }
                    ],
                },
                "installed_capability": {"status": "UNKNOWN", "records": []},
                "acquired_capability": {"status": "UNKNOWN", "records": []},
                "experience": {
                    "status": "KNOWN_RECORDS",
                    "records": [
                        {
                            "record_id": "AUS_ROOVER_2026_TESTING",
                            "subject_id": "ROO_VER",
                            "status": "OBSERVED_DEVELOPMENT_TESTING",
                            "scope": "TERRESTRIAL_ROVER_MOBILITY_AND_INTEGRATION_TESTING",
                            "counterparty_id": "ELO2",
                            "valid_from": START_YEAR,
                            "valid_to": None,
                            "provenance_refs": [
                                "ASA_2026_08_13_ROO_VER_TESTING"
                            ],
                        }
                    ],
                },
                "owned_infrastructure": {"status": "UNKNOWN", "records": []},
                "relationships": {
                    "status": "KNOWN_RECORDS",
                    "records": [
                        {
                            "record_id": "AUS_NASA_ROOVER_PARTNERSHIP",
                            "subject_id": "ROO_VER",
                            "status": "OBSERVED_MISSION_PARTNERSHIP",
                            "scope": "ROO_VER_CLPS_CT4",
                            "counterparty_id": "NASA",
                            "valid_from": 2021,
                            "valid_to": None,
                            "provenance_refs": [
                                "NASA_2021_10_12_AUSTRALIA_ROVER_AGREEMENT",
                                "NASA_2026_03_27_CLPS_CT4_ROO_VER",
                            ],
                        }
                    ],
                },
            }
        ],
        "events": [],
    }


def _compile_accessibility(capture: dict[str, Any]) -> dict[str, Any]:
    """Compile qualified geometry plus scoped service evidence; unknown stays unknown."""
    reference = capture["transport"]["roover_reference"]
    run = reference["document"]
    assessment = run["assessment"]
    context = assessment["solar_context"]
    roover = capture["actor"]["roover_service"]
    government = capture["actor"]["aus_government_access"]["case"]

    constraints: list[str] = []
    for segment in assessment["segments"]:
        if segment["status"] != "FEASIBLE":
            constraints.extend(
                f"{segment['name']}:{item}"
                for item in segment.get("unresolved", ())
            )
    constraints.append("END_TO_END_TRANSPORT_REMAINS_UNKNOWN")

    provenance = [
        f"ROOVER_TRANSPORT_RUN_SHA256:{reference['source_sha256']}",
        f"SERVICE_EVIDENCE:{assessment['service_evidence_id']}:{assessment['service_evidence_sha256']}",
        f"DE440:{capture['solar']['ephemeris_source']['sha256']}",
    ]
    return {
        "format": "CIVPROP_ACCESSIBILITY_V1",
        "contract_version": "1.0.0",
        "epoch_policy": "ANNUAL_REFERENCE_EPOCH_JULY_01_UTC",
        "location_bindings": [
            {"location_id": "EARTH_SURFACE", "body_id": "EARTH"},
            {"location_id": "EARTH_ORBIT", "body_id": "EARTH"},
            {"location_id": "LUNA_SURFACE", "body_id": "MOON"},
            {"location_id": "CISLUNAR_FREE_SPACE", "body_id": None},
        ],
        "geometry_samples": [
            {
                "origin_body_id": "EARTH",
                "destination_body_id": "MOON",
                "epoch_utc": assessment["reference_epoch_utc"],
                "straight_line_separation_km": assessment["earth_moon_distance_km"],
                "relative_speed_km_s": assessment["earth_moon_relative_speed_km_s"],
                "uncertainty_km": context["earth"]["provenance"].get("uncertainty_km"),
                "reference_frame": context["earth"]["reference_frame"],
                "source_status": "QUALIFIED",
                "navigation_grade": True,
                "provenance_refs": provenance,
            }
        ],
        "service_paths": [
            {
                "service_id": "AUS_ROOVER_CLPS_CT4_IM5",
                "actor_id": "AUS",
                "provider_id": government["provider_id"],
                "subject_id": roover["payload_id"],
                "origin_location_id": "EARTH_SURFACE",
                "destination_location_id": "LUNA_SURFACE",
                "mission_class": "NAMED_PAYLOAD_DELIVERY",
                "service_class": "CLPS_LUNAR_DELIVERY",
                "valid_from_year": START_YEAR,
                "valid_to_year": None,
                "target_year": roover["target_landing_year"],
                "status": assessment["status"],
                "limiting_constraints": constraints,
                "provenance_refs": provenance,
                "required_technology_ids": [],
                "cost_components": [
                    {
                        "component_id": "ROUTE_LENGTH",
                        "status": "UNKNOWN",
                        "value": None,
                        "unit": "km",
                        "uncertainty": None,
                    },
                    {
                        "component_id": "TRANSFER_DURATION",
                        "status": "UNKNOWN",
                        "value": None,
                        "unit": "s",
                        "uncertainty": None,
                    },
                    {
                        "component_id": "DELTA_V",
                        "status": "UNKNOWN",
                        "value": None,
                        "unit": "km/s",
                        "uncertainty": None,
                    },
                    {
                        "component_id": "SERVICE_PRICE",
                        "status": "UNKNOWN",
                        "value": None,
                        "unit": "currency/service-unit",
                        "uncertainty": None,
                    },
                ],
                "generalized_cost": {
                    "status": "UNKNOWN",
                    "value": None,
                    "unit": None,
                    "uncertainty": None,
                },
            }
        ],
    }


def _compile_demand_pressure() -> dict[str, Any]:
    """Compile causal stock-flow demand/pressure parameters; no annual demand curves."""
    return {
        "format": "CIVPROP_DEMAND_PRESSURE_V1",
        "contract_version": "1.0.0",
        "scope": "NON_EARTH_SURFACE",
        "excluded_location_ids": ["EARTH_SURFACE"],
        "parameter_status": "UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1",
        "channels": [
            {
                "channel_id": "HABITAT",
                "unit": "person",
                "available_field": "habitat",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {
                        "field": "biological_population",
                        "coefficient": 1.0,
                        "coefficient_unit": "person/person",
                    },
                    {
                        "field": "transient_population",
                        "coefficient": 1.0,
                        "coefficient_unit": "person/person",
                    },
                ],
            },
            {
                "channel_id": "TRANSPORT",
                "unit": "tonnes/year",
                "available_field": "transport",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {
                        "field": "transient_population",
                        "coefficient": 4.0,
                        "coefficient_unit": "tonnes/year/person",
                    }
                ],
            },
            {
                "channel_id": "INDUSTRIAL",
                "unit": "tonnes/year",
                "available_field": "industrial",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {
                        "field": "workforce",
                        "coefficient": 4.0,
                        "coefficient_unit": "tonnes/year/person",
                    }
                ],
            },
            {
                "channel_id": "RESOURCE",
                "unit": "tonnes/year",
                "available_field": "resource",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {
                        "field": "biological_population",
                        "coefficient": 1.0,
                        "coefficient_unit": "tonnes/year/person",
                    },
                    {
                        "field": "transient_population",
                        "coefficient": 1.0,
                        "coefficient_unit": "tonnes/year/person",
                    },
                ],
            },
            {
                "channel_id": "POWER",
                "unit": "MW",
                "available_field": "power",
                "decay": 0.60,
                "gain": 0.24,
                "drivers": [
                    {
                        "field": "biological_population",
                        "coefficient": 0.025,
                        "coefficient_unit": "MW/person",
                    },
                    {
                        "field": "transient_population",
                        "coefficient": 0.025,
                        "coefficient_unit": "MW/person",
                    },
                ],
            },
        ],
        # Real commitments are not assigned numeric infrastructure requirements
        # unless the admitted evidence actually supplies one. Roo-ver therefore
        # does not silently become generic logistics demand.
        "strategic_requirements": [],
    }


def _compile_project_economics(capture: dict[str, Any]) -> dict[str, Any]:
    raw = copy.deepcopy(capture["model_parameters"]["project_economics_v1"])
    load_project_economics_package(raw)
    return raw


def _compile_mission_knowledge(capture: dict[str, Any]) -> dict[str, Any]:
    raw = copy.deepcopy(capture["model_parameters"]["mission_knowledge_v1"])
    load_mission_knowledge_package(raw)
    return raw


def _compile_pressure_observability(
    capture: dict[str, Any],
) -> dict[str, Any]:
    raw = copy.deepcopy(
        capture["model_parameters"]["pressure_observability_v1"]
    )
    load_pressure_observability_package(raw)
    return raw


def _compile_resource_mass_balance(
    capture: dict[str, Any],
) -> dict[str, Any]:
    raw = copy.deepcopy(
        capture["model_parameters"]["resource_mass_balance_v1"]
    )
    load_resource_mass_balance_package(raw)
    return raw


def _compile_production_accounting(
    capture: dict[str, Any],
) -> dict[str, Any]:
    raw = copy.deepcopy(
        capture["model_parameters"]["production_accounting_v1"]
    )
    load_production_accounting_package(raw)
    return raw


def _compile_power_balance(
    capture: dict[str, Any],
) -> dict[str, Any]:
    raw = copy.deepcopy(
        capture["model_parameters"]["power_balance_v1"]
    )
    load_power_balance_package(raw)
    return raw


def _compile_traffic_fleet(
    capture: dict[str, Any],
) -> dict[str, Any]:
    raw = copy.deepcopy(
        capture["model_parameters"]["traffic_fleet_v1"]
    )
    load_traffic_fleet_package(raw)
    return raw


def _compile_resource_physical_realization(
    capture: dict[str, Any],
) -> dict[str, Any]:
    assertion = capture["resource"]["assertion"]
    if assertion["key"] != "MOON_POLAR_WATER_ICE":
        raise ValueError("unexpected lunar resource assertion")
    if assertion["abundance_semantics"] != "PRESENT_UNQUANTIFIED":
        raise ValueError(
            "GAP-008 default physical boundary expects unquantified abundance"
        )
    raw = {
        "format": "CIVPROP_RESOURCE_PHYSICAL_REALIZATION_V1",
        "contract_version": "1.0.0",
        "resources": [
            {
                "resource_id": "MOON_POLAR_WATER",
                "location_id": "LUNA_SURFACE",
                "realization_status": "UNKNOWN",
                "stock_status": "UNKNOWN",
                "opening_stock_tonnes": None,
                "grade_status": "UNKNOWN",
                "grade_mass_fraction": None,
                "inventory_status": "UNKNOWN",
                "opening_inventory_tonnes": None,
                "provenance_refs": [
                    "dev/solar_civprop_m4b/campaign_assertions.json#MOON_POLAR_WATER_ICE",
                    "dev/solar_civprop_resource_contract/RESOURCE_STATE_CONTRACT_V1.sql",
                    "dev/solar_civprop_resource_contract/RESOURCE_COVERAGE_CONTRACT_V1.json",
                ],
            }
        ],
    }
    load_resource_physical_realization(raw)
    return raw


def _migrate_capacity_units(scenario: dict[str, Any]) -> None:
    """Replace Method Lab normalized capacity units with explicit physical units."""
    multipliers = {
        "power": 1.0,
        "resource": 100.0,
        "industrial": 100.0,
        "habitat": 1.0,
        "shipyard": 100.0,
        "transport": 100.0,
    }
    for location in scenario["locations"]:
        capacities = location["initial_state"]["capacities"]
        for dimension, factor in multipliers.items():
            capacities[dimension] = float(capacities.get(dimension, 0.0)) * factor

    scenario["units"].update(
        {
            "capacity": "dimension_specific_physical_units",
            "power": "MW",
            "resource": "tonnes/year",
            "industrial": "tonnes/year",
            "habitat": "person",
            "shipyard": "tonnes/year",
            "transport": "tonnes/year",
            "project_capital": "USD_2026_billion",
        }
    )


def _apply_project_economics(
    scenario: dict[str, Any],
    package_raw: dict[str, Any],
) -> None:
    package = load_project_economics_package(package_raw)
    runtime = ProjectEconomicsRuntime(package)
    for project in scenario["project_archetypes"]:
        resolved = runtime.resolve(
            project["project_archetype_id"],
            year=START_YEAR,
        )
        project["capital_cost"] = resolved.capital_cost
        project["construction_lag_years"] = resolved.construction_lag_years
        project["output_capacities"] = dict(resolved.output_capacities)
        project["minimum_input_capacities"] = dict(
            resolved.minimum_input_capacities
        )
    scenario["project_economics_v1"] = package_raw


def _compile_scenario(capture: dict[str, Any]) -> dict[str, Any]:
    base = json.loads((METHOD_LAB_DIR / "scenario_v1.json").read_text())
    scenario = copy.deepcopy(base)
    scenario["fixture_id"] = COMPILED_FIXTURE_ID
    scenario["classification"] = (
        "COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1"
    )

    global_2026 = capture["earth"]["global_2026"]
    earth = next(
        x for x in scenario["locations"] if x["location_id"] == "EARTH_SURFACE"
    )
    earth["initial_state"]["biological_population"] = global_2026[
        "biological_population"
    ]
    earth["initial_state"]["workforce"] = global_2026["legacy_employment"]
    earth["initial_state"]["capacities"]["habitat"] = global_2026[
        "biological_population"
    ]
    _migrate_capacity_units(scenario)

    scenario["actors"] = [{"actor_id": "AUS", "actor_type": "STATE"}]
    scenario["actor_state_v1"] = _compile_actor_state(capture)
    scenario["actor_capability"] = []
    scenario["accessibility_v1"] = _compile_accessibility(capture)
    scenario.pop("accessibility", None)
    scenario["demand_pressure_v1"] = _compile_demand_pressure()
    scenario.pop("demand_signals", None)
    project_economics = _compile_project_economics(capture)
    _apply_project_economics(scenario, project_economics)

    belief = copy.deepcopy(base["resource_beliefs"][0])
    belief["evidence_status"] = "EMPIRICAL_PRESENCE_PLUS_SCENARIO_PRIOR"
    scenario["resource_beliefs"] = [belief]

    mission_knowledge = _compile_mission_knowledge(capture)
    scenario["mission_knowledge_v1"] = mission_knowledge
    scenario["pressure_observability_v1"] = (
        _compile_pressure_observability(capture)
    )
    scenario["resource_mass_balance_v1"] = (
        _compile_resource_mass_balance(capture)
    )
    scenario["production_accounting_v1"] = (
        _compile_production_accounting(capture)
    )
    scenario["power_balance_v1"] = _compile_power_balance(capture)
    scenario["traffic_fleet_v1"] = _compile_traffic_fleet(capture)
    scenario["project_archetypes"] = [
        project
        for project in scenario["project_archetypes"]
        if project["project_kind"] != "MISSION"
    ]

    scenario["authority_context"] = {
        "compiler": {
            "compiler_contract": "CIVPROP_INPUT_COMPILER_V1",
            "gap_resolution": {
                "GAP-001": "CLOSED",
                "GAP-002": "CLOSED",
                "GAP-003": "CLOSED",
                "GAP-004": "CLOSED",
                "GAP-005": "CLOSED",
                "GAP-006": "CLOSED",
                "GAP-007": "CLOSED",
                "GAP-008": "CLOSED",
                "GAP-009": "CLOSED",
                "GAP-010": "CLOSED",
                "GAP-011": "CLOSED",
            },
            "compatibility_envelope": (
                "CIVPROP_METHOD_LAB_SCENARIO_V1 retained for locked runner compatibility"
            ),
            "engine_consumption_note": (
                "Authority context is frozen/provenanced in runtime input but HYBRID_V1 "
                "currently consumes only fields represented in the compatibility envelope."
            ),
        },
        "earth": {
            "snapshot": capture["earth"]["snapshot"],
            "aus_area": capture["earth"]["aus_area"],
            "global_2026": capture["earth"]["global_2026"],
            "aus_demographic_2026_2036": capture["earth"][
                "aus_demographic_2026_2036"
            ],
            "aus_economic_2026_2036": capture["earth"]["aus_economic_2026_2036"],
        },
        "solar": capture["solar"],
        "transport": capture["transport"],
        "model_parameters": capture["model_parameters"],
        "timeline": capture["timeline"],
        "resource": capture["resource"],
        "actor": capture["actor"],
    }
    scenario["assumption_register"] = _assumption_register()
    return scenario


def _compile_truth(capture: dict[str, Any]) -> dict[str, Any]:
    truth = json.loads((METHOD_LAB_DIR / "truth_v1.json").read_text())
    truth["fixture_id"] = COMPILED_FIXTURE_ID
    truth["classification"] = (
        "EVALUATOR_ONLY_SYNTHETIC_TRUTH_FOR_COMPATIBILITY_NOT_RUNTIME_AUTHORITY"
    )
    truth["notes"] = [
        "Actor decisions never consume this evaluator-only realization directly.",
        "Mission/Knowledge V1 permits only the observation runtime to read the legacy hidden present/absent realization when an admitted mission executes.",
        "The legacy present/grade_index values remain synthetic Mission/Knowledge compatibility truth and are not Resource Mass Balance stock or grade.",
        "Resource Mass Balance V1 uses the separate evaluator physical-realization boundary below; the default lunar stock, grade and inventory remain UNKNOWN.",
    ]
    truth["resource_physical_realization_v1"] = (
        _compile_resource_physical_realization(capture)
    )
    return truth


def compile_from_capture(
    capture_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    capture_path = Path(capture_path or default_capture_path())
    output_dir = Path(output_dir or default_output_dir())
    capture = json.loads(capture_path.read_text())
    if capture.get("format") != AUTHORITY_CAPTURE_FORMAT:
        raise ValueError("unexpected authority capture format")

    scenario = _compile_scenario(capture)
    truth = _compile_truth(capture)

    output_dir.mkdir(parents=True, exist_ok=True)
    scenario_bytes = _write_json(output_dir / "scenario_v1.json", scenario)
    truth_bytes = _write_json(output_dir / "truth_v1.json", truth)
    scenario_sha = _sha256_bytes(scenario_bytes)
    truth_sha = _sha256_bytes(truth_bytes)
    bundle_sha = _sha256_bytes(scenario_bytes + b"\n" + truth_bytes)

    manifest = {
        "format": "CIVPROP_METHOD_LAB_BUNDLE_V1",
        "fixture_id": COMPILED_FIXTURE_ID,
        "scenario_file": "scenario_v1.json",
        "truth_file": "truth_v1.json",
        "sha256": {
            "scenario_v1.json": scenario_sha,
            "truth_v1.json": truth_sha,
        },
        "bundle_sha256": bundle_sha,
        "basis": {
            "compiler_contract": "CIVPROP_INPUT_COMPILER_V1",
            "authority_capture_id": capture["capture_id"],
            "authority_capture_sha256": _sha256_path(capture_path),
            "source_basis_commit": capture["source_basis_commit"],
            "locked_runner_ref": "engineering/civprop/run_civprop_v1.py",
        },
        "authority": COMPILED_AUTHORITY,
    }
    manifest_bytes = _write_json(output_dir / "manifest_v1.json", manifest)

    gap_resolution = {f"GAP-{i:03d}": "OPEN" for i in range(1, 16)}
    gap_resolution["GAP-001"] = "CLOSED"
    gap_resolution["GAP-002"] = "CLOSED"
    gap_resolution["GAP-003"] = "CLOSED"
    gap_resolution["GAP-004"] = "CLOSED"
    gap_resolution["GAP-005"] = "CLOSED"
    gap_resolution["GAP-006"] = "CLOSED"
    gap_resolution["GAP-007"] = "CLOSED"
    gap_resolution["GAP-008"] = "CLOSED"
    gap_resolution["GAP-009"] = "CLOSED"
    gap_resolution["GAP-010"] = "CLOSED"
    gap_resolution["GAP-011"] = "CLOSED"
    compiler_manifest = {
        "format": COMPILER_MANIFEST_FORMAT,
        "compiler_id": "CIVPROP_INPUT_COMPILER_V1",
        "compiler_version": "1.10.0",
        "compiler_source_sha256": _sha256_path(HERE / "compile_inputs_v1.py"),
        "runtime_input": {
            "fixture_id": COMPILED_FIXTURE_ID,
            "scenario_format": scenario["format"],
            "scenario_sha256": scenario_sha,
            "bundle_sha256": bundle_sha,
            "authority": COMPILED_AUTHORITY,
        },
        "authority_capture": {
            "capture_id": capture["capture_id"],
            "path": CANONICAL_CAPTURE_REPO_PATH,
            "sha256": _sha256_path(capture_path),
            "source_basis_commit": capture["source_basis_commit"],
        },
        "source_snapshots": {
            "earth": capture["earth"]["snapshot"],
            "timeline": capture["timeline"]["snapshot"],
            "solar_ephemeris": {
                "ephemeris_source_id": capture["solar"]["ephemeris_source"][
                    "ephemeris_source_id"
                ],
                "sha256": capture["solar"]["ephemeris_source"]["sha256"],
                "status": capture["solar"]["ephemeris_source"]["status"],
                "navigation_grade": capture["solar"]["ephemeris_source"][
                    "navigation_grade"
                ],
            },
        },
        "source_file_sha256": capture["source_file_sha256"],
        "postgres_query_sha256": capture["postgres_query_sha256"],
        "gap_resolution": gap_resolution,
        "assumption_register": scenario["assumption_register"],
        "package_files": {
            "scenario_v1.json": scenario_sha,
            "truth_v1.json": truth_sha,
            "manifest_v1.json": _sha256_bytes(manifest_bytes),
        },
        "semantics": {
            "gap1_closed_means": (
                "Promoted Earth/Solar/Timeline/resource/actor authority is captured "
                "read-only, frozen with hashes, and deterministically compiled into the "
                "locked runner envelope. Other open gaps remain explicit placeholders."
            ),
            "gap2_closed_means": (
                "A versioned Actor State V1 separates identity, scoped rights/contracts, "
                "provider access, capability, experience and finance. AUS generic spendable "
                "allocation is explicitly UNKNOWN; the observed AUD 42 million Roo-ver "
                "commitment remains scoped and cannot fund generic CIVPROP projects."
            ),
            "gap3_closed_means": (
                "A versioned Accessibility V1 boundary combines qualified frozen Solar geometry "
                "with actor-scoped provider/service evidence, preserves FEASIBLE/INFEASIBLE/UNKNOWN, "
                "and exposes decomposed physical/service quantities without treating body-center "
                "separation as route length. The default synthetic accessibility table is removed."
            ),
            "gap4_closed_means": (
                "Demand/Pressure V1 derives requirements from current civilization stocks plus "
                "explicit scoped strategic requirements, compares them with installed capacity, "
                "and carries unmet demand into decaying pressure in the same channel unit. The "
                "default OFFWORLD_* and WATER_RESOURCE_DEMAND annual fixture curves are removed."
            ),
            "gap5_closed_means": (
                "Project Economics V1 supplies a versioned Earth-Orbit-Luna parameter set with "
                "economic/physical units, low-nominal-high uncertainty, explicit scale behavior, "
                "technology-year adjustments and component provenance. The default runtime no "
                "longer consumes METHOD_LAB_SYNTHETIC_V1 project economics."
            ),
            "gap6_closed_means": (
                "Mission/Knowledge V1 separates mission actions from infrastructure, preserves "
                "actor-visible probabilistic knowledge, permits hidden physical realization only "
                "inside the keyed observation runtime, applies deterministic Bayesian updates, "
                "and feeds posterior resource belief into later project scoring. The first "
                "admitted observation model is binary resource detection."
            ),
            "gap7_closed_means": (
                "Pressure Observability V1 emits reconstructable annual pressure transitions, "
                "quantified contributions and per-opportunity qualification arithmetic with "
                "stable provenance IDs. Selected project decisions link to the exact pressure "
                "qualification record. The causal path records no synthetic discharge and the "
                "legacy Method Lab path exposes its historical discharge explicitly."
            ),
            "gap8_closed_means": (
                "Resource Mass Balance V1 separates evidence/belief from evaluator-only physical "
                "realization and provides stock, feed extraction, grade, recovery, tailings, "
                "inventory and depletion accounting with hard capacity and conservation checks. "
                "Unquantified lunar abundance remains UNKNOWN/null in the default physical state."
            ),
            "gap9_closed_means": (
                "Production Accounting V1 separates physical output feasibility from monetary "
                "valuation and gross productive-capital accounting. Required unresolved service "
                "constraints propagate UNKNOWN; value added is gross output minus intermediate "
                "consumption; operating cost remains distinct; commissioned project capital is "
                "investment and no depreciation is applied before GAP-013."
            ),
            "gap10_closed_means": (
                "Power Balance V1 separates installed MW, average generation, peak and average "
                "load, firm capacity, reserve assumptions, annual MWh, unserved energy and "
                "curtailment. Population peak load reuses the POWER demand state drivers; "
                "facility operating loads, average-load factors and generator availability/firmness "
                "remain UNKNOWN unless separately qualified. Timeline thresholds provide context "
                "and never auto-create capacity."
            ),
            "gap11_closed_means": (
                "Traffic/Fleet V1 separates local transport handling capacity from actual OD "
                "movement. Explicit OD allocations bind GAP-004 transport demand to GAP-003 "
                "services and versioned fleet assets; vehicle mission duration, turnaround and "
                "availability bound annual trips, cargo/passenger movement, ship calls, backlog "
                "and route utilization. Unassigned demand remains UNASSIGNED_OD, and timeline "
                "transport milestones never auto-spawn routes or vehicles."
            ),
            "does_not_mean": (
                "An UNKNOWN allocation is zero or an inferred government budget; a geometry sample "
                "is a route, transfer solution, fleet allocation, service price, or actor entitlement; "
                "the uncalibrated demand coefficients, mission priors/instrument model, or "
                "scenario project-economic ranges are empirical forecasts; Dorrington-Olsen is a "
                "lunar facility cost model; evaluator truth is actor-visible; lunar water "
                "presence establishes a quantified mineable inventory, ore grade, extraction "
                "rate or recovery efficiency; Earth sector values or ratios are valid off-world "
                "prices, productivity or utilization; project capital cost is operating cost or "
                "output price; installed MW equals average generation or annual MWh; the "
                "2040 ENE-MOD-INDUSTRIAL scenario threshold auto-builds or certifies generation; "
                "installed transport handling capacity is realized OD movement; TRN-MOD-HEAVY "
                "or TRN-MOD-NEP auto-spawns routes, services or fleet assets; the named Roo-ver "
                "CLPS path is generic freight entitlement; off-world initial infrastructure or "
                "demographic depth are production solved."
            ),
        },
    }
    _write_json(output_dir / "compiler_manifest_v1.json", compiler_manifest)
    return compiler_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture and compile CIVPROP real-authority input package V1."
    )
    parser.add_argument("--database", default="loom_dev")
    parser.add_argument("--capture-live", action="store_true")
    parser.add_argument("--capture-path", type=Path, default=default_capture_path())
    parser.add_argument("--output-dir", type=Path, default=default_output_dir())
    args = parser.parse_args()

    if args.capture_live:
        capture_live_authority(args.capture_path, database=args.database)
    if not args.capture_path.exists():
        raise SystemExit(
            f"authority capture missing: {args.capture_path}; use --capture-live"
        )
    manifest = compile_from_capture(args.capture_path, args.output_dir)
    print(
        json.dumps(
            {
                "compiler": manifest["compiler_id"],
                "fixture_id": manifest["runtime_input"]["fixture_id"],
                "runtime_input_sha256": manifest["runtime_input"]["scenario_sha256"],
                "gap_001": manifest["gap_resolution"]["GAP-001"],
                "gap_002": manifest["gap_resolution"]["GAP-002"],
                "gap_003": manifest["gap_resolution"]["GAP-003"],
                "gap_004": manifest["gap_resolution"]["GAP-004"],
                "gap_005": manifest["gap_resolution"]["GAP-005"],
                "gap_006": manifest["gap_resolution"]["GAP-006"],
                "gap_007": manifest["gap_resolution"]["GAP-007"],
                "gap_008": manifest["gap_resolution"]["GAP-008"],
                "gap_009": manifest["gap_resolution"]["GAP-009"],
                "gap_010": manifest["gap_resolution"]["GAP-010"],
                "gap_011": manifest["gap_resolution"]["GAP-011"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
