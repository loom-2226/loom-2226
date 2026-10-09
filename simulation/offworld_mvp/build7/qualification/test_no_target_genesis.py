"""Increment 1 proof: generated WORLD exists before any Offworld target does."""
import os
import unittest
from decimal import Decimal as D
from unittest.mock import patch
from uuid import uuid4

from simulation.offworld_mvp.build6e.named_world import _runtime_epoch_rows
from simulation.offworld_mvp.build7.generated_campaign import (
    _build_kernel, _record_empty_year, _target_from_generated, load_config,
    main, resume_world_run, start_world_run,
)


WORLD = dict(scenario_id='00000000-0000-0000-0000-000000000001',
             scenario_key='SOLAR_WATER_NO_TARGET_TEST', sealed_world_digest='0'*64,
             body_count=90)
FORBIDDEN = {'wa_run.world_binding', 'wa_run.stock_state',
             'wa_run.accessibility_assessment', 'wa_run.recoverability_assessment',
             'wa_run.reserve_interpretation', 'wa_run.project',
             'wa_run.project_location', 'wa_run.project_party',
             'wa_run.settlement', 'wa_run.settlement_location',
             'wa_run.settlement_state', 'wa_run.settlement_asset',
             'wa_run.asset', 'wa_run.asset_location',
             'wa_run.mission', 'wa_run.observation'}


class NoTargetGenesisTests(unittest.TestCase):
    def test_normal_new_accepts_seed_without_body(self):
        with patch('simulation.offworld_mvp.build7.generated_campaign.start_world_run',
                   return_value={'run_id':'TEST'}) as start, patch('builtins.print'):
            main(['new','--world-seed','TEST'])
        self.assertEqual(start.call_args.kwargs['world_seed'],'TEST')
        self.assertNotIn('body',start.call_args.kwargs)

    def test_unbound_kernel_and_compiler_have_no_selected_offworld_history(self):
        kernel,history=_build_kernel(None,load_config(),world_seed='TEST',world=WORLD)
        self.assertEqual(len(kernel.agents),3)
        self.assertEqual(kernel.capital_coupling['USA'],{'F':D(0),'X':D(0),'R':D(0),'S':D(0)})
        self.assertEqual(kernel.state.projects,{})
        self.assertEqual(kernel.colonies,{})
        self.assertEqual(kernel.resources,{})
        self.assertEqual(kernel.population.offworld,{})
        self.assertEqual(kernel.population.in_transit,{})
        self.assertEqual(set(kernel.state.nodes),{'EARTH:USA'})
        self.assertNotIn('site_binding_key',dict(kernel.boundary_manifest.parameters))
        self.assertNotIn('build7.site_node_id',dict(kernel.boundary_manifest.parameters))
        self.assertNotIn('PRIMARY_TARGET',repr(kernel.boundary_manifest))
        self.assertFalse(any('GEN_SITE' in str(value) or 'AUTHORED_SITE' in str(value)
                             for value in kernel.boundary_manifest.assertions))
        self.assertTrue(all(not actor.information for actor in kernel.agents.values()))
        _record_empty_year(kernel,history,2026)
        rows,terminals=_runtime_epoch_rows(kernel,None,first=True,start_index=0,
            epoch_id='ACTION:1:record_earth_reference_year',agent_logins={})
        tables={table for table,_ in rows}
        self.assertTrue({'wa_run.execution','wa_run.causal_envelope','wa_run.artifact',
                         'wa_run.actor_reference','wa_run.population_origin',
                         'wa_run.population_state'}<=tables)
        self.assertFalse(tables & FORBIDDEN)
        population=[row for table,row in rows if table=='wa_run.population_state']
        self.assertEqual(len(population),1)
        self.assertEqual(population[0]['position_key'],'EARTH')
        self.assertEqual(len(terminals),2)

    def test_bound_opening_still_projects_targeted_rows(self):
        binding=dict(body_key='CERES',body_name='Ceres',body_id='00000000-0000-0000-0000-000000000002',
            scenario_id=WORLD['scenario_id'],scenario_key=WORLD['scenario_key'],
            model_id='00000000-0000-0000-0000-000000000003',
            policy_id='00000000-0000-0000-0000-000000000004',
            world_id='00000000-0000-0000-0000-000000000005',
            world_site_id='00000000-0000-0000-0000-000000000006',
            deposit_id='00000000-0000-0000-0000-000000000007',
            site_id='00000000-0000-0000-0000-000000000008',
            feature_id='00000000-0000-0000-0000-000000000009',
            resource_class='WATER_BEARING_MATERIAL',block={'target_mass_kg':D('123000000')},
            result_hash='0'*64)
        target=_target_from_generated(binding,load_config())
        kernel,history=_build_kernel(target,load_config(),world_seed='TEST')
        _record_empty_year(kernel,history,2026)
        rows,_=_runtime_epoch_rows(kernel,target['binding'],first=True,start_index=0,
            epoch_id='ACTION:1:record_earth_reference_year',agent_logins={})
        tables=[table for table,_ in rows]
        for table in ('wa_run.world_binding','wa_run.stock_state',
                      'wa_run.accessibility_assessment','wa_run.recoverability_assessment',
                      'wa_run.reserve_interpretation','wa_run.project','wa_run.project_location',
                      'wa_run.settlement','wa_run.settlement_location'):
            self.assertIn(table,tables)
        self.assertEqual(tables.count('wa_run.project'),2)
        self.assertEqual(tables.count('wa_run.settlement'),1)
        self.assertEqual(tables.count('wa_run.population_state'),3)


