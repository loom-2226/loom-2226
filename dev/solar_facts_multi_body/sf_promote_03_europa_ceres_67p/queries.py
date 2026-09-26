"""Body-neutral read APIs for the multi-body Solar Facts representation."""
import sqlite3

def _query(db,sql,args=()):
 c=sqlite3.connect(db);c.row_factory=sqlite3.Row
 try:return [dict(r) for r in c.execute(sql,args)]
 finally:c.close()
def facts_by_body(db,body_id):return _query(db,'SELECT * FROM fact WHERE body_id=? ORDER BY fact_id',(body_id,))
def observations_by_body(db,body_id):return _query(db,'SELECT * FROM observation WHERE body_id=? ORDER BY observation_id',(body_id,))
def provenance_by_assertion(db,assertion_id):
 return _query(db,"""SELECT p.assertion_id,p.body_id,p.property_code,p.evidence_class,p.scope_type,p.temporal_context,p.notes AS assertion_notes,s.source_id,s.provider,s.title,s.doi,s.url,sa.artifact_id,sa.sha256,sa.byte_count,sa.local_path,r.disposition,r.reason FROM promotion_assertion p JOIN source s USING(source_id) JOIN source_artifact sa USING(artifact_id) JOIN promotion_review r USING(promotion_assertion_id) WHERE p.assertion_id=?""",(assertion_id,))
def regional_evidence_by_body(db,body_id):
 return _query(db,"""SELECT b.region_id,b.canonical_name,b.region_type,o.observation_id,o.instrument,o.spatial_context,o.observation_time_start,o.observation_time_end,o.notes FROM body_region b LEFT JOIN observation o ON o.region_id=b.region_id WHERE b.body_id=? ORDER BY b.region_id,o.observation_id""",(body_id,))
def material_evidence_by_body(db,body_id):return _query(db,'SELECT m.*,b.canonical_name AS region_name,o.instrument,s.title AS source_title FROM material_evidence m LEFT JOIN body_region b ON b.region_id=m.region_id LEFT JOIN observation o USING(observation_id) LEFT JOIN source s USING(source_id) WHERE m.body_id=? ORDER BY m.material_evidence_id',(body_id,))
def model_products_by_body(db,body_id):
 return _query(db,"""SELECT 'BODY_MODEL' AS model_table,model_product_id AS id,model_type AS kind,model_name AS name,model_version AS version,region_id,source_id,notes FROM body_model_product WHERE body_id=? UNION ALL SELECT 'ORIENTATION_MODEL',orientation_model_id,'ORIENTATION',model_name,model_version,NULL,source_id,notes FROM orientation_model WHERE body_id=? ORDER BY model_table,id""",(body_id,body_id))
def activity_evidence_by_body(db,body_id):return _query(db,'SELECT * FROM activity_fact WHERE body_id=? ORDER BY activity_id',(body_id,))
def frontier_by_campaign(db,campaign_id):return _query(db,'SELECT * FROM epistemic_frontier WHERE campaign_id=? ORDER BY variable',(campaign_id,))
def historical_knowledge_by_body(db,body_id):
 return _query(db,"""SELECT DISTINCT e.event_time,e.event_type,e.event_key,s.provider,s.title,e.notes FROM knowledge_event e JOIN source s ON s.source_id=e.target_source_id WHERE e.target_source_id IN (SELECT source_id FROM promotion_assertion WHERE body_id=?) OR e.target_source_id IN (SELECT source_id FROM source_assertion WHERE fact_id IN (SELECT fact_id FROM fact WHERE body_id=?)) OR e.target_source_id IN (SELECT source_id FROM observation WHERE body_id=?) OR e.target_source_id IN (SELECT source_id FROM activity_fact WHERE body_id=?) OR e.target_source_id IN (SELECT source_id FROM body_model_product WHERE body_id=?) OR e.target_source_id IN (SELECT source_id FROM orientation_model WHERE body_id=?) ORDER BY e.event_time,e.event_key""",(body_id,body_id,body_id,body_id,body_id,body_id))
def same_property_across_bodies(db,property_code):
 return _query(db,"""SELECT f.body_id,f.fact_id,f.property_code,f.value_numeric,f.value_min,f.value_max,f.value_text,f.canonical_unit,f.evidence_class,f.spatial_context,f.temporal_context,s.source_id,s.title FROM fact f LEFT JOIN source_assertion x USING(fact_id) LEFT JOIN source s USING(source_id) WHERE f.property_code=? ORDER BY f.body_id,f.fact_id,s.source_id""",(property_code,))
