#!/usr/bin/env python3
"""GAP-001 CIVPROP real-authority input compiler V1.

The compiler does two distinct things:

1. capture promoted/read-only authority into one frozen evidence artifact;
2. compile that frozen artifact into the currently locked CIVPROP runner envelope.

It intentionally does NOT solve later gaps. Where the engine still requires a value
whose production semantics belong to GAP-002+ (budgets, accessibility, demand,
project economics, etc.), the compiler carries forward the existing Method Lab
fixture value and registers it explicitly as an assumption.

This lets us replace ad-hoc input assembly without laundering unresolved model
assumptions into authority.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


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
ROOVER_PATH = HERE / "civprop0/roover_service_envelope.json"


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
    roover = json.loads(ROOVER_PATH.read_text())

    source_paths = [
        RESOURCE_PATH,
        FLEET_ACCESS_PATH,
        ROOVER_PATH,
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
        "captured_for_gap": "GAP-001_REAL_INPUT_COMPILER",
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
        "solar": {
            "bodies": rows["solar_bodies"],
            "identifiers": rows["solar_identifiers"],
            "ephemeris_source": rows["ephemeris_source"][0],
            "ephemeris_coverage": rows["ephemeris_coverage"],
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
            "roover_service": roover,
            "source_paths": {
                "fleet_access": str(FLEET_ACCESS_PATH.relative_to(REPO_ROOT)),
                "roover_service": str(ROOVER_PATH.relative_to(REPO_ROOT)),
            },
        },
    }
    _write_json(output_path, capture)
    return capture


def _assumption_register() -> list[dict[str, str]]:
    return [
        {
            "assumption_id": "ASSUME-GAP002-AUS-BUDGET",
            "gap_id": "GAP-002",
            "status": "EXPLICIT_PLACEHOLDER",
            "semantics": (
                "AUS starting_capital=70 and annual_capital_inflow=8 scenario_credit "
                "are copied from the Method Lab public-financier fixture; they are not "
                "Australian government spending, GDP, investment, or observed cash."
            ),
        },
        {
            "assumption_id": "ASSUME-GAP002-AUS-CAPABILITIES",
            "gap_id": "GAP-002",
            "status": "EXPLICIT_PLACEHOLDER",
            "semantics": (
                "Generic engine technology statuses are copied from the Method Lab "
                "public actor and relabeled AUS. Real Roo-ver/Fleet evidence is "
                "preserved separately and does not grant generic capability."
            ),
        },
        {
            "assumption_id": "ASSUME-GAP003-ACCESSIBILITY",
            "gap_id": "GAP-003",
            "status": "EXPLICIT_PLACEHOLDER",
            "semantics": (
                "Origin/destination FEASIBLE/UNKNOWN series and generalized_cost are "
                "the existing Method Lab synthetic transport fixture."
            ),
        },
        {
            "assumption_id": "ASSUME-GAP004-DEMAND",
            "gap_id": "GAP-004",
            "status": "EXPLICIT_PLACEHOLDER",
            "semantics": (
                "Transport, industrial, habitat-interest and water demand series are "
                "the existing Method Lab exogenous synthetic signals."
            ),
        },
        {
            "assumption_id": "ASSUME-GAP005-PROJECT-ECONOMICS",
            "gap_id": "GAP-005",
            "status": "EXPLICIT_PLACEHOLDER",
            "semantics": (
                "Facility costs, construction lags and capacity quantities remain "
                "METHOD_LAB_SYNTHETIC_V1 parameter values."
            ),
        },
        {
            "assumption_id": "ASSUME-GAP006-RESOURCE-PRIOR",
            "gap_id": "GAP-006",
            "status": "EXPLICIT_PLACEHOLDER",
            "semantics": (
                "The empirical lunar-water assertion establishes presence in scoped "
                "footprints but not a numeric site probability. Prior=0.45, sensitivity=0.80 "
                "and false_positive=0.10 remain Method Lab observation fixtures."
            ),
        },
        {
            "assumption_id": "ASSUME-GAP012-OFFWORLD-INITIAL-STATE",
            "gap_id": "GAP-012",
            "status": "EXPLICIT_PLACEHOLDER",
            "semantics": (
                "Initial Earth-orbit/Luna/cislunar engine capacities remain the Method "
                "Lab boundary fixture; they are not a compiled empirical 2026 infrastructure inventory."
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

    public_fixture = next(
        x for x in base["actors"] if x["actor_id"] == "LAB_PUBLIC"
    )
    scenario["actors"] = [
        {
            "actor_id": "AUS",
            "actor_type": "PUBLIC_FINANCIER",
            "starting_capital": public_fixture["starting_capital"],
            "annual_capital_inflow": public_fixture["annual_capital_inflow"],
        }
    ]

    scenario["actor_capability"] = [
        {
            **row,
            "actor_id": "AUS",
        }
        for row in base["actor_capability"]
        if row["actor_id"] == "LAB_PUBLIC"
    ]

    belief = copy.deepcopy(base["resource_beliefs"][0])
    belief["evidence_status"] = "EMPIRICAL_PRESENCE_PLUS_SCENARIO_PRIOR"
    scenario["resource_beliefs"] = [belief]

    scenario["authority_context"] = {
        "compiler": {
            "compiler_contract": "CIVPROP_INPUT_COMPILER_V1",
            "gap_resolution": {"GAP-001": "CLOSED"},
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
        "timeline": capture["timeline"],
        "resource": capture["resource"],
        "actor": capture["actor"],
    }
    scenario["assumption_register"] = _assumption_register()
    return scenario


def _compile_truth() -> dict[str, Any]:
    truth = json.loads((METHOD_LAB_DIR / "truth_v1.json").read_text())
    truth["fixture_id"] = COMPILED_FIXTURE_ID
    truth["classification"] = (
        "EVALUATOR_ONLY_SYNTHETIC_TRUTH_FOR_COMPATIBILITY_NOT_RUNTIME_AUTHORITY"
    )
    truth["notes"] = [
        "HYBRID_V1 does not consume this file for decisions or state transitions.",
        "This evaluator-only realization remains synthetic until GAP-006/GAP-008 provide a qualified hidden physical realization contract.",
    ]
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
    truth = _compile_truth()

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
    compiler_manifest = {
        "format": COMPILER_MANIFEST_FORMAT,
        "compiler_id": "CIVPROP_INPUT_COMPILER_V1",
        "compiler_version": "1.0.0",
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
            "does_not_mean": (
                "Budgets, accessibility, demand, project economics, hidden truth, "
                "off-world initial infrastructure, or demographic depth are production solved."
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
                "output_dir": str(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
