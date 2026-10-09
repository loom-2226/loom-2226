"""A body REMOTE mission can follow a separately bound REGION project."""
import os
import unittest
from dataclasses import replace
from decimal import Decimal as D
from hashlib import sha256
from uuid import uuid4

from loom_world_authority import store
from offworld_kernel import policy_runner as workers
from offworld_kernel.exploration_protocol import build_exploration_request
from offworld_kernel.mvp_state import BodyRemoteObservation
from simulation.offworld_mvp.build6e.named_world import (
    BodyRemoteBinding, NamedWorldBlocked,
    _check_retained_prospecting_projects_for_remote,
)
from simulation.offworld_mvp.build7 import generated_campaign as campaign
from simulation.offworld_mvp.build7 import runtime_flow as flow
from simulation.offworld_mvp.build7.exploration_choice import choose_remote_characterization


@unittest.skipUnless(os.getenv('PGSERVICEFILE'), 'PGSERVICEFILE required for governed persistence proof')
class PostProjectRemotePersistenceTests(unittest.TestCase):
    def test_second_body_preserves_project_and_replays_with_spatial_guards(self):
        import psycopg

        opened=campaign.start_world_run(reference_service='reference_reader',
            science_writer_service='science_writer',world_writer_service='world_writer',
            runtime_service='runtime',world_seed='BUILD7-I6-POSTPROJECT-'+uuid4().hex)
        run_id=opened['run_id']

        def execute():
            k,h,_,opening=campaign.run_world_prospecting_initiation(
                reference_service='reference_reader',runtime_service='runtime',run_id=run_id,
                _return_runtime=True)
            self.assertEqual(opening['prospecting_decision'],'INITIATE_PROJECT')
            project_id=opening['project_id']
            project=k.state.projects[project_id]
            project_cash=k.state.accounts[project.cash_account_id].balance
            capital=dict(k.capital_coupling['USA'])
            commitments=len(k.state.commitments)
            transactions=len(k.state.transactions)
            actor=k.agents['PUB']
            characterized={obs.body_id for obs in k.observations.values()
                if isinstance(obs,BodyRemoteObservation) and obs.id in actor.information}
            key=sha256((campaign.load_config()['runtime']['policy_seed']+
                '|PUB|2027|BODY_REMOTE_CHOICE_V1').encode()).hexdigest()
            cost=next(a.value for a in k.boundary_manifest.assertions
                if a.assertion_id=='PUB:exploration.REMOTE_COST')
            choice=choose_remote_characterization(
                candidates=campaign.derive_world_mission_candidates(k,h,2027),
                characterized_bodies=characterized,
                public_balance=k.state.accounts[actor.account_id].balance,
                remote_cost=cost,decision_key=key)
            self.assertEqual(choice.outcome,'SELECT')
            self.assertNotEqual(choice.body_id,opening['selected_body_id'])
            with psycopg.connect(service='runtime') as conn:
                scenario_id,world_id,body_id=store.read_run_body_world_identity(
                    conn,run_id,choice.body_id)
            h['named_binding']=BodyRemoteBinding(scenario_id,world_id,body_id,
                choice.body_id,'BODY_REMOTE:2027:'+choice.body_id)
            request=build_exploration_request('BODY_REMOTE:2027:'+choice.body_id,2,
                '','','REMOTE',body_id=choice.body_id,question_ref=campaign.BODY_QUESTION)
            decision,decision_ref=flow.policy_epoch(k,h,'BODY_REMOTE:2027:'+choice.body_id,
                'PUB','2',request,('exploration.REMOTE_COST',),
                workers.run_public_explorer_policy,workers.public_explorer_policy_version())
            self.assertEqual(decision.outcome.value,'AUTHORIZE')
            params=h['params']
            observations,asset,_=flow.system_epoch(k,h,'explore_paid','2',
                (2,'PUB','','','earth_supplier',decision.authorized_cost),
                dict(channel='REMOTE',public=False,false_positive=D(params['remote_fp']),
                    false_negative=D(params['remote_fn']),update_belief=False,
                    parent_ids=(decision.id,),body_id=choice.body_id,
                    question_ref=campaign.BODY_QUESTION),(decision_ref,))
            self.assertIsNone(asset)
            self.assertEqual(len(observations),4)
            for obs in observations:
                flow.system_epoch(k,h,'update_agent_belief_from_observation','2',
                    (2,'PUB',obs.id,'BODY:'+choice.body_id+':'+obs.question_ref,
                     D(params['remote_detection']),D(params['remote_fp']),
                     'BUILD7_BODY_MATERIAL_REMOTE_V1',campaign.AUTHORIZATION),
                    decision_refs=(decision_ref,))
            self.assertEqual(k.state.projects[project_id].status,'EXPLORING')
            self.assertEqual(k.state.accounts[project.cash_account_id].balance,project_cash)
            self.assertEqual(k.capital_coupling['USA'],capital)
            self.assertEqual(len(k.state.commitments),commitments)
            self.assertEqual(len(k.state.transactions),transactions+1)  # PUBLIC mission payment
            return k,h,opening,choice,observations

        first=execute()
        with psycopg.connect(service='runtime') as conn:
            before=tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                (run_id,)).fetchone()[0] for table in
                ('wa_run.mission','wa_run.observation','wa_run.project',
                 'wa_run.project_location','wa_run.world_binding','wa_info.belief'))
            self.assertEqual(before,(2,8,1,1,2,12))  # PUB: eight; SPN: four
            missions=conn.execute('SELECT mission_id,body_id,world_id FROM wa_run.mission '
                'WHERE run_id=%s ORDER BY mission_id',(run_id,)).fetchall()
            self.assertEqual(len({row[1] for row in missions}),2)
            bindings=conn.execute('SELECT body_id,world_id FROM wa_run.world_binding '
                'WHERE run_id=%s',(run_id,)).fetchall()
            self.assertEqual({(body,world) for _,body,world in missions},set(bindings))
            for mission_id,body_id,world_id in missions:
                self.assertEqual(conn.execute('SELECT count(*) FROM wa_run.observation '
                    'WHERE run_id=%s AND mission_id=%s AND body_id=%s AND world_id=%s',
                    (run_id,mission_id,body_id,world_id)).fetchone()[0],4)
            self.assertEqual(conn.execute('SELECT count(*) FROM wa_run.project_location pl '
                'JOIN wa_geo.location l ON l.location_id=pl.location_id '
                "WHERE pl.run_id=%s AND pl.project_id=%s AND pl.binding_key='PROSPECTING_REGION' "
                'AND l.body_id=%s',(run_id,first[2]['project_id'],
                store.stable_uuid('BODY','LOOM_BODY_V1',first[2]['selected_body_id'],
                    'IDENTITY_V1'))).fetchone()[0],1)
            self.assertEqual(conn.execute('SELECT count(*) FROM wa_info.action_authorization a '
                'JOIN wa_run.mission m ON a.run_id=m.run_id '
                'AND a.planned_action_ref=m.planned_activity_artifact_ref '
                'WHERE m.run_id=%s',(run_id,)).fetchone()[0],2)
            beliefs=conn.execute('SELECT actor_id,split_part(belief_key,\':\',2),count(*) '
                'FROM wa_info.belief WHERE run_id=%s GROUP BY 1,2',(run_id,)).fetchall()
            self.assertEqual(set(beliefs),{
                ('PUB',first[2]['selected_body_id'],4),('PUB',first[3].body_id,4),
                ('SPN',first[2]['selected_body_id'],4)})

        replay=execute()
        self.assertTrue(all(status=='ALREADY_MATCHED' for _,status in replay[1]['epoch_commits']))
        self.assertEqual([(o.id,o.signal) for o in first[4]],
                         [(o.id,o.signal) for o in replay[4]])
        with psycopg.connect(service='runtime') as conn:
            after=tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                (run_id,)).fetchone()[0] for table in
                ('wa_run.mission','wa_run.observation','wa_run.project',
                 'wa_run.project_location','wa_run.world_binding','wa_info.belief'))
        self.assertEqual(after,before)

        # A forged project-region relationship cannot accompany a REMOTE epoch.
        k,h,opening,choice,_=replay
        original=k.prospecting_project_creation_records[0]
        k.prospecting_project_creation_records[0]=replace(original,location_id=str(uuid4()))
        with self.assertRaisesRegex(NamedWorldBlocked,'BLOCKED_BODY_REMOTE_PROJECT_ORIGIN'):
            _check_retained_prospecting_projects_for_remote(
                k,k.causal_envelopes,len(k.causal_envelopes))
        k.prospecting_project_creation_records[0]=original

        # A body-B request carried under body A's binding still fails admission.
        with psycopg.connect(service='runtime') as conn:
            scenario_id,world_id,body_id=store.read_run_body_world_identity(
                conn,run_id,opening['selected_body_id'])
        h['named_binding']=BodyRemoteBinding(scenario_id,world_id,body_id,
            opening['selected_body_id'],'BODY_REMOTE:WRONG:'+opening['selected_body_id'])
        request=build_exploration_request('BODY_REMOTE:WRONG:'+choice.body_id,2,
            '','','REMOTE',body_id=choice.body_id,question_ref=campaign.BODY_QUESTION)
        with self.assertRaisesRegex(NamedWorldBlocked,'BLOCKED_BODY_REMOTE_MISSION_SCOPE'):
            flow.policy_epoch(k,h,'BODY_REMOTE:WRONG:'+choice.body_id,'PUB','2',request,
                ('exploration.REMOTE_COST',),workers.run_public_explorer_policy,
                workers.public_explorer_policy_version())


if __name__=='__main__':unittest.main()
