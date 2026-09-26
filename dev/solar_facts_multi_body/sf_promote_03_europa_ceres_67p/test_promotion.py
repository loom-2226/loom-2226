from __future__ import annotations
import hashlib,json,os,shutil,sqlite3,tempfile,unittest
from pathlib import Path
from promote import BASE,OUT,build,EXPECTED_BASE_SHA,EXPECTED_67P,EXPECTED_CERES,sha
from validate import require_valid,violations
from queries import facts_by_body,observations_by_body,provenance_by_assertion,regional_evidence_by_body,material_evidence_by_body,model_products_by_body,activity_evidence_by_body,frontier_by_campaign,historical_knowledge_by_body,same_property_across_bodies
from narrator import narrate
from sf03_qualify import body_digest,whole_digest
ROOT=Path(__file__).resolve().parent
class ThreeBodyPromotionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.labroot=Path(os.environ['ARP_EUROPA_LAB_ROOT']) if os.environ.get('ARP_EUROPA_LAB_ROOT') else None
  cls.db=build(OUT,cls.labroot)
 def test_baseline_is_exact_sf_promote_02_and_existing_digests_are_unchanged(self):
  self.assertEqual(EXPECTED_BASE_SHA,sha(BASE)[0]);self.assertEqual(EXPECTED_67P,body_digest(self.db,'COMET_67P'));self.assertEqual(EXPECTED_CERES,body_digest(self.db,'CERES'))
 def test_database_integrity_foreign_keys_and_preferred_firewall(self):
  c=sqlite3.connect(self.db);self.assertEqual('ok',c.execute('pragma integrity_check').fetchone()[0]);self.assertEqual([],list(c.execute('pragma foreign_key_check')));self.assertEqual(0,c.execute('select count(*) from preferred_fact').fetchone()[0]);require_valid(self.db)
 def test_all_three_body_neutral_query_lanes(self):
  for body in ('COMET_67P','CERES','EUROPA'):
   self.assertGreater(len(facts_by_body(self.db,body)),0)
   self.assertIsInstance(observations_by_body(self.db,body),list)
   self.assertIsInstance(regional_evidence_by_body(self.db,body),list)
   self.assertIsInstance(material_evidence_by_body(self.db,body),list)
   self.assertIsInstance(model_products_by_body(self.db,body),list)
   self.assertIsInstance(activity_evidence_by_body(self.db,body),list)
  self.assertEqual(10,len(observations_by_body(self.db,'EUROPA')))
  self.assertEqual(3,len(activity_evidence_by_body(self.db,'EUROPA')))
  self.assertEqual(6,len(frontier_by_campaign(self.db,'ARP-QUAL-02-EUROPA')))
  self.assertGreaterEqual(len(historical_knowledge_by_body(self.db,'EUROPA')),10)
 def test_provenance_region_material_model_and_frontier_are_body_scoped(self):
  record=provenance_by_assertion(self.db,'eu-juno-shell')[0]
  self.assertEqual('EUROPA',record['body_id']);self.assertEqual('SCHEMA_LIEN',record['disposition']);self.assertEqual(64,len(record['sha256']))
  regions=regional_evidence_by_body(self.db,'EUROPA');self.assertTrue(any(r['canonical_name']=='Leading hemisphere' for r in regions))
  m=material_evidence_by_body(self.db,'EUROPA');self.assertEqual('UNKNOWN',m[0]['abundance_semantics']);self.assertIsNone(m[0]['abundance_value'])
  self.assertTrue(any(r['kind']=='ORIENTATION' for r in model_products_by_body(self.db,'EUROPA')))
 def test_shared_gm_property_does_not_merge_evidence_lineages(self):
  rec=same_property_across_bodies(self.db,'GM');bodies={r['body_id'] for r in rec}
  self.assertEqual({'COMET_67P','CERES','EUROPA'},bodies)
  sources={b:{r['source_id'] for r in rec if r['body_id']==b and r['source_id'] is not None} for b in bodies}
  for a in sources:
   for b in sources:
    if a<b:self.assertFalse(sources[a]&sources[b])
 def test_every_europa_assertion_has_exactly_one_explicit_disposition(self):
  c=sqlite3.connect(self.db);self.assertEqual((17,17),c.execute("select (select count(*) from promotion_assertion where campaign_id='ARP-QUAL-02-EUROPA'),(select count(*) from promotion_review r join promotion_assertion p using(promotion_assertion_id) where p.campaign_id='ARP-QUAL-02-EUROPA')").fetchone())
  self.assertEqual({'HOLD','PROMOTE','SCHEMA_LIEN'}, {r[0] for r in c.execute("select distinct r.disposition from promotion_review r join promotion_assertion p using(promotion_assertion_id) where p.campaign_id='ARP-QUAL-02-EUROPA'")})
 def test_narrator_never_launders_inference_candidate_unknown_or_scope(self):
  text=narrate(self.db,'EUROPA').lower()
  for forbidden in ['ocean was directly measured','active geysers','ocean contains nacl','shielding','surface temperature:']:
   self.assertNotIn(forbidden,text)
  self.assertIn('candidate factual records',text);self.assertIn('no preferred fact is selected',text)
 def test_campaign_specific_cross_body_hostile_mutations_fail_safely(self):
  mutations=[
   ('europa_ocean_to_ceres',"UPDATE promotion_assertion SET body_id='CERES' WHERE assertion_id='eu-ocean-inference'"),
   ('europa_plume_to_67p',"UPDATE activity_fact SET body_id='COMET_67P' WHERE activity_type='PLUME_CANDIDATE_EVIDENCE' AND body_id='EUROPA' LIMIT 1"),
   ('ceres_source_reuse',"INSERT INTO source_assertion(fact_id,source_id,assertion_role,notes) SELECT fact_id,(SELECT source_id FROM promotion_assertion WHERE campaign_id='ARP-QUAL-02-EUROPA' LIMIT 1),'SUPPORTING','cross-body attack' FROM fact WHERE body_id='CERES' LIMIT 1"),
   ('67p_coma_source_to_europa_ocean',"UPDATE promotion_assertion SET source_id=1 WHERE assertion_id='eu-ocean-inference'"),
   ('cross_body_model_region',"INSERT INTO region_model_product(region_id,model_product_id,relationship) SELECT region_id,(SELECT model_product_id FROM body_model_product WHERE body_id='EUROPA' LIMIT 1),'HOSTILE' FROM body_region WHERE body_id='CERES' LIMIT 1"),
   ('cross_body_frontier',"UPDATE epistemic_frontier SET variable='CERES_EUROPA_FRONTIER_LEAK' WHERE campaign_id='ARP-QUAL-02-EUROPA' LIMIT 1"),
   ('cross_body_derivation',"UPDATE promotion_lineage SET input_assertion_ids_json='[\"CERES:ACTIVITY_INTERPRETATION:1:1\"]' WHERE promotion_assertion_id=(SELECT promotion_assertion_id FROM promotion_assertion WHERE assertion_id='eu-ocean-inference')"),
   ('unknown_to_zero',"UPDATE fact SET value_numeric=0 WHERE body_id='EUROPA' AND property_code='GM'"),
   ('candidate_to_current',"UPDATE promotion_assertion SET status='CURRENT' WHERE assertion_id='eu-plume-galileo-candidate'"),
   ('post_cutoff',"UPDATE source SET publication_date='2026-01-01' WHERE source_id=(SELECT source_id FROM promotion_assertion WHERE assertion_id='eu-juno-shell')"),
   ('radiation_source_to_other_body',"UPDATE observation SET body_id='CERES' WHERE body_id='EUROPA' AND instrument='Juno/MWR'"),
   ('regional_composition_to_global',"UPDATE material_evidence SET region_id=NULL WHERE body_id='EUROPA'"),
   ('ceres_water_source_reused_in_europa',"UPDATE source_assertion SET source_id=(SELECT source_id FROM source_assertion JOIN fact USING(fact_id) WHERE fact.body_id='CERES' LIMIT 1) WHERE fact_id=(SELECT fact_id FROM fact WHERE body_id='EUROPA' AND property_code='GM' LIMIT 1)"),
   ('67p_coma_source_reused_in_europa_ocean',"UPDATE source_assertion SET source_id=(SELECT source_id FROM observation WHERE body_id='COMET_67P' LIMIT 1) WHERE fact_id=(SELECT fact_id FROM fact WHERE body_id='EUROPA' AND property_code='GM' LIMIT 1)"),
  ]
  for name,sql in mutations:
   with self.subTest(name=name),tempfile.TemporaryDirectory() as td:
    p=Path(td)/'attack.db';shutil.copy2(self.db,p);c=sqlite3.connect(p);c.execute('pragma foreign_keys=off')
    rejected=False
    try:c.execute(sql);c.commit()
    except sqlite3.DatabaseError:rejected=True
    c.close();self.assertTrue(rejected or violations(p),name)
 def test_duplicate_identity_and_cross_body_replay_collisions_are_blocked(self):
  c=sqlite3.connect(self.db);self.assertEqual(1,c.execute("select count(*) from body where body_id='EUROPA'").fetchone()[0]);self.assertEqual(1,c.execute("select count(*) from body_authority where authority_system='loom_solar.body' and authority_identifier='EUROPA'").fetchone()[0]);self.assertEqual(0,c.execute("select count(*) from preferred_fact where body_id='EUROPA'").fetchone()[0])
 def test_deterministic_replay_and_reverse_sql_row_order(self):
  with tempfile.TemporaryDirectory() as td:
   a=build(Path(td)/'a.sqlite3',self.labroot);b=build(Path(td)/'b.sqlite3',self.labroot)
   self.assertEqual(sha(a)[0],sha(b)[0])
   # Reverse SQL insertion order in an ephemeral semantic clone, preserving the frozen database authority.
   src=sqlite3.connect(a);lines=list(src.iterdump());src.close();rev=Path(td)/'reverse.sqlite3';c=sqlite3.connect(rev);c.execute('pragma foreign_keys=off')
   ddl=[x for x in lines if not x.startswith('INSERT INTO') and x not in ('BEGIN TRANSACTION;','COMMIT;')]
   ins=[x for x in lines if x.startswith('INSERT INTO')]
   for x in ddl:c.execute(x)
   for x in reversed(ins):c.execute(x)
   c.commit();c.close()
   for body in ('COMET_67P','CERES','EUROPA'):self.assertEqual(body_digest(a,body),body_digest(rev,body))
   self.assertEqual(whole_digest(a),whole_digest(rev))
if __name__=='__main__':unittest.main()
