from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

QUALIFIED_DUPLICATE_PAIRS = (
    ("NODE:HEL-03", "NODE:HEL-10"),
    ("NODE:HEL-04", "NODE:HEL-06"),
    ("NODE:HEL-07", "NODE:HEL-08"),
)

HARD_CONSERVATION_FIELDS = (
    "resident_population",
    "workforce",
    "annual_value_added",
    "capital_stock",
    "replacement_value",
)

PRESERVE_BY_DEFAULT_FIELDS = (
    "power_average_mw",
    "power_peak_mw",
    "habitable_capacity",
    "cargo_throughput_tonnes_year",
    "passenger_movements_year",
    "ship_calls_year",
)

ADMISSIBLE_UPSTREAM_DRIVER_FIELDS = (
    "civ_governance_profile.primary_owner_operator",
    "civ_governance_profile.corporate_proxy_governance",
    "civ_influence_edge.actor_subject_id",
    "civ_influence_edge.influence_domain",
    "civ_influence_edge.influence_weight",
    "civ_influence_edge.control_class",
    "civ_influence_edge.basis",
    "civ_census_node_relation.zone_subject_id",
    "civ_census_node_relation.basis_code",
)

FORBIDDEN_AS_ALLOCATOR_INPUTS = (
    "civ_node_texture_overlay",
    "civ_place_dna",
    "civ_social_pressure",
    "civ_social_state",
)


def build_design_contract() -> dict:
    return {
        "schema": "LOOM_CIVSTATE_HEL_ALLOCATOR_V2_DESIGN_CONTRACT_V1",
        "status": "PASS",
        "scope": "DESIGN_ONLY_NO_DATABASE_MUTATION",
        "objective": "REDUCE_UNEARNED_HEL_STATE_TWINNING_WITHOUT_BREAKING_PARENT_CONSERVATION_OR_INVENTING_ROLE_SEMANTICS",
        "conservation_authority": "LOCKED_CANON_A20",
        "semantic_guardrail": "LOCKED_CANON_A08_POPULATION_THROUGHPUT_STRATEGIC_IMPORTANCE_REMAIN_SEPARATE",
        "hard_conservation_fields": list(HARD_CONSERVATION_FIELDS),
        "preserve_by_default_fields": list(PRESERVE_BY_DEFAULT_FIELDS),
        "admissible_upstream_driver_fields": list(ADMISSIBLE_UPSTREAM_DRIVER_FIELDS),
        "forbidden_as_allocator_inputs": list(FORBIDDEN_AS_ALLOCATOR_INPUTS),
        "forbidden_input_reason": "DOWNSTREAM_OR_BEHAVIORAL_FIELDS_MAY_BE_CONSEQUENCES_OF_THE_ALLOCATION_AND_MUST_NOT_BE_USED_CIRCULARLY",
        "normalization_rule": "NORMALIZE_ONLY_WITHIN_A_PARENT_ALLOCATION_POOL_USING_DOCUMENTED_UPSTREAM_DRIVERS; NEVER_GLOBAL_RANDOMIZE",
        "residual_rule": "PRESERVE_EXISTING_PARENT_RESIDUAL_ACCOUNTING; NAMED_INFRASTRUCTURE_NEED_NOT_ABSORB_ALL_PARENT_ECONOMY",
        "pair_uniqueness_rule": "UNIQUENESS_IS_NOT_AN_OBJECTIVE; IDENTICAL_OUTPUTS_ARE_ALLOWED_WHERE_AUTHORITATIVE_DRIVERS_DO_NOT_DIFFER",
        "insufficient_driver_rule": "REFUSE_TO_FORCE_DIVERSITY_WHEN_UPSTREAM_AUTHORITY_DOES_NOT_DIFFERENTIATE_A_PAIR",
        "acceptance_tests": [
            "hard parent totals conserved to numeric tolerance",
            "residual accounting preserved",
            "no display-name or natural-language role inference",
            "no random jitter",
            "no downstream texture/place/social fields used as allocator inputs",
            "A08 separation maintained: population, throughput and strategic importance are not collapsed into one score",
            "deterministic replay from identical authoritative inputs yields identical outputs",
            "pair differences require traceable upstream-driver differences",
            "all new allocations carry explicit derivation/provenance metadata",
        ],
        "name_inference_authority": "ZERO",
        "random_jitter_authority": "ZERO",
        "downstream_feedback_authority": "ZERO",
        "coefficient_invention_authority": "ZERO_UNTIL_SEPARATE_MODEL_QUALIFICATION",
        "mutation_authority": "ZERO",
        "next_action": "QUALIFY_DRIVER_COVERAGE_AND_PARENT_ALLOCATION_POOLS_BEFORE_IMPLEMENTING_ANY_REALLOCATOR",
    }


