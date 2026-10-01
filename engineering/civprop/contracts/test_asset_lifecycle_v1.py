import unittest
from engineering.civprop.contracts.asset_lifecycle_v1 import *
from engineering.civprop.method_lab.contracts import FacilityRecord, CapacityVector

def fac(fid='f1',kind='MINE',year=2030,capital=100.0):
    return FacilityRecord(fid,kind,'MOON','AUS',2029,year,'COMMISSIONED',capital,CapacityVector())

class AssetLifecycleV1Tests(unittest.TestCase):
    def test_unknown_policy_does_not_invent_decay_or_maintenance(self):
        s=AssetLifecycleRuntimeV1([]).project([fac()],2030,2032)
        self.assertTrue(all(x.depreciation is None and x.maintenance_required is None for x in s))
        self.assertEqual(s[0].usable_capacity_fraction,1)
        self.assertTrue(all(x.usable_capacity_fraction is None for x in s[1:]))
        self.assertTrue(all(x.status==UNKNOWN for x in s[1:]))
    def test_explicit_depreciation_and_maintenance(self):
        p=LifecyclePolicyV1('MINE',.10,2,.05)
        s=AssetLifecycleRuntimeV1([p]).project([fac()],2030,2032)
        self.assertAlmostEqual(s[1].closing_gross_productive_capital,81.0)
        self.assertTrue(s[2].maintenance_required)
        self.assertAlmostEqual(s[2].maintenance_requirement,4.05)
    def test_failure_removes_usable_capacity(self):
        s=AssetLifecycleRuntimeV1([], [LifecycleEventV1(2031,'f1','FAILURE')]).project([fac()],2030,2032)
        self.assertEqual(s[1].status,FAILED); self.assertEqual(s[1].usable_capacity_fraction,0)
    def test_retirement_and_abandonment_remove_capacity(self):
        for kind in ('RETIREMENT','ABANDONMENT'):
            s=AssetLifecycleRuntimeV1([], [LifecycleEventV1(2031,'f1',kind)]).project([fac()],2030,2031)
            self.assertEqual(s[-1].usable_capacity_fraction,0)
    def test_explicit_service_life_retires(self):
        s=AssetLifecycleRuntimeV1([LifecyclePolicyV1('MINE',service_life_years=2)]).project([fac()],2030,2032)
        self.assertEqual(s[-1].status,RETIRED)
    def test_replacement_is_separate_from_growth(self):
        s=AssetLifecycleRuntimeV1([], [LifecycleEventV1(2031,'f1','REPLACEMENT',25)]).project([fac()],2030,2031)
        self.assertEqual(s[-1].replacement_investment,25); self.assertEqual(s[-1].growth_investment,0)
        self.assertEqual(s[-1].closing_gross_productive_capital,125)
    def test_restore_can_return_failed_asset_to_service(self):
        ev=[LifecycleEventV1(2031,'f1','FAILURE'),LifecycleEventV1(2032,'f1','RESTORE')]
        s=AssetLifecycleRuntimeV1([],ev).project([fac()],2030,2032)
        self.assertEqual(s[-1].status,ACTIVE); self.assertEqual(s[-1].usable_capacity_fraction,1)
    def test_failure_suppresses_production(self):
        from types import SimpleNamespace
        lifecycle=AssetLifecycleRuntimeV1([], [LifecycleEventV1(2031,'f1','FAILURE')]).project([fac()],2030,2031)
        prod=[SimpleNamespace(year=2031,facility_id='f1',physical_output_status='KNOWN',physical_output_quantity=80.0)]
        row=project_production_through_lifecycle(prod,lifecycle)[0]
        self.assertEqual(row.post_lifecycle_output_status,'KNOWN'); self.assertEqual(row.post_lifecycle_output_quantity,0.0)

    def test_unknown_lifecycle_propagates_unknown_production(self):
        from types import SimpleNamespace
        lifecycle=AssetLifecycleRuntimeV1([]).project([fac()],2030,2031)
        prod=[SimpleNamespace(year=2031,facility_id='f1',physical_output_status='KNOWN',physical_output_quantity=80.0)]
        row=project_production_through_lifecycle(prod,lifecycle)[0]
        self.assertEqual(row.post_lifecycle_output_status,'UNKNOWN'); self.assertIsNone(row.post_lifecycle_output_quantity)

    def test_terminal_state_persists_without_policy(self):
        states=AssetLifecycleRuntimeV1([], [LifecycleEventV1(2031,'f1','FAILURE')]).project([fac()],2030,2033)
        by_year={x.year:x for x in states}
        self.assertEqual(by_year[2031].status,'FAILED')
        self.assertEqual(by_year[2032].status,'FAILED')
        self.assertEqual(by_year[2033].status,'FAILED')
        self.assertEqual(by_year[2033].usable_capacity_fraction,0.0)

    def test_invalid_parameters_fail_closed(self):
        with self.assertRaises(ValueError): LifecyclePolicyV1('MINE',1.1)
        with self.assertRaises(ValueError): LifecyclePolicyV1('MINE',maintenance_interval_years=0)
        with self.assertRaises(ValueError): LifecycleEventV1(2030,'f1','FAILURE',1)

if __name__=='__main__': unittest.main()
