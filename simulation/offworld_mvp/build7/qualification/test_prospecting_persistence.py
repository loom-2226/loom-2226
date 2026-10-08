"""Governed Increment 4 prospecting creation and exact replay proof."""
import os
import unittest

from simulation.offworld_mvp.build7.generated_campaign import (
    run_world_prospecting_initiation, start_world_run,
)


@unittest.skipUnless(os.getenv('PGSERVICEFILE'),'PGSERVICEFILE required for governed persistence proof')
class Increment4ProspectingPersistenceTests(unittest.TestCase):
    def test_endogenous_prospecting_project_persists_once_and_replays(self):
        import psycopg

        opened=start_world_run(reference_service='reference_reader',
            science_writer_service='science_writer',world_writer_service='world_writer',
            runtime_service='runtime',world_seed='BUILD7-INCR4-POSITIVE-V2')
        run_id=opened['run_id']
        first=run_world_prospecting_initiation(reference_service='reference_reader',
            runtime_service='runtime',run_id=run_id)
        self.assertEqual(first['prospecting_decision'],'INITIATE_PROJECT')
        self.assertEqual(first['projects'],1)
        self.assertEqual(first['project_stage'],'PROSPECTING')
        self.assertEqual(first['project_cash'],'20')
        self.assertEqual(first['capital_disbursed'],'20')
        self.assertGreater(float(first['capital_mobilized']),20)
        self.assertEqual(first['capital_coupling']['X'],'20')
        self.assertGreaterEqual(float(first['capital_coupling']['F']),0)
        self.assertEqual(first['earth_shadow']['capital_diverted_to_offworld'],'20')
        self.assertEqual((first['settlements'],first['offworld_population']),(0,0))

        replay=run_world_prospecting_initiation(reference_service='reference_reader',
            runtime_service='runtime',run_id=run_id)
        for key in ('selected_body_id','prospecting_decision','prospecting_opportunity_id',
                    'prospecting_region_key','prospecting_location_id','project_id',
                    'project_cash','capital_mobilized','capital_disbursed',
                    'capital_coupling','earth_shadow'):
            self.assertEqual(replay[key],first[key],key)
        self.assertTrue(all(status=='ALREADY_MATCHED' for _,status in replay['epoch_commits']))

        with psycopg.connect(service='runtime') as conn:
            project=conn.execute('SELECT project_id,original_project_artifact_ref FROM wa_run.project '
                'WHERE run_id=%s',(run_id,)).fetchall()
            self.assertEqual(len(project),1)
            location=conn.execute('SELECT pl.world_id,pl.body_id,pl.site_id,pl.location_id,'
                'pl.purpose_ref,l.location_kind,l.origin_kind,l.source_ref '
                'FROM wa_run.project_location pl JOIN wa_geo.location l USING(location_id) '
                'WHERE pl.run_id=%s',(run_id,)).fetchone()
            self.assertEqual(location[:3],(None,None,None))
            self.assertEqual(location[4:7],('PROSPECTING','REGION','AUTHORED_SPATIAL_ANCHOR'))
            self.assertTrue(location[7].startswith('AUTHORED_SPATIAL_ANCHOR:BUILD7_PROSPECTING_REGIONS_V1:'))
            self.assertEqual(str(location[3]),first['prospecting_location_id'])
            self.assertEqual(conn.execute('SELECT count(*) FROM wa_run.project_party '
                'WHERE run_id=%s AND organization_id=%s',(run_id,'SPN')).fetchone()[0],1)
            self.assertEqual(conn.execute('SELECT count(*) FROM wa_run.project_location '
                'WHERE run_id=%s',(run_id,)).fetchone()[0],1)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_geo.location l JOIN wa_geo.body b "
                "ON b.body_id=l.body_id WHERE b.semantic_key=%s AND l.source_ref LIKE "
                "'AUTHORED_SPATIAL_ANCHOR:BUILD7_PROSPECTING_REGIONS_V1:%%'",
                (first['selected_body_id'],)).fetchone()[0],10)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_geo.location WHERE source_ref LIKE "
                "'AUTHORED_SPATIAL_ANCHOR:BUILD7_PROSPECTING_REGIONS_V1:%%'").fetchone()[0],900)
            for table in ('wa_run.asset','wa_run.stock_state','wa_run.accessibility_assessment',
                          'wa_run.recoverability_assessment','wa_run.reserve_interpretation',
                          'wa_run.settlement','wa_run.settlement_location'):
                self.assertEqual(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                    (run_id,)).fetchone()[0],0,table)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_run.population_state "
                "WHERE run_id=%s AND position_key<>'EARTH'",(run_id,)).fetchone()[0],0)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_info.belief WHERE run_id=%s "
                "AND actor_id='SPN' AND belief_key LIKE %s",(run_id,
                'BODY:'+first['selected_body_id']+':%')).fetchone()[0],4)


if __name__=='__main__':unittest.main()
