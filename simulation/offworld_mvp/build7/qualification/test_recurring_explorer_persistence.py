"""Historical pinned-campaign regression; its outcomes are not general criteria."""
import os
import unittest

from simulation.offworld_mvp.build7.generated_campaign import start_world_run, run_world_annual


@unittest.skipUnless(os.getenv('PGSERVICEFILE'), 'PGSERVICEFILE required for governed persistence proof')
class RecurringExplorerPersistenceTests(unittest.TestCase):
    def test_historical_fixed_seed_campaign_regression(self):
        import psycopg

        opened=start_world_run(reference_service='reference_reader',
            science_writer_service='science_writer',world_writer_service='world_writer',
            runtime_service='runtime',
            world_seed='BUILD7-INDEPENDENT-AUDIT-dc6ae50c67134fbb83f857c56437320e')
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
        self.assertEqual(tuple(row[5] for row in sponsor),
            ('29.58025335469291','9.58025335469291'))
        investments=first['sponsor_investment_annual']
        self.assertEqual(len(investments),1)
        self.assertEqual(investments[0][0:3],(2030,'INITIATE_PROJECT',
            'POSITIVE_CHARACTERIZATION_FUNDED'))
        self.assertIsNotNone(investments[0][3])
        self.assertEqual(first['projects'],2)
        self.assertIn(first['project_status'],('EXPLORING','ABANDONED'))
        self.assertEqual(first['project_cash'],'0')
        self.assertEqual(first['capital_coupling']['F'],'9.58025335469291')
        self.assertEqual(first['capital_coupling']['X'],'40')
        self.assertEqual(first['sponsor_funds'],'9.58025335469291')
        self.assertEqual(first['commitments'],2)
        self.assertEqual(first['country_capital_disbursements'],2)
        self.assertEqual(dict(first['project_cash_by_id'])[investments[0][3]],'20')
        self.assertEqual(first['study_expenses'],1)
        self.assertEqual(first['regional_observations'],4)

        with psycopg.connect(service='runtime') as conn:
            counts=tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                (run_id,)).fetchone()[0] for table in
                ('wa_run.mission','wa_run.observation','wa_run.world_binding',
                 'wa_run.project','wa_run.project_location','wa_info.belief'))
            self.assertEqual(counts,(7,28,6,2,2,52))
            bodies=conn.execute("SELECT b.semantic_key,count(*) FROM wa_run.mission m "
                "JOIN wa_geo.body b ON b.body_id=m.body_id WHERE m.run_id=%s "
                "AND m.interaction_contract_ref='REMOTE:EXPLORATION_REQUEST_BODY_V1' "
                'GROUP BY b.semantic_key ORDER BY b.semantic_key',(run_id,)).fetchall()
            self.assertEqual({body for body,_ in bodies},{row[2] for row in choices})
            self.assertTrue(all(count==1 for _,count in bodies))
            project_bodies=conn.execute('SELECT b.semantic_key FROM wa_run.project_location pl '
                'JOIN wa_geo.location l ON l.location_id=pl.location_id '
                'JOIN wa_geo.body b ON b.body_id=l.body_id '
                'WHERE pl.run_id=%s',(run_id,)).fetchall()
            self.assertEqual({row[0] for row in project_bodies},
                {choices[0][2],investments[0][3].split(':')[1]})
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_run.observation "
                "WHERE run_id=%s AND method_ref='REMOTE'",(run_id,)).fetchone()[0],24)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_run.observation "
                "WHERE run_id=%s AND method_ref='REGION'",(run_id,)).fetchone()[0],4)

        replay=run_world_annual(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2031)
        for key in ('exploration_annual','annual','project_id','project_status','study_maturity',
                    'project_cash','capital_coupling','public_balance','sponsor_opportunity_annual'):
            self.assertEqual(replay[key],first[key],key)
        for key in ('sponsor_investment_annual','project_ids','project_cash_by_id',
                    'sponsor_funds','commitments','country_capital_disbursements'):
            self.assertEqual(replay[key],first[key],key)
        self.assertTrue(all(status=='ALREADY_MATCHED' for _,status in replay['epoch_commits']))
        with psycopg.connect(service='runtime') as conn:
            replay_counts=tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                (run_id,)).fetchone()[0] for table in
                ('wa_run.mission','wa_run.observation','wa_run.world_binding',
                 'wa_run.project','wa_run.project_location','wa_info.belief'))
        self.assertEqual(replay_counts,counts)

    def test_two_project_studies_persist_and_replay_independently(self):
        import psycopg

        opened=start_world_run(reference_service='reference_reader',
            science_writer_service='science_writer',world_writer_service='world_writer',
            runtime_service='runtime',
            world_seed='BUILD7-INDEPENDENT-AUDIT-dc6ae50c67134fbb83f857c56437320e')
        run_id=opened['run_id']
        first=run_world_annual(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2035)
        project_ids=first['project_ids']
        self.assertGreaterEqual(len(project_ids),2)
        region_studies=[row for row in first['project_annual'] if row[2]!='NO_ACTION']
        studied={row[1] for row in region_studies}
        self.assertGreaterEqual(len(studied),2)
        self.assertTrue(studied.issubset(set(project_ids)))
        authorized={pid for _,pid,outcome in first['project_annual'] if outcome=='AUTHORIZE'}
        outcomes={pid:{outcome for _,project_id,outcome in first['project_annual']
            if project_id==pid} for pid in project_ids}
        for pid in project_ids:
            self.assertIn('AUTHORIZE',outcomes[pid],pid)
            self.assertTrue(any(outcome.startswith('STUDY_') for outcome in outcomes[pid]),pid)
            self.assertTrue(outcomes[pid].intersection({'ADVANCE','DEFER','ABANDON'}),pid)
        self.assertGreaterEqual(first['study_expenses'],len(project_ids))
        self.assertTrue(all(balance=='0' for _,balance in first['project_cash_by_id']))
        with psycopg.connect(service='runtime') as conn:
            region_bindings=conn.execute('SELECT binding_key FROM wa_run.world_binding '
                "WHERE run_id=%s AND binding_key LIKE 'PROSPECTING_REGION:%%' "
                'ORDER BY binding_key COLLATE "C"',(run_id,)).fetchall()
            self.assertEqual(len(region_bindings),len(authorized))
            projects=conn.execute('SELECT project_id FROM wa_run.project_location '
                "WHERE run_id=%s AND binding_key='PROSPECTING_REGION' "
                'ORDER BY project_id COLLATE "C"',(run_id,)).fetchall()
            self.assertEqual({row[0] for row in projects},set(project_ids))
            study_missions=conn.execute('SELECT project_id FROM wa_run.mission '
                "WHERE run_id=%s AND interaction_contract_ref='REGION:BUILD7_REGION_STUDY_V1' "
                'ORDER BY project_id COLLATE "C"',(run_id,)).fetchall()
            self.assertEqual({row[0] for row in study_missions},authorized)
            observed_projects=conn.execute('SELECT m.project_id,count(o.observation_id) '
                'FROM wa_run.mission m JOIN wa_run.observation o '
                'USING (run_id,mission_id) WHERE m.run_id=%s '
                "AND m.interaction_contract_ref='REGION:BUILD7_REGION_STUDY_V1' "
                "AND o.method_ref='REGION' GROUP BY m.project_id "
                'ORDER BY m.project_id COLLATE "C"',(run_id,)).fetchall()
            self.assertEqual({pid for pid,count in observed_projects if count>0},authorized)
            persisted_counts=tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                (run_id,)).fetchone()[0] for table in
                ('wa_run.mission','wa_run.observation','wa_run.world_binding',
                 'wa_run.project','wa_run.project_location','wa_info.belief'))
        replay=run_world_annual(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2035)
        for key in ('project_ids','project_annual','annual','project_cash_by_id',
                    'capital_coupling','sponsor_investment_annual'):
            self.assertEqual(replay[key],first[key],key)
        self.assertTrue(all(status=='ALREADY_MATCHED' for _,status in replay['epoch_commits']))
        with psycopg.connect(service='runtime') as conn:
            replay_counts=tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                (run_id,)).fetchone()[0] for table in
                ('wa_run.mission','wa_run.observation','wa_run.world_binding',
                 'wa_run.project','wa_run.project_location','wa_info.belief'))
        self.assertEqual(replay_counts,persisted_counts)


if __name__=='__main__':unittest.main()
