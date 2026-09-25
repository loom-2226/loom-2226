from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from ingest.knowledge import knowledge_snapshot

ROOT = Path(__file__).resolve().parent
DB = ROOT / "LOOM_SOLAR_HCQ01_CERES.sqlite3"
CUTOFF = "2025-12-31T23:59:59Z"


def main() -> int:
    conn = sqlite3.connect(DB)
    allowed_evidence = ["DIRECT_SAMPLE", "IN_SITU_DIRECT", "IN_SITU_REMOTE", "EARTH_REMOTE", "DYNAMICAL_INFERENCE", "ANALOG_INFERENCE", "PHYSICAL_MODEL", "THEORETICAL_EXPECTATION", "DERIVED"]
    allowed_confidence = ["VERY_HIGH", "HIGH", "MODERATE", "LOW", "CONTESTED", "UNKNOWN"]
    allowed_roles = ["PRIMARY", "SUPPORTING", "CONTRADICTING", "SUPERSEDING"]
    tables = ["body", "source", "observation", "body_region", "fact", "source_assertion", "material_evidence", "activity_fact", "body_model_product", "region_model_product", "gravity_model", "orientation_model", "derived_quantity", "derived_input", "preferred_fact"]
    counts = {table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in tables}
    cross_body = {
        "fact_region": conn.execute("SELECT count(*) FROM fact f JOIN body_region r ON r.region_id=f.region_id WHERE f.body_id<>r.body_id").fetchone()[0],
        "observation_region": conn.execute("SELECT count(*) FROM observation o JOIN body_region r ON r.region_id=o.region_id WHERE o.body_id<>r.body_id").fetchone()[0],
        "material_region": conn.execute("SELECT count(*) FROM material_evidence m JOIN body_region r ON r.region_id=m.region_id WHERE m.body_id<>r.body_id").fetchone()[0],
        "activity_region": conn.execute("SELECT count(*) FROM activity_fact a JOIN body_region r ON r.region_id=a.region_id WHERE a.body_id<>r.body_id").fetchone()[0],
        "model_region": conn.execute("SELECT count(*) FROM body_model_product m JOIN body_region r ON r.region_id=m.region_id WHERE m.body_id<>r.body_id").fetchone()[0],
        "region_model": conn.execute("SELECT count(*) FROM region_model_product rp JOIN body_region r ON r.region_id=rp.region_id JOIN body_model_product m ON m.model_product_id=rp.model_product_id WHERE r.body_id<>m.body_id").fetchone()[0],
        "fact_observation": conn.execute("SELECT count(*) FROM fact_observation fo JOIN fact f ON f.fact_id=fo.fact_id JOIN observation o ON o.observation_id=fo.observation_id WHERE f.body_id<>o.body_id").fetchone()[0],
    }
    snapshots = {year: {key: len(value) for key, value in knowledge_snapshot(conn, cutoff).items()} for year, cutoff in (("2010", "2010-12-31T23:59:59Z"), ("2016", "2016-12-31T23:59:59Z"), ("2025", CUTOFF))}
    evidence_values = {table: [row[0] for row in conn.execute(f"SELECT DISTINCT evidence_class FROM {table} ORDER BY evidence_class")] for table in ("fact", "material_evidence", "activity_fact")}
    report = {
        "round": 2,
        "qualification_status": "QUALIFIED_WITH_LIMITATIONS",
        "blockers": [],
        "limitations": ["raw artifact/hash/audit manifests remain external to frozen SQLite tables", "no native historical knowledge-event relation", "orientation uncertainty retained in notes because frozen table has no uncertainty columns"],
        "database_sha256": hashlib.sha256(DB.read_bytes()).hexdigest(),
        "counts": counts,
        "integrity_check": conn.execute("PRAGMA integrity_check").fetchone()[0],
        "foreign_key_check": conn.execute("PRAGMA foreign_key_check").fetchall(),
        "controlled_vocabulary": {"evidence_class": allowed_evidence, "confidence_class": allowed_confidence, "assertion_role": allowed_roles, "fact_status": ["CANDIDATE", "CURRENT", "RETIRED"]},
        "actual_evidence_values": evidence_values,
        "actual_confidence_values": {table: [row[0] for row in conn.execute(f"SELECT DISTINCT confidence_class FROM {table} ORDER BY confidence_class")] for table in ("fact", "material_evidence", "activity_fact")},
        "actual_assertion_roles": [row[0] for row in conn.execute("SELECT DISTINCT assertion_role FROM source_assertion ORDER BY assertion_role")],
        "actual_fact_statuses": {table: [row[0] for row in conn.execute(f"SELECT DISTINCT fact_status FROM {table} ORDER BY fact_status")] for table in ("fact", "material_evidence")},
        "source_types": conn.execute("SELECT source_type,count(*) FROM source GROUP BY source_type ORDER BY source_type").fetchall(),
        "regional_links": {"observations_linked": conn.execute("SELECT count(*) FROM observation WHERE region_id IS NOT NULL").fetchone()[0], "regional_models_linked": conn.execute("SELECT count(*) FROM body_model_product WHERE region_id IS NOT NULL").fetchone()[0], "region_model_relationships": conn.execute("SELECT count(*) FROM region_model_product").fetchone()[0]},
        "cross_body_violations": cross_body,
        "psr_water_area_rows": conn.execute("SELECT count(*) FROM material_evidence WHERE material_family='water_ice' AND areal_extent IS NOT NULL").fetchone()[0],
        "derived_lineage": conn.execute("SELECT dq.property_code, dq.value_numeric, dq.unit, f.property_code, f.fact_status FROM derived_quantity dq JOIN derived_input di ON di.derived_id=dq.derived_id JOIN fact f ON f.fact_id=di.fact_id ORDER BY dq.derived_id").fetchall(),
        "gravity_model_metadata": conn.execute("SELECT gravitational_parameter,reference_radius,normalization,coefficient_convention,reference_epoch,notes FROM gravity_model").fetchall(),
        "orientation_model_metadata": conn.execute("SELECT pole_ra_deg,pole_dec_deg,prime_meridian_deg,prime_meridian_rate,rotation_period_seconds,notes FROM orientation_model").fetchall(),
        "knowledge_snapshots": snapshots,
        "post_cutoff_sources": conn.execute("SELECT count(*) FROM source WHERE publication_date> ?", (CUTOFF,)).fetchone()[0],
        "provenance_gaps": conn.execute("SELECT count(*) FROM fact f LEFT JOIN source_assertion sa ON sa.fact_id=f.fact_id WHERE sa.fact_id IS NULL").fetchone()[0],
        "qualification_queries": {
            "admissible_candidate_facts": conn.execute("SELECT fact_id,property_code,value_numeric,value_min,value_max,canonical_unit FROM fact WHERE fact_status='CANDIDATE' ORDER BY fact_id").fetchall(),
            "water_ice_related_evidence": conn.execute("SELECT material_family,material_species,evidence_class,region_id,notes FROM material_evidence WHERE lower(material_family) LIKE '%water%' OR lower(material_family) LIKE '%ice%' OR lower(material_family) LIKE '%vapor%' ORDER BY material_evidence_id").fetchall(),
            "occator_evidence": conn.execute("SELECT 'material',material_family,evidence_class,region_id FROM material_evidence WHERE region_id IN (SELECT region_id FROM body_region WHERE canonical_name='Occator crater') UNION ALL SELECT 'activity',activity_type,evidence_class,region_id FROM activity_fact WHERE region_id IN (SELECT region_id FROM body_region WHERE canonical_name='Occator crater') UNION ALL SELECT 'observation',observation_product_id,observation_method,region_id FROM observation WHERE region_id IN (SELECT region_id FROM body_region WHERE canonical_name='Occator crater')").fetchall(),
            "modeled_or_inferred_claims": conn.execute("SELECT property_code,evidence_class FROM fact WHERE evidence_class IN ('DYNAMICAL_INFERENCE','PHYSICAL_MODEL','DERIVED') UNION ALL SELECT activity_type,evidence_class FROM activity_fact WHERE evidence_class='PHYSICAL_MODEL'").fetchall(),
            "regional_model_products": conn.execute("SELECT m.model_name,r.canonical_name,rp.relationship FROM body_model_product m JOIN region_model_product rp ON rp.model_product_id=m.model_product_id JOIN body_region r ON r.region_id=rp.region_id ORDER BY m.model_product_id").fetchall(),
            "derived_lineage_complete": conn.execute("SELECT dq.property_code,dq.value_numeric,dq.unit,f.property_code,f.fact_status FROM derived_quantity dq JOIN derived_input di ON di.derived_id=dq.derived_id JOIN fact f ON f.fact_id=di.fact_id").fetchall(),
            "legitimate_unknowns": conn.execute("SELECT 'gravity_model.reference_epoch',gravity_model_id FROM gravity_model WHERE reference_epoch IS NULL UNION ALL SELECT 'fact.confidence_class',fact_id FROM fact WHERE confidence_class='UNKNOWN'").fetchall(),
            "sources_and_types": conn.execute("SELECT title,source_type FROM source ORDER BY source_id").fetchall(),
            "unknown_confidence": conn.execute("SELECT 'fact',fact_id,property_code FROM fact WHERE confidence_class='UNKNOWN'").fetchall(),
            "competing_interpretations": conn.execute("SELECT activity_type,notes FROM activity_fact WHERE notes LIKE '%competing%' OR description LIKE '%competing%'").fetchall(),
            "records_without_provenance": conn.execute("SELECT f.fact_id FROM fact f LEFT JOIN source_assertion sa ON sa.fact_id=f.fact_id WHERE sa.fact_id IS NULL").fetchall()
        },
        "preferred_fact_rows": counts["preferred_fact"],
        "ephemeris_tables": [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND lower(name) LIKE '%ephemeris%'")],
        "civprop_tables": [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND lower(name) LIKE '%civprop%'")],
    }
    (ROOT / "round2_review_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
