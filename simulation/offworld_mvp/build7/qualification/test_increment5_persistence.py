"""Governed annual REGION study, next-year review, and exact replay."""
import os
import unittest
import uuid
from unittest.mock import Mock, patch

from loom_world_authority import store
from simulation.offworld_mvp.build7.generated_campaign import start_world_run, run_world_annual


@unittest.skipUnless(os.getenv('PGSERVICEFILE'),'PGSERVICEFILE required for governed persistence proof')
class Increment5PersistenceTests(unittest.TestCase):
    def test_ambiguous_region_resolution_fails_closed(self):
        conn=Mock()
        conn.execute.return_value.fetchall.return_value=[('BODY',),('BODY',)]
        with patch.object(store,'_require_session_group'):
            with self.assertRaises(store.IntegrityFailure):
                store.read_run_region_world_identity(conn,'RUN','PROJECT',uuid.uuid4())

    def test_annual_region_study_reopens_and_reviews_changed_state(self):
        import psycopg
        opened=start_world_run(reference_service='reference_reader',
            science_writer_service='science_writer',world_writer_service='world_writer',
            runtime_service='runtime',world_seed='BUILD7-I5-QUAL-POSITIVE-V3')
        run_id=opened['run_id']
        first=run_world_annual(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2029)
        self.assertEqual(first['generated_body_count'],90)
        self.assertEqual(first['projects'],1)
        self.assertEqual(first['annual'][0][1],'AUTHORIZE')
        self.assertTrue(first['annual'][1][1].startswith('STUDY_'))
        self.assertIn(first['annual'][2][1],('ADVANCE','DEFER','ABANDON'))
        self.assertEqual(first['study_expenses'],1)
        self.assertEqual(first['regional_observations'],4)
        self.assertEqual(first['study_reviews'],1)
        self.assertEqual(first['project_cash'],'0')
        with psycopg.connect(service='runtime') as conn:
            self.assertEqual(conn.execute('SELECT count(*) FROM wa_run.world_binding '
                "WHERE run_id=%s AND binding_key NOT LIKE 'BODY_REMOTE:%%'",
                (run_id,)).fetchone()[0],0)
            self.assertEqual(conn.execute('SELECT count(*) FROM wa_run.project '
                'WHERE run_id=%s',(run_id,)).fetchone()[0],1)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_geo.location WHERE source_ref LIKE "
                "'AUTHORED_SPATIAL_ANCHOR:BUILD7_PROSPECTING_REGIONS_V1:%%'").fetchone()[0],900)
            self.assertEqual(conn.execute("SELECT count(*) FROM (SELECT body_id FROM wa_geo.location "
                "WHERE source_ref LIKE 'AUTHORED_SPATIAL_ANCHOR:BUILD7_PROSPECTING_REGIONS_V1:%%' "
                "GROUP BY body_id HAVING count(*)<>10) invalid").fetchone()[0],0)
            project_id=first['project_id']
            location_id=conn.execute('SELECT location_id FROM wa_run.project_location '
                'WHERE run_id=%s AND project_id=%s',(run_id,project_id)).fetchone()[0]
            self.assertEqual(store.read_run_region_world_identity(conn,run_id,project_id,location_id)[1],
                store.read_run_body_world_identity(conn,run_id,project_id.split(':')[1])[1])
            truth=store.load_run_region_material_truth(conn,run_id,project_id,location_id)
            self.assertEqual(set(truth),{'VOLATILES','METALS','SILICATES_ROCK','CARBONACEOUS_ORGANICS'})
            with self.assertRaises(store.IntegrityFailure):
                store.read_run_region_world_identity(conn,run_id,project_id,uuid.uuid4())
            with self.assertRaises(store.IntegrityFailure):
                store.read_run_region_world_identity(conn,run_id,'MISSING',location_id)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_run.observation "
                "WHERE run_id=%s AND measurement_schema_ref='REGION_MATERIAL_SIGNAL_V1'",
                (run_id,)).fetchone()[0],4)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_info.belief "
                "WHERE run_id=%s AND actor_id='SPN' AND belief_key LIKE %s",
                (run_id,'%:REGION:'+str(location_id)+':%')).fetchone()[0],4)
            for table in ('wa_run.stock_state','wa_run.recoverability_assessment',
                          'wa_run.reserve_interpretation','wa_run.settlement'):
                self.assertEqual(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                    (run_id,)).fetchone()[0],0,table)
        with psycopg.connect(service='agent_spn') as conn:
            with self.assertRaises(Exception):
                store.load_run_region_material_truth(conn,run_id,project_id,location_id)
        replay=run_world_annual(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2029)
        for key in ('project_id','annual','project_status','study_maturity','project_cash',
                    'study_expenses','regional_observations','study_reviews'):
            self.assertEqual(replay[key],first[key],key)
        self.assertTrue(all(status=='ALREADY_MATCHED' for _,status in replay['epoch_commits']))


if __name__=='__main__':unittest.main()
