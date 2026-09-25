from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from .models import StagingRecord
from .validate import reject_duplicate


def ensure_identity_anchor(conn: sqlite3.Connection) -> None:
    conn.execute("INSERT OR IGNORE INTO body(body_id,canonical_name,body_class,status) VALUES(?,?,?,?)",
                 ("CERES", "Ceres", "DWARF_PLANET", "CANDIDATE"))
    conn.commit()


def load_candidate(conn: sqlite3.Connection, record: StagingRecord) -> dict[str, int]:
    """Load only candidate rows; identity and source rows are also candidate-scope."""
    source = record.source
    cur = conn.execute(
        "INSERT INTO source(source_type,provider,title,authors,doi,url,publication_date,product_name,product_version,persistent_identifier,retrieved_at,citation_text) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (source.source_type, source.provider, source.title, source.authors, source.doi, source.url,
         source.publication_date, source.product_name if hasattr(source, "product_name") else None,
         source.product_version if hasattr(source, "product_version") else None,
         source.persistent_identifier, source.retrieved_at, source.citation_text),
    )
    source_id = cur.lastrowid
    ensure_identity_anchor(conn)
    obs_ids: dict[str, int] = {}
    region_ids: dict[str, int] = {}
    for region in record.regions:
        cur = conn.execute(
            "INSERT INTO body_region(body_id,parent_region_id,region_type,canonical_name,latitude_min_deg,latitude_max_deg,"
            "longitude_min_deg,longitude_max_deg,reference_frame,description,confidence_class,source_id,notes) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (region.body_id, region.parent_region_id if hasattr(region, "parent_region_id") else None,
             region.region_type, region.canonical_name, region.latitude_min_deg, region.latitude_max_deg,
             region.longitude_min_deg, region.longitude_max_deg, region.reference_frame, region.description,
             region.confidence_class, source_id, region.notes),
        )
        if region.region_ref:
            region_ids[region.region_ref] = cur.lastrowid
    for obs in record.observations:
        cur = conn.execute(
            "INSERT INTO observation(body_id,region_id,mission,spacecraft,instrument,observation_product_id,observation_method,"
            "observation_time_start,observation_time_end,spatial_context,source_id) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (obs.body_id, region_ids.get(obs.region_ref, obs.region_id), obs.mission, obs.spacecraft, obs.instrument, obs.observation_product_id, obs.observation_method,
             obs.observation_time_start, obs.observation_time_end, obs.spatial_context, source_id),
        )
        obs_ids[obs.observation_product_id or str(cur.lastrowid)] = cur.lastrowid
    fact_ids: list[int] = []
    # Rebuilds from preserved artifacts are deterministic; source retrieval time is
    # the stable event timestamp for candidate rows unless an explicit load time is supplied.
    now = record.metadata.get("loaded_at", source.retrieved_at)
    for fact in record.facts:
        if reject_duplicate(conn, fact, source_id=source_id):
            raise ValueError(f"DUPLICATE_ASSERTION: {fact.property_code}")
        cur = conn.execute(
            "INSERT INTO fact(body_id,region_id,property_code,value_semantics,value_numeric,value_min,value_max,"
            "uncertainty_plus,uncertainty_minus,canonical_unit,reported_value_text,reported_unit,evidence_class,"
            "measurement_method,spatial_context,temporal_context,confidence_class,fact_status,knowledge_valid_from,"
            "knowledge_valid_until,supersedes_fact_id,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (fact.body_id, region_ids.get(fact.region_ref, fact.region_id), fact.property_code, fact.value_semantics, fact.normalized_value,
             fact.value_min, fact.value_max, fact.uncertainty_plus, fact.uncertainty_minus, fact.normalized_unit,
             fact.reported_value_text, fact.reported_unit, fact.evidence_class, fact.measurement_method,
             fact.spatial_context, fact.temporal_context, fact.confidence_class, fact.fact_status,
             fact.knowledge_valid_from, fact.knowledge_valid_until, fact.supersedes_fact_id, now, fact.notes),
        )
        fact_id = cur.lastrowid
        fact_ids.append(fact_id)
        conn.execute("INSERT INTO source_assertion(fact_id,source_id,assertion_role,source_locator,notes) VALUES(?,?,?,?,?)",
                     (fact_id, source_id, fact.assertion_role, fact.source_locator, "raw artifact linked by audit manifest"))
        if fact.observation_ref:
            conn.execute("INSERT INTO fact_observation(fact_id,observation_id) VALUES(?,?)",
                         (fact_id, obs_ids[fact.observation_ref]))
    material_ids: list[int] = []
    for material in record.materials:
        cur = conn.execute(
            "INSERT INTO material_evidence(body_id,region_id,material_family,material_species,physical_form,"
            "host_material,location_context,evidence_class,abundance_semantics,abundance_value,abundance_min,"
            "abundance_max,abundance_unit,reported_abundance,areal_extent,areal_extent_unit,measurement_method,"
            "confidence_class,fact_status,observation_id,source_id,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (material.body_id, region_ids.get(material.region_ref, material.region_id), material.material_family,
             material.material_species, material.physical_form, material.host_material, material.location_context,
             material.evidence_class, material.abundance_semantics, material.abundance_value, material.abundance_min,
             material.abundance_max, material.abundance_unit, material.reported_abundance, material.areal_extent,
             material.areal_extent_unit, material.measurement_method, material.confidence_class, material.fact_status,
             obs_ids.get(material.observation_ref), source_id, material.notes),
        )
        material_ids.append(cur.lastrowid)
    activity_ids: list[int] = []
    for activity in record.activities:
        cur = conn.execute(
            "INSERT INTO activity_fact(body_id,region_id,activity_type,description,evidence_class,confidence_class,"
            "observation_id,source_id,notes) VALUES(?,?,?,?,?,?,?,?,?)",
            (activity.body_id, region_ids.get(activity.region_ref), activity.activity_type, activity.description,
             activity.evidence_class, activity.confidence_class, obs_ids.get(activity.observation_ref), source_id,
             activity.notes),
        )
        activity_ids.append(cur.lastrowid)
    model_product_ids: list[int] = []
    for product in record.model_products:
        cur = conn.execute(
            "INSERT INTO body_model_product(body_id,region_id,model_type,model_name,model_version,reference_frame,"
            "resolution_description,source_id,persistent_identifier,product_url,sha256,byte_count,notes) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (product.body_id, region_ids.get(product.region_ref, product.region_id), product.model_type, product.model_name, product.model_version,
             product.reference_frame, product.resolution_description, source_id, product.persistent_identifier,
             product.product_url, product.sha256, product.byte_count, product.notes),
        )
        model_product_ids.append(cur.lastrowid)
        if product.region_ref and product.region_ref in region_ids:
            conn.execute("INSERT INTO region_model_product(region_id,model_product_id,relationship) VALUES(?,?,?)",
                         (region_ids[product.region_ref], cur.lastrowid, "DESCRIBES"))
    gravity_model_ids: list[int] = []
    for model in record.gravity_models:
        cur = conn.execute(
            "INSERT INTO gravity_model(body_id,model_name,model_version,gravitational_parameter,gm_unit,"
            "reference_radius,reference_radius_unit,maximum_degree,maximum_order,normalization,coefficient_convention,"
            "reference_frame,reference_epoch,source_id,persistent_identifier,product_url,sha256,byte_count,validity_notes,notes) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (model.body_id, model.model_name, model.model_version, model.gravitational_parameter, model.gm_unit,
             model.reference_radius, model.reference_radius_unit, model.maximum_degree, model.maximum_order,
             model.normalization, model.coefficient_convention, model.reference_frame, model.reference_epoch,
             source_id, model.persistent_identifier, model.product_url, model.sha256, model.byte_count,
             model.validity_notes, model.notes),
        )
        gravity_model_ids.append(cur.lastrowid)
    orientation_ids: list[int] = []
    for model in record.orientation_models:
        cur = conn.execute(
            "INSERT INTO orientation_model(body_id,model_name,model_version,model_authority,reference_frame,reference_epoch,"
            "pole_ra_deg,pole_dec_deg,pole_ra_rate,pole_dec_rate,prime_meridian_deg,prime_meridian_rate,"
            "rotation_period_seconds,rotation_state,libration_model,source_id,persistent_identifier,product_url,sha256,notes) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (model.body_id, model.model_name, model.model_version, model.model_authority, model.reference_frame,
             model.reference_epoch, model.pole_ra_deg, model.pole_dec_deg, model.pole_ra_rate, model.pole_dec_rate,
             model.prime_meridian_deg, model.prime_meridian_rate, model.rotation_period_seconds, model.rotation_state,
             model.libration_model, source_id, model.persistent_identifier, model.product_url, model.sha256, model.notes),
        )
        orientation_ids.append(cur.lastrowid)
    derived_ids: list[int] = []
    for derived in record.derived_quantities:
        cur = conn.execute(
            "INSERT INTO derived_quantity(body_id,property_code,value_numeric,unit,derivation_method,"
            "derivation_version,reference_epoch,computed_at,notes) VALUES(?,?,?,?,?,?,?,?,?)",
            (derived.body_id, derived.property_code, derived.value_numeric, derived.unit, derived.derivation_method,
             derived.derivation_version, derived.reference_epoch, now, derived.notes),
        )
        derived_id = cur.lastrowid
        derived_ids.append(derived_id)
        for property_code in derived.input_property_codes:
            input_row = conn.execute(
                "SELECT fact_id FROM fact WHERE body_id=? AND property_code=? ORDER BY fact_id DESC LIMIT 1",
                (derived.body_id, property_code),
            ).fetchone()
            if input_row is None:
                raise ValueError(f"missing derived input fact: {property_code}")
            conn.execute("INSERT INTO derived_input(derived_id,fact_id,input_role) VALUES(?,?,?)",
                         (derived_id, input_row[0], "INPUT"))
    conn.commit()
    return {"source_id": source_id, "fact_ids": fact_ids, "observation_ids": list(obs_ids.values()),
            "model_product_ids": model_product_ids, "gravity_model_ids": gravity_model_ids,
            "material_ids": material_ids, "activity_ids": activity_ids, "orientation_ids": orientation_ids,
            "derived_ids": derived_ids}