@unittest.skipUnless(os.getenv('PGSERVICEFILE'),'PGSERVICEFILE required for governed persistence proof')
class NoTargetPersistenceTests(unittest.TestCase):
    def test_commit_reopen_empty_year_and_exact_replay(self):
        import psycopg
        seed='BUILD7-INCR1-TEST-'+uuid4().hex
        opened=start_world_run(reference_service='reference_reader',science_writer_service='science_writer',
            world_writer_service='world_writer',runtime_service='runtime',world_seed=seed)
        run_id=opened['run_id']
        self.assertEqual(opened['generated_body_count'],90)
        self.assertEqual(opened['candidate_mission_count'],90)
        self.assertEqual(opened['epoch_commits'][0][1],'COMMITTED')
        first=resume_world_run(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2027)
        self.assertEqual(first['epoch_commits'][0][1],'ALREADY_MATCHED')
        self.assertEqual(first['epoch_commits'][1][1],'COMMITTED')
        self.assertEqual(first['candidate_mission_count'],90)
        replay=resume_world_run(reference_service='reference_reader',runtime_service='runtime',
            run_id=run_id,through_year=2027)
        self.assertEqual(replay['epoch_commits'],(
            ('ACTION:1:record_earth_reference_year','ALREADY_MATCHED'),
            ('ACTION:2:record_earth_reference_year','ALREADY_MATCHED')))
        self.assertEqual(replay['candidate_mission_digest'],first['candidate_mission_digest'])
        with psycopg.connect(service='runtime') as conn:
            scenario_id=conn.execute('SELECT scenario_id FROM wa_run.execution WHERE run_id=%s',(run_id,)).fetchone()[0]
            world_count=conn.execute('SELECT count(*) FROM wa_world.realization WHERE scenario_id=%s',(scenario_id,)).fetchone()[0]
            self.assertEqual(world_count,90)
            for table in FORBIDDEN:
                count=conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',(run_id,)).fetchone()[0]
                self.assertEqual(count,0,table)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_run.population_state WHERE run_id=%s AND position_key<>'EARTH'",(run_id,)).fetchone()[0],0)
            self.assertEqual(conn.execute("SELECT count(*) FROM wa_info.agent_fact WHERE run_id=%s AND value_lexeme LIKE '%%GEN_SITE%%'",(run_id,)).fetchone()[0],0)
            self.assertEqual(conn.execute('SELECT count(*) FROM wa_run.causal_envelope WHERE run_id=%s',(run_id,)).fetchone()[0],5)


if __name__=='__main__':
    unittest.main()
