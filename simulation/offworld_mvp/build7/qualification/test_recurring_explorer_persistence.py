"""A normal annual campaign reopens the PUBLIC exploration window each year."""
import os
import unittest
from uuid import uuid4

from simulation.offworld_mvp.build7.generated_campaign import start_world_run, run_world_annual


@unittest.skipUnless(os.getenv('PGSERVICEFILE'), 'PGSERVICEFILE required for governed persistence proof')
class RecurringExplorerPersistenceTests(unittest.TestCase):
    def test_later_visible_choices_preserve_region_project_and_replay(self):
        import psycopg

        opened=start_world_run(reference_service='reference_reader',
            science_writer_service='science_writer',world_writer_service='world_writer',
            runtime_service='runtime',world_seed='BUILD7-I6-RECURRING-'+uuid4().hex)
        run_id=opened['run_id']
        first=run_world_annual(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2031)
        choices=first['exploration_annual']
        self.assertEqual(tuple(row[0] for row in choices),(2026,2027,2028,2029,2030,2031))
        self.assertTrue(all(row[1]=='SELECT' for row in choices))
        self.assertEqual(len({row[2] for row in choices}),6)
        self.assertEqual(tuple(row[4] for row in choices),('90','80','70','60','50','40'))
        self.assertTrue(all(row[3]=='UNRESOLVED_BODY_CHARACTERIZATION' for row in choices))
        sponsor=first['sponsor_opportunity_annual']
        self.assertEqual(tuple(row[0] for row in sponsor),(2030,2031))
        self.assertTrue(all(row[1] in ('CONSIDER_PROSPECTING','RETAIN_PROJECT','WAIT')
                            for row in sponsor))
        self.assertTrue(all(row[3]=='VISIBLE_ALTERNATIVE_WITHIN_FINANCING_CAPACITY'
                            for row in sponsor if row[1]=='CONSIDER_PROSPECTING'))
        self.assertTrue(all(len(row[4])>=4 for row in sponsor))
        self.assertTrue(all(row[5]==first['capital_coupling']['F'] for row in sponsor))
        self.assertEqual(first['projects'],1)
        self.assertIn(first['project_status'],('EXPLORING','ABANDONED'))
        self.assertEqual(first['project_cash'],'0')
        self.assertEqual(first['capital_coupling']['X'],'20')
        self.assertEqual(first['study_expenses'],1)
        self.assertEqual(first['regional_observations'],4)

        with psycopg.connect(service='runtime') as conn:
            counts=tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                (run_id,)).fetchone()[0] for table in
                ('wa_run.mission','wa_run.observation','wa_run.world_binding',
                 'wa_run.project','wa_run.project_location','wa_info.belief'))
            self.assertEqual(counts,(7,28,6,1,1,52))
            bodies=conn.execute("SELECT b.semantic_key,count(*) FROM wa_run.mission m "
                "JOIN wa_geo.body b ON b.body_id=m.body_id WHERE m.run_id=%s "
                "AND m.interaction_contract_ref='REMOTE:EXPLORATION_REQUEST_BODY_V1' "
                'GROUP BY b.semantic_key ORDER BY b.semantic_key',(run_id,)).fetchall()
            self.assertEqual({body for body,_ in bodies},{row[2] for row in choices})
            self.assertTrue(all(count==1 for _,count in bodies))
            project_body=conn.execute('SELECT b.semantic_key FROM wa_run.project_location pl '
                'JOIN wa_geo.location l ON l.location_id=pl.location_id '
                'JOIN wa_geo.body b ON b.body_id=l.body_id '
                'WHERE pl.run_id=%s',(run_id,)).fetchone()[0]
            self.assertEqual(project_body,choices[0][2])
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_run.observation "
                "WHERE run_id=%s AND method_ref='REMOTE'",(run_id,)).fetchone()[0],24)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_run.observation "
                "WHERE run_id=%s AND method_ref='REGION'",(run_id,)).fetchone()[0],4)

        replay=run_world_annual(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2031)
        for key in ('exploration_annual','annual','project_id','project_status','study_maturity',
                    'project_cash','capital_coupling','public_balance','sponsor_opportunity_annual'):
            self.assertEqual(replay[key],first[key],key)
        self.assertTrue(all(status=='ALREADY_MATCHED' for _,status in replay['epoch_commits']))
        with psycopg.connect(service='runtime') as conn:
            replay_counts=tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                (run_id,)).fetchone()[0] for table in
                ('wa_run.mission','wa_run.observation','wa_run.world_binding',
                 'wa_run.project','wa_run.project_location','wa_info.belief'))
        self.assertEqual(replay_counts,counts)


if __name__=='__main__':unittest.main()
