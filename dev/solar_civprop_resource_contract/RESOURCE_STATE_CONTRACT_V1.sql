-- CIVPROP resource-state contract over existing Solar Facts v0.3-R1 semantics.
-- This is a consumer view contract, not a replacement material schema.
CREATE VIEW IF NOT EXISTS civprop_material_state_v1 AS
SELECT
  m.material_evidence_id,
  m.body_id,
  m.region_id,
  m.material_family,
  m.material_species,
  m.physical_form,
  m.evidence_class,
  m.abundance_semantics,
  m.abundance_value,
  m.abundance_min,
  m.abundance_max,
  m.abundance_unit,
  m.reported_abundance,
  m.depth_min, m.depth_max, m.depth_unit,
  m.thickness_min, m.thickness_max, m.thickness_unit,
  m.areal_extent, m.areal_extent_unit,
  m.estimated_volume, m.estimated_volume_unit,
  m.spatial_heterogeneity,
  m.measurement_resolution,
  m.measurement_method,
  m.confidence_class,
  m.fact_status,
  m.observation_id,
  m.source_id,
  CASE
    WHEN m.abundance_semantics='UNKNOWN' THEN 'UNKNOWN'
    WHEN m.abundance_value IS NOT NULL THEN 'QUANTIFIED'
    WHEN m.abundance_min IS NOT NULL OR m.abundance_max IS NOT NULL THEN 'BOUNDED'
    WHEN lower(m.abundance_semantics) IN ('present','detected','presence') THEN 'PRESENT_UNQUANTIFIED'
    WHEN lower(m.abundance_semantics) IN ('absent','not_detected','non_detection') THEN 'ABSENT_OR_NONDETECTION'
    WHEN lower(m.abundance_semantics) LIKE '%upper%' THEN 'UPPER_LIMIT'
    ELSE 'EVIDENCE_OTHER'
  END AS civprop_resource_state
FROM material_evidence m;
