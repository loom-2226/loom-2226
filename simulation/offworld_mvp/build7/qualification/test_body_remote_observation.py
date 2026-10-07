"""Governed, project-free body characterization and exact reopen proof."""
import os
import unittest
from uuid import uuid4

from simulation.offworld_mvp.build7.generated_campaign import (
    run_world_remote_choice, start_world_run)
from simulation.offworld_mvp.build7.opportunities import load_visible_inputs


@unittest.skipUnless(os.getenv('PGSERVICEFILE'), 'PGSERVICEFILE required for governed persistence proof')
class BodyRemoteObservationPersistenceTests(unittest.TestCase):
    def test_body_mission_observation_knowledge_and_replay(self):
        import psycopg
        from psycopg import sql
        from psycopg.rows import dict_row
        from loom_world_authority.store import stable_uuid

        opened=start_world_run(reference_service='reference_reader',
            science_writer_service='science_writer',world_writer_service='world_writer',
            runtime_service='runtime',world_seed='BUILD7-INCR3-TEST-'+uuid4().hex)
        run_id=opened['run_id']
        self.assertEqual(opened['candidate_mission_count'],90)
        self.assertEqual((opened['projects'],opened['settlements'],opened['offworld_population']),(0,0,0))

        first=run_world_remote_choice(reference_service='reference_reader',
            runtime_service='runtime',run_id=run_id)
        self.assertEqual(first['choice'],'SELECT')
        self.assertEqual(first['public_balance'],'90')
        self.assertEqual((first['projects'],first['settlements'],first['offworld_population']),(0,0,0))
        _,screen=load_visible_inputs()
        selected=next(row for row in screen['rows']
                      if row['body_id']==first['selected_body_id'] and row['year']==2026)
        self.assertEqual(selected['accessibility_status'],'SCREENED')
        self.assertEqual([status for _,status in first['epoch_commits']],
                         ['ALREADY_MATCHED','COMMITTED','COMMITTED','COMMITTED'])

        replay=run_world_remote_choice(reference_service='reference_reader',
            runtime_service='runtime',run_id=run_id)
        self.assertEqual([status for _,status in replay['epoch_commits']],['ALREADY_MATCHED']*4)
        for key in ('choice','selected_candidate_id','selected_body_id','observation_id',
                    'observation_signal','posterior','public_balance','candidate_mission_digest'):
            self.assertEqual(replay[key],first[key],key)

        with psycopg.connect(service='runtime') as conn:
            for table,expected in (
                ('wa_run.world_binding',1),('wa_run.mission',1),('wa_run.observation',1),
                ('wa_info.information_artifact',1),('wa_info.possession',1),('wa_info.belief',1),
                ('wa_run.project',0),('wa_run.project_location',0),('wa_run.stock_state',0),
                ('wa_run.asset',0),('wa_run.settlement',0)):
                count=conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',(run_id,)).fetchone()[0]
                self.assertEqual(count,expected,table)
            mission=conn.execute('SELECT project_id,target_location_id,body_id,interaction_contract_ref '
                'FROM wa_run.mission WHERE run_id=%s',(run_id,)).fetchone()
            observation=conn.execute('SELECT location_id,body_id,method_ref,measurement_schema_ref '
                'FROM wa_run.observation WHERE run_id=%s',(run_id,)).fetchone()
            self.assertIsNone(mission[0]);self.assertIsNone(mission[1]);self.assertIsNone(observation[0])
            self.assertEqual(mission[2],observation[1])
            selected_uuid=stable_uuid('BODY','LOOM_BODY_V1',first['selected_body_id'],'IDENTITY_V1')
            self.assertEqual(mission[2],selected_uuid)
            self.assertEqual(conn.execute('SELECT body_id FROM wa_run.world_binding WHERE run_id=%s',
                (run_id,)).fetchone()[0],selected_uuid)
            self.assertEqual(mission[3],'REMOTE:EXPLORATION_REQUEST_BODY_V1')
            self.assertEqual(observation[2:4],('REMOTE','BODY_REMOTE_SIGNAL_V1'))
            self.assertEqual(conn.execute('SELECT count(*) FROM wa_run.causal_envelope WHERE run_id=%s',
                (run_id,)).fetchone()[0],8)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_run.population_state "
                "WHERE run_id=%s AND position_key<>'EARTH'",(run_id,)).fetchone()[0],0)

        # NULL location is admitted only for the two explicit body REMOTE
        # contracts. A fabricated unbound mission/observation still fails.
        with psycopg.connect(service='runtime',row_factory=dict_row) as conn:
            conn.execute('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')
            def insert_copy(table,row):
                cols=tuple(row)
                conn.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                    sql.SQL(table),sql.SQL(',').join(map(sql.Identifier,cols)),
                    sql.SQL(',').join(sql.Placeholder() for _ in cols)),tuple(row.values()))
            mission=dict(conn.execute('SELECT * FROM wa_run.mission WHERE run_id=%s',(run_id,)).fetchone())
            observation=dict(conn.execute('SELECT * FROM wa_run.observation WHERE run_id=%s',(run_id,)).fetchone())
            with self.assertRaises(psycopg.errors.CheckViolation):
                with conn.transaction():
                    insert_copy('wa_run.mission',mission|dict(mission_id='FORGED-UNBOUND',
                        interaction_contract_ref='REMOTE:OTHER'))
            with self.assertRaises(psycopg.errors.CheckViolation):
                with conn.transaction():
                    insert_copy('wa_run.observation',observation|dict(observation_id='FORGED-UNBOUND',
                        measurement_schema_ref='OTHER_SIGNAL'))


if __name__=='__main__':unittest.main()
