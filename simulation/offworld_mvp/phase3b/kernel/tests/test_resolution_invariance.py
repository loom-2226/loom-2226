import unittest
from decimal import Decimal as D

from offworld_kernel.build3 import RunIdentity
from offworld_kernel.build4 import OwnershipStake
from offworld_kernel.kernel import InvariantError
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.mvp_state import AggregateState, AgentKind, AgentState
from offworld_kernel.resolution import (
    ExposureAllocationBasis,
    ExposureSelectionBasis,
    ResolutionExposurePlan,
)
from offworld_kernel.resolution_fixture import paired_resolution_invariance_fixture


class ResolutionInvarianceTests(unittest.TestCase):
    def test_equal_member_plan_derives_quarter_share_not_free_parameter(self):
        plan=ResolutionExposurePlan(
            'P','AGG','FIRM_01',1,
            ExposureSelectionBasis.VALIDATION_FIXTURE_STABLE_ID,
            'FIXTURE:FIRM_01',
            ExposureAllocationBasis.EQUAL_MEMBER_PRO_RATA,
            'MODEL:EQUAL_MEMBER_PRO_RATA',
        )
        self.assertEqual(plan.validate_and_fraction(4),D('0.25'))

        bad=ResolutionExposurePlan(
            'P2','AGG','FIRM_01',1,
            ExposureSelectionBasis.VALIDATION_FIXTURE_STABLE_ID,
            'FIXTURE:FIRM_01',
            ExposureAllocationBasis.EQUAL_MEMBER_PRO_RATA,
            'MODEL:EQUAL_MEMBER_PRO_RATA',
            D('0.25'),
        )
        with self.assertRaisesRegex(InvariantError,'may not also supply explicit share'):
            bad.validate_and_fraction(4)

    def test_selection_and_allocation_require_declared_references(self):
        with self.assertRaisesRegex(InvariantError,'selection basis requires'):
            ResolutionExposurePlan(
                'P','AGG','FIRM_01',1,
                ExposureSelectionBasis.EXPLICIT_AUTHORIZED_ID,'',
                ExposureAllocationBasis.EQUAL_MEMBER_PRO_RATA,'MODEL:EQUAL_MEMBER_PRO_RATA',
            ).validate_and_fraction(4)

        with self.assertRaisesRegex(InvariantError,'allocation basis requires'):
            ResolutionExposurePlan(
                'P','AGG','FIRM_01',1,
                ExposureSelectionBasis.EXPLICIT_AUTHORIZED_ID,'AUTH:SELECT:FIRM_01',
                ExposureAllocationBasis.EQUAL_MEMBER_PRO_RATA,'',
            ).validate_and_fraction(4)

    def test_explicit_share_requires_declared_share(self):
        plan=ResolutionExposurePlan(
            'P','AGG','FIRM_01',1,
            ExposureSelectionBasis.EXPLICIT_AUTHORIZED_ID,
            'AUTH:SELECT:FIRM_01',
            ExposureAllocationBasis.EXPLICIT_AUTHORIZED_SHARE,
            'AUTH:SHARE:FIRM_01',
        )
        with self.assertRaisesRegex(InvariantError,'requires share'):
            plan.validate_and_fraction(4)

    def test_exposure_plan_reconciles_cash_resources_claims_and_live_ownership(self):
        aggregate_only,exposed=paired_resolution_invariance_fixture(1)
        k,result,trajectory,terminal,plan=exposed

        self.assertEqual(len(k.resolution_exposure_records),1)
        rec=k.resolution_exposure_records[0]
        self.assertEqual(rec.plan_id,plan.plan_id)
        self.assertEqual(rec.selection_basis,'VALIDATION_FIXTURE_STABLE_ID')
        self.assertEqual(rec.selection_ref,'FIXTURE:RESOLUTION_EQUIVALENCE:FIRM_01')
        self.assertEqual(rec.allocation_basis,'EQUAL_MEMBER_PRO_RATA')
        self.assertEqual(rec.allocation_fraction,D('0.25'))

        self.assertEqual(k.state.accounts['sector_cash'].balance,D('87'))
        self.assertEqual(k.state.accounts['firm_cash'].balance,D('29'))
        self.assertEqual(k.aggregates['FIRM_SECTOR'].member_count,3)
        self.assertEqual(k.aggregates['FIRM_SECTOR'].resource_holdings['RESOURCE_X'],D('30'))
        self.assertEqual(k.agents['FIRM_01'].resource_holdings['RESOURCE_X'],D('10'))
        self.assertEqual(k.aggregates['FIRM_SECTOR'].claim_holdings['VEH'],D('0.75'))
        self.assertEqual(k.agents['FIRM_01'].claim_holdings['VEH'],D('0.25'))

        live={(s.owner_id,s.vehicle_id):s.share for s in k.ownership_stakes}
        self.assertEqual(live[('FIRM_SECTOR','VEH')],D('0.75'))
        self.assertEqual(live[('FIRM_01','VEH')],D('0.25'))
        self.assertEqual(sum((s.share for s in k.ownership_stakes if s.vehicle_id=='VEH'),D('0')),D('1'))

    def test_same_horizon_is_pathwise_resolution_invariant(self):
        aggregate_only,exposed=paired_resolution_invariance_fixture(5)
        ka,ra,ta,terminal_a,plan_a=aggregate_only
        ke,re,te,terminal_e,plan_e=exposed

        # Same represented economic trajectory despite different representation.
        self.assertEqual(len(ta),5)
        self.assertEqual(len(te),5)
        for (year_a,total_a),(year_e,total_e) in zip(ta,te):
            with self.subTest(year=year_a):
                self.assertEqual(year_a,year_e)
                self.assertEqual(total_a,total_e)

        self.assertEqual(terminal_a,terminal_e)
        self.assertEqual(terminal_a.represented_cash,D('180'))
        self.assertEqual(terminal_a.source_cash,D('920'))
        self.assertEqual(terminal_a.all_non_boundary_cash,D('1100'))
        self.assertEqual(terminal_a.represented_members,4)
        self.assertEqual(dict(terminal_a.resource_totals),{'RESOURCE_X':D('40')})
        self.assertEqual(dict(terminal_a.claim_totals),{'VEH':D('1')})
        self.assertEqual(dict(terminal_a.live_ownership_totals),{'VEH':D('1')})
        self.assertEqual(terminal_a.value_paid_to_representation,D('80'))

        # Representation differs, as intended.
        self.assertNotIn('FIRM_01',ka.agents)
        self.assertIn('FIRM_01',ke.agents)
        self.assertEqual(len(ka.resolution_exposure_records),0)
        self.assertEqual(len(ke.resolution_exposure_records),1)

        # The invariant comparison is about system totals, not byte-identical runs.
        self.assertNotEqual(ra.final_fingerprint,re.final_fingerprint)

    def test_exposure_plan_event_records_why_identity_and_share_exist(self):
        _,exposed=paired_resolution_invariance_fixture(1)
        k,_,_,_,_=exposed
        plan_events=[e for e in k.event_log if e['kind']=='AGGREGATE_TO_AGENT_EXPOSURE_PLAN']
        self.assertEqual(len(plan_events),1)
        e=plan_events[0]
        self.assertEqual(e['selection_basis'],'VALIDATION_FIXTURE_STABLE_ID')
        self.assertEqual(e['selection_ref'],'FIXTURE:RESOLUTION_EQUIVALENCE:FIRM_01')
        self.assertEqual(e['allocation_basis'],'EQUAL_MEMBER_PRO_RATA')
        self.assertEqual(e['allocation_fraction'],'0.25')


if __name__=='__main__':
    unittest.main()
