from __future__ import annotations

import sqlite3

from .models import FactCandidate, Finding, StagingRecord, ValidationReport

CUTOFF = "2025-12-31T23:59:59Z"
EVIDENCE_CLASSES = {"DIRECT_SAMPLE", "IN_SITU_DIRECT", "IN_SITU_REMOTE", "EARTH_REMOTE", "DYNAMICAL_INFERENCE", "ANALOG_INFERENCE", "PHYSICAL_MODEL", "THEORETICAL_EXPECTATION", "DERIVED"}
CONFIDENCE_CLASSES = {"VERY_HIGH", "HIGH", "MODERATE", "LOW", "CONTESTED", "UNKNOWN"}
ASSERTION_ROLES = {"PRIMARY", "SUPPORTING", "CONTRADICTING", "SUPERSEDING"}
FACT_STATUSES = {"CANDIDATE", "CURRENT", "RETIRED"}
ATTRACTIVENESS_CODES = {"CERES_AWESOMENESS", "RESOURCE_POTENTIAL", "HABITATION_POTENTIAL"}
NON_NEGATIVE_PROPERTIES = {"MASS", "GM", "MEAN_RADIUS", "EQUATORIAL_RADIUS", "POLAR_RADIUS", "VOLUME"}
DIMENSION_LOCATOR_TOKENS = {
    "MEAN_RADIUS": "mean radius",
    "EQUATORIAL_RADIUS": "equatorial radius",
    "POLAR_RADIUS": "polar radius",
    "TRIAXIAL_AXIS_A": "axis a",
    "TRIAXIAL_AXIS_B": "axis b",
    "TRIAXIAL_AXIS_C": "axis c",
}


def _finding(code: str, message: str, decision: str = "REJECT") -> Finding:
    return Finding(code, message, decision)  # type: ignore[arg-type]


