"""Two-project isolation for Build 7's existing REGION study contracts."""
import unittest
from decimal import Decimal
from types import SimpleNamespace

from offworld_kernel.boundary import _resolve_live
from offworld_kernel.project_study import region_study_activity_id, region_study_plan_id


class ProjectStudyIsolationTests(unittest.TestCase):
    def test_study_fact_resolution_uses_project_scope_and_unique_activity(self):
        project_ids=('PROSPECT:BODY_A:REGION_01','PROSPECT:BODY_B:REGION_01')
        activities={region_study_activity_id(pid):SimpleNamespace(
            id=region_study_activity_id(pid),project_id=pid,status=SimpleNamespace(value='PROPOSED'),
            capital_commitment=Decimal('1'),priority=1) for pid in project_ids}
        projects={pid:SimpleNamespace(id=pid,owners={'SPN':Decimal(1)},
            cash_account_id='cash:'+str(i),status='EXPLORING')
            for i,pid in enumerate(project_ids)}
        plans={region_study_plan_id(pid):SimpleNamespace(
            id=region_study_plan_id(pid),project_id=pid,next_maturity=SimpleNamespace(value='SURFACE_OR_SAMPLE_CHARACTERIZED'))
            for pid in project_ids}
        kernel=SimpleNamespace(
            boundary_manifest=SimpleNamespace(source_resolver_bindings=(),parameters=(),
                run_id='RUN',authorization_ref='TEST',scenario_id='SCENARIO'),
            state=SimpleNamespace(projects=projects,accounts={
                'cash:0':SimpleNamespace(balance=Decimal('17')),
                'cash:1':SimpleNamespace(balance=Decimal('29'))}),
            project_activities=activities,project_study_plans=plans,
            project_study_states={pid:SimpleNamespace(maturity=SimpleNamespace(value='REMOTE_CHARACTERIZED'))
                for pid in project_ids},project_study_result_records=[],agents={'SPN':SimpleNamespace(information=set())},
            causal_envelopes=[])
        resolved=[]
        for pid in project_ids:
            concept='activity.'+region_study_activity_id(pid)+'.PROJECT_ID'
            request=SimpleNamespace(consumer_id='SPN',subject_id=pid,scope='PROJECT:'+pid,
                concept=concept,world_context='REALIZED',context_id='RUN',perspective='AGENT',
                perspective_actor_id='SPN',effective_time='1',knowledge_cutoff='1',
                required_unit='IDENTITY',required_role='ADMITTED_INFORMATION',
                request_id='FACT:'+pid,time_basis='SIM_TIME')
            resolved.append(_resolve_live(kernel,request).value)
        self.assertEqual(tuple(resolved),project_ids)


if __name__=='__main__':
    unittest.main()
