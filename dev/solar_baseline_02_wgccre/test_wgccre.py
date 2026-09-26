import hashlib
import json
import sqlite3
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DB=HERE/'LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3'
SOURCE=HERE/'reports/source_acquisition.json'

class WGCCREDataQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn=sqlite3.connect(DB)
        cls.conn.row_factory=sqlite3.Row
        cls.freeze=json.loads(SOURCE.read_text())
        cls.wgccre_ids={x['acquired_artifact_sha256'] for x in cls.freeze['sources'] if 'acquired_artifact_sha256' in x}
        cls.wgccre_ids.add(cls.freeze['sources'][0]['sha256'])

    @classmethod
    def tearDownClass(cls): cls.conn.close()

    def test_existing_identity_population_and_zero_preference(self):
        self.assertEqual(self.conn.execute('select count(*) from authority_body_ref').fetchone()[0],110)
        self.assertEqual(self.conn.execute('select count(*) from candidate_assertion').fetchone()[0],922)
        self.assertEqual(self.conn.execute('select count(*) from candidate_assertion where preferred_fact<>0').fetchone()[0],0)
        self.assertEqual(self.conn.execute("select count(*) from candidate_assertion where source_artifact_id in (?,?)",tuple(sorted(self.wgccre_ids))).fetchone()[0],134)

    def test_table1_to3_rows_are_bound_to_existing_bodies(self):
        self.assertEqual(self.conn.execute("select count(distinct body_id) from candidate_assertion where source_artifact_id in (?,?)",tuple(sorted(self.wgccre_ids))).fetchone()[0],44)
        self.assertIsNotNone(self.conn.execute("select 1 from candidate_assertion where body_id='COMET_67P' and property_code='PRIME_MERIDIAN_MODEL'").fetchone())
        self.assertIsNotNone(self.conn.execute("select 1 from candidate_assertion where body_id='PLUTO' and property_code='PRIME_MERIDIAN_MODEL'").fetchone())
        self.assertEqual(self.conn.execute("select count(*) from authority_body_ref where canonical_name like '%52 Europa%'").fetchone()[0],0)

    def test_europa_asteroid_collision_is_held_and_moon_parent_scoped(self):
        collision=self.conn.execute("select body_id,external_id,disposition,notes from identity_crosswalk where external_id_scheme='WGCCRE_MPC_NUMBER' and external_id='52'").fetchone()
        self.assertIsNone(collision['body_id']);self.assertEqual(collision['disposition'],'HOLD')
        moon=self.conn.execute("select * from identity_crosswalk where external_id_scheme='WGCCRE_TABLE_ROW' and external_id='TABLE_2:Europa'").fetchone()
        self.assertEqual(moon['body_id'],'EUROPA');self.assertIn('matching WGCCRE parent heading',moon['match_basis'])

    def test_phobos_corrigendum_is_preserved_without_preference(self):
        rows=self.conn.execute("select disposition,reported_value,source_artifact_id from candidate_assertion where body_id='PHOBOS' and property_code='PRIME_MERIDIAN_MODEL'").fetchall()
        legacy=[r for r in rows if r['source_artifact_id']==self.freeze['sources'][0]['sha256']]
        corrected=[r for r in rows if r['source_artifact_id']==self.freeze['sources'][1]['acquired_artifact_sha256']]
        self.assertEqual(len(legacy),1);self.assertEqual(legacy[0]['disposition'],'HOLD')
        self.assertIn('+ 1.143 sin(M5)',legacy[0]['reported_value'])
        self.assertEqual(len(corrected),1);self.assertEqual(corrected[0]['disposition'],'CANDIDATE')
        self.assertIn('35.18774440',corrected[0]['reported_value']);self.assertIn('− 1.143 sin(M5)',corrected[0]['reported_value'])
        self.assertEqual(self.conn.execute("select preferred_fact from candidate_assertion where assertion_id=(select assertion_id from candidate_assertion where body_id='PHOBOS' and source_artifact_id=?)",(corrected[0]['source_artifact_id'],)).fetchone()[0],0)

    def test_temporal_scopes_and_non_numeric_models_are_retained(self):
        for body,count in (('TEMPEL1',4),('BORRELLY',3),('COMET_67P',3)):
            self.assertEqual(self.conn.execute("select count(*) from candidate_assertion where body_id=? and scope='EPOCH_SCOPED_MODEL'",(body,)).fetchone()[0],count)
        self.assertEqual(self.conn.execute("select count(*) from candidate_assertion where body_id='HARTLEY2' and source_artifact_id in (?,?)",tuple(sorted(self.wgccre_ids))).fetchone()[0],0)
        self.assertEqual(self.conn.execute("select count(*) from coverage where property_code='PRIME_MERIDIAN_RATE_MODEL'").fetchone()[0],2)

    def test_integrity_and_input_authority_files(self):
        self.assertEqual(self.conn.execute('pragma integrity_check').fetchone()[0],'ok')
        self.assertEqual(self.conn.execute('pragma foreign_key_check').fetchall(),[])
        for x in self.freeze['sources'][:2]:
            self.assertRegex(x.get('sha256',x.get('acquired_artifact_sha256')),r'^[a-f0-9]{64}$')
        self.assertEqual(hashlib.sha256((HERE/'derived/WGCCRE_2019_Phobos_correction_excerpt.txt').read_bytes()).hexdigest(),self.freeze['sources'][1]['frozen_derivative_sha256'])

if __name__=='__main__':unittest.main()
