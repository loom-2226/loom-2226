#!/usr/bin/env python3
"""LOOM 2226 read-only Canon Context Projection v0.1.

Bounded E1.1 implementation. It assembles existing governed WORLD/CIVSTATE
records into a compact projection for Ceres without creating new canon,
state, physics, or model authority.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = "LOOM_CANON_CONTEXT_PROJECTION_V1"
SUPPORTED_ENTITY_IDS = {"CER", "CERES"}


def _ro_conn(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(path)
    uri = f"file:{path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _has_relation(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _rows(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def _one(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def _source_entry(database: str, relation: str, row: dict[str, Any] | None = None) -> dict[str, Any]:
    out = {"database": database, "relation": relation}
    if row:
        for key in ("source", "source_id", "derivation_id", "epistemic_status", "canon_status"):
            if row.get(key) is not None:
                out[key] = row[key]
    return out


def build_ceres_projection(world_db: Path, civstate_db: Path) -> dict[str, Any]:
    with _ro_conn(world_db) as w, _ro_conn(civstate_db) as c:
        required_world = ("atlas_profiles", "infrastructure_nodes")
        required_civ = ("civ_runtime_place_context",)
        missing = [
            f"WORLD.{r}" for r in required_world if not _has_relation(w, r)
        ] + [
            f"CIVSTATE.{r}" for r in required_civ if not _has_relation(c, r)
        ]
        if missing:
            raise RuntimeError("Required projection relations missing: " + ", ".join(missing))

        profile = _one(w, "SELECT * FROM atlas_profiles WHERE entity_id='CER'")
        if not profile:
            raise RuntimeError("Ceres profile CER not found in WORLD.atlas_profiles")

        infrastructure = _rows(
            w,
            """SELECT entity_id, node_name, facility_type, traffic, commercial_1,
                      commercial_2, commercial_regime, civil_authority,
                      administrative_authority, security_authority,
                      synthetic_constituency_1, institutional_morphology, source
               FROM infrastructure_nodes
               WHERE parent_entity_id='CER'
               ORDER BY entity_id""",
        )

        place_context = _rows(
            c,
            """SELECT subject_id, display_name, navigator_entity_id, governance_style,
                      security_posture, commercial_openness, corporate_proxy_level,
                      local_autonomy, institutional_trust, synthetic_acceptance,
                      migration_openness, frontier_mentality, scarcity_pressure,
                      social_tension, law_enforcement_reach, data_sharing_level,
                      outsider_attitude, ultimate_sovereign, local_civil_authority,
                      administrative_authority, security_provider,
                      primary_owner_operator, resident_population,
                      transient_daily_population, workforce, annual_value_added,
                      power_average_mw, cargo_throughput_tonnes_year,
                      strategic_importance, economic_centrality,
                      transport_centrality
               FROM civ_runtime_place_context
               WHERE navigator_entity_id LIKE 'CER-P%'
               ORDER BY navigator_entity_id""",
        )
        pc_by_entity = {r["navigator_entity_id"]: r for r in place_context}

        demographics = (
            _one(
                c,
                """SELECT subject_id, year, biological_population, synthetic_population,
                          transient_population, working_age_population, median_age,
                          households, derivation_id
                   FROM civ_demographic_state
                   WHERE subject_id='BODY:CERES:CERES' AND year=2226""",
            )
            if _has_relation(c, "civ_demographic_state")
            else None
        )
        economics = (
            _one(
                c,
                """SELECT subject_id, year, value_added, investment, productive_capital,
                          infrastructure_capital, productivity_index, income_per_capita,
                          derivation_id
                   FROM civ_economic_state
                   WHERE subject_id='BODY:CERES:CERES' AND year=2226""",
            )
            if _has_relation(c, "civ_economic_state")
            else None
        )
        mobility = (
            _one(w, "SELECT * FROM region_mobility WHERE region='Ceres + Belt network'")
            if _has_relation(w, "region_mobility")
            else None
        )
        morphology = (
            _one(w, "SELECT * FROM regional_morphology WHERE system='Ceres'")
            if _has_relation(w, "regional_morphology")
            else None
        )
        influence = (
            _rows(
                c,
                """SELECT subject_id, subject_name, actor_name, influence_domain,
                          influence_weight, control_class, basis, derivation_id
                   FROM v_graph_civstate_influence_edges
                   WHERE subject_id LIKE 'NODE:CER-P%'
                   ORDER BY subject_id, influence_domain, actor_name""",
            )
            if _has_relation(c, "v_graph_civstate_influence_edges")
            else []
        )
        actor_exposure = (
            _rows(
                c,
                """SELECT actor_name, geography_name, geography_subject_id, sector_id,
                          control_weight, service_dependency_weight, derivation_id
                   FROM v_graph_civstate_actor_exposure
                   WHERE geography_subject_id LIKE 'NODE:CER-P%'
                   ORDER BY geography_subject_id, actor_name""",
            )
            if _has_relation(c, "v_graph_civstate_actor_exposure")
            else []
        )

        places = []
        for item in infrastructure:
            eid = item["entity_id"]
            runtime = pc_by_entity.get(eid)
            places.append(
                {
                    "entity_id": eid,
                    "name": item["node_name"],
                    "role": item["facility_type"],
                    "traffic_class": item["traffic"],
                    "authorities": {
                        "civil": item["civil_authority"],
                        "administrative": item["administrative_authority"],
                        "security": item["security_authority"],
                    },
                    "commercial": {
                        "primary": item["commercial_1"],
                        "secondary": item["commercial_2"],
                        "regime": item["commercial_regime"],
                    },
                    "synthetic_constituency": item["synthetic_constituency_1"],
                    "institutional_morphology": item["institutional_morphology"],
                    "runtime_context": runtime,
                    "provenance": [
                        _source_entry("WORLD", "infrastructure_nodes", item),
                        _source_entry("CIVSTATE", "civ_runtime_place_context", runtime),
                    ],
                }
            )

        return {
            "schema": SCHEMA,
            "entity": {
                "entity_id": "CER",
                "name": profile.get("title") or "Ceres",
                "summary": profile.get("summary"),
                "canon_status": profile.get("status"),
                "biological": profile.get("bio"),
                "synthetic": profile.get("synth"),
            },
            "system_demography_2226": demographics,
            "system_economy_2226": economics,
            "mobility": mobility,
            "regional_morphology": morphology,
            "places": places,
            "influence_edges": influence,
            "actor_exposure": actor_exposure,
            "availability": {
                "demography": demographics is not None,
                "economy": economics is not None,
                "mobility": mobility is not None,
                "regional_morphology": morphology is not None,
                "place_count": len(places),
                "influence_edge_count": len(influence),
                "actor_exposure_count": len(actor_exposure),
            },
            "authority_policy": {
                "read_only": True,
                "model_access_to_sqlite": False,
                "calculation_authority": "DETERMINISTIC_SOURCE_ONLY",
                "state_authority": "NONE",
                "canon_mutation": False,
                "campaign_mutation": False,
            },
            "provenance": {
                "entity": _source_entry("WORLD", "atlas_profiles", profile),
                "demography": _source_entry("CIVSTATE", "civ_demographic_state", demographics),
                "economy": _source_entry("CIVSTATE", "civ_economic_state", economics),
                "mobility": _source_entry("WORLD", "region_mobility", mobility),
                "regional_morphology": _source_entry("WORLD", "regional_morphology", morphology),
                "influence_edges": {"database": "CIVSTATE", "relation": "v_graph_civstate_influence_edges"},
                "actor_exposure": {"database": "CIVSTATE", "relation": "v_graph_civstate_actor_exposure"},
            },
        }


def build_projection(world_db: Path, civstate_db: Path, entity: str) -> dict[str, Any]:
    token = entity.strip().upper()
    if token not in SUPPORTED_ENTITY_IDS:
        raise ValueError(
            f"E1.1 v0.1 supports only Ceres/CER; got {entity!r}. "
            "Do not generalize until the Ceres contract is tested."
        )
    return build_ceres_projection(world_db, civstate_db)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--entity", default="CER")
    p.add_argument("--out")
    args = p.parse_args()

    root = Path(args.root).expanduser().resolve()
    world_db = root / "data" / "LOOM_2226.sqlite3"
    civstate_db = root / "data" / "LOOM_2226_CIVSTATE.sqlite3"
    result = build_projection(world_db, civstate_db, args.entity)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).expanduser().write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
