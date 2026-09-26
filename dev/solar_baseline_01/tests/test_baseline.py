import hashlib,json,os,shutil,sqlite3,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.environ.get('BASELINE_DB',ROOT/'LOOM_SOLAR_BASELINE_01_CANDIDATE_V19.sqlite3'))
CONTROL=Path(__file__).resolve().parents[3]/'dev/solar_facts_multi_body/sf_promote_03_europa_ceres_67p/LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3'
sys.path.insert(0,str(ROOT/'scripts'))
from semantic_digest import digest
from queries import facts_by_body,provenance_by_assertion,same_property_by_body
sys.path.insert(0,str(CONTROL.parent))
from sf03_qualify import body_digest,whole_digest
class BaselineQualification(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.con=sqlite3.connect(DB);cls.con.execute('pragma foreign_keys=on');cls.con.row_factory=sqlite3.Row
  cls.pre=json.loads((ROOT/'reports/pre_mutation_freeze.json').read_text())
 def test_sqlite_integrity_and_foreign_keys(self):
  self.assertEqual('ok',self.con.execute('pragma integrity_check').fetchone()[0]);self.assertEqual([],list(self.con.execute('pragma foreign_key_check')))
 def test_existing_identity_population_exactly_110(self):
  rows=self.con.execute('select body_id from authority_body_ref order by body_id').fetchall()
  source=(ROOT/'raw/loom_solar_identity_snapshot.tsv').read_text().splitlines()
  self.assertEqual(110,len(rows));self.assertEqual(110,len(source));self.assertEqual({r['body_id'] for r in rows},{l.split('|')[0] for l in source})
  self.assertEqual(0,self.con.execute("select count(*) from authority_body_ref where authority<>'loom_solar.body'").fetchone()[0])
 def test_candidate_and_preference_firewall(self):
  self.assertEqual(788,self.con.execute('select count(*) from candidate_assertion').fetchone()[0])
  self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where fact_status<>'CANDIDATE' or preferred_fact<>0").fetchone()[0])
  self.assertEqual({'CANDIDATE','HOLD'}, {r[0] for r in self.con.execute('select distinct disposition from candidate_assertion')})
  self.assertEqual(758,self.con.execute("select count(*) from candidate_assertion where disposition='CANDIDATE'").fetchone()[0])
  self.assertEqual(30,self.con.execute("select count(*) from candidate_assertion where disposition='HOLD'").fetchone()[0])
 def test_collision_europa_moon_and_asteroid_52(self):
  self.assertEqual('EUROPA',self.con.execute("select body_id from body_identifier_ref where authority='NAIF' and identifier_value='502'").fetchone()[0])
  self.assertIsNone(self.con.execute("select body_id from body_identifier_ref where authority='NAIF' and identifier_value='2000052'").fetchone())
  self.assertEqual(0,self.con.execute("select count(*) from identity_crosswalk where external_id='2000052' and body_id='EUROPA'").fetchone()[0])
 def test_barycenter_primary_identity_holds(self):
  held={'DIDYMOS','EURYBATES','KLEOPATRA','PATROCLUS'}
  got={r[0] for r in self.con.execute("select distinct body_id from candidate_assertion where disposition='HOLD'")}
  self.assertEqual(held,got)
  for b in held:self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where body_id=? and disposition='CANDIDATE'",(b,)).fetchone()[0])
 def test_naif_alias_requires_official_formula_and_exact_returned_id(self):
  x=self.con.execute("select * from identity_crosswalk where external_id='2101955' and body_id='BENNU'").fetchone()
  self.assertIsNotNone(x);self.assertIn('legacy/extended alias formula',x['match_basis']);self.assertEqual('MATCH_ALIAS',x['disposition'])
 def test_comet_aliases_do_not_create_new_identities(self):
  p=ROOT/'raw/sbdb_spk_1000012.json';data=json.loads(p.read_text())
  self.assertEqual('1000012',data['object']['spkid']);self.assertTrue(data['object'].get('des_alt'))
  self.assertEqual(110,self.con.execute('select count(*) from authority_body_ref').fetchone()[0])
 def test_name_only_crosswalk_is_not_used_for_small_bodies(self):
  self.assertEqual(0,self.con.execute("select count(*) from identity_crosswalk where match_basis like '%NAME%' and external_id_scheme<>'JPL_CANONICAL_NAME_AND_BODY_CLASS'").fetchone()[0])
  self.assertEqual(0,self.con.execute("select count(*) from identity_crosswalk where external_id_scheme='JPL_CANONICAL_NAME_AND_BODY_CLASS' and notes not like '%class bounds collision risk%'").fetchone()[0])
 def test_diameter_radius_and_shape_remain_distinct(self):
  codes={r[0] for r in self.con.execute('select distinct property_code from candidate_assertion')}
  for x in ('EFFECTIVE_DIAMETER','MEAN_RADIUS','EQUATORIAL_RADIUS','TRIAXIAL_DIMENSIONS','TRIAXIAL_RADII'):self.assertIn(x,codes)
  self.assertNotIn('RADIUS',codes);self.assertGreater(self.con.execute("select count(*) from candidate_assertion where property_code='TRIAXIAL_DIMENSIONS' and normalized_value is null").fetchone()[0],0)
 def test_km_m_and_radius_terrain_semantics_do_not_launder(self):
  # This adapter retains reported units; it does not perform a silent km<->m
  # scale change and it never treats reference shape as local terrain elevation.
  rows=self.con.execute("select property_code,reported_unit,normalized_unit,scope from candidate_assertion where property_code in ('EFFECTIVE_DIAMETER','MEAN_RADIUS','EQUATORIAL_RADIUS','TRIAXIAL_RADII','TRIAXIAL_DIMENSIONS') and normalized_value is not null").fetchall()
  self.assertTrue(rows)
  self.assertTrue(all(r['reported_unit']==r['normalized_unit'] for r in rows))
  self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where property_code in ('LOCAL_TERRAIN_ELEVATION','SURFACE_ELEVATION','TOPOGRAPHIC_HEIGHT')").fetchone()[0])
  self.assertNotIn('regional_elevation', {r[0] for r in self.con.execute("select name from sqlite_master where type='table'")})
  self.assertTrue(all(r['scope'] in ('BODY','BODY_IDENTITY') for r in rows))
 def test_gm_mass_and_volume_are_not_conflated(self):
  self.assertNotEqual('MASS','GM');self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where property_code='VOLUME'").fetchone()[0])
  self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where property_code='GM' and reported_unit in ('kg','10^18 kg','10^24 kg')").fetchone()[0])
 def test_only_geometric_albedo_is_loaded(self):
  self.assertGreater(self.con.execute("select count(*) from candidate_assertion where property_code='GEOMETRIC_ALBEDO'").fetchone()[0],0)
  self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where property_code like '%BOND%'").fetchone()[0])
 def test_rotation_units_and_orientation_models_stay_separate(self):
  r=facts_by_body(self.con,'CERES'); periods=[x for x in r if x['property_code']=='ROTATION_PERIOD']
  self.assertIn('d',{x['reported_unit'] for x in periods});self.assertIn('h',{x['reported_unit'] for x in periods})
  self.assertTrue(all(x['normalized_unit']==x['reported_unit'] for x in periods))
  self.assertGreater(self.con.execute("select count(*) from candidate_assertion where property_code='PRIME_MERIDIAN_MODEL' and epistemic_class='PHYSICAL_MODEL'").fetchone()[0],0)
 def test_unknowns_never_become_zero(self):
  self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where reported_value='0' and property_code in ('MASS','GM','VOLUME')").fetchone()[0])
  self.assertEqual(0,self.con.execute("select count(*) from coverage where disposition='FIELD_NULL_IN_SOURCE' and assertion_count>0").fetchone()[0])
 def test_ranges_limits_and_vector_uncertainties_are_preserved(self):
  r=self.con.execute("select reported_value,reported_uncertainty,normalized_value from candidate_assertion where body_id='CERES' and property_code='TRIAXIAL_DIMENSIONS' limit 1").fetchone()
  self.assertIn('x',r['reported_value']);self.assertIsNone(r['normalized_value'])
  self.assertIsNotNone(self.con.execute("select 1 from candidate_assertion where reported_uncertainty is not null limit 1").fetchone())
  limit=self.con.execute("select reported_value,normalized_value from candidate_assertion where body_id='KERBEROS' and property_code='GM' and reported_value like '<%'").fetchone()
  self.assertEqual('<0.0002',limit['reported_value']);self.assertEqual('<0.0002',limit['normalized_value'])
 def test_density_and_reference_value_semantics_are_preserved(self):
  self.assertGreater(self.con.execute("select count(*) from candidate_assertion where epistemic_class='DERIVED' and source_value_kind='DERIVED_PARAMETER'").fetchone()[0],0)
  self.assertGreater(self.con.execute("select count(*) from candidate_assertion where epistemic_class='UNKNOWN' and source_value_kind='REFERENCE_CONSTANT'").fetchone()[0],0)
  self.assertGreater(self.con.execute("select count(*) from candidate_assertion where epistemic_class='DYNAMICAL_INFERENCE' and property_code='GM'").fetchone()[0],0)
 def test_phase4_ephemerides_not_duplicated(self):
  tables={r[0] for r in self.con.execute("select name from sqlite_master where type='table'")}
  self.assertNotIn('ephemeris',tables);self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where property_code in ('POSITION_VECTOR','STATE_VECTOR','VELOCITY_VECTOR','ORBITAL_STATE')").fetchone()[0])
 def test_sources_and_hashes_are_complete(self):
  self.assertEqual(65,self.con.execute('select count(*) from source_artifact').fetchone()[0])
  self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where source_artifact_id is null or source_lineage is null or source_payload_json is null").fetchone()[0])
  self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion a left join source_artifact s on s.artifact_id=a.source_artifact_id where s.artifact_id is null").fetchone()[0])
 def test_live_api_version_difference_and_temporal_capture_are_recorded(self):
  first=json.loads((ROOT/'reports/first_pass_sbdb_acquisition_manifest.json').read_text())
  cross=json.loads((ROOT/'reports/sbdb_identity_crosswalk.json').read_text())
  self.assertTrue(any(x['error']=='unexpected API signature' for x in first['failures']))
  self.assertEqual(1,cross['match_alias']);self.assertEqual(4,cross['identity_hold'])
  self.assertTrue(all(r['signature']['version']=='1.3' for r in cross['records']))
 def test_conflicts_are_preserved_without_preference(self):
  rows=list(self.con.execute("select normalized_value from candidate_assertion where body_id='CERES' and property_code='GM' and disposition='CANDIDATE'"))
  self.assertGreaterEqual(len({r[0] for r in rows}),2)
  self.assertEqual(0,self.con.execute("select count(*) from candidate_assertion where preferred_fact<>0").fetchone()[0])
 def test_crosswalk_is_body_scoped_and_lineage_includes_source_id(self):
  for r in self.con.execute("select body_id,source_lineage,source_payload_json from candidate_assertion where source_lineage like 'NAIF:%'"):
   self.assertEqual(r['body_id'],json.loads(r['source_payload_json'])['loom_body_id'])
  self.assertGreater(self.con.execute("select count(*) from identity_crosswalk where disposition='HOLD'").fetchone()[0],0)
 def test_cross_body_source_payload_mutation_fails_closed(self):
  row=self.con.execute("select assertion_id from candidate_assertion where body_id='EUROPA' limit 1").fetchone()
  with tempfile.TemporaryDirectory() as td:
   attack=Path(td)/'cross-body.sqlite3';shutil.copy2(DB,attack);con=sqlite3.connect(attack)
   with self.assertRaises(sqlite3.IntegrityError):
    con.execute("update candidate_assertion set body_id='CERES' where assertion_id=?",(row['assertion_id'],))
   con.close()
 def test_shared_source_artifacts_do_not_merge_body_lineages(self):
  shared=list(self.con.execute("select source_artifact_id from candidate_assertion group by source_artifact_id having count(distinct body_id)>1"))
  self.assertTrue(shared)
  for item in shared:
   a=item['source_artifact_id']
   rows=list(self.con.execute("select distinct body_id,source_lineage,json_extract(source_payload_json,'$.loom_body_id') payload_body from candidate_assertion where source_artifact_id=?",(a,)))
   self.assertGreater(len({x['body_id'] for x in rows}),1)
   self.assertEqual(len(rows),len({(x['body_id'],x['source_lineage']) for x in rows}))
   self.assertTrue(all(x['body_id']==x['payload_body'] for x in rows))
 def test_generic_queries_keep_body_provenance(self):
  eu=facts_by_body(self.con,'EUROPA');ce=facts_by_body(self.con,'CERES')
  self.assertTrue(eu);self.assertTrue(ce);self.assertTrue(all(x['body_id']=='EUROPA' for x in eu));self.assertTrue(all(x['body_id']=='CERES' for x in ce))
  row=eu[0];self.assertEqual(row['source_artifact_id'],provenance_by_assertion(self.con,row['assertion_id'])['source_artifact_artifact_id'])
  same=same_property_by_body(self.con,'GM');self.assertGreater(len({x['body_id'] for x in same}),2)
 def test_no_downstream_engineering_or_economic_judgments(self):
  banned=('ISRU','RESOURCE_SCORE','ORE_GRADE','MINING','HABITATION','SHIELDING','DELTA_V','TRANSPORT_COST','CIVPROP','CIVSTATE','SETTLEMENT')
  codes=[r[0] for r in self.con.execute('select distinct property_code from candidate_assertion')]
  self.assertFalse([x for x in codes if any(y in x for y in banned)])
 def test_three_body_baseline_file_and_semantics_unchanged(self):
  self.assertEqual(self.pre['qualified_sf03_database_sha256'],hashlib.sha256(CONTROL.read_bytes()).hexdigest())
  for b in ('CERES','COMET_67P','EUROPA'):self.assertEqual(self.pre['qualified_sf03_body_digests'][b],body_digest(CONTROL,b))
  self.assertEqual(self.pre['qualified_sf03_whole_semantic_digest'],whole_digest(CONTROL))
  self.assertEqual(0,sqlite3.connect(CONTROL).execute('select count(*) from preferred_fact').fetchone()[0])
 def test_replay_semantic_digest_matches_frozen_report(self):
  self.assertEqual(digest(DB),json.loads((ROOT/'reports/determinism_report.json').read_text())['canonical_semantic_digest'])
if __name__=='__main__':unittest.main(verbosity=2)