def validate(conn: sqlite3.Connection, record: StagingRecord) -> ValidationReport:
    findings: list[Finding] = []
    source = record.source
    if not source.url or not source.title or not source.retrieved_at:
        findings.append(_finding("MISSING_SOURCE_PROVENANCE", "source URL, title and retrieval time are required"))
    if source.publication_date > CUTOFF:
        findings.append(_finding("PUBLICATION_AFTER_CUTOFF", f"{source.publication_date} is after {CUTOFF}"))
    known_props = {row[0]: (row[4], row[5]) for row in conn.execute("SELECT * FROM property_definition")}
    body_ids = {row[0] for row in conn.execute("SELECT body_id FROM body")}
    region_ids = {row[0] for row in conn.execute("SELECT region_id FROM body_region")}
    region_body_by_id = {row[0]: row[1] for row in conn.execute("SELECT region_id,body_id FROM body_region")}
    region_refs = {region.region_ref for region in record.regions if region.region_ref}
    region_body_by_ref = {region.region_ref: region.body_id for region in record.regions if region.region_ref}
    region_name_by_ref = {region.region_ref: (region.canonical_name or "").lower() for region in record.regions if region.region_ref}
    observation_body_by_ref = {observation.observation_product_id: observation.body_id for observation in record.observations if observation.observation_product_id}
    for fact in record.facts:
        if fact.property_code not in known_props:
            findings.append(_finding("UNKNOWN_PROPERTY_CODE", fact.property_code))
            continue
        if fact.evidence_class not in EVIDENCE_CLASSES:
            findings.append(_finding("UNKNOWN_EVIDENCE_CLASS", fact.evidence_class))
        if fact.confidence_class not in CONFIDENCE_CLASSES:
            findings.append(_finding("UNKNOWN_CONFIDENCE_CLASS", fact.confidence_class))
        if fact.assertion_role not in ASSERTION_ROLES:
            findings.append(_finding("UNKNOWN_ASSERTION_ROLE", fact.assertion_role))
        if fact.fact_status not in FACT_STATUSES:
            findings.append(_finding("UNKNOWN_FACT_STATUS", fact.fact_status))
        elif fact.fact_status != "CANDIDATE":
            findings.append(_finding("NON_CANDIDATE_LOAD", fact.fact_status))
        if fact.body_id not in body_ids:
            findings.append(_finding("UNRESOLVED_BODY", fact.body_id))
        if fact.region_id is not None and fact.region_id not in region_ids:
            findings.append(_finding("UNRESOLVED_REGION", str(fact.region_id)))
        if fact.region_id in region_body_by_id and region_body_by_id[fact.region_id] != fact.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", fact.property_code))
        if fact.region_ref is not None and fact.region_ref not in region_refs:
            findings.append(_finding("UNRESOLVED_REGION", fact.region_ref))
        if fact.region_ref in region_body_by_ref and region_body_by_ref[fact.region_ref] != fact.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", fact.property_code))
        if not fact.source_id:
            findings.append(_finding("MISSING_SOURCE_PROVENANCE", fact.property_code))
        if fact.uncertainty_plus is not None and fact.uncertainty_plus < 0:
            findings.append(_finding("NEGATIVE_UNCERTAINTY", fact.property_code))
        if fact.uncertainty_minus is not None and fact.uncertainty_minus < 0:
            findings.append(_finding("NEGATIVE_UNCERTAINTY", fact.property_code))
        if fact.normalized_value is not None and fact.normalized_value < 0 and fact.property_code in NON_NEGATIVE_PROPERTIES:
            findings.append(_finding("NEGATIVE_VALUE", fact.property_code))
        if fact.value_min is not None and fact.value_max is not None and fact.value_min > fact.value_max:
            findings.append(_finding("MIN_GREATER_THAN_MAX", fact.property_code))
        if fact.evidence_class == "DERIVED" and (not fact.notes or "lineage" not in (fact.notes or "").lower()):
            findings.append(_finding("DERIVED_WITHOUT_LINEAGE", fact.property_code))
        if fact.preferred_fact_requested:
            findings.append(_finding("EXTRACTOR_REQUESTED_PREFERRED_FACT", fact.property_code))
        if fact.property_code in ATTRACTIVENESS_CODES or fact.value_semantics in ATTRACTIVENESS_CODES:
            findings.append(_finding("ATTRACTIVENESS_MASQUERADING_AS_FACT", fact.property_code))
        canonical_unit, value_kind = known_props[fact.property_code]
        if canonical_unit and fact.normalized_unit and fact.normalized_unit != canonical_unit:
            findings.append(_finding("INVALID_UNIT", f"{fact.property_code}: {fact.normalized_unit} != {canonical_unit}"))
        if fact.normalized_value is None and fact.reported_value_text not in (None, "UNKNOWN"):
            if fact.value_min is None or fact.value_max is None:
                findings.append(_finding("UNNORMALIZED_VALUE", fact.property_code))
        if fact.reported_value_text == "UNKNOWN":
            findings.append(_finding("UNKNOWN_VALUE", fact.property_code, "REVIEW"))
        if reject_duplicate(conn, fact, source_url=source.url):
            findings.append(_finding("DUPLICATE_ASSERTION", fact.property_code))
        expected_token = DIMENSION_LOCATOR_TOKENS.get(fact.property_code)
        locator = (fact.source_locator or "").lower()
        dimension_tokens = {token for token in DIMENSION_LOCATOR_TOKENS.values() if token in locator}
        if expected_token and dimension_tokens and expected_token not in dimension_tokens:
            findings.append(_finding("SEMANTIC_PROPERTY_MISMATCH", f"{fact.property_code}: {fact.source_locator}"))
        if not fact.value_semantics.strip():
            findings.append(_finding("INVALID_VALUE_SEMANTICS", fact.property_code))
        if fact.observation_ref and fact.observation_ref not in observation_body_by_ref:
            findings.append(_finding("UNRESOLVED_OBSERVATION", fact.observation_ref))
        if fact.observation_ref in observation_body_by_ref and observation_body_by_ref[fact.observation_ref] != fact.body_id:
            findings.append(_finding("CROSS_BODY_OBSERVATION_MISMATCH", fact.property_code))
    for region in record.regions:
        if region.body_id not in body_ids:
            findings.append(_finding("UNRESOLVED_BODY", region.body_id))
        if region.region_id is None and region.canonical_name:
            if not region.region_ref:
                findings.append(_finding("UNRESOLVED_REGION", region.canonical_name))
    for observation in record.observations:
        if observation.body_id not in body_ids:
            findings.append(_finding("UNRESOLVED_BODY", observation.body_id))
        if observation.region_ref is not None and observation.region_ref not in region_refs:
            findings.append(_finding("UNRESOLVED_REGION", observation.region_ref))
        if observation.region_ref in region_body_by_ref and region_body_by_ref[observation.region_ref] != observation.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", observation.observation_product_id or "observation"))
        if observation.region_id in region_body_by_id and region_body_by_id[observation.region_id] != observation.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", observation.observation_product_id or "observation"))
        if observation.region_ref is None and observation.region_id is None and observation.spatial_context:
            if any(name and name in observation.spatial_context.lower() for name in region_name_by_ref.values()):
                findings.append(_finding("RESOLVABLE_REGION_UNLINKED", observation.spatial_context))
    for material in record.materials:
        if material.region_ref is not None and material.region_ref not in region_refs:
            findings.append(_finding("UNRESOLVED_REGION", material.region_ref))
        if material.region_ref in region_body_by_ref and region_body_by_ref[material.region_ref] != material.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", material.material_family))
        if material.region_id in region_body_by_id and region_body_by_id[material.region_id] != material.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", material.material_family))
        if material.region_ref is None and material.region_id is None and material.location_context:
            if any(name and name in material.location_context.lower() for name in region_name_by_ref.values()):
                findings.append(_finding("RESOLVABLE_REGION_UNLINKED", material.location_context))
        if material.evidence_class not in EVIDENCE_CLASSES:
            findings.append(_finding("UNKNOWN_EVIDENCE_CLASS", material.evidence_class))
        if material.confidence_class not in CONFIDENCE_CLASSES:
            findings.append(_finding("UNKNOWN_CONFIDENCE_CLASS", material.confidence_class))
        if material.fact_status not in FACT_STATUSES:
            findings.append(_finding("UNKNOWN_FACT_STATUS", material.fact_status))
        elif material.fact_status != "CANDIDATE":
            findings.append(_finding("NON_CANDIDATE_LOAD", material.fact_status))
        if material.material_family == "water_ice" and material.areal_extent is not None and ("psr" in (material.notes or "").lower() or "cold-trap" in (material.physical_form or "").lower()):
            findings.append(_finding("MODELED_AREA_AS_ICE", material.material_family))
        if any(token in material.material_family.upper() for token in ("RESOURCE", "HABITATION", "CIVPROP")):
            findings.append(_finding("ATTRACTIVENESS_MASQUERADING_AS_FACT", material.material_family))
    for activity in record.activities:
        if activity.evidence_class not in EVIDENCE_CLASSES:
            findings.append(_finding("UNKNOWN_EVIDENCE_CLASS", activity.evidence_class))
        if activity.confidence_class not in CONFIDENCE_CLASSES:
            findings.append(_finding("UNKNOWN_CONFIDENCE_CLASS", activity.confidence_class))
        if activity.region_ref in region_body_by_ref and region_body_by_ref[activity.region_ref] != activity.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", activity.activity_type))
    for product in record.model_products:
        if any(token in product.model_type.upper() for token in ("EPHEMERIS", "CIVPROP", "RESOURCE", "HABITATION")):
            findings.append(_finding("FORBIDDEN_AUTHORITY_SURFACE", product.model_type))
        if product.region_id in region_body_by_id and region_body_by_id[product.region_id] != product.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", product.model_name))
        if product.region_ref is None and product.region_id is None:
            if any(name and name in product.model_name.lower() for name in region_name_by_ref.values()):
                findings.append(_finding("RESOLVABLE_REGION_UNLINKED", product.model_name))
        if product.region_ref in region_body_by_ref and region_body_by_ref[product.region_ref] != product.body_id:
            findings.append(_finding("CROSS_BODY_REGION_MISMATCH", product.model_name))
    for derived in record.derived_quantities:
        if derived.property_code not in known_props:
            findings.append(_finding("UNKNOWN_PROPERTY_CODE", derived.property_code))
        if not derived.input_property_codes:
            findings.append(_finding("DERIVED_WITHOUT_LINEAGE", derived.property_code))
        for input_property in derived.input_property_codes:
            if not any(f.property_code == input_property for f in record.facts):
                findings.append(_finding("DERIVED_INPUT_UNRESOLVED", input_property))
    if any(f.decision == "REJECT" for f in findings):
        decision = "REJECT"
    elif findings:
        decision = "REVIEW"
    else:
        decision = "PASS"
    return ValidationReport(decision, tuple(findings))


def reject_duplicate(conn: sqlite3.Connection, fact: FactCandidate, *, source_id: int | None = None, source_url: str | None = None) -> bool:
    if source_id is not None:
        query = "SELECT 1 FROM fact f JOIN source_assertion sa ON sa.fact_id=f.fact_id WHERE f.body_id=? AND f.property_code=? AND sa.source_id=? AND sa.assertion_role=?"
        args = (fact.body_id, fact.property_code, source_id, fact.assertion_role)
    else:
        query = "SELECT 1 FROM fact f JOIN source_assertion sa ON sa.fact_id=f.fact_id JOIN source s ON s.source_id=sa.source_id WHERE f.body_id=? AND f.property_code=? AND s.url=? AND sa.assertion_role=?"
        args = (fact.body_id, fact.property_code, source_url, fact.assertion_role)
    return conn.execute(query, args).fetchone() is not None