def validate_candidate_plan(candidate: dict) -> dict:
    violations: list[str] = []
    if candidate.get("uses_display_names"):
        violations.append("DISPLAY_NAME_INFERENCE_FORBIDDEN")
    if candidate.get("uses_random_jitter"):
        violations.append("RANDOM_JITTER_FORBIDDEN")
    if candidate.get("uses_downstream_fields"):
        violations.append("DOWNSTREAM_CIRCULAR_INPUTS_FORBIDDEN")
    if not candidate.get("preserves_hard_totals"):
        violations.append("A20_HARD_TOTAL_CONSERVATION_REQUIRED")
    if not candidate.get("preserves_residual_accounting"):
        violations.append("PARENT_RESIDUAL_ACCOUNTING_MUST_BE_PRESERVED")
    if candidate.get("forces_pair_uniqueness"):
        violations.append("FORCED_PAIR_UNIQUENESS_FORBIDDEN")

    pair_distinctness = candidate.get("pair_driver_distinctness", {})
    unresolved = sorted(pair for pair, distinct in pair_distinctness.items() if not distinct)
    if violations:
        status = "REJECT"
    elif unresolved:
        status = "PASS_WITH_UNRESOLVED_DIFFERENTIATION"
    else:
        status = "PASS"
    return {
        "schema": "LOOM_CIVSTATE_HEL_ALLOCATOR_V2_CANDIDATE_VALIDATION_V1",
        "status": status,
        "violations": violations,
        "unresolved_pairs": unresolved,
        "mutation_authority": "ZERO",
    }


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def inspect_runtime_support(db_path: str | Path) -> dict:
    conn = sqlite3.connect(f"file:{Path(db_path)}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        support = {}
        for field in ADMISSIBLE_UPSTREAM_DRIVER_FIELDS:
            table, column = field.split(".", 1)
            support[field] = table in tables and column in _table_columns(conn, table)

        assumptions = {}
        if "civ_assumption" in tables:
            cols = _table_columns(conn, "civ_assumption")
            if {"assumption_id", "statement", "status"}.issubset(cols):
                for aid in ("A08", "A20"):
                    row = conn.execute(
                        "SELECT assumption_id, statement, status FROM civ_assumption WHERE assumption_id=?",
                        (aid,),
                    ).fetchone()
                    assumptions[aid] = dict(row) if row else None

        pair_driver_distinctness = {}
        if "civ_governance_profile" in tables and "civ_influence_edge" in tables:
            for left, right in QUALIFIED_DUPLICATE_PAIRS:
                gov_left = conn.execute(
                    "SELECT primary_owner_operator, corporate_proxy_governance FROM civ_governance_profile WHERE subject_id=? AND year=2226",
                    (left,),
                ).fetchall()
                gov_right = conn.execute(
                    "SELECT primary_owner_operator, corporate_proxy_governance FROM civ_governance_profile WHERE subject_id=? AND year=2226",
                    (right,),
                ).fetchall()
                inf_left = conn.execute(
                    "SELECT actor_subject_id, influence_domain, influence_weight, control_class, basis FROM civ_influence_edge WHERE subject_id=? AND year=2226 ORDER BY actor_subject_id, influence_domain, influence_weight, control_class, basis",
                    (left,),
                ).fetchall()
                inf_right = conn.execute(
                    "SELECT actor_subject_id, influence_domain, influence_weight, control_class, basis FROM civ_influence_edge WHERE subject_id=? AND year=2226 ORDER BY actor_subject_id, influence_domain, influence_weight, control_class, basis",
                    (right,),
                ).fetchall()
                pair_driver_distinctness[f"{left}|{right}"] = (
                    [tuple(r) for r in gov_left] != [tuple(r) for r in gov_right]
                    or [tuple(r) for r in inf_left] != [tuple(r) for r in inf_right]
                )

        candidate = {
            "uses_display_names": False,
            "uses_random_jitter": False,
            "uses_downstream_fields": False,
            "preserves_hard_totals": True,
            "preserves_residual_accounting": True,
            "pair_driver_distinctness": pair_driver_distinctness,
            "forces_pair_uniqueness": False,
        }
        return {
            "schema": "LOOM_CIVSTATE_HEL_ALLOCATOR_V2_RUNTIME_SUPPORT_V1",
            "status": "PASS",
            "driver_field_support": support,
            "locked_assumptions": assumptions,
            "pair_driver_distinctness": pair_driver_distinctness,
            "candidate_validation": validate_candidate_plan(candidate),
            "interpretation": "CURRENT_STRUCTURAL_DRIVERS_MAY_BE_INSUFFICIENT_FOR_ALL_PREVIOUSLY_DUPLICATE_PAIRS;_DO_NOT_FORCE_DIVERSITY",
            "mutation_authority": "ZERO",
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="HEL allocator-v2 non-mutating design contract")
    parser.add_argument("--db", default="data/LOOM_2226_CIVSTATE.sqlite3")
    args = parser.parse_args()
    output = {
        "contract": build_design_contract(),
        "runtime_support": inspect_runtime_support(args.db),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
